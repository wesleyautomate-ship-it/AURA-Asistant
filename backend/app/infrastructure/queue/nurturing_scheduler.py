#!/usr/bin/env python3
"""
Proactive Nurturing Scheduler for Blueprint 2.0: Proactive AI Copilot
Handles background jobs for lead follow-ups and proactive notifications
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv
import asyncio
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize database connection
db_url = os.getenv(
    "DATABASE_URL", "postgresql://admin:password123@localhost:5432/real_estate_db"
)
engine = create_engine(db_url)


class NurturingScheduler:
    """Proactive nurturing scheduler for lead management"""

    def __init__(self, action_engine=None):
        self.action_engine = action_engine
        self.is_running = False

    async def start_scheduler(self):
        """Start the nurturing scheduler"""
        self.is_running = True
        logger.info("🚀 Starting Proactive Nurturing Scheduler...")

        while self.is_running:
            try:
                # Run daily jobs at 7 AM
                now = datetime.now()
                if now.hour == 7 and now.minute < 5:  # Run once between 7:00-7:05 AM
                    await self.run_daily_follow_up_job()
                    await self.run_nurture_identification_job()
                    await asyncio.sleep(
                        300
                    )  # Sleep for 5 minutes to avoid duplicate runs

                # Run hourly checks for scheduled tasks
                if now.minute < 5:  # Run once per hour
                    await self.run_scheduled_tasks_check()

                # Sleep for 1 minute before next check
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in nurturing scheduler: {e}")
                await asyncio.sleep(60)

    async def run_daily_follow_up_job(self):
        """Daily follow-up job (runs at 7 AM)"""
        logger.info("📞 Running daily follow-up job...")

        try:
            with engine.connect() as conn:
                # Get leads with scheduled follow-ups for today
                result = conn.execute(
                    text(
                        """
                    SELECT l.id, l.name, l.email, l.agent_id, l.next_follow_up_at,
                           u.first_name, u.last_name
                    FROM leads l
                    LEFT JOIN users u ON l.agent_id = u.id
                    WHERE l.next_follow_up_at::date = CURRENT_DATE
                    AND l.status NOT IN ('closed', 'lost')
                    ORDER BY l.next_follow_up_at ASC
                """
                    )
                )

                follow_ups = []
                for row in result.fetchall():
                    follow_ups.append(
                        {
                            "lead_id": row.id,
                            "lead_name": row.name,
                            "lead_email": row.email,
                            "agent_id": row.agent_id,
                            "agent_name": f"{row.first_name} {row.last_name}"
                            if row.first_name
                            else "Unknown",
                            "scheduled_time": row.next_follow_up_at.isoformat()
                            if row.next_follow_up_at
                            else None,
                        }
                    )

                # Create notifications for each follow-up
                for follow_up in follow_ups:
                    await self.create_follow_up_notification(follow_up)

                logger.info(
                    f"✅ Daily follow-up job completed. {len(follow_ups)} follow-ups scheduled."
                )

        except Exception as e:
            logger.error(f"Error in daily follow-up job: {e}")

    async def run_nurture_identification_job(self):
        """Nurture identification job (runs at 8 AM)"""
        logger.info("🔍 Running nurture identification job...")

        try:
            with engine.connect() as conn:
                # Find leads that need attention (no contact in 5+ days)
                result = conn.execute(
                    text(
                        """
                    SELECT l.id, l.name, l.email, l.agent_id, l.last_contacted_at,
                           l.nurture_status, u.first_name, u.last_name
                    FROM leads l
                    LEFT JOIN users u ON l.agent_id = u.id
                    WHERE (l.last_contacted_at IS NULL OR 
                           l.last_contacted_at < NOW() - INTERVAL '5 days')
                    AND l.status NOT IN ('closed', 'lost')
                    AND l.nurture_status != 'Closed'
                    ORDER BY l.last_contacted_at ASC NULLS FIRST
                """
                    )
                )

                leads_needing_attention = []
                for row in result.fetchall():
                    leads_needing_attention.append(
                        {
                            "lead_id": row.id,
                            "lead_name": row.name,
                            "lead_email": row.email,
                            "agent_id": row.agent_id,
                            "agent_name": f"{row.first_name} {row.last_name}"
                            if row.first_name
                            else "Unknown",
                            "last_contacted": row.last_contacted_at.isoformat()
                            if row.last_contacted_at
                            else None,
                            "nurture_status": row.nurture_status,
                        }
                    )

                # Create nurture suggestions for each lead
                for lead in leads_needing_attention:
                    await self.create_nurture_suggestion_notification(lead)

                # Update nurture status for leads that haven't been contacted
                conn.execute(
                    text(
                        """
                    UPDATE leads 
                    SET nurture_status = 'Needs Follow-up'
                    WHERE (last_contacted_at IS NULL OR 
                           last_contacted_at < NOW() - INTERVAL '5 days')
                    AND status NOT IN ('closed', 'lost')
                    AND nurture_status != 'Closed'
                """
                    )
                )

                conn.commit()

                logger.info(
                    f"✅ Nurture identification job completed. {len(leads_needing_attention)} leads need attention."
                )

        except Exception as e:
            logger.error(f"Error in nurture identification job: {e}")

    async def run_scheduled_tasks_check(self):
        """Check for scheduled tasks and create notifications"""
        logger.info("⏰ Running scheduled tasks check...")

        try:
            with engine.connect() as conn:
                # Get scheduled interactions for the next hour
                result = conn.execute(
                    text(
                        """
                    SELECT lh.id, lh.lead_id, lh.interaction_type, lh.content, 
                           lh.scheduled_for, l.client_name as lead_name, l.agent_id,
                           u.first_name, u.last_name
                    FROM lead_history lh
                    JOIN leads l ON lh.lead_id = l.id
                    LEFT JOIN users u ON l.agent_id = u.id
                    WHERE lh.scheduled_for BETWEEN NOW() AND NOW() + INTERVAL '1 hour'
                    AND lh.interaction_type IN ('follow_up', 'call', 'meeting')
                    ORDER BY lh.scheduled_for ASC
                """
                    )
                )

                scheduled_tasks = []
                for row in result.fetchall():
                    scheduled_tasks.append(
                        {
                            "history_id": row.id,
                            "lead_id": row.lead_id,
                            "lead_name": row.lead_name,
                            "agent_id": row.agent_id,
                            "agent_name": f"{row.first_name} {row.last_name}"
                            if row.first_name
                            else "Unknown",
                            "interaction_type": row.interaction_type,
                            "content": row.content,
                            "scheduled_for": row.scheduled_for.isoformat()
                            if row.scheduled_for
                            else None,
                        }
                    )

                # Create notifications for scheduled tasks
                for task in scheduled_tasks:
                    await self.create_scheduled_task_notification(task)

                if scheduled_tasks:
                    logger.info(
                        f"✅ Scheduled tasks check completed. {len(scheduled_tasks)} tasks found."
                    )

        except Exception as e:
            logger.error(f"Error in scheduled tasks check: {e}")

    async def create_follow_up_notification(self, follow_up: Dict[str, Any]):
        """Create notification for scheduled follow-up"""
        try:
            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO notifications 
                    (user_id, notification_type, title, message, related_lead_id, 
                     priority, created_at)
                    VALUES (:user_id, :notification_type, :title, :message, 
                           :related_lead_id, :priority, NOW())
                """
                    ),
                    {
                        "user_id": follow_up["agent_id"],
                        "notification_type": "follow_up",
                        "title": f"Follow-up Scheduled: {follow_up['lead_name']}",
                        "message": f"You have a follow-up scheduled with {follow_up['lead_name']} today at {follow_up['scheduled_time'][11:16]}.",
                        "related_lead_id": follow_up["lead_id"],
                        "priority": "high",
                    },
                )

                conn.commit()
                logger.info(
                    f"Created follow-up notification for {follow_up['lead_name']}"
                )

        except Exception as e:
            logger.error(f"Error creating follow-up notification: {e}")

    async def create_nurture_suggestion_notification(self, lead: Dict[str, Any]):
        """Create notification for nurture suggestion"""
        try:
            # Generate nurture suggestion if action engine is available
            suggestion = "It's been a while since you contacted this lead. Consider reaching out to maintain engagement."

            if self.action_engine:
                nurture_data = self.action_engine.create_nurture_suggestion(
                    lead["lead_id"]
                )
                if "suggestion" in nurture_data:
                    suggestion = nurture_data["suggestion"]

            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO notifications 
                    (user_id, notification_type, title, message, related_lead_id, 
                     priority, created_at)
                    VALUES (:user_id, :notification_type, :title, :message, 
                           :related_lead_id, :priority, NOW())
                """
                    ),
                    {
                        "user_id": lead["agent_id"],
                        "notification_type": "nurture_suggestion",
                        "title": f"Lead Nurture Suggestion: {lead['lead_name']}",
                        "message": suggestion,
                        "related_lead_id": lead["lead_id"],
                        "priority": "medium",
                    },
                )

                conn.commit()
                logger.info(
                    f"Created nurture suggestion notification for {lead['lead_name']}"
                )

        except Exception as e:
            logger.error(f"Error creating nurture suggestion notification: {e}")

    async def create_scheduled_task_notification(self, task: Dict[str, Any]):
        """Create notification for scheduled task"""
        try:
            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO notifications 
                    (user_id, notification_type, title, message, related_lead_id, 
                     priority, created_at)
                    VALUES (:user_id, :notification_type, :title, :message, 
                           :related_lead_id, :priority, NOW())
                """
                    ),
                    {
                        "user_id": task["agent_id"],
                        "notification_type": "scheduled_task",
                        "title": f"Scheduled {task['interaction_type'].title()}: {task['lead_name']}",
                        "message": f"You have a {task['interaction_type']} scheduled with {task['lead_name']} at {task['scheduled_for'][11:16]}.",
                        "related_lead_id": task["lead_id"],
                        "priority": "high",
                    },
                )

                conn.commit()
                logger.info(
                    f"Created scheduled task notification for {task['lead_name']}"
                )

        except Exception as e:
            logger.error(f"Error creating scheduled task notification: {e}")

    def stop_scheduler(self):
        """Stop the nurturing scheduler"""
        self.is_running = False
        logger.info("🛑 Proactive Nurturing Scheduler stopped.")

    async def run_manual_nurture_check(self) -> Dict[str, Any]:
        """Run a manual nurture check and return results"""
        logger.info("🔍 Running manual nurture check...")

        try:
            with engine.connect() as conn:
                # Get leads needing attention
                result = conn.execute(
                    text(
                        """
                    SELECT l.id, l.client_name, l.client_email, l.agent_id, l.last_contacted_at,
                           l.nurture_status, l.status
                    FROM leads l
                    WHERE (l.last_contacted_at IS NULL OR 
                           l.last_contacted_at < NOW() - INTERVAL '5 days')
                    AND l.status NOT IN ('closed', 'lost')
                    AND l.nurture_status != 'Closed'
                    ORDER BY l.last_contacted_at ASC NULLS FIRST
                    LIMIT 10
                """
                    )
                )

                leads = []
                for row in result.fetchall():
                    leads.append(
                        {
                            "lead_id": row.id,
                            "lead_name": row.client_name,
                            "lead_email": row.client_email,
                            "agent_id": row.agent_id,
                            "last_contacted": row.last_contacted_at.isoformat()
                            if row.last_contacted_at
                            else None,
                            "nurture_status": row.nurture_status,
                            "status": row.status,
                        }
                    )

                return {
                    "success": True,
                    "leads_needing_attention": leads,
                    "total_count": len(leads),
                    "check_time": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error in manual nurture check: {e}")
            return {
                "success": False,
                "error": str(e),
                "check_time": datetime.now().isoformat(),
            }


# Global scheduler instance
nurturing_scheduler = NurturingScheduler()


async def start_nurturing_scheduler():
    """Start the nurturing scheduler (to be called from main.py)"""
    await nurturing_scheduler.start_scheduler()


def stop_nurturing_scheduler():
    """Stop the nurturing scheduler"""
    nurturing_scheduler.stop_scheduler()
