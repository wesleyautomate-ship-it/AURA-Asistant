from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import logging
import json

from app.core.database import get_db
from app.core.utils import hash_password, verify_password, generate_access_token, generate_refresh_token, verify_jwt_token, generate_session_token
from app.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class ErrorResponse(BaseModel):
    error: dict

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens"""
    try:
        # Find user by email
        result = db.execute(text("""
            SELECT id, email, password_hash, first_name, last_name, role, is_active, email_verified
            FROM users WHERE email = :email
        """), {"email": request.email})
        
        user_data = result.fetchone()
        
        if not user_data:
            logger.warning(f"Login attempt with non-existent email: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}}
            )
        
        # Check if user is active
        if not user_data.is_active:
            logger.warning(f"Login attempt with inactive user: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "ACCOUNT_DISABLED", "message": "Account is disabled"}}
            )
        
        # Verify password
        if not verify_password(request.password, user_data.password_hash):
            logger.warning(f"Login attempt with invalid password: {request.email}")
            # Log failed attempt to audit log
            db.execute(text("""
                INSERT INTO audit_logs (user_id, event_type, event_data, success, error_message, created_at)
                VALUES (:user_id, 'login_failed', :event_data, false, 'Invalid password', CURRENT_TIMESTAMP)
            """), {
                "user_id": user_data.id,
                "event_data": json.dumps({"email": request.email, "reason": "invalid_password"})
            })
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}}
            )
        
        # Generate tokens
        access_token = generate_access_token(user_data.id, user_data.email, user_data.role)
        refresh_token = generate_refresh_token(user_data.id)
        session_token = generate_session_token()
        
        # Store session
        expires_at = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        db.execute(text("""
            INSERT INTO user_sessions (user_id, session_token, refresh_token, expires_at, is_active, created_at, last_used)
            VALUES (:user_id, :session_token, :refresh_token, :expires_at, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {
            "user_id": user_data.id,
            "session_token": session_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at
        })
        
        # Log successful login
        db.execute(text("""
            INSERT INTO audit_logs (user_id, event_type, event_data, success, created_at)
            VALUES (:user_id, 'login_success', :event_data, true, CURRENT_TIMESTAMP)
        """), {
            "user_id": user_data.id,
            "event_data": json.dumps({"email": request.email})
        })
        
        db.commit()
        
        logger.info(f"Successful login for user: {request.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user_data.id,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "role": user_data.role
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "Authentication failed"}}
        )

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = verify_jwt_token(request.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid refresh token"}}
            )
        
        user_id = int(payload.get("sub"))
        
        # Check if refresh token exists and is active
        result = db.execute(text("""
            SELECT us.id, us.user_id, us.expires_at, us.is_active,
                   u.email, u.role, u.is_active as user_active
            FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            WHERE us.refresh_token = :refresh_token AND us.user_id = :user_id
        """), {"refresh_token": request.refresh_token, "user_id": user_id})
        
        session_data = result.fetchone()
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "INVALID_TOKEN", "message": "Refresh token not found"}}
            )
        
        if not session_data.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "TOKEN_REVOKED", "message": "Refresh token has been revoked"}}
            )
        
        if not session_data.user_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "ACCOUNT_DISABLED", "message": "Account is disabled"}}
            )
        
        if datetime.utcnow() > session_data.expires_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "TOKEN_EXPIRED", "message": "Refresh token has expired"}}
            )
        
        # Generate new access token
        access_token = generate_access_token(user_id, session_data.email, session_data.role)
        
        # Update session last_used
        db.execute(text("""
            UPDATE user_sessions 
            SET last_used = CURRENT_TIMESTAMP 
            WHERE id = :session_id
        """), {"session_id": session_data.id})
        
        # Log token refresh
        db.execute(text("""
            INSERT INTO audit_logs (user_id, event_type, event_data, success, created_at)
            VALUES (:user_id, 'token_refresh', :event_data, true, CURRENT_TIMESTAMP)
        """), {
            "user_id": user_id,
            "event_data": json.dumps({"session_id": session_data.id})
        })
        
        db.commit()
        
        logger.info(f"Token refreshed for user: {user_id}")
        
        return RefreshResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "Token refresh failed"}}
        )
