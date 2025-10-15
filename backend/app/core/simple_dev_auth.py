#!/usr/bin/env python3
"""
Simple Development Authentication Bypass
========================================

A simplified version of development authentication bypass that works
with the existing authentication system without complex JWT handling.
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .models import User
from .utils import generate_access_token, generate_refresh_token


def is_development_mode() -> bool:
    """Check if we're running in development mode"""
    environment = os.getenv("ENVIRONMENT", "development")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    return environment in ["development", "docker"] or debug


def get_or_create_dev_user(db: Session, role: str = "agent") -> Optional[User]:
    """
    Get or create a development user

    Args:
        db: Database session
        role: User role (admin, agent, employee)

    Returns:
        User object or None if not in dev mode
    """
    if not is_development_mode():
        return None

    # Development user emails
    dev_emails = {
        "admin": "admin@dubai-estate.com",
        "agent": "agent@dubai-estate.com",
        "employee": "employee@dubai-estate.com",
    }

    email = dev_emails.get(role, dev_emails["agent"])

    # Try to find existing user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Create development user if it doesn't exist
        from .utils import hash_password

        user = User(
            email=email,
            password_hash=hash_password("dev123"),  # Simple dev password
            first_name="Development",
            last_name=role.title(),
            role=role,
            is_active=True,
            email_verified=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def create_dev_login_response(user: User) -> Dict[str, Any]:
    """
    Create login response for development user

    Args:
        user: User object

    Returns:
        Login response data
    """
    if not is_development_mode():
        raise HTTPException(
            status_code=403, detail="Development login not available in production"
        )

    # Generate tokens using existing system
    access_token = generate_access_token(user.id, user.email, user.role)
    refresh_token = generate_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 30 * 60,  # 30 minutes
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
        },
    }
