#!/usr/bin/env python3

"""
Database Table Creation Script
==============================

Creates the essential tables needed for the intelligence pipeline:
- ai_tasks (for task orchestration)
- intelligence_content (for storing generated content)
"""

import json

from app.core.database import get_db
from sqlalchemy import text

try:
    from app.domain.ai.property_brochure_service import DEFAULT_LISTINGS
except ImportError:
    DEFAULT_LISTINGS = []


def create_tables():
    """Create essential tables for the intelligence pipeline"""

    db_session = next(get_db())

    try:
        print("🔨 Creating database tables...")

        # Create ai_tasks table
        print("Creating ai_tasks table...")
        db_session.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS ai_tasks (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                task_type TEXT NOT NULL,
                input_data JSON NOT NULL,
                output_data JSON NULL,
                status TEXT NOT NULL DEFAULT 'queued',
                priority INTEGER NOT NULL DEFAULT 5,
                progress INTEGER NOT NULL DEFAULT 0,
                error_message TEXT NULL,
                retries INTEGER NOT NULL DEFAULT 0,
                max_retries INTEGER NOT NULL DEFAULT 3,
                worker_id TEXT NULL,
                started_at DATETIME NULL,
                completed_at DATETIME NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )

        # Create indexes for ai_tasks
        db_session.execute(
            text("CREATE INDEX IF NOT EXISTS ix_ai_tasks_user_id ON ai_tasks(user_id)")
        )
        db_session.execute(
            text("CREATE INDEX IF NOT EXISTS ix_ai_tasks_status ON ai_tasks(status)")
        )
        db_session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_ai_tasks_task_type ON ai_tasks(task_type)"
            )
        )
        db_session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_ai_tasks_priority ON ai_tasks(priority)"
            )
        )

        # Create intelligence_content table
        print("Creating intelligence_content table...")
        db_session.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS intelligence_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT UNIQUE NOT NULL,
                task_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                title TEXT NOT NULL,
                enhanced BOOLEAN NOT NULL DEFAULT 1,
                quality_scores JSON NOT NULL,
                memory_context JSON NOT NULL,
                generated_content JSON NOT NULL,
                metadata JSON NOT NULL,
                export_ready BOOLEAN NOT NULL DEFAULT 1,
                version TEXT NOT NULL DEFAULT '3.4',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )

        # Create indexes for intelligence_content
        db_session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_intelligence_content_id ON intelligence_content(content_id)"
            )
        )
        db_session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_intelligence_content_task_id ON intelligence_content(task_id)"
            )
        )
        db_session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_intelligence_content_type ON intelligence_content(content_type)"
            )
        )
        db_session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_intelligence_content_created ON intelligence_content(created_at)"
            )
        )

        # Create listings table for property brochures
        print("Creating listings table...")
        db_session.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS listings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                subtitle TEXT NULL,
                price REAL NOT NULL,
                location TEXT NOT NULL,
                property_type TEXT NULL,
                bedrooms REAL NULL,
                bathrooms REAL NULL,
                area_sqft REAL NULL,
                highlights JSON NULL,
                description TEXT,
                images JSON NULL,
                amenities JSON NULL,
                neighborhood_insights JSON NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )

        # Create indexes for listings
        db_session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_listings_location ON listings(location)"
            )
        )
        db_session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_listings_property_type ON listings(property_type)"
            )
        )

        if DEFAULT_LISTINGS:
            existing_listings = db_session.execute(
                text("SELECT COUNT(*) FROM listings")
            ).scalar()
            if not existing_listings:
                print("Seeding default listings for brochure generator...")
                for listing in DEFAULT_LISTINGS:
                    payload = listing.copy()
                    highlights = payload.get("highlights")
                    images = payload.get("images")
                    amenities = payload.get("amenities")
                    neighborhood = payload.get("neighborhood_insights")
                    payload_json = {
                        "id": payload.get("id"),
                        "title": payload.get("title"),
                        "subtitle": payload.get("subtitle"),
                        "price": payload.get("price", 0),
                        "location": payload.get("location"),
                        "property_type": payload.get("property_type"),
                        "bedrooms": payload.get("bedrooms"),
                        "bathrooms": payload.get("bathrooms"),
                        "area_sqft": payload.get("area_sqft"),
                        "highlights": json.dumps(highlights) if highlights else None,
                        "description": payload.get("description"),
                        "images": json.dumps(images) if images else None,
                        "amenities": json.dumps(amenities) if amenities else None,
                        "neighborhood_insights": json.dumps(neighborhood)
                        if neighborhood
                        else None,
                    }
                    db_session.execute(
                        text(
                            """
                        INSERT OR IGNORE INTO listings (
                            id, title, subtitle, price, location, property_type, bedrooms, bathrooms,
                            area_sqft, highlights, description, images, amenities, neighborhood_insights, created_at
                        ) VALUES (
                            :id, :title, :subtitle, :price, :location, :property_type, :bedrooms, :bathrooms,
                            :area_sqft, :highlights, :description, :images, :amenities, :neighborhood_insights, CURRENT_TIMESTAMP
                        )
                    """
                        ),
                        payload_json,
                    )

        # Create users table (minimal for development)
        print("Creating users table...")
        db_session.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'client',
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )

        # Insert a development user if it doesn't exist
        print("Creating development user...")
        db_session.execute(
            text(
                """
            INSERT OR IGNORE INTO users (id, email, password_hash, first_name, last_name, role)
            VALUES (1, 'admin@dubai-estate.com', 'dev_hash', 'Admin', 'User', 'admin')
        """
            )
        )

        # Commit all changes
        db_session.commit()

        print("✅ Database tables created successfully!")

        # Verify tables exist
        result = db_session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result.fetchall()]

        print(f"📋 Created tables: {', '.join(sorted(tables))}")

        # Test ai_tasks table
        result = db_session.execute(text("SELECT COUNT(*) FROM ai_tasks"))
        task_count = result.fetchone()[0]
        print(f"🔍 ai_tasks table ready with {task_count} records")

        # Test intelligence_content table
        result = db_session.execute(text("SELECT COUNT(*) FROM intelligence_content"))
        content_count = result.fetchone()[0]
        print(f"🔍 intelligence_content table ready with {content_count} records")

        # Test listings table
        result = db_session.execute(text("SELECT COUNT(*) FROM listings"))
        listing_count = result.fetchone()[0]
        print(f"🔍 listings table ready with {listing_count} records")

        # Test users table
        result = db_session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.fetchone()[0]
        print(f"🔍 users table ready with {user_count} records")

        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        db_session.rollback()
        return False

    finally:
        db_session.close()


if __name__ == "__main__":
    success = create_tables()
    exit(0 if success else 1)
