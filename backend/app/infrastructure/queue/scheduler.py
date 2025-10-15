#!/usr/bin/env python3
"""
Daily Briefing Scheduler for Dubai Real Estate RAG System
This module handles the automated daily briefing generation for real estate agents
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_manager import AIEnhancementManager
from app.core.settings import DATABASE_URL, GOOGLE_API_KEY, AI_MODEL
import google.generativeai as genai

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DailyBriefingScheduler:
    """Scheduler for daily briefing generation"""

    def __init__(self):
        self.engine = create_engine(DATABASE_URL)

        # Configure Google Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(AI_MODEL)

        # Initialize AI Manager
        self.ai_manager = AIEnhancementManager(DATABASE_URL, self.model)

        # Initialize scheduler
        self.scheduler = AsyncIOScheduler()

    async def send_daily_briefings(self):
        """Send daily briefings to all active agents"""
        try:
            logger.info("🔄 Starting daily briefing generation...")

            # Get all active agents
            active_agents = self._get_active_agents()

            if not active_agents:
                logger.info("ℹ️ No active agents found")
                return

            logger.info(f"📧 Generating briefings for {len(active_agents)} agents")

            for agent in active_agents:
                try:
                    # Generate briefing for the agent
                    briefing_text = self.ai_manager.generate_daily_briefing_for_agent(
                        agent["id"]
                    )

                    # Save briefing as a message in the agent's primary conversation
                    await self._save_briefing_message(agent["id"], briefing_text)

                    logger.info(
                        f"✅ Briefing generated for agent {agent['first_name']} {agent['last_name']}"
                    )

                except Exception as e:
                    logger.error(
                        f"❌ Error generating briefing for agent {agent['id']}: {e}"
                    )

            logger.info("✅ Daily briefing generation completed")

        except Exception as e:
            logger.error(f"❌ Error in send_daily_briefings: {e}")

    def _get_active_agents(self) -> List[Dict[str, Any]]:
        """Get all active agents from the database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT id, first_name, last_name, email
                    FROM users 
                    WHERE role = 'agent' 
                    AND is_active = TRUE
                    ORDER BY id
                """
                    )
                )

                return [dict(row._mapping) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error fetching active agents: {e}")
            return []

    async def _save_briefing_message(self, agent_id: int, briefing_text: str):
        """Save the briefing as a message in the agent's primary conversation"""
        try:
            with self.engine.connect() as conn:
                # Get or create the agent's primary conversation
                conversation_id = self._get_or_create_agent_conversation(conn, agent_id)

                # Save the briefing message
                conn.execute(
                    text(
                        """
                    INSERT INTO messages (conversation_id, role, content, message_type, metadata)
                    VALUES (:conversation_id, :role, :content, :message_type, :metadata)
                """
                    ),
                    {
                        "conversation_id": conversation_id,
                        "role": "assistant",
                        "content": briefing_text,
                        "message_type": "text",
                        "metadata": '{"type": "daily_briefing", "generated_at": "'
                        + datetime.now().isoformat()
                        + '"}',
                    },
                )

                conn.commit()
                logger.info(f"💾 Briefing saved to conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Error saving briefing message: {e}")

    def _get_or_create_agent_conversation(self, conn, agent_id: int) -> int:
        """Get or create the agent's primary conversation thread"""
        try:
            # Try to get existing primary conversation
            result = conn.execute(
                text(
                    """
                SELECT id FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": f"agent_{agent_id}_primary"},
            )

            row = result.fetchone()
            if row:
                return row[0]

            # Create new primary conversation
            result = conn.execute(
                text(
                    """
                INSERT INTO conversations (session_id, role, title)
                VALUES (:session_id, :role, :title)
                RETURNING id
            """
                ),
                {
                    "session_id": f"agent_{agent_id}_primary",
                    "role": "agent",
                    "title": f"Agent {agent_id} - Primary Conversation",
                },
            )

            conversation_id = result.fetchone()[0]
            conn.commit()
            return conversation_id

        except Exception as e:
            logger.error(f"Error getting/creating agent conversation: {e}")
            raise

    def start_scheduler(self):
        """Start the scheduler with daily briefing job"""
        try:
            # Add the daily briefing job - runs at 7:00 AM Dubai time
            self.scheduler.add_job(
                func=self.send_daily_briefings,
                trigger=CronTrigger(hour=7, minute=0, timezone="Asia/Dubai"),
                id="daily_briefing",
                name="Daily Briefing Generation",
                replace_existing=True,
            )

            # Start the scheduler
            self.scheduler.start()
            logger.info("🚀 Daily briefing scheduler started")
            logger.info("⏰ Daily briefings will be generated at 7:00 AM Dubai time")

        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")

    def stop_scheduler(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("🛑 Daily briefing scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")


# Global scheduler instance
scheduler_instance = None


def start_daily_briefing_scheduler():
    """Start the daily briefing scheduler"""
    global scheduler_instance

    try:
        scheduler_instance = DailyBriefingScheduler()
        scheduler_instance.start_scheduler()
        return scheduler_instance
    except Exception as e:
        logger.error(f"❌ Failed to start daily briefing scheduler: {e}")
        return None


def stop_daily_briefing_scheduler():
    """Stop the daily briefing scheduler"""
    global scheduler_instance

    if scheduler_instance:
        scheduler_instance.stop_scheduler()


# For testing purposes
async def test_daily_briefing():
    """Test function to generate a daily briefing"""
    try:
        scheduler = DailyBriefingScheduler()
        await scheduler.send_daily_briefings()
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")


if __name__ == "__main__":
    # Test the scheduler
    asyncio.run(test_daily_briefing())
