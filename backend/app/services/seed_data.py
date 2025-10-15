"""
Sample Data Seeding Service
===========================

This service populates the database with sample data for development and testing.
"""

import logging
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal

# Import models
from app.core.models import User, UserSession, Role, Permission
from app.core.utils import hash_password
from app.domain.listings.enhanced_real_estate_models import (
    EnhancedProperty,
    EnhancedClient,
    EnhancedLead,
    Transaction,
)

logger = logging.getLogger(__name__)


def seed_sample_users(db: Session):
    """Seed sample users for development"""
    logger.info("Seeding sample users...")

    # Check if users already exist
    if db.query(User).count() > 0:
        logger.info("Users already exist, skipping user seeding")
        return

    users_data = [
        {
            "email": "admin@propertypro.ai",
            "password": "Admin123!",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
        },
        {
            "email": "agent@propertypro.ai",
            "password": "Agent123!",
            "first_name": "John",
            "last_name": "Agent",
            "role": "agent",
        },
        {
            "email": "manager@propertypro.ai",
            "password": "Manager123!",
            "first_name": "Sarah",
            "last_name": "Manager",
            "role": "employee",
        },
    ]

    for user_data in users_data:
        user = User(
            email=user_data["email"],
            password_hash=hash_password(user_data["password"]),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            is_active=True,
            email_verified=True,
            created_at=datetime.utcnow(),
        )
        db.add(user)

    db.commit()
    logger.info(f"Created {len(users_data)} sample users")


def seed_sample_properties(db: Session):
    """Seed sample properties for development"""
    logger.info("Seeding sample properties...")

    # Check if properties already exist
    if db.query(EnhancedProperty).count() > 0:
        logger.info("Properties already exist, skipping property seeding")
        return

    properties_data = [
        {
            "title": "Luxury Downtown Apartment",
            "description": "Modern 2BR/2BA apartment in the heart of downtown with stunning city views.",
            "price_aed": Decimal("850000"),
            "location": "Downtown Dubai",
            "property_type": "Apartment",
            "bedrooms": 2,
            "bathrooms": 2,
            "area_sqft": Decimal("1200"),
            "listing_status": "available",
            "features": {
                "parking": 1,
                "balcony": True,
                "city_view": True,
                "furnished": True,
            },
        },
        {
            "title": "Spacious Family Villa",
            "description": "Beautiful 4BR/3BA villa with private garden and pool in a quiet neighborhood.",
            "price_aed": Decimal("2400000"),
            "location": "Arabian Ranches",
            "property_type": "Villa",
            "bedrooms": 4,
            "bathrooms": 3,
            "area_sqft": Decimal("3200"),
            "listing_status": "available",
            "features": {"parking": 2, "garden": True, "pool": True, "maid_room": True},
        },
        {
            "title": "Beachfront Studio",
            "description": "Cozy studio apartment with direct beach access and sea views.",
            "price_aed": Decimal("650000"),
            "location": "Dubai Marina",
            "property_type": "Studio",
            "bedrooms": 0,
            "bathrooms": 1,
            "area_sqft": Decimal("600"),
            "listing_status": "available",
            "features": {"beach_access": True, "sea_view": True, "balcony": True},
        },
        {
            "title": "Modern Office Space",
            "description": "Professional office space in prime business district.",
            "price_aed": Decimal("180000"),
            "location": "Business Bay",
            "property_type": "Commercial",
            "bedrooms": 0,
            "bathrooms": 2,
            "area_sqft": Decimal("1500"),
            "listing_status": "available",
            "features": {"parking": 3, "conference_room": True, "reception": True},
        },
        {
            "title": "Cozy 1BR Apartment",
            "description": "Perfect starter home with modern amenities and great location.",
            "price_aed": Decimal("520000"),
            "location": "Jumeirah Village Circle",
            "property_type": "Apartment",
            "bedrooms": 1,
            "bathrooms": 1,
            "area_sqft": Decimal("750"),
            "listing_status": "pending",
            "features": {"parking": 1, "gym": True, "pool": True},
        },
    ]

    for prop_data in properties_data:
        property_obj = EnhancedProperty(
            title=prop_data["title"],
            description=prop_data["description"],
            price_aed=prop_data["price_aed"],
            price=prop_data["price_aed"],  # Legacy field
            location=prop_data["location"],
            property_type=prop_data["property_type"],
            bedrooms=prop_data["bedrooms"],
            bathrooms=prop_data["bathrooms"],
            area_sqft=prop_data["area_sqft"],
            listing_status=prop_data["listing_status"],
            features=prop_data["features"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(property_obj)

    db.commit()
    logger.info(f"Created {len(properties_data)} sample properties")


def seed_sample_clients(db: Session):
    """Seed sample clients for development"""
    logger.info("Seeding sample clients...")

    # Check if clients already exist
    if db.query(EnhancedClient).count() > 0:
        logger.info("Clients already exist, skipping client seeding")
        return

    clients_data = [
        {
            "name": "Ahmed Al-Rashid",
            "email": "ahmed.rashid@email.com",
            "phone": "+971 50 123 4567",
            "client_type": "buyer",
            "budget_min": Decimal("500000"),
            "budget_max": Decimal("1200000"),
            "preferred_location": "Dubai Marina, Downtown Dubai",
            "requirements": "2-3 bedroom apartment with sea or city view, parking required",
            "client_status": "active",
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@email.com",
            "phone": "+971 55 987 6543",
            "client_type": "investor",
            "budget_min": Decimal("800000"),
            "budget_max": Decimal("2000000"),
            "preferred_location": "Business Bay, DIFC",
            "requirements": "Commercial properties or high-ROI residential units",
            "client_status": "active",
        },
        {
            "name": "Mohammed Hassan",
            "email": "mohammed.hassan@email.com",
            "phone": "+971 50 555 1234",
            "client_type": "seller",
            "budget_min": Decimal("0"),
            "budget_max": Decimal("0"),
            "preferred_location": "Arabian Ranches",
            "requirements": "Looking to sell 4BR villa, need market analysis",
            "client_status": "active",
        },
        {
            "name": "Emma Wilson",
            "email": "emma.wilson@email.com",
            "phone": "+971 56 789 0123",
            "client_type": "buyer",
            "budget_min": Decimal("300000"),
            "budget_max": Decimal("700000"),
            "preferred_location": "JVC, Sports City",
            "requirements": "First-time buyer, studio or 1BR apartment",
            "client_status": "active",
        },
        {
            "name": "David Chen",
            "email": "david.chen@email.com",
            "phone": "+971 52 456 7890",
            "client_type": "buyer",
            "budget_min": Decimal("1500000"),
            "budget_max": Decimal("3500000"),
            "preferred_location": "Emirates Hills, Palm Jumeirah",
            "requirements": "Luxury villa with private pool and garden",
            "client_status": "active",
        },
    ]

    for client_data in clients_data:
        client = EnhancedClient(
            name=client_data["name"],
            email=client_data["email"],
            phone=client_data["phone"],
            client_type=client_data["client_type"],
            budget_min=client_data["budget_min"],
            budget_max=client_data["budget_max"],
            preferred_location=client_data["preferred_location"],
            requirements=client_data["requirements"],
            client_status=client_data["client_status"],
            relationship_start_date=date.today(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(client)

    db.commit()
    logger.info(f"Created {len(clients_data)} sample clients")


def seed_all_data(db: Session):
    """Seed all sample data for development"""
    logger.info("Starting database seeding for development...")

    try:
        seed_sample_users(db)
        seed_sample_properties(db)
        seed_sample_clients(db)

        logger.info("Database seeding completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        db.rollback()
        return False
