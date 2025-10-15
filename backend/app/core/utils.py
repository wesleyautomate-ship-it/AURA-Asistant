"""
Authentication utilities for password hashing, JWT tokens, and validation
"""

import bcrypt
import jwt
import re
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from email_validator import validate_email, EmailNotValidError
import logging
from app.core.settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    try:
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
        return password_hash.decode("utf-8")
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash using bcrypt

    Args:
        password: Plain text password to verify
        password_hash: Hashed password to check against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def generate_jwt_token(
    payload: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a JWT token

    Args:
        payload: Token payload data
        expires_delta: Optional expiration time

    Returns:
        JWT token string
    """
    try:
        to_encode = payload.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT token generation failed: {e}")
        raise


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.JWTError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"JWT token verification error: {e}")
        return None


def generate_access_token(user_id: int, email: str, role: str) -> str:
    """
    Generate an access token for a user

    Args:
        user_id: User ID
        email: User email
        role: User role

    Returns:
        Access token string
    """
    payload = {"sub": str(user_id), "email": email, "role": role, "type": "access"}
    return generate_jwt_token(
        payload, timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def generate_refresh_token(user_id: int) -> str:
    """
    Generate a refresh token for a user

    Args:
        user_id: User ID

    Returns:
        Refresh token string
    """
    payload = {"sub": str(user_id), "type": "refresh"}
    return generate_jwt_token(payload, timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS))


def generate_session_token() -> str:
    """
    Generate a secure session token

    Returns:
        Session token string
    """
    return secrets.token_urlsafe(32)


def validate_email_address(email: str) -> bool:
    """
    Validate email address format

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength

    Args:
        password: Password to validate

    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []

    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    # Check for uppercase letters
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    # Check for lowercase letters
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    # Check for numbers
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number")

    # Check for special characters
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        warnings.append("Consider adding special characters for better security")

    # Check for common patterns
    if re.search(r"(.)\1{2,}", password):
        warnings.append("Avoid repeating characters")

    # Check for common passwords
    common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
    if password.lower() in common_passwords:
        errors.append("Password is too common")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "score": max(0, 10 - len(errors) * 2 - len(warnings)),
    }


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token

    Args:
        length: Token length

    Returns:
        Secure token string
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', "", text)

    # Remove extra whitespace
    sanitized = " ".join(sanitized.split())

    return sanitized.strip()


def validate_username(username: str) -> Dict[str, Any]:
    """
    Validate username format

    Args:
        username: Username to validate

    Returns:
        Dictionary with validation results
    """
    errors = []

    # Check minimum length
    if len(username) < 3:
        errors.append("Username must be at least 3 characters long")

    # Check maximum length
    if len(username) > 50:
        errors.append("Username must be less than 50 characters")

    # Check for valid characters
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        errors.append(
            "Username can only contain letters, numbers, underscores, and hyphens"
        )

    # Check for reserved words
    reserved_words = ["admin", "root", "system", "user", "guest", "test"]
    if username.lower() in reserved_words:
        errors.append("Username is reserved and cannot be used")

    return {"is_valid": len(errors) == 0, "errors": errors}


def get_password_requirements() -> Dict[str, Any]:
    """
    Get password requirements for frontend validation

    Returns:
        Dictionary with password requirements
    """
    return {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special": False,  # Optional but recommended
        "max_length": 128,
        "common_passwords_blocked": True,
    }
