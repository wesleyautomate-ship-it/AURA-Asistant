#!/usr/bin/env python3
"""
Nurturing Router for Blueprint 2.0: Proactive AI Copilot
Handles API endpoints for proactive lead nurturing and agenda management
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Import secure authentication
from auth.middleware import get_current_user
from auth.models import User

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize database connection
db_url = os.getenv(
    "DATABASE_URL", "postgresql://admin:password123@localhost:5432/real_estate_db"
)
engine = create_engine(db_url)

router = APIRouter(prefix="/nurturing", tags=["Lead Nurturing"])

# Pydantic models for request/response
class InteractionRequest(BaseModel):
    interaction_type: str
    content: str
    scheduled_for: Optional[datetime] = None


class FollowUpRequest(BaseModel):
    follow_up_date: datetime
    interaction_type: str = "follow_up"
    notes: str = ""


class NotificationUpdateRequest(BaseModel):
    is_read: bool = True


@router.get("/users/me/agenda")
async def get_user_agenda(current_user: User = Depends(get_current_user)):
    """
    Get today's agenda with scheduled tasks and nurturing suggestions
    """
    try:
        with engine.connect() as conn:
            # Get scheduled follow-ups for today
            follow_ups_result = conn.execute(
                text(
                    """
                SELECT l.id, l.client_name, l.client_email, l.next_follow_up_at, l.nurture_status
                FROM leads l
                WHERE l.agent_id = :agent_id
                AND l.next_follow_up_at::date = CURRENT_DATE
                AND l.status NOT IN ('closed', 'lost')
                ORDER BY l.next_follow_up_at ASC
            """
                ),
                {"agent_id": current_user.id},
            )

            follow_ups = []
            for row in follow_ups_result.fetchall():
                follow_ups.append(
                    {
                        "lead_id": row.id,
                        "lead_name": row.client_name,
                        "lead_email": row.client_email,
                        "scheduled_time": row.next_follow_up_at.isoformat()
                        if row.next_follow_up_at
                        else None,
                        "nurture_status": row.nurture_status,
                        "type": "scheduled_follow_up",
                    }
                )

            # Get leads needing attention
            attention_result = conn.execute(
                text(
                    """
                SELECT l.id, l.client_name, l.client_email, l.last_contacted_at, l.nurture_status
                FROM leads l
                WHERE l.agent_id = :agent_id
                AND (l.last_contacted_at IS NULL OR 
                     l.last_contacted_at < NOW() - INTERVAL '5 days')
                AND l.status NOT IN ('closed', 'lost')
                AND l.nurture_status != 'Closed'
                ORDER BY l.last_contacted_at ASC NULLS FIRST
                LIMIT 5
            """
                ),
                {"agent_id": current_user.id},
            )

            attention_needed = []
            for row in attention_result.fetchall():
                attention_needed.append(
                    {
                        "lead_id": row.id,
                        "lead_name": row.client_name,
                        "lead_email": row.client_email,
                        "last_contacted": row.last_contacted_at.isoformat()
                        if row.last_contacted_at
                        else None,
                        "nurture_status": row.nurture_status,
                        "type": "needs_attention",
                    }
                )

            # Get unread notifications
            notifications_result = conn.execute(
                text(
                    """
                SELECT id, notification_type, title, message, related_lead_id, 
                       priority, created_at
                FROM notifications
                WHERE user_id = :user_id AND is_read = FALSE
                ORDER BY created_at DESC
                LIMIT 10
            """
                ),
                {"user_id": current_user.id},
            )

            notifications = []
            for row in notifications_result.fetchall():
                notifications.append(
                    {
                        "id": row.id,
                        "notification_type": row.notification_type,
                        "title": row.title,
                        "message": row.message,
                        "related_lead_id": row.related_lead_id,
                        "priority": row.priority,
                        "created_at": row.created_at.isoformat()
                        if row.created_at
                        else None,
                    }
                )

            return {
                "date": datetime.now().date().isoformat(),
                "scheduled_follow_ups": follow_ups,
                "leads_needing_attention": attention_needed,
                "notifications": notifications,
                "summary": {
                    "total_follow_ups": len(follow_ups),
                    "leads_needing_attention": len(attention_needed),
                    "unread_notifications": len(notifications),
                },
            }

    except Exception as e:
        logger.error(f"Error getting user agenda: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving agenda")


@router.get("/leads/{lead_id}/history")
async def get_lead_history(
    lead_id: int, current_user: User = Depends(get_current_user)
):
    """
    Get lead interaction history
    """
    try:
        with engine.connect() as conn:
            # Verify lead belongs to current user
            lead_check = conn.execute(
                text(
                    """
                SELECT id, agent_id FROM leads WHERE id = :lead_id
            """
                ),
                {"lead_id": lead_id},
            )

            lead_row = lead_check.fetchone()
            if not lead_row:
                raise HTTPException(status_code=404, detail="Lead not found")

            if lead_row.agent_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied - you can only view your own leads",
                )

            # Get interaction history
            result = conn.execute(
                text(
                    """
                SELECT id, interaction_type, content, created_at, scheduled_for
                FROM lead_history
                WHERE lead_id = :lead_id
                ORDER BY created_at DESC
                LIMIT 20
            """
                ),
                {"lead_id": lead_id},
            )

            history = []
            for row in result.fetchall():
                history.append(
                    {
                        "id": row.id,
                        "interaction_type": row.interaction_type,
                        "content": row.content,
                        "created_at": row.created_at.isoformat()
                        if row.created_at
                        else None,
                        "scheduled_for": row.scheduled_for.isoformat()
                        if row.scheduled_for
                        else None,
                    }
                )

            return {
                "lead_id": lead_id,
                "history": history,
                "total_interactions": len(history),
            }

    except Exception as e:
        logger.error(f"Error getting lead history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving lead history")


@router.post("/leads/{lead_id}/interaction")
async def log_interaction(
    lead_id: int,
    interaction: InteractionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Log a new interaction with a lead
    """
    try:
        with engine.connect() as conn:
            # Verify lead belongs to current user
            lead_check = conn.execute(
                text(
                    """
                SELECT id, agent_id FROM leads WHERE id = :lead_id
            """
                ),
                {"lead_id": lead_id},
            )

            lead_row = lead_check.fetchone()
            if not lead_row:
                raise HTTPException(status_code=404, detail="Lead not found")

            if lead_row.agent_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied - you can only interact with your own leads",
                )

            # Add interaction to history
            conn.execute(
                text(
                    """
                INSERT INTO lead_history 
                (lead_id, agent_id, interaction_type, content, scheduled_for, created_at)
                VALUES (:lead_id, :agent_id, :interaction_type, :content, :scheduled_for, NOW())
            """
                ),
                {
                    "lead_id": lead_id,
                    "agent_id": current_user.id,
                    "interaction_type": interaction.interaction_type,
                    "content": interaction.content,
                    "scheduled_for": interaction.scheduled_for,
                },
            )

            # Update lead's last contacted timestamp (if not a scheduled interaction)
            if not interaction.scheduled_for:
                conn.execute(
                    text(
                        """
                    UPDATE leads 
                    SET last_contacted_at = NOW(), updated_at = NOW()
                    WHERE id = :lead_id
                """
                    ),
                    {"lead_id": lead_id},
                )

            conn.commit()

            return {
                "success": True,
                "message": "Interaction logged successfully",
                "lead_id": lead_id,
                "interaction_type": interaction.interaction_type,
                "logged_at": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
        raise HTTPException(status_code=500, detail="Error logging interaction")


@router.put("/leads/{lead_id}/follow-up")
async def schedule_follow_up(
    lead_id: int,
    follow_up: FollowUpRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Schedule a follow-up for a lead
    """
    try:
        with engine.connect() as conn:
            # Verify lead belongs to current user
            lead_check = conn.execute(
                text(
                    """
                SELECT id, agent_id FROM leads WHERE id = :lead_id
            """
                ),
                {"lead_id": lead_id},
            )

            lead_row = lead_check.fetchone()
            if not lead_row:
                raise HTTPException(status_code=404, detail="Lead not found")

            if lead_row.agent_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied - you can only schedule follow-ups for your own leads",
                )

            # Add scheduled interaction to history
            conn.execute(
                text(
                    """
                INSERT INTO lead_history 
                (lead_id, agent_id, interaction_type, content, scheduled_for, created_at)
                VALUES (:lead_id, :agent_id, :interaction_type, :content, :scheduled_for, NOW())
            """
                ),
                {
                    "lead_id": lead_id,
                    "agent_id": current_user.id,
                    "interaction_type": follow_up.interaction_type,
                    "content": follow_up.notes,
                    "scheduled_for": follow_up.follow_up_date,
                },
            )

            # Update lead's next follow-up date
            conn.execute(
                text(
                    """
                UPDATE leads 
                SET next_follow_up_at = :follow_up_date, updated_at = NOW()
                WHERE id = :lead_id
            """
                ),
                {"follow_up_date": follow_up.follow_up_date, "lead_id": lead_id},
            )

            conn.commit()

            return {
                "success": True,
                "message": f"Follow-up scheduled for {follow_up.follow_up_date.strftime('%B %d, %Y at %I:%M %p')}",
                "lead_id": lead_id,
                "scheduled_date": follow_up.follow_up_date.isoformat(),
            }

    except Exception as e:
        logger.error(f"Error scheduling follow-up: {e}")
        raise HTTPException(status_code=500, detail="Error scheduling follow-up")


@router.get("/notifications")
async def get_notifications(
    current_user: User = Depends(get_current_user), limit: int = 20, offset: int = 0
):
    """
    Get user notifications
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT id, notification_type, title, message, related_lead_id, 
                       priority, is_read, created_at
                FROM notifications
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """
                ),
                {"user_id": current_user.id, "limit": limit, "offset": offset},
            )

            notifications = []
            for row in result.fetchall():
                notifications.append(
                    {
                        "id": row.id,
                        "notification_type": row.notification_type,
                        "title": row.title,
                        "message": row.message,
                        "related_lead_id": row.related_lead_id,
                        "priority": row.priority,
                        "is_read": row.is_read,
                        "created_at": row.created_at.isoformat()
                        if row.created_at
                        else None,
                    }
                )

            # Get unread count
            unread_result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as unread_count
                FROM notifications
                WHERE user_id = :user_id AND is_read = FALSE
            """
                ),
                {"user_id": current_user.id},
            )

            unread_count = unread_result.fetchone().unread_count

            return {
                "notifications": notifications,
                "total": len(notifications),
                "unread_count": unread_count,
                "limit": limit,
                "offset": offset,
            }

    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving notifications")


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    update: NotificationUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Mark notification as read/unread
    """
    try:
        with engine.connect() as conn:
            # Verify notification belongs to current user
            notification_check = conn.execute(
                text(
                    """
                SELECT id, user_id FROM notifications WHERE id = :notification_id
            """
                ),
                {"notification_id": notification_id},
            )

            notification_row = notification_check.fetchone()
            if not notification_row:
                raise HTTPException(status_code=404, detail="Notification not found")

            if notification_row.user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied - you can only update your own notifications",
                )

            # Update notification read status
            conn.execute(
                text(
                    """
                UPDATE notifications 
                SET is_read = :is_read
                WHERE id = :notification_id
            """
                ),
                {"is_read": update.is_read, "notification_id": notification_id},
            )

            conn.commit()

            return {
                "success": True,
                "message": f"Notification marked as {'read' if update.is_read else 'unread'}",
                "notification_id": notification_id,
                "is_read": update.is_read,
            }

    except Exception as e:
        logger.error(f"Error updating notification: {e}")
        raise HTTPException(status_code=500, detail="Error updating notification")


@router.get("/leads/needing-attention")
async def get_leads_needing_attention(
    current_user: User = Depends(get_current_user), days_threshold: int = 5
):
    """
    Get leads that need attention based on last contact date
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT l.id, l.name, l.email, l.phone, l.status, l.nurture_status, 
                       l.last_contacted_at, l.next_follow_up_at, l.notes
                FROM leads l
                WHERE l.agent_id = :agent_id
                AND (l.last_contacted_at IS NULL OR 
                     l.last_contacted_at < NOW() - INTERVAL ':days_threshold days')
                AND l.status NOT IN ('closed', 'lost')
                AND l.nurture_status != 'Closed'
                ORDER BY l.last_contacted_at ASC NULLS FIRST
            """
                ),
                {"agent_id": current_user.id, "days_threshold": days_threshold},
            )

            leads = []
            for row in result.fetchall():
                leads.append(
                    {
                        "id": row.id,
                        "name": row.name,
                        "email": row.email,
                        "phone": row.phone,
                        "status": row.status,
                        "nurture_status": row.nurture_status,
                        "last_contacted_at": row.last_contacted_at.isoformat()
                        if row.last_contacted_at
                        else None,
                        "next_follow_up_at": row.next_follow_up_at.isoformat()
                        if row.next_follow_up_at
                        else None,
                        "notes": row.notes,
                        "days_since_contact": (
                            datetime.now() - row.last_contacted_at
                        ).days
                        if row.last_contacted_at
                        else 999,
                    }
                )

            return {
                "leads": leads,
                "total_count": len(leads),
                "days_threshold": days_threshold,
                "generated_at": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"Error getting leads needing attention: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving leads")


@router.post("/leads/{lead_id}/nurture-suggestion")
async def generate_nurture_suggestion(
    lead_id: int, current_user: User = Depends(get_current_user)
):
    """
    Generate a nurture suggestion for a specific lead
    """
    try:
        # Import action engine here to avoid circular imports
        from action_engine import ActionEngine

        action_engine = ActionEngine()

        # Generate nurture suggestion
        suggestion_data = action_engine.create_nurture_suggestion(lead_id)

        if "error" in suggestion_data:
            raise HTTPException(status_code=400, detail=suggestion_data["error"])

        return suggestion_data

    except Exception as e:
        logger.error(f"Error generating nurture suggestion: {e}")
        raise HTTPException(
            status_code=500, detail="Error generating nurture suggestion"
        )
