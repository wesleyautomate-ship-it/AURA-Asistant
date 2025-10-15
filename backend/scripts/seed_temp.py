#!/usr/bin/env python3
"""Direct SQLite seeding"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'propertypro_dev.db')

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

print("\nSeeding users...")
# Create sample users
users = [
    ("sarah.johnson@realtorpro.ae", "Sarah", "Johnson", "agent"),
    ("michael.chen@realtorpro.ae", "Michael", "Chen", "agent"),
    ("fatima.ali@realtorpro.ae", "Fatima", "Ali", "agent"),
]

password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/6UzqU/rJ3Uy"  # demo123

for email, first_name, last_name, role in users:
    try:
        cur.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, email_verified)
            VALUES (?, ?, ?, ?, ?, 1, 1)
        """, (email, password_hash, first_name, last_name, role))
        print(f"✓ Created user: {email}")
    except sqlite3.IntegrityError:
        print(f"✓ User {email} already exists")

conn.commit()

# Get agent IDs
cur.execute("SELECT id FROM users WHERE role = 'agent'")
agent_ids = [row[0] for row in cur.fetchall()]
print(f"Found {len(agent_ids)} agents")

print("\nSeeding properties...")
# Sample data
locations = ["Downtown Dubai", "Dubai Marina", "Palm Jumeirah", "Business Bay", "Dubai Hills"]
types = ["apartment", "villa", "townhouse", "penthouse", "studio"]

for i in range(30):
    title = f"{random.choice(types).capitalize()} in {random.choice(locations)}"
    price = random.randint(500000, 5000000)
    bedrooms = random.randint(1, 5)
    
    cur.execute("""
        INSERT INTO properties (title, description, property_type, price, price_aed, 
                             location, area_sqft, bedrooms, bathrooms, listing_status,
                             agent_id, furnishing_status, gym_available, pool_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, f"Sample property {i+1}", random.choice(types), price, price,
        random.choice(locations), random.randint(800, 3000), bedrooms, bedrooms,
        random.choice(["live", "live", "sold"]), random.choice(agent_ids),
        random.choice(["furnished", "unfurnished"]), random.choice([0, 1]), random.choice([0, 1])
    ))

conn.commit()
print(f"Created {i+1} properties")

print("\nSeeding leads...")
first_names = ["Ahmed", "Fatima", "John", "Sarah", "Mohammed", "Lisa"]
last_names = ["Al Maktoum", "Smith", "Johnson", "Williams", "Brown"]

for i in range(20):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    email = f"lead{i}@example.com"
    
    cur.execute("""
        INSERT INTO leads (name, email, phone, status, source, budget_min, budget_max,
                       property_type, nurture_status, assigned_agent_id, lead_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, email, f"+971-5{random.randint(10000000,99999999)}", 
        random.choice(["new", "contacted", "qualified"]),
        random.choice(["website", "referral", "social_media"]),
        random.randint(500000, 1000000), random.randint(1000000, 2000000),
        random.choice(types), random.choice(["new", "hot", "warm", "cold"]),
        random.choice(agent_ids), random.randint(30, 95)
    ))

conn.commit()
print(f"Created {i+1} leads")

print("\nAll done! Sample credentials:")
print("Email: sarah.johnson@realtorpro.ae")
print("Password: demo123\n")

cur.close()
conn.close()