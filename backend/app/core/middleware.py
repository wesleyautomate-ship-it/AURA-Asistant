"""
Authentication middleware for JWT validation, RBAC, and security
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import logging
import time
from datetime import datetime, timedelta
import json
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from .database import get_db
from .models import User, UserSession, Role, Permission, AuditLog
from .utils import verify_jwt_token, sanitize_input
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Rate limiter instance
rate_limiter = RateLimiter()

class AuthMiddleware:
    """Authentication middleware class"""
    
    def __init__(self, app):
        self.app = app
        self.rate_limiter = RateLimiter()
    
    async def __call__(self, scope, receive, send):
        """Process request through authentication middleware"""
        
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Add security headers
            async def send_with_headers(message):
                if message["type"] == "http.response.start":
                    message["headers"].extend([
                        (b"X-Content-Type-Options", b"nosniff"),
                        (b"X-Frame-Options", b"DENY"),
                        (b"X-XSS-Protection", b"1; mode=block"),
                        (b"Strict-Transport-Security", b"max-age=31536000; includeSubDomains"),
                        (b"Content-Security-Policy", b"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"),
                        (b"Referrer-Policy", b"strict-origin-when-cross-origin")
                    ])
                await send(message)
            
            await self.app(scope, receive, send_with_headers)
        else:
            await self.app(scope, receive, send)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured request/response logging middleware."""

    def __init__(self, app, logger_name: str = "app.request"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        self.logger.info(
            "incoming_request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed = time.perf_counter() - start_time
            self.logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "elapsed_ms": round(elapsed * 1000, 2),
                }
            )
            raise exc

        elapsed = time.perf_counter() - start_time
        self.logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": round(elapsed * 1000, 2),
            }
        )

        if request_id:
            response.headers["X-Request-ID"] = request_id

        return response

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Authenticated user object
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify JWT token
        payload = verify_jwt_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Get user from database
        user_id = int(payload.get("sub"))
        try:
            user = db.query(User).filter(User.id == user_id).first()
        except Exception as db_error:
            logger.error(f"Database error in authentication: {db_error}")
            # If database is unavailable, create a minimal user object from token
            user = User(
                id=user_id,
                email=payload.get("email", "unknown@example.com"),
                role=payload.get("role", "agent"),
                is_active=True
            )
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if user.is_locked:
            raise HTTPException(
                status_code=401,
                detail="User account is locked",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if session is still valid
        session = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.session_token == credentials.credentials,
            UserSession.is_active == True
        ).first()
        
        if not session or session.is_expired:
            raise HTTPException(
                status_code=401,
                detail="Session expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Update session last used time
        session.last_used = datetime.utcnow()
        db.commit()
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_roles(required_roles: List[str]):
    """
    Decorator to require specific roles
    
    Args:
        required_roles: List of required roles
        
    Returns:
        Dependency function
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

def require_permissions(required_permissions: List[str]):
    """
    Decorator to require specific permissions
    
    Args:
        required_permissions: List of required permissions
        
    Returns:
        Dependency function
    """
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Get user's roles and their permissions
        user_roles = db.query(Role).join(
            Role.users
        ).filter(User.id == current_user.id).all()
        
        user_permissions = set()
        for role in user_roles:
            for permission in role.permissions:
                user_permissions.add(permission.name)
        
        # Check if user has all required permissions
        missing_permissions = set(required_permissions) - user_permissions
        if missing_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Missing permissions: {', '.join(missing_permissions)}"
            )
        
        return current_user
    return permission_checker

def rate_limit(requests_per_minute: int = 60):
    """
    Rate limiting decorator
    
    Args:
        requests_per_minute: Maximum requests per minute
        
    Returns:
        Dependency function
    """
    def rate_limiter_checker(request: Request):
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        if not rate_limiter.is_allowed(client_ip, user_agent, requests_per_minute):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
    
    return rate_limiter_checker

def log_audit_event(
    event_type: str,
    event_data: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None
):
    """
    Log audit event
    
    Args:
        event_type: Type of event
        event_data: Event data
        success: Whether event was successful
        error_message: Error message if failed
    """
    def audit_logger(
        request: Request,
        current_user: Optional[User] = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        try:
            audit_log = AuditLog(
                user_id=current_user.id if current_user else None,
                event_type=event_type,
                event_data=json.dumps(event_data) if event_data else None,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                success=success,
                error_message=error_message
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    return audit_logger

def validate_input_data():
    """
    Input validation middleware
    """
    def input_validator(request: Request):
        # This would be implemented based on specific endpoint requirements
        # For now, we'll just sanitize basic inputs
        pass
    
    return input_validator

# Convenience functions for common role checks
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_agent_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require agent or admin role"""
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Agent or admin access required")
    return current_user

def require_employee_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require employee or admin role"""
    if current_user.role not in ["employee", "admin"]:
        raise HTTPException(status_code=403, detail="Employee or admin access required")
    return current_user

# Optional authentication for endpoints that can work with or without auth
def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise
    
    Args:
        credentials: Optional HTTP authorization credentials
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
