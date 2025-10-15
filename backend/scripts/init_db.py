#!/usr/bin/env python3
"""
Simple Database Initialization Script
===================================
Creates essential tables in SQLite database without ORM dependencies.
"""

import sqlite3
import os
from pathlib import Path

# Ensure we're in backend directory
os.chdir(Path(__file__).parent.parent)

# Database file
DB_FILE = "./propertypro_dev.db"

# SQL to create tables
CREATE_TABLES = """
-- Users table
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

-- Create indices
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(location);
CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(listing_status);
CREATE INDEX IF NOT EXISTS idx_properties_agent ON properties(agent_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_agent ON leads(assigned_agent_id);
"""

def main():
    print("\nInitializing database...")
    print(f"Database file: {DB_FILE}")
    
    try:
        # Create db directory if needed
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        
        # Connect and create tables
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        # Split into individual statements and execute
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
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  • {table}: {count} rows")
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()