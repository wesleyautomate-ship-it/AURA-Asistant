#!/usr/bin/env python3
"""
Simplified Database Seeding Script
===================================
Works with existing database tables without requiring full model configuration.
"""

import sys
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from app.core.database import get_db
from app.core.settings import DATABASE_URL

# Sample data
DUBAI_LOCATIONS = [
    "Downtown Dubai", "Dubai Marina", "Palm Jumeirah", "Business Bay",
    "Dubai Hills Estate", "Arabian Ranches", "JBR", "Emirates Hills", "DIFC"
]

PROPERTY_TYPES = ["apartment", "villa", "townhouse", "penthouse", "studio"]


def seed_users(db):
    """Create sample users using raw SQL"""
    users_data = [
        ("sarah.johnson@realtorpro.ae", "Sarah", "Johnson", "agent"),
        ("michael.chen@realtorpro.ae", "Michael", "Chen", "agent"),
        ("fatima.ali@realtorpro.ae", "Fatima", "Ali", "agent"),
    ]
    
    password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/6UzqU/rJ3Uy"  # demo123
    
    created = 0
    for email, first_name, last_name, role in users_data:
        # Check if exists
        result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
        existing = result.fetchone()
        
        if not existing:
            db.execute(
                text("""
                    INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, email_verified)
                    VALUES (:email, :password_hash, :first_name, :last_name, :role, 1, 1)
                """),
                {
                    "email": email,
                    "password_hash": password_hash,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": role
                }
            )
            created += 1
            print(f"✓ Created user: {email}")
        else:
            print(f"✓ User {email} already exists")
    
    db.commit()
    
    # Get user IDs
    result = db.execute(text("SELECT id FROM users WHERE role = 'agent'"))
    agent_ids = [row[0] for row in result.fetchall()]
    
    return agent_ids, created


def seed_properties(db, agent_ids):
    """Create sample properties using raw SQL"""
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
        
        db.execute(
            text("""
                INSERT INTO properties 
                (title, description, property_type, price, price_aed, location, area_sqft, 
                 bedrooms, bathrooms, listing_status, agent_id, furnishing_status, 
                 gym_available, pool_available, security_24_7, created_at)
                VALUES 
                (:title, :description, :property_type, :price, :price_aed, :location, :area_sqft,
                 :bedrooms, :bathrooms, :listing_status, :agent_id, :furnishing_status,
                 :gym_available, :pool_available, :security_24_7, :created_at)
            """),
            {
                "title": title,
                "description": description,
                "property_type": property_type,
                "price": price,
                "price_aed": price,
                "location": location,
                "area_sqft": area,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "listing_status": random.choice(["live", "live", "live", "sold"]),
                "agent_id": random.choice(agent_ids),
                "furnishing_status": random.choice(["furnished", "unfurnished", "semi-furnished"]),
                "gym_available": random.choice([1, 1, 0]),
                "pool_available": random.choice([1, 1, 0]),
                "security_24_7": 1,
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 180))
            }
        )
        created += 1
    
    db.commit()
    return created


def seed_leads(db, agent_ids):
    """Create sample leads using raw SQL"""
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
        
        db.execute(
            text("""
                INSERT INTO leads 
                (name, email, phone, status, source, budget_min, budget_max, 
                 property_type, nurture_status, assigned_agent_id, lead_score, 
                 urgency_level, preferred_contact_method, created_at)
                VALUES 
                (:name, :email, :phone, :status, :source, :budget_min, :budget_max,
                 :property_type, :nurture_status, :assigned_agent_id, :lead_score,
                 :urgency_level, :preferred_contact_method, :created_at)
            """),
            {
                "name": name,
                "email": email,
                "phone": phone,
                "status": random.choice(["new", "contacted", "qualified", "viewing"]),
                "source": random.choice(["website", "referral", "social_media", "property_portal"]),
                "budget_min": budget_min,
                "budget_max": budget_max,
                "property_type": random.choice(PROPERTY_TYPES),
                "nurture_status": random.choice(["new", "hot", "warm", "cold"]),
                "assigned_agent_id": random.choice(agent_ids),
                "lead_score": random.randint(30, 95),
                "urgency_level": random.choice(["low", "normal", "high"]),
                "preferred_contact_method": random.choice(["email", "phone", "whatsapp"]),
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 90))
            }
        )
        created += 1
    
    db.commit()
    return created


def main():
    """Main seeding function"""
    print("\n" + "=" * 60)
    print("🌱 AURA RealtorProAI - Simple Database Seeding")
    print("=" * 60 + "\n")
    print(f"📊 Database: {DATABASE_URL}\n")
    
    db = next(get_db())
    
    try:
        print("👤 Seeding users...")
        agent_ids, users_created = seed_users(db)
        print(f"   Created {users_created} new users, {len(agent_ids)} agents total")
        
        if not agent_ids:
            print("\n❌ No agents found. Please check the database.")
            return
        
        print("\n🏠 Seeding properties...")
        properties_created = seed_properties(db, agent_ids)
        print(f"   Created {properties_created} properties")
        
        print("\n📞 Seeding leads...")
        leads_created = seed_leads(db, agent_ids)
        print(f"   Created {leads_created} leads")
        
        print("\n" + "=" * 60)
        print("✅ Database seeding completed!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   • Agents: {len(agent_ids)}")
        print(f"   • Properties: {properties_created}")
        print(f"   • Leads: {leads_created}")
        print(f"\n🔐 Sample credentials:")
        print(f"   Email: sarah.johnson@realtorpro.ae")
        print(f"   Password: demo123\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
