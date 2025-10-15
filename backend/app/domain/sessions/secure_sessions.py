"""
Secure Session Management for Dubai Real Estate RAG System

This module provides secure session endpoints with proper user authentication
and role-based access control to prevent data leakage between users.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import uuid

from auth.middleware import get_current_user, require_admin, require_agent_or_admin
from auth.models import User
from auth.database import get_db

# Import the existing models and response types
from chat_sessions_router import (
    ChatSessionListResponse,
    ChatSessionResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
)
from sqlalchemy import text
from database_manager import get_db_connection

router = APIRouter()


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List chat sessions for the authenticated user with role-based filtering

    - Admin users can see all conversations
    - Agent users can see their own conversations and assigned client conversations
    - Client users can only see their own conversations
    """
    try:
        with get_db_connection() as conn:
            # Build query based on user role
            if current_user.role == "admin":
                # Admin can see all conversations
                query = """
                    SELECT 
                        c.id, c.session_id, c.role, c.title, c.created_at, c.updated_at, c.is_active,
                        COUNT(m.id) as message_count
                    FROM conversations c
                    LEFT JOIN messages m ON c.id = m.conversation_id
                    WHERE c.is_active = TRUE
                    GROUP BY c.id, c.session_id, c.role, c.title, c.created_at, c.updated_at, c.is_active
                    ORDER BY c.updated_at DESC
                    LIMIT :limit OFFSET :offset
                """
                params = {"limit": limit, "offset": offset}

            elif current_user.role == "agent":
                # Agent can see their own conversations and assigned client conversations
                query = """
                    SELECT 
                        c.id, c.session_id, c.role, c.title, c.created_at, c.updated_at, c.is_active,
                        COUNT(m.id) as message_count
                    FROM conversations c
                    LEFT JOIN messages m ON c.id = m.conversation_id
                    WHERE c.is_active = TRUE 
                    AND (c.user_id = :user_id OR c.role = 'client')
                    GROUP BY c.id, c.session_id, c.role, c.title, c.created_at, c.updated_at, c.is_active
                    ORDER BY c.updated_at DESC
                    LIMIT :limit OFFSET :offset
                """
                params = {"user_id": current_user.id, "limit": limit, "offset": offset}

            else:
                # Client can only see their own conversations
                query = """
                    SELECT 
                        c.id, c.session_id, c.role, c.title, c.created_at, c.updated_at, c.is_active,
                        COUNT(m.id) as message_count
                    FROM conversations c
                    LEFT JOIN messages m ON c.id = m.conversation_id
                    WHERE c.is_active = TRUE AND c.user_id = :user_id
                    GROUP BY c.id, c.session_id, c.role, c.title, c.created_at, c.updated_at, c.is_active
                    ORDER BY c.updated_at DESC
                    LIMIT :limit OFFSET :offset
                """
                params = {"user_id": current_user.id, "limit": limit, "offset": offset}

            result = conn.execute(text(query), params)

            sessions = []
            for row in result:
                # Get user preferences for this session
                prefs_result = conn.execute(
                    text(
                        """
                    SELECT user_preferences FROM conversation_preferences 
                    WHERE session_id = :session_id
                """
                    ),
                    {"session_id": row[1]},
                )
                prefs_row = prefs_result.fetchone()
                if prefs_row and prefs_row[0]:
                    if isinstance(prefs_row[0], str):
                        user_preferences = json.loads(prefs_row[0])
                    else:
                        user_preferences = prefs_row[0]
                else:
                    user_preferences = {}

                sessions.append(
                    ChatSessionResponse(
                        session_id=row[1],
                        title=row[3],
                        role=row[2],
                        created_at=str(row[4]),
                        updated_at=str(row[5]),
                        message_count=row[7],
                        user_preferences=user_preferences,
                        is_active=row[6],
                    )
                )

            # Get total count based on user role
            if current_user.role == "admin":
                count_query = (
                    "SELECT COUNT(*) FROM conversations WHERE is_active = TRUE"
                )
                count_params = {}
            elif current_user.role == "agent":
                count_query = """
                    SELECT COUNT(*) FROM conversations 
                    WHERE is_active = TRUE AND (user_id = :user_id OR role = 'client')
                """
                count_params = {"user_id": current_user.id}
            else:
                count_query = "SELECT COUNT(*) FROM conversations WHERE is_active = TRUE AND user_id = :user_id"
                count_params = {"user_id": current_user.id}

            count_result = conn.execute(text(count_query), count_params)
            total_count = count_result.fetchone()[0]

            return ChatSessionListResponse(sessions=sessions, total_count=total_count)

    except Exception as e:
        print(f"Error listing chat sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get chat session with full history - with user access control

    Users can only access conversations they own or have permission to view
    """
    try:
        with get_db_connection() as conn:
            # Check if user has access to this session
            if current_user.role == "admin":
                # Admin can access any session
                session_query = """
                    SELECT id, session_id, role, title, created_at, updated_at, is_active, user_id
                    FROM conversations 
                    WHERE session_id = :session_id AND is_active = TRUE
                """
                session_params = {"session_id": session_id}
            elif current_user.role == "agent":
                # Agent can access their own sessions or client sessions
                session_query = """
                    SELECT id, session_id, role, title, created_at, updated_at, is_active, user_id
                    FROM conversations 
                    WHERE session_id = :session_id AND is_active = TRUE 
                    AND (user_id = :user_id OR role = 'client')
                """
                session_params = {"session_id": session_id, "user_id": current_user.id}
            else:
                # Client can only access their own sessions
                session_query = """
                    SELECT id, session_id, role, title, created_at, updated_at, is_active, user_id
                    FROM conversations 
                    WHERE session_id = :session_id AND is_active = TRUE AND user_id = :user_id
                """
                session_params = {"session_id": session_id, "user_id": current_user.id}

            session_result = conn.execute(text(session_query), session_params)
            session_row = session_result.fetchone()

            if not session_row:
                raise HTTPException(
                    status_code=404, detail="Chat session not found or access denied"
                )

            # Get messages for this session
            messages_result = conn.execute(
                text(
                    """
                SELECT id, conversation_id, role, content, timestamp, message_type, metadata
                FROM messages 
                WHERE conversation_id = :conversation_id
                ORDER BY timestamp ASC
            """
                ),
                {"conversation_id": session_row[0]},
            )

            messages = []
            for msg_row in messages_result:
                metadata = json.loads(msg_row[6]) if msg_row[6] else None
                messages.append(
                    ChatMessageResponse(
                        id=msg_row[0],
                        session_id=session_id,
                        role=msg_row[2],
                        content=msg_row[3],
                        timestamp=str(msg_row[4]),
                        message_type=msg_row[5],
                        metadata=metadata,
                    )
                )

            return ChatHistoryResponse(
                session_id=session_id,
                title=session_row[3],
                role=session_row[2],
                created_at=str(session_row[4]),
                updated_at=str(session_row[5]),
                messages=messages,
                is_active=session_row[6],
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions")
async def create_chat_session(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Create a new chat session for the authenticated user
    """
    try:
        session_id = str(uuid.uuid4())

        with get_db_connection() as conn:
            result = conn.execute(
                text(
                    """
                INSERT INTO conversations (session_id, role, title, user_id, created_at, updated_at, is_active)
                VALUES (:session_id, :role, :title, :user_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE)
                RETURNING id, session_id, role, title, created_at, updated_at, is_active
            """
                ),
                {
                    "session_id": session_id,
                    "role": current_user.role,
                    "title": f"Chat Session - {current_user.full_name}",
                    "user_id": current_user.id,
                },
            )

            new_session = result.fetchone()
            conn.commit()

            return ChatSessionResponse(
                session_id=new_session[1],
                title=new_session[3],
                role=new_session[2],
                created_at=str(new_session[4]),
                updated_at=str(new_session[5]),
                message_count=0,
                user_preferences={},
                is_active=new_session[6],
            )

    except Exception as e:
        print(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
