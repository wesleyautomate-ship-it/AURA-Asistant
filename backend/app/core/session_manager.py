"""
Session Management and Isolation for Dubai Real Estate RAG System
================================================================

This module implements secure session management to ensure complete isolation
between different users and their conversations.
"""

import logging
import uuid
import json
import hashlib
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


@dataclass
class SessionContext:
    """Session context with isolation controls"""

    session_id: str
    user_id: str
    user_role: str
    created_at: datetime
    last_activity: datetime
    conversation_history: deque = field(default_factory=lambda: deque(maxlen=50))
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    access_level: str = "client"
    allowed_data_types: List[str] = field(default_factory=list)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Secure Session Manager with User Isolation"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # In-memory session cache for performance
        self.session_cache: Dict[str, SessionContext] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> set of session_ids

        # Session cleanup task
        self.cleanup_interval = 300  # 5 minutes
        self.session_timeout = 3600  # 1 hour

        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_sessions())

    async def create_session(
        self, user_id: str, user_role: str, metadata: Optional[Dict] = None
    ) -> SessionContext:
        """Create a new isolated session for user"""
        try:
            session_id = str(uuid.uuid4())

            # Create session context
            session_context = SessionContext(
                session_id=session_id,
                user_id=user_id,
                user_role=user_role,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                metadata=metadata or {},
            )

            # Store in database
            await self._store_session_in_db(session_context)

            # Cache session
            self.session_cache[session_id] = session_context

            # Track user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)

            logger.info(
                f"Created session {session_id} for user {user_id} with role {user_role}"
            )
            return session_context

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get session context with isolation checks"""
        try:
            # Check cache first
            if session_id in self.session_cache:
                session = self.session_cache[session_id]
                if (
                    session.is_active
                    and (datetime.now() - session.last_activity).seconds
                    < self.session_timeout
                ):
                    session.last_activity = datetime.now()
                    return session
                else:
                    # Session expired
                    await self.invalidate_session(session_id)
                    return None

            # Load from database
            session = await self._load_session_from_db(session_id)
            if session and session.is_active:
                self.session_cache[session_id] = session
                return session

            return None

        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None

    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session"""
        try:
            # Remove from cache
            if session_id in self.session_cache:
                session = self.session_cache[session_id]
                user_id = session.user_id

                # Remove from user sessions
                if user_id in self.user_sessions:
                    self.user_sessions[user_id].discard(session_id)
                    if not self.user_sessions[user_id]:
                        del self.user_sessions[user_id]

                del self.session_cache[session_id]

            # Mark as inactive in database
            await self._invalidate_session_in_db(session_id)

            logger.info(f"Invalidated session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error invalidating session {session_id}: {e}")
            return False

    async def get_user_sessions(self, user_id: str) -> List[SessionContext]:
        """Get all active sessions for a user"""
        try:
            sessions = []

            # Get from cache
            if user_id in self.user_sessions:
                for session_id in self.user_sessions[user_id]:
                    session = await self.get_session(session_id)
                    if session:
                        sessions.append(session)

            return sessions

        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []

    async def add_message_to_session(
        self, session_id: str, message: Dict[str, Any]
    ) -> bool:
        """Add message to session with isolation"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False

            # Add message to conversation history
            session.conversation_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "role": message.get("role", "user"),
                    "content": message.get("content", ""),
                    "message_type": message.get("message_type", "text"),
                    "metadata": message.get("metadata", {}),
                }
            )

            # Update last activity
            session.last_activity = datetime.now()

            # Store in database
            await self._store_session_in_db(session)

            return True

        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {e}")
            return False

    async def get_session_history(
        self, session_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history for session with isolation"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return []

            # Return recent messages
            return list(session.conversation_history)[-limit:]

        except Exception as e:
            logger.error(f"Error getting history for session {session_id}: {e}")
            return []

    async def update_user_preferences(
        self, session_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences for session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False

            # Update preferences
            session.user_preferences.update(preferences)
            session.last_activity = datetime.now()

            # Store in database
            await self._store_session_in_db(session)

            return True

        except Exception as e:
            logger.error(f"Error updating preferences for session {session_id}: {e}")
            return False

    async def clear_session_history(self, session_id: str) -> bool:
        """Clear conversation history for session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False

            # Clear history
            session.conversation_history.clear()
            session.last_activity = datetime.now()

            # Store in database
            await self._store_session_in_db(session)

            return True

        except Exception as e:
            logger.error(f"Error clearing history for session {session_id}: {e}")
            return False

    def is_session_isolated(self, session_id: str, user_id: str) -> bool:
        """Check if session belongs to user (isolation check)"""
        try:
            if session_id not in self.session_cache:
                return False

            session = self.session_cache[session_id]
            return session.user_id == user_id and session.is_active

        except Exception as e:
            logger.error(f"Error checking session isolation: {e}")
            return False

    async def _store_session_in_db(self, session: SessionContext) -> None:
        """Store session in database"""
        try:
            with self.engine.connect() as conn:
                # Store session metadata
                conn.execute(
                    text(
                        """
                    INSERT INTO user_sessions (
                        user_id, session_token, refresh_token, expires_at, 
                        session_data, created_at, is_active
                    ) VALUES (
                        :user_id, :session_token, :refresh_token, :expires_at,
                        :session_data, :created_at, :is_active
                    ) ON CONFLICT (session_token) DO UPDATE SET
                        session_data = :session_data,
                        expires_at = :expires_at,
                        is_active = :is_active
                """
                    ),
                    {
                        "user_id": session.user_id,
                        "session_token": session.session_id,
                        "refresh_token": str(uuid.uuid4()),
                        "expires_at": session.last_activity + timedelta(hours=24),
                        "session_data": json.dumps(
                            {
                                "user_role": session.user_role,
                                "conversation_history": list(
                                    session.conversation_history
                                ),
                                "user_preferences": session.user_preferences,
                                "access_level": session.access_level,
                                "allowed_data_types": session.allowed_data_types,
                                "metadata": session.metadata,
                            }
                        ),
                        "created_at": session.created_at,
                        "is_active": session.is_active,
                    },
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error storing session in database: {e}")
            raise

    async def _load_session_from_db(self, session_id: str) -> Optional[SessionContext]:
        """Load session from database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT user_id, session_data, created_at, is_active
                    FROM user_sessions 
                    WHERE session_token = :session_id AND is_active = TRUE
                """
                    ),
                    {"session_id": session_id},
                )

                row = result.fetchone()
                if not row:
                    return None

                session_data = json.loads(row[1])

                session = SessionContext(
                    session_id=session_id,
                    user_id=row[0],
                    user_role=session_data.get("user_role", "client"),
                    created_at=row[2],
                    last_activity=datetime.now(),
                    conversation_history=deque(
                        session_data.get("conversation_history", []), maxlen=50
                    ),
                    user_preferences=session_data.get("user_preferences", {}),
                    access_level=session_data.get("access_level", "client"),
                    allowed_data_types=session_data.get("allowed_data_types", []),
                    is_active=row[3],
                    metadata=session_data.get("metadata", {}),
                )

                return session

        except Exception as e:
            logger.error(f"Error loading session from database: {e}")
            return None

    async def _invalidate_session_in_db(self, session_id: str) -> None:
        """Mark session as inactive in database"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text(
                        """
                    UPDATE user_sessions 
                    SET is_active = FALSE 
                    WHERE session_token = :session_id
                """
                    ),
                    {"session_id": session_id},
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error invalidating session in database: {e}")

    async def _cleanup_expired_sessions(self) -> None:
        """Cleanup expired sessions"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = []

                # Check cache for expired sessions
                for session_id, session in self.session_cache.items():
                    if (
                        current_time - session.last_activity
                    ).seconds > self.session_timeout:
                        expired_sessions.append(session_id)

                # Invalidate expired sessions
                for session_id in expired_sessions:
                    await self.invalidate_session(session_id)

                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

                # Wait for next cleanup
                await asyncio.sleep(self.cleanup_interval)

            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error


# Global session manager instance
session_manager = None


def initialize_session_manager(db_url: str):
    """Initialize the global session manager"""
    global session_manager
    session_manager = SessionManager(db_url)
    logger.info("✅ Session Manager initialized successfully")


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    if session_manager is None:
        raise RuntimeError(
            "Session Manager not initialized. Call initialize_session_manager() first."
        )
    return session_manager
