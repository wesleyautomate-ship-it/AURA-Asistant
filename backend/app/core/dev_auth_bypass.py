#!/usr/bin/env python3
"""
Development Authentication Bypass
=================================

This module provides development-only authentication bypass functionality.
It should NEVER be used in production environments.

Features:
- Auto-login with predefined development users
- Bypass authentication middleware in development
- Generate valid JWT tokens for development users
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import jwt
try:
    from jwt.exceptions import JWTError
except ImportError:
    # For older versions of PyJWT
    from jwt import InvalidTokenError as JWTError

from .settings import SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
# Simplified imports to avoid circular dependencies
# from .database import get_db
# from .models import User
# from .token_manager import generate_access_token

# Development users - NEVER use in production
DEV_USERS = {
    "admin": {
        "id": 1,
        "email": "admin@dubai-estate.com",
        "first_name": "Development",
        "last_name": "Admin",
        "role": "admin",
        "is_active": True,
        "email_verified": True
    },
    "agent": {
        "id": 2,
        "email": "agent@dubai-estate.com", 
        "first_name": "Development",
        "last_name": "Agent",
        "role": "agent",
        "is_active": True,
        "email_verified": True
    },
    "employee": {
        "id": 3,
        "email": "employee@dubai-estate.com",
        "first_name": "Development", 
        "last_name": "Employee",
        "role": "employee",
        "is_active": True,
        "email_verified": True
    }
}

def is_development_mode() -> bool:
    """Check if we're running in development mode"""
    # Check DISABLE_AUTH flag first (for explicit bypass)
    disable_auth = os.getenv("DISABLE_AUTH", "false").lower() in ("true", "1", "yes")
    if disable_auth:
        print(f"[DEV_AUTH] DISABLE_AUTH is set, returning True")
        return True
    
    environment = os.getenv("ENVIRONMENT", "development")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    result = environment in ["development", "docker"] or debug
    print(f"[DEV_AUTH] Environment: {environment}, Debug: {debug}, Result: {result}")
    return result

def get_dev_user(role: str = "agent") -> Optional[Dict[str, Any]]:
    """
    Get a development user by role
    
    Args:
        role: User role (admin, agent, employee)
        
    Returns:
        Development user data or None if not in dev mode
    """
    if not is_development_mode():
        return None
        
    return DEV_USERS.get(role, DEV_USERS["agent"])

def create_dev_token(role: str = "agent") -> Optional[str]:
    """
    Create a development JWT token
    
    Args:
        role: User role for the token
        
    Returns:
        JWT token string or None if not in dev mode
    """
    if not is_development_mode():
        return None
        
    dev_user = get_dev_user(role)
    if not dev_user:
        return None
        
    # Create token with development user data
    token_data = {
        "sub": str(dev_user["id"]),
        "email": dev_user["email"],
        "role": dev_user["role"],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "dev_mode": True  # Flag to indicate this is a dev token
    }
    
    return jwt.encode(token_data, SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_dev_current_user(
    # db: Session = Depends(get_db)  # Simplified for development
) -> Optional[dict]:
    """
    Get current user with development bypass
    
    This function can be used as a dependency to automatically
    authenticate development users without requiring login.
    """
    if not is_development_mode():
        return None
        
    # Return a mock user object for development
    # In a real scenario, you might want to create/fetch from database
    dev_user_data = get_dev_user("agent")
    if not dev_user_data:
        return None
        
    # Create a mock User object
    class DevUser:
        def __init__(self, user_data):
            self.id = user_data["id"]
            self.email = user_data["email"]
            self.first_name = user_data["first_name"]
            self.last_name = user_data["last_name"]
            self.role = user_data["role"]
            self.is_active = user_data["is_active"]
            self.email_verified = user_data["email_verified"]
            self.is_dev_user = True
            
    return DevUser(dev_user_data)

def dev_login_endpoint_data(role: str = "agent") -> Dict[str, Any]:
    """
    Generate login response data for development
    
    Args:
        role: User role (admin, agent, employee)
        
    Returns:
        Login response data matching the real login endpoint
    """
    if not is_development_mode():
        raise HTTPException(
            status_code=403,
            detail="Development login not available in production"
        )
        
    dev_user = get_dev_user(role)
    if not dev_user:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid development role: {role}"
        )
        
    access_token = create_dev_token(role)
    if not access_token:
        raise HTTPException(
            status_code=500,
            detail="Failed to create development token"
        )
        
    return {
        "access_token": access_token,
        "refresh_token": f"dev-refresh-{role}",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": dev_user["id"],
            "email": dev_user["email"],
            "first_name": dev_user["first_name"],
            "last_name": dev_user["last_name"],
            "role": dev_user["role"],
            "is_active": dev_user["is_active"],
            "email_verified": dev_user["email_verified"]
        }
    }

# Development middleware bypass
def should_bypass_auth() -> bool:
    """Check if authentication should be bypassed in development"""
    return is_development_mode()

def get_dev_auth_headers(role: str = "agent") -> Dict[str, str]:
    """
    Get development authentication headers
    
    Args:
        role: User role for authentication
        
    Returns:
        Headers dict with Authorization header
    """
    if not is_development_mode():
        return {}
        
    token = create_dev_token(role)
    if not token:
        return {}
        
    return {"Authorization": f"Bearer {token}"}
