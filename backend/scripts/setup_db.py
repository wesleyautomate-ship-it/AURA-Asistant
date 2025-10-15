#!/usr/bin/env python3
"""
Setup Database Script
===================
Creates SQLite database and tables for AURA RealtorProAI.
"""

import sqlite3
import os
from pathlib import Path

# Database file
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'propertypro_dev.db'))

# Drop all tables first
DROP_TABLES = """
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS properties;
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS ai_tasks;
DROP TABLE IF EXISTS intelligence_content;
"""

# SQL to create essential tables
CREATE_TABLES = """
-- Users table (simplified)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'client',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    email_verified BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Properties table
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    property_type VARCHAR(50),
    price DECIMAL(15,2),
    price_aed DECIMAL(15,2),
    location VARCHAR(255),
    area_sqft DECIMAL(10,2),
    bedrooms INTEGER,
    bathrooms INTEGER,
    listing_status VARCHAR(20) DEFAULT 'draft',
    agent_id INTEGER REFERENCES users(id),
    furnishing_status VARCHAR(50),
    gym_available BOOLEAN DEFAULT 0,
    pool_available BOOLEAN DEFAULT 0,
    security_24_7 BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'new',
    source VARCHAR(100),
    budget_min DECIMAL(12,2),
    budget_max DECIMAL(12,2),
    property_type VARCHAR(100),
    nurture_status VARCHAR(20) DEFAULT 'new',
    assigned_agent_id INTEGER REFERENCES users(id),
    lead_score INTEGER DEFAULT 0,
    urgency_level VARCHAR(20) DEFAULT 'normal',
    preferred_contact_method VARCHAR(20) DEFAULT 'email',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- AI Tasks table (for CMA workflow)
CREATE TABLE IF NOT EXISTS ai_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(64) UNIQUE NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    user_id INTEGER REFERENCES users(id),
    input_data TEXT,
    output_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Intelligence Content table
CREATE TABLE IF NOT EXISTS intelligence_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id VARCHAR(64) UNIQUE NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    content TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indices
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(location);
CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(listing_status);
CREATE INDEX IF NOT EXISTS idx_properties_agent ON properties(agent_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_agent ON leads(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_task_id ON ai_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_ai_tasks_status ON ai_tasks(status);
CREATE INDEX IF NOT EXISTS idx_intelligence_content_id ON intelligence_content(content_id);
"""

def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("🗄️ AURA RealtorProAI - Database Setup")
    print("=" * 60)
    
    # Ensure we're in project root
    os.chdir(Path(__file__).parent.parent)
    
    print(f"\n📊 Database: {DB_FILE}\n")
    
    try:
        # Delete existing database
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            print("✓ Removed existing database")
        
        # Connect and create tables
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        # Drop any existing tables
        print("\nDropping existing tables...")
        for statement in DROP_TABLES.split(";"):
            if statement.strip():
                cur.execute(statement)
                
        # Create new tables
        print("Creating tables...")
        for statement in CREATE_TABLES.split(";"):
            if statement.strip():
                cur.execute(statement)
        
        conn.commit()
        
        # Print table info
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        
        print("\n✅ Database initialized successfully!")
        print(f"\nTables created:")
        for table in sorted(tables):
            if table != "sqlite_sequence":
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"  • {table}: {count} rows")
        
        print("\n🔄 You can now run the seeding script:")
        print("   python backend/scripts/seed_sqlite.py")
        
    except sqlite3.Error as e:
        print(f"\n❌ SQLite error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()