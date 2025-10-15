#!/usr/bin/env python3
"""
Direct SQLite Database Seeding Script
===================================
Seeds the database with test data using direct SQLite connection.
"""

import sqlite3
from datetime import datetime, timedelta
import random
import os

# Sample data
DUBAI_LOCATIONS = [
    "Downtown Dubai", "Dubai Marina", "Palm Jumeirah", "Business Bay",
    "Dubai Hills Estate", "Arabian Ranches", "JBR", "Emirates Hills", "DIFC"
]

PROPERTY_TYPES = ["apartment", "villa", "townhouse", "penthouse", "studio"]

def seed_users(cur):
    """Create sample users"""
    users = [
        ("sarah.johnson@realtorpro.ae", "Sarah", "Johnson", "agent"),
        ("michael.chen@realtorpro.ae", "Michael", "Chen", "agent"),
        ("fatima.ali@realtorpro.ae", "Fatima", "Ali", "agent"),
    ]
    
    password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/6UzqU/rJ3Uy"  # demo123
    created = 0
    
    for email, first_name, last_name, role in users:
        # Check if user exists
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, email_verified)
                VALUES (?, ?, ?, ?, ?, 1, 1)
            """, (email, password_hash, first_name, last_name, role))
            created += 1
            print(f"✓ Created user: {email}")
        else:
            print(f"✓ User {email} already exists")
    
    # Get agent IDs
    cur.execute("SELECT id FROM users WHERE role = 'agent'")
    agent_ids = [row[0] for row in cur.fetchall()]
    
    return agent_ids, created


def seed_properties(cur, agent_ids):
    """Create sample properties"""
    created = 0
    
    for i in range(30):
        location = random.choice(DUBAI_LOCATIONS)
        property_type = random.choice(PROPERTY_TYPES)
        
        # Price based on type
        base_prices = {
            "studio": (450000, 750000),
            "apartment": (800000, 2500000),
            "townhouse": (1500000, 4000000),
            "villa": (3000000, 15000000),
            "penthouse": (5000000, 25000000),
        }
        price = random.randint(*base_prices[property_type])
        
        # Bedrooms
        bedrooms_range = {
            "studio": (0, 0), "apartment": (1, 3), "townhouse": (2, 4),
            "villa": (3, 7), "penthouse": (3, 5),
        }
        bedrooms = random.randint(*bedrooms_range[property_type])
        bathrooms = bedrooms if bedrooms > 0 else 1
        
        # Area
        area_ranges = {
            "studio": (400, 650), "apartment": (700, 2000), "townhouse": (1800, 3500),
            "villa": (3500, 15000), "penthouse": (3000, 8000),
        }
        area = random.randint(*area_ranges[property_type])
        
        title = f"{property_type.capitalize()} in {location}"
        description = f"Beautiful {property_type} with {bedrooms} bedrooms in {location}"
        
        cur.execute("""
            INSERT INTO properties (
                title, description, property_type, price, price_aed, location, 
                area_sqft, bedrooms, bathrooms, listing_status, agent_id, 
                furnishing_status, gym_available, pool_available, security_24_7,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, description, property_type, price, price, location,
            area, bedrooms, bathrooms, random.choice(["live", "live", "live", "sold"]),
            random.choice(agent_ids), random.choice(["furnished", "unfurnished", "semi-furnished"]),
            random.choice([1, 1, 0]), random.choice([1, 1, 0]), 1,
            (datetime.utcnow() - timedelta(days=random.randint(1, 180))).isoformat()
        ))
        created += 1
    
    return created


def seed_leads(cur, agent_ids):
    """Create sample leads"""
    first_names = ["Ahmed", "Fatima", "John", "Sarah", "Mohammed", "Lisa", "Omar", "Emily"]
    last_names = ["Al Maktoum", "Smith", "Johnson", "Williams", "Brown", "Jones"]
    
    created = 0
    for i in range(20):
        first = random.choice(first_names)
        last = random.choice(last_names)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@email.com"
        phone = f"+971-{random.randint(50, 59)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        budget_min = random.choice([500000, 1000000, 2000000, 5000000])
        budget_max = budget_min * 2
        
        cur.execute("""
            INSERT INTO leads (
                name, email, phone, status, source, budget_min, budget_max,
                property_type, nurture_status, assigned_agent_id, lead_score,
                urgency_level, preferred_contact_method, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, email, phone, random.choice(["new", "contacted", "qualified", "viewing"]),
            random.choice(["website", "referral", "social_media", "property_portal"]),
            budget_min, budget_max, random.choice(PROPERTY_TYPES),
            random.choice(["new", "hot", "warm", "cold"]), random.choice(agent_ids),
            random.randint(30, 95), random.choice(["low", "normal", "high"]),
            random.choice(["email", "phone", "whatsapp"]),
            (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat()
        ))
        created += 1
    
    return created


def main():
    """Main seeding function"""
    print("\n" + "=" * 60)
    print("🌱 AURA RealtorProAI - Direct SQLite Seeding")
    print("=" * 60 + "\n")
    
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'propertypro_dev.db'))
    print(f"📊 Database: {DB_FILE}\n")
    
    try:
    # Connect to SQLite database
        db_path = os.path.abspath(DB_FILE)
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            return
            
        conn = sqlite3.connect(db_path)
        print(f"Connected to: {db_path}")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        print("👤 Seeding users...")
        agent_ids, users_created = seed_users(cur)
        print(f"   Created {users_created} new users, {len(agent_ids)} agents total")
        
        if not agent_ids:
            print("\n❌ No agents found. Please check the database.")
            return
        
        print("\n🏠 Seeding properties...")
        properties_created = seed_properties(cur, agent_ids)
        print(f"   Created {properties_created} properties")
        
        print("\n📞 Seeding leads...")
        leads_created = seed_leads(cur, agent_ids)
        print(f"   Created {leads_created} leads")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ Database seeding completed!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   • Agents: {len(agent_ids)}")
        print(f"   • Properties: {properties_created}")
        print(f"   • Leads: {leads_created}")
        print("\n🔐 Sample credentials:")
        print("   Email: sarah.johnson@realtorpro.ae")
        print("   Password: demo123\n")
        
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


if __name__ == "__main__":
    main()