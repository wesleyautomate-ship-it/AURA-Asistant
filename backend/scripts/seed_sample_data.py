#!/usr/bin/env python3
"""
Database Seeding Script for AURA RealtorProAI
==============================================

Populates the database with realistic sample data for testing and demonstration:
- Users (agents)
- Properties (Dubai real estate)
- Leads (potential clients)
- Clients (converted leads)
- Transactions (property deals)

Usage:
    python scripts/seed_sample_data.py
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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db
from app.core.settings import DATABASE_URL
from app.core.models import User, Base
from app.domain.listings.enhanced_real_estate_models import (
    EnhancedProperty,
    EnhancedLead,
    EnhancedClient,
)

# Sample data
DUBAI_LOCATIONS = [
    "Downtown Dubai",
    "Dubai Marina",
    "Palm Jumeirah",
    "Business Bay",
    "Dubai Hills Estate",
    "Arabian Ranches",
    "Jumeirah Beach Residence (JBR)",
    "Emirates Hills",
    "DIFC",
    "Al Barsha",
]

PROPERTY_TYPES = ["apartment", "villa", "townhouse", "penthouse", "studio"]

PROPERTY_TITLES = [
    "Luxurious {type} with Burj Khalifa View",
    "Modern {type} in Prime Location",
    "Spacious {type} with Marina View",
    "Stunning {type} Near Dubai Mall",
    "Brand New {type} with Pool Access",
    "Elegant {type} in Gated Community",
    "Contemporary {type} with Garden",
    "Premium {type} with Beach Access",
    "Exclusive {type} in High-Rise Tower",
    "Charming {type} with Skyline View",
]

AMENITIES = {
    "apartment": ["gym", "pool", "parking", "security", "concierge"],
    "villa": ["garden", "pool", "garage", "security", "maid_room"],
    "townhouse": ["garden", "parking", "community_pool", "playground"],
    "penthouse": ["private_pool", "terrace", "gym", "concierge", "valet"],
    "studio": ["gym", "pool", "parking", "security"],
}


def create_sample_users(db):
    """Create sample agent users"""
    users = [
        {
            "email": "sarah.johnson@realtorpro.ae",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/6UzqU/rJ3Uy",  # password: "demo123"
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "agent",
            "is_active": True,
            "email_verified": True,
        },
        {
            "email": "michael.chen@realtorpro.ae",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/6UzqU/rJ3Uy",
            "first_name": "Michael",
            "last_name": "Chen",
            "role": "agent",
            "is_active": True,
            "email_verified": True,
        },
        {
            "email": "fatima.ali@realtorpro.ae",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/6UzqU/rJ3Uy",
            "first_name": "Fatima",
            "last_name": "Ali",
            "role": "agent",
            "is_active": True,
            "email_verified": True,
        },
    ]

    created_users = []
    for user_data in users:
        # Check if user already exists
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            print(f"✓ User {user_data['email']} already exists")
            created_users.append(existing)
        else:
            user = User(**user_data)
            db.add(user)
            db.flush()
            created_users.append(user)
            print(f"✓ Created user: {user_data['email']}")

    db.commit()
    return created_users


def create_sample_properties(db, agents):
    """Create sample properties"""
    properties = []

    for i in range(30):
        location = random.choice(DUBAI_LOCATIONS)
        property_type = random.choice(PROPERTY_TYPES)
        title_template = random.choice(PROPERTY_TITLES)
        title = title_template.format(type=property_type.capitalize())

        # Price based on property type and location
        base_prices = {
            "studio": (450000, 750000),
            "apartment": (800000, 2500000),
            "townhouse": (1500000, 4000000),
            "villa": (3000000, 15000000),
            "penthouse": (5000000, 25000000),
        }

        price_min, price_max = base_prices[property_type]
        price = Decimal(random.randint(price_min, price_max))

        # Bedrooms and bathrooms
        bedrooms_range = {
            "studio": (0, 0),
            "apartment": (1, 3),
            "townhouse": (2, 4),
            "villa": (3, 7),
            "penthouse": (3, 5),
        }
        bedrooms = random.randint(*bedrooms_range[property_type])
        bathrooms = bedrooms if bedrooms > 0 else 1

        # Area in sqft
        area_ranges = {
            "studio": (400, 650),
            "apartment": (700, 2000),
            "townhouse": (1800, 3500),
            "villa": (3500, 15000),
            "penthouse": (3000, 8000),
        }
        area = Decimal(random.randint(*area_ranges[property_type]))

        # Description
        descriptions = [
            f"This stunning {property_type} offers an exceptional living experience in the heart of {location}. "
            f"Featuring {bedrooms} bedrooms and {bathrooms} bathrooms across {area} sqft, this property combines "
            f"luxury and comfort. Perfect for those seeking a premium lifestyle in Dubai's most sought-after location.",
            f"Discover this magnificent {property_type} located in prestigious {location}. With {area} sqft of "
            f"thoughtfully designed living space, including {bedrooms} spacious bedrooms and {bathrooms} elegant bathrooms, "
            f"this property represents the epitome of Dubai luxury living.",
            f"Welcome to your dream home in {location}. This exceptional {property_type} spans {area} sqft and "
            f"features {bedrooms} bedrooms and {bathrooms} bathrooms. Ideally situated with easy access to Dubai's "
            f"finest dining, shopping, and entertainment venues.",
        ]

        property_data = {
            "title": title,
            "description": random.choice(descriptions),
            "property_type": property_type,
            "price": price,
            "price_aed": price,
            "location": location,
            "area_sqft": area,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "listing_status": random.choice(["live", "live", "live", "sold"]),
            "agent_id": random.choice(agents).id,
            "features": {
                "amenities": random.sample(
                    AMENITIES.get(property_type, []), k=min(3, len(AMENITIES.get(property_type, [])))
                ),
                "parking_spaces": random.randint(1, 3),
                "year_built": random.randint(2018, 2024),
            },
            "furnishing_status": random.choice(["furnished", "unfurnished", "semi-furnished"]),
            "pet_friendly": random.choice([True, False]),
            "gym_available": random.choice([True, True, False]),
            "pool_available": random.choice([True, True, False]),
            "security_24_7": True,
            "rera_number": f"RERA{random.randint(10000, 99999)}",
            "developer_name": random.choice(
                ["Emaar", "Dubai Properties", "Nakheel", "Damac", "Meraas"]
            ),
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 180)),
        }

        prop = EnhancedProperty(**property_data)
        db.add(prop)
        properties.append(prop)

    db.commit()
    print(f"✓ Created {len(properties)} properties")
    return properties


def create_sample_leads(db, agents):
    """Create sample leads"""
    first_names = [
        "Ahmed",
        "Fatima",
        "John",
        "Sarah",
        "Mohammed",
        "Lisa",
        "Omar",
        "Emily",
        "Hassan",
        "Anna",
    ]
    last_names = [
        "Al Maktoum",
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Davis",
        "Wilson",
        "Moore",
        "Taylor",
    ]

    leads = []
    for i in range(20):
        first = random.choice(first_names)
        last = random.choice(last_names)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@email.com"
        phone = f"+971-{random.randint(50, 59)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

        budget_ranges = [
            (500000, 1000000),
            (1000000, 2000000),
            (2000000, 5000000),
            (5000000, 10000000),
        ]
        budget_min, budget_max = random.choice(budget_ranges)

        lead_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "status": random.choice(["new", "contacted", "qualified", "viewing"]),
            "source": random.choice(
                ["website", "referral", "social_media", "property_portal", "walk_in"]
            ),
            "budget_min": Decimal(budget_min),
            "budget_max": Decimal(budget_max),
            "preferred_areas": random.sample(DUBAI_LOCATIONS, k=random.randint(2, 4)),
            "property_type": random.choice(PROPERTY_TYPES),
            "nurture_status": random.choice(["new", "hot", "warm", "cold"]),
            "assigned_agent_id": random.choice(agents).id,
            "lead_score": random.randint(30, 95),
            "urgency_level": random.choice(["low", "normal", "high"]),
            "preferred_contact_method": random.choice(["email", "phone", "whatsapp"]),
            "notes": f"Interested in {random.choice(PROPERTY_TYPES)} properties in {random.choice(DUBAI_LOCATIONS)}.",
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 90)),
        }

        lead = EnhancedLead(**lead_data)
        db.add(lead)
        leads.append(lead)

    db.commit()
    print(f"✓ Created {len(leads)} leads")
    return leads


def create_sample_clients(db, agents, leads):
    """Create sample clients (converted leads)"""
    clients = []

    # Convert some leads to clients
    converted_leads = random.sample(leads, k=min(8, len(leads)))

    for lead in converted_leads:
        client_data = {
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "budget_min": lead.budget_min,
            "budget_max": lead.budget_max,
            "preferred_location": random.choice(lead.preferred_areas_list or DUBAI_LOCATIONS),
            "requirements": f"Looking for {lead.property_type} in preferred locations",
            "client_type": random.choice(["buyer", "investor"]),
            "lead_id": lead.id,
            "assigned_agent_id": lead.assigned_agent_id,
            "client_status": "active",
            "relationship_start_date": datetime.utcnow().date()
            - timedelta(days=random.randint(10, 60)),
            "client_tier": random.choice(["standard", "premium", "vip"]),
        }

        client = EnhancedClient(**client_data)
        db.add(client)
        clients.append(client)

    db.commit()
    print(f"✓ Created {len(clients)} clients")
    return clients


def main():
    """Main seeding function"""
    print("\n" + "=" * 60)
    print("🌱 AURA RealtorProAI - Database Seeding Script")
    print("=" * 60 + "\n")

    print(f"📊 Database URL: {DATABASE_URL}\n")

    # Get database session
    db = next(get_db())

    try:
        # Seed data
        print("👤 Creating sample users...")
        agents = create_sample_users(db)

        print("\n🏠 Creating sample properties...")
        properties = create_sample_properties(db, agents)

        print("\n📞 Creating sample leads...")
        leads = create_sample_leads(db, agents)

        print("\n🤝 Creating sample clients...")
        clients = create_sample_clients(db, agents, leads)

        print("\n" + "=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   • Users (Agents): {len(agents)}")
        print(f"   • Properties: {len(properties)}")
        print(f"   • Leads: {len(leads)}")
        print(f"   • Clients: {len(clients)}")
        print(f"\n💡 You can now test the application with realistic data!\n")
        print("🔐 Sample credentials:")
        print("   Email: sarah.johnson@realtorpro.ae")
        print("   Password: demo123\n")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
