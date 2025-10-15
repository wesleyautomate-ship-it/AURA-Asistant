"""
Token Management for Dubai Real Estate RAG System

This module provides secure token management with refresh logic,
session tracking, and race condition prevention for authentication.
"""

import jwt
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from sqlalchemy import text
from database_manager import get_db_connection

from app.core.settings import SECRET_KEY, ALGORITHM
from auth.models import User

logger = logging.getLogger(__name__)

# Security configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_REFRESH_TOKENS_PER_USER = 5
TOKEN_REFRESH_THRESHOLD_MINUTES = 5  # Refresh if expires within 5 minutes

# Token blacklist for logout
token_blacklist: set = set()

# Active refresh tokens per user
user_refresh_tokens: Dict[int, set] = {}

security = HTTPBearer()


class TokenManager:
    """Manages JWT tokens with refresh logic and security features"""

    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM

    def create_access_token(self, user: User) -> str:
        """Create a new access token"""
        try:
            payload = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "type": "access",
                "exp": datetime.utcnow()
                + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                "iat": datetime.utcnow(),
                "jti": str(uuid.uuid4()),  # JWT ID for unique identification
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created access token for user {user.id}")
            return token

        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise HTTPException(status_code=500, detail="Failed to create access token")

    def create_refresh_token(self, user: User) -> str:
        """Create a new refresh token"""
        try:
            payload = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "type": "refresh",
                "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                "iat": datetime.utcnow(),
                "jti": str(uuid.uuid4()),
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            # Track refresh token for user
            if user.id not in user_refresh_tokens:
                user_refresh_tokens[user.id] = set()

            user_refresh_tokens[user.id].add(token)

            # Limit number of refresh tokens per user
            if len(user_refresh_tokens[user.id]) > MAX_REFRESH_TOKENS_PER_USER:
                # Remove oldest token (simple approach - in production use Redis)
                oldest_token = list(user_refresh_tokens[user.id])[0]
                user_refresh_tokens[user.id].remove(oldest_token)

            logger.info(f"Created refresh token for user {user.id}")
            return token

        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to create refresh token"
            )

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a token"""
        try:
            # Check if token is blacklisted
            if token in token_blacklist:
                raise HTTPException(status_code=401, detail="Token has been revoked")

            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(status_code=401, detail="Invalid token type")

            # Check if token is expired
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(status_code=401, detail="Token has expired")

            # For refresh tokens, verify it's still valid for this user
            if token_type == "refresh":
                user_id = int(payload.get("sub"))
                if (
                    user_id not in user_refresh_tokens
                    or token not in user_refresh_tokens[user_id]
                ):
                    raise HTTPException(
                        status_code=401, detail="Refresh token not found"
                    )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError as e:
            logger.error(f"JWT verification error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(status_code=401, detail="Token verification failed")

    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token, "refresh")
            user_id = int(payload.get("sub"))

            # Get user from database
            with get_db_connection() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT id, email, role, full_name, is_active 
                    FROM users WHERE id = :user_id
                """
                    ),
                    {"user_id": user_id},
                )
                user_data = result.fetchone()

                if not user_data:
                    raise HTTPException(status_code=401, detail="User not found")

                if not user_data.is_active:
                    raise HTTPException(
                        status_code=401, detail="User account is disabled"
                    )

                # Create user object
                user = User(
                    id=user_data.id,
                    email=user_data.email,
                    role=user_data.role,
                    full_name=user_data.full_name,
                    is_active=user_data.is_active,
                )

            # Create new access token
            new_access_token = self.create_access_token(user)

            # Optionally create new refresh token (rotate refresh tokens)
            new_refresh_token = self.create_refresh_token(user)

            # Remove old refresh token
            if (
                user_id in user_refresh_tokens
                and refresh_token in user_refresh_tokens[user_id]
            ):
                user_refresh_tokens[user_id].remove(refresh_token)

            logger.info(f"Refreshed tokens for user {user_id}")
            return new_access_token, new_refresh_token

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise HTTPException(status_code=500, detail="Failed to refresh token")

    def revoke_token(self, token: str) -> bool:
        """Revoke a token (add to blacklist)"""
        try:
            # Verify token first to get payload
            payload = self.verify_token(token)
            token_type = payload.get("type")

            # Add to blacklist
            token_blacklist.add(token)

            # If it's a refresh token, remove from user's active tokens
            if token_type == "refresh":
                user_id = int(payload.get("sub"))
                if (
                    user_id in user_refresh_tokens
                    and token in user_refresh_tokens[user_id]
                ):
                    user_refresh_tokens[user_id].remove(token)

            logger.info(f"Revoked {token_type} token")
            return True

        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

    def revoke_all_user_tokens(self, user_id: int) -> bool:
        """Revoke all tokens for a specific user"""
        try:
            # Revoke all refresh tokens for user
            if user_id in user_refresh_tokens:
                for token in user_refresh_tokens[user_id].copy():
                    token_blacklist.add(token)
                user_refresh_tokens[user_id].clear()

            logger.info(f"Revoked all tokens for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error revoking all tokens for user {user_id}: {e}")
            return False

    def should_refresh_token(self, token: str) -> bool:
        """Check if token should be refreshed (expires soon)"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp_timestamp = payload.get("exp")

            if not exp_timestamp:
                return False

            # Check if token expires within threshold
            time_until_expiry = exp_timestamp - datetime.utcnow().timestamp()
            return time_until_expiry < (TOKEN_REFRESH_THRESHOLD_MINUTES * 60)

        except Exception:
            return False

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens from memory"""
        try:
            cleaned_count = 0

            # Clean up expired tokens from blacklist
            current_time = datetime.utcnow().timestamp()
            expired_tokens = set()

            for token in token_blacklist:
                try:
                    payload = jwt.decode(
                        token, self.secret_key, algorithms=[self.algorithm]
                    )
                    if payload.get("exp", 0) < current_time:
                        expired_tokens.add(token)
                except:
                    # Invalid token, remove it
                    expired_tokens.add(token)

            token_blacklist.difference_update(expired_tokens)
            cleaned_count += len(expired_tokens)

            # Clean up expired refresh tokens
            for user_id in list(user_refresh_tokens.keys()):
                expired_user_tokens = set()
                for token in user_refresh_tokens[user_id]:
                    try:
                        payload = jwt.decode(
                            token, self.secret_key, algorithms=[self.algorithm]
                        )
                        if payload.get("exp", 0) < current_time:
                            expired_user_tokens.add(token)
                    except:
                        expired_user_tokens.add(token)

                user_refresh_tokens[user_id].difference_update(expired_user_tokens)
                cleaned_count += len(expired_user_tokens)

                # Remove empty user entries
                if not user_refresh_tokens[user_id]:
                    del user_refresh_tokens[user_id]

            logger.info(f"Cleaned up {cleaned_count} expired tokens")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")
            return 0

    def get_token_stats(self) -> Dict[str, Any]:
        """Get token management statistics"""
        try:
            total_refresh_tokens = sum(
                len(tokens) for tokens in user_refresh_tokens.values()
            )

            return {
                "blacklisted_tokens": len(token_blacklist),
                "active_refresh_tokens": total_refresh_tokens,
                "users_with_tokens": len(user_refresh_tokens),
                "max_refresh_tokens_per_user": MAX_REFRESH_TOKENS_PER_USER,
                "access_token_expiry_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
                "refresh_token_expiry_days": REFRESH_TOKEN_EXPIRE_DAYS,
            }
        except Exception as e:
            logger.error(f"Error getting token stats: {e}")
            return {"error": str(e)}


# Global token manager instance
token_manager = TokenManager()

# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get current authenticated user from token"""
    try:
        token = credentials.credentials
        payload = token_manager.verify_token(token, "access")
        user_id = int(payload.get("sub"))

        # Get user from database
        with get_db_connection() as conn:
            result = conn.execute(
                text(
                    """
                SELECT id, email, role, full_name, is_active 
                FROM users WHERE id = :user_id
            """
                ),
                {"user_id": user_id},
            )
            user_data = result.fetchone()

            if not user_data:
                raise HTTPException(status_code=401, detail="User not found")

            if not user_data.is_active:
                raise HTTPException(status_code=401, detail="User account is disabled")

            return User(
                id=user_data.id,
                email=user_data.email,
                role=user_data.role,
                full_name=user_data.full_name,
                is_active=user_data.is_active,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    try:
        if not credentials:
            return None
        return await get_current_user(credentials)
    except HTTPException:
        return None
