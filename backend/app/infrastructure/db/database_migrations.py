#!/usr/bin/env python3
"""
Database Migration Script for Blueprint 2.0: Proactive AI Copilot
Implements schema changes for Web-Based Content Delivery and Proactive Lead Nurturing
"""

import logging
from sqlalchemy import create_engine, text
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseMigration:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

    def run_migrations(self):
        """Run all Blueprint 2.0 migrations"""
        logger.info("🚀 Starting Blueprint 2.0 database migrations...")

        try:
            with self.engine.connect() as conn:
                # Phase 1.1: Create generated_documents table
                self._create_generated_documents_table(conn)

                # Phase 1.2: Enhance leads table
                self._enhance_leads_table(conn)

                # Phase 1.3: Create lead_history table (if not exists)
                self._create_lead_history_table(conn)

                # Phase 1.4: Create notifications table
                self._create_notifications_table(conn)

                # Phase 1.5: Create tasks table (if not exists)
                self._create_tasks_table(conn)

                conn.commit()
                logger.info("✅ All Blueprint 2.0 migrations completed successfully!")

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise

    def _create_generated_documents_table(self, conn):
        """Create generated_documents table for web-based content delivery"""
        logger.info("📄 Creating generated_documents table...")

        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS generated_documents (
                id SERIAL PRIMARY KEY,
                document_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                content_html TEXT,
                preview_summary TEXT,
                result_url VARCHAR(500),
                file_path VARCHAR(500), -- Keep for backward compatibility
                agent_id INTEGER REFERENCES users(id),
                session_id VARCHAR(255),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )

        # Create indexes for performance
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_generated_documents_agent_id 
            ON generated_documents(agent_id)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_generated_documents_type 
            ON generated_documents(document_type)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_generated_documents_created_at 
            ON generated_documents(created_at)
        """
            )
        )

        logger.info("✅ generated_documents table created successfully")

    def _enhance_leads_table(self, conn):
        """Add new columns to leads table for proactive nurturing"""
        logger.info("👥 Enhancing leads table...")

        # Add new columns for proactive nurturing
        columns_to_add = [
            ("last_contacted_at", "TIMESTAMP"),
            ("next_follow_up_at", "TIMESTAMP"),
            ("nurture_status", "VARCHAR(50) DEFAULT 'New'"),
            ("assigned_agent_id", "INTEGER REFERENCES users(id)"),
        ]

        for column_name, column_type in columns_to_add:
            conn.execute(
                text(
                    f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='leads' AND column_name='{column_name}'
                    ) THEN
                        ALTER TABLE leads ADD COLUMN {column_name} {column_type};
                    END IF;
                END $$;
            """
                )
            )

        # Create indexes for new columns
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_leads_nurture_status 
            ON leads(nurture_status)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_leads_next_follow_up 
            ON leads(next_follow_up_at)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_leads_last_contacted 
            ON leads(last_contacted_at)
        """
            )
        )

        logger.info("✅ leads table enhanced successfully")

    def _create_lead_history_table(self, conn):
        """Create lead_history table for tracking interactions"""
        logger.info("📝 Creating lead_history table...")

        # First, check if the table exists and what columns it has
        result = conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'lead_history'
        """
            )
        ).fetchall()

        existing_columns = [row[0] for row in result]

        if not existing_columns:
            # Table doesn't exist, create it
            conn.execute(
                text(
                    """
                CREATE TABLE lead_history (
                    id SERIAL PRIMARY KEY,
                    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
                    agent_id INTEGER REFERENCES users(id),
                    interaction_type VARCHAR(50) NOT NULL, -- 'call', 'email', 'meeting', 'note'
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scheduled_for TIMESTAMP, -- For future scheduled interactions
                    metadata JSONB
                )
            """
                )
            )
        else:
            # Table exists, add missing columns
            if "agent_id" not in existing_columns:
                conn.execute(
                    text(
                        """
                    ALTER TABLE lead_history 
                    ADD COLUMN agent_id INTEGER REFERENCES users(id)
                """
                    )
                )

            if "scheduled_for" not in existing_columns:
                conn.execute(
                    text(
                        """
                    ALTER TABLE lead_history 
                    ADD COLUMN scheduled_for TIMESTAMP
                """
                    )
                )

            if "metadata" not in existing_columns:
                conn.execute(
                    text(
                        """
                    ALTER TABLE lead_history 
                    ADD COLUMN metadata JSONB
                """
                    )
                )

        # Create indexes only for columns that exist
        if "lead_id" in existing_columns:
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_lead_history_lead_id 
                ON lead_history(lead_id)
            """
                )
            )

        if "agent_id" in existing_columns:
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_lead_history_agent_id 
                ON lead_history(agent_id)
            """
                )
            )

        if "created_at" in existing_columns:
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_lead_history_created_at 
                ON lead_history(created_at)
            """
                )
            )

        if "scheduled_for" in existing_columns:
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_lead_history_scheduled_for 
                ON lead_history(scheduled_for)
            """
                )
            )

        logger.info("✅ lead_history table created/updated successfully")

    def _create_notifications_table(self, conn):
        """Create notifications table for proactive alerts"""
        logger.info("🔔 Creating notifications table...")

        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                notification_type VARCHAR(50) NOT NULL, -- 'follow_up', 'nurture_suggestion', 'scheduled_task'
                title VARCHAR(255) NOT NULL,
                message TEXT,
                related_lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
                related_document_id INTEGER REFERENCES generated_documents(id) ON DELETE CASCADE,
                priority VARCHAR(20) DEFAULT 'medium', -- 'high', 'medium', 'low'
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_for TIMESTAMP, -- For scheduled notifications
                metadata JSONB
            )
        """
            )
        )

        # Create indexes
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
            ON notifications(user_id)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_notifications_is_read 
            ON notifications(is_read)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_notifications_created_at 
            ON notifications(created_at)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_notifications_scheduled_for 
            ON notifications(scheduled_for)
        """
            )
        )

        logger.info("✅ notifications table created successfully")

    def _create_tasks_table(self, conn):
        """Create tasks table for background task management"""
        logger.info("📋 Creating tasks table...")

        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                task_id VARCHAR(255) UNIQUE NOT NULL,
                task_type VARCHAR(50) NOT NULL, -- 'document_generation', 'lead_nurturing', 'notification'
                status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
                agent_id INTEGER REFERENCES users(id),
                related_lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
                related_document_id INTEGER REFERENCES generated_documents(id) ON DELETE CASCADE,
                progress DECIMAL(5,2) DEFAULT 0.0,
                result_data JSONB,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                metadata JSONB
            )
        """
            )
        )

        # Create indexes
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_tasks_task_id 
            ON tasks(task_id)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_tasks_status 
            ON tasks(status)
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_tasks_agent_id 
            ON tasks(agent_id)
        """
            )
        )

        logger.info("✅ tasks table created successfully")


def main():
    """Run the migration script"""
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://admin:password123@localhost:5432/real_estate_db"
    )

    migration = DatabaseMigration(db_url)
    migration.run_migrations()


if __name__ == "__main__":
    main()
