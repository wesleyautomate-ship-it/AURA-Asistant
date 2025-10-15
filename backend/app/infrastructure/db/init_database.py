"""
Database initialization script to create all required tables
"""

import os
from sqlalchemy import (
    create_engine,
    text,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Numeric,
    Text,
    Boolean,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from env_loader import load_env

load_env()

# Database connection
database_url = os.getenv(
    "DATABASE_URL", "postgresql://admin:password123@localhost:5432/real_estate_db"
)
engine = create_engine(database_url)
Base = declarative_base()


def check_table_schema(conn, table_name):
    """Check the schema of an existing table"""
    try:
        result = conn.execute(
            text(
                f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """
            )
        )
        columns = {row[0]: row[1] for row in result}
        return columns
    except Exception as e:
        print(f"Error checking schema for {table_name}: {e}")
        return {}


def init_database():
    """Initialize all database tables"""
    try:
        with engine.connect() as conn:
            # Check existing tables and their schemas
            print("🔍 Checking existing database schema...")

            # Check properties table
            properties_columns = check_table_schema(conn, "properties")
            if properties_columns:
                print(
                    f"Properties table exists with columns: {list(properties_columns.keys())}"
                )
            else:
                # Create properties table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS properties (
                        id SERIAL PRIMARY KEY,
                        address VARCHAR(255) NOT NULL,
                        price NUMERIC(12, 2),
                        bedrooms INTEGER,
                        bathrooms NUMERIC(3, 1),
                        square_feet INTEGER,
                        property_type VARCHAR(100),
                        description TEXT,
                        listing_status VARCHAR(20) DEFAULT 'draft',
                        agent_id INTEGER REFERENCES users(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )
                print("✅ Properties table created")

            # Check clients table
            clients_columns = check_table_schema(conn, "clients")
            if clients_columns:
                print(
                    f"Clients table exists with columns: {list(clients_columns.keys())}"
                )
            else:
                # Create clients table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS clients (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255),
                        phone VARCHAR(50),
                        budget_min NUMERIC(12, 2),
                        budget_max NUMERIC(12, 2),
                        preferred_location VARCHAR(255),
                        requirements TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )
                print("✅ Clients table created")

            # Create conversations table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    user_id INTEGER REFERENCES users(id),
                    role VARCHAR(50) DEFAULT 'client',
                    title VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """
                )
            )

            # Add user_id column if it doesn't exist (for existing tables)
            try:
                conn.execute(
                    text(
                        "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"
                    )
                )
                print("✅ user_id column ensured in conversations table")
            except Exception as e:
                print(f"⚠️ user_id column check: {e}")

            # Create messages table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER REFERENCES conversations(id),
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    message_type VARCHAR(50) DEFAULT 'text',
                    metadata JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Create users table (for authentication)
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    role VARCHAR(50) DEFAULT 'client',
                    is_active BOOLEAN DEFAULT TRUE,
                    email_verified BOOLEAN DEFAULT FALSE,
                    email_verification_token VARCHAR(255) UNIQUE,
                    password_reset_token VARCHAR(255) UNIQUE,
                    password_reset_expires TIMESTAMP,
                    last_login TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Create user_sessions table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    refresh_token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    session_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """
                )
            )

            # Ensure session_data column exists (for existing tables)
            try:
                conn.execute(
                    text(
                        "ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS session_data JSONB"
                    )
                )
                print("✅ session_data column ensured in user_sessions table")
            except Exception as e:
                print(f"⚠️ session_data column check: {e}")

            # Create audit_logs table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    action VARCHAR(100) NOT NULL,
                    resource_type VARCHAR(50),
                    resource_id INTEGER,
                    details JSONB,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Create conversation_preferences table for ChatGPT-style sessions
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS conversation_preferences (
                    session_id VARCHAR(255) PRIMARY KEY,
                    user_preferences JSONB NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Create access audit log table for security monitoring
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS access_audit_log (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255) NOT NULL,
                    user_role VARCHAR(50) NOT NULL,
                    data_type VARCHAR(100) NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45)
                )
            """
                )
            )

            # Create feedback log table for quality improvement
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS feedback_log (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    user_role VARCHAR(50) NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    feedback_type VARCHAR(50) NOT NULL,
                    rating INTEGER,
                    text_feedback TEXT,
                    category VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analyzed BOOLEAN DEFAULT FALSE,
                    improvement_suggestions JSONB,
                    metadata JSONB
                )
            """
                )
            )

            # Create response quality log table for performance tracking
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS response_quality_log (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    user_role VARCHAR(50) NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    quality_indicators JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Create indexes only if columns exist
            if "address" in properties_columns:
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_properties_address ON properties(address)"
                    )
                )
            if "price" in properties_columns:
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price)"
                    )
                )
            if "property_type" in properties_columns:
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type)"
                    )
                )

            if "name" in clients_columns:
                conn.execute(
                    text("CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name)")
                )
            if "email" in clients_columns:
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email)"
                    )
                )

            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)"
                )
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)"
                )
            )

            conn.commit()
            print("✅ Database tables and indexes created successfully")

            # Insert sample data if tables are empty
            insert_sample_data(conn, properties_columns, clients_columns)

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


def insert_sample_data(conn, properties_columns, clients_columns):
    """Insert sample data for testing"""
    try:
        # Check if properties table is empty
        result = conn.execute(text("SELECT COUNT(*) FROM properties"))
        if result.fetchone()[0] == 0:
            # Insert sample properties based on actual schema
            if "address" in properties_columns:
                sample_properties = [
                    (
                        "Downtown Dubai, Burj Khalifa Area",
                        2500000,
                        2,
                        2.5,
                        1200,
                        "apartment",
                        "Luxury apartment with Burj Khalifa view",
                    ),
                    (
                        "Palm Jumeirah, Shoreline Apartments",
                        3500000,
                        3,
                        3.0,
                        1800,
                        "apartment",
                        "Beachfront apartment with private beach access",
                    ),
                    (
                        "Dubai Marina, Marina Gate",
                        1800000,
                        1,
                        1.0,
                        800,
                        "apartment",
                        "Modern studio with marina views",
                    ),
                    (
                        "Emirates Hills, Villa 123",
                        8500000,
                        5,
                        6.0,
                        4500,
                        "villa",
                        "Luxury villa with private pool and garden",
                    ),
                    (
                        "Jumeirah Beach Residence",
                        2200000,
                        2,
                        2.0,
                        1400,
                        "apartment",
                        "Beachfront apartment with sea views",
                    ),
                ]

                for prop in sample_properties:
                    conn.execute(
                        text(
                            """
                        INSERT INTO properties (address, price, bedrooms, bathrooms, square_feet, property_type, description)
                        VALUES (:address, :price, :bedrooms, :bathrooms, :square_feet, :property_type, :description)
                    """
                        ),
                        {
                            "address": prop[0],
                            "price": prop[1],
                            "bedrooms": prop[2],
                            "bathrooms": prop[3],
                            "square_feet": prop[4],
                            "property_type": prop[5],
                            "description": prop[6],
                        },
                    )

                print("✅ Sample properties inserted")
            else:
                print("⚠️ Properties table schema doesn't match expected columns")

        # Check if clients table is empty
        result = conn.execute(text("SELECT COUNT(*) FROM clients"))
        if result.fetchone()[0] == 0:
            # Insert sample clients based on actual schema
            if "name" in clients_columns:
                sample_clients = [
                    (
                        "Ahmed Al Mansouri",
                        "ahmed@email.com",
                        "+971501234567",
                        2000000,
                        3000000,
                        "Downtown Dubai",
                        "Looking for luxury apartment",
                    ),
                    (
                        "Sarah Johnson",
                        "sarah@email.com",
                        "+971502345678",
                        1500000,
                        2500000,
                        "Dubai Marina",
                        "Prefer modern apartments",
                    ),
                    (
                        "Mohammed Hassan",
                        "mohammed@email.com",
                        "+971503456789",
                        5000000,
                        8000000,
                        "Emirates Hills",
                        "Looking for villa with garden",
                    ),
                    (
                        "Lisa Chen",
                        "lisa@email.com",
                        "+971504567890",
                        1000000,
                        2000000,
                        "Palm Jumeirah",
                        "Beachfront property preferred",
                    ),
                ]

                for client in sample_clients:
                    conn.execute(
                        text(
                            """
                        INSERT INTO clients (name, email, phone, budget_min, budget_max, preferred_location, requirements)
                        VALUES (:name, :email, :phone, :budget_min, :budget_max, :preferred_location, :requirements)
                    """
                        ),
                        {
                            "name": client[0],
                            "email": client[1],
                            "phone": client[2],
                            "budget_min": client[3],
                            "budget_max": client[4],
                            "preferred_location": client[5],
                            "requirements": client[6],
                        },
                    )

                print("✅ Sample clients inserted")
            else:
                print("⚠️ Clients table schema doesn't match expected columns")

        conn.commit()

    except Exception as e:
        print(f"❌ Sample data insertion failed: {e}")


if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_database()
    print("✅ Database initialization completed!")
