#!/usr/bin/env python3
"""
Mock Property Listings Seeder
============================

Creates sample property listings for testing the brochure generation feature.
Inserts 5 sample listings linked to the development user, including one with
a blank description to test AI autofill functionality.
"""

import sys
import os
import json
from datetime import datetime, date
from decimal import Decimal

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.models import User
from app.domain.listings.enhanced_real_estate_models import EnhancedProperty, Base

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./propertypro_dev.db')

def create_db_session():
    """Create database session"""
    engine = create_engine(DATABASE_URL)
    # Don't create all tables - just use existing database
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def get_or_create_dev_user(db):
    """Get or create the development user"""
    user = db.query(User).filter(User.email == 'admin@aura.ai').first()
    if not user:
        user = User(
            email='admin@aura.ai',
            password_hash='dev-hash',  # Not used in dev mode
            first_name='AURA',
            last_name='Developer',
            role='agent',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created development user: {user.full_name} (ID: {user.id})")
    else:
        print(f"✅ Found existing development user: {user.full_name} (ID: {user.id})")
    return user

def create_mock_listings(db, agent_user):
    """Create mock property listings"""
    
    # Sample listing data
    mock_listings = [
        {
            'title': 'Marina Heights Penthouse',
            'description': 'Stunning 3-bedroom penthouse with breathtaking views of Dubai Marina. Features include a private terrace, premium finishes, and access to world-class amenities. Perfect for luxury living in the heart of Dubai.',
            'property_type': 'Penthouse',
            'price_aed': Decimal('4200000'),
            'location': 'Dubai Marina, UAE',
            'area_sqft': Decimal('2500'),
            'bedrooms': 3,
            'bathrooms': 4,
            'listing_status': 'active',
            'features': {
                'private_terrace': True,
                'marina_view': True,
                'premium_finishes': True,
                'built_in_wardrobes': True,
                'smart_home_system': True,
                'covered_parking': 2
            },
            'property_images': [
                'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800',
                'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'
            ],
            'neighborhood_data': {
                'district': 'Dubai Marina',
                'proximity_to_metro': '5 minutes walk',
                'nearby_amenities': ['Marina Mall', 'Beach', 'Restaurants', 'Marina Walk'],
                'schools_nearby': ['GEMS Wellington International School', 'Dubai International Academy']
            },
            'furnishing_status': 'Unfurnished',
            'view_type': 'Marina and Sea View',
            'parking_spaces': 2,
            'pool_available': True,
            'gym_available': True,
            'security_24_7': True
        },
        {
            'title': 'Downtown Dubai Luxury Apartment',
            'description': '',  # Empty description to test AI autofill
            'property_type': 'Apartment',
            'price_aed': Decimal('2800000'),
            'location': 'Downtown Dubai, UAE',
            'area_sqft': Decimal('1800'),
            'bedrooms': 2,
            'bathrooms': 3,
            'listing_status': 'active',
            'features': {
                'burj_khalifa_view': True,
                'high_floor': True,
                'premium_finishes': True,
                'built_in_kitchen': True,
                'balcony': True,
                'covered_parking': 1
            },
            'property_images': [
                'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800'
            ],
            'neighborhood_data': {
                'district': 'Downtown Dubai',
                'proximity_to_metro': '2 minutes walk',
                'nearby_amenities': ['Dubai Mall', 'Burj Khalifa', 'Dubai Opera', 'DIFC'],
                'schools_nearby': ['Repton School Dubai', 'Dubai International Academy']
            },
            'furnishing_status': 'Semi-furnished',
            'view_type': 'Burj Khalifa and City View',
            'parking_spaces': 1,
            'pool_available': True,
            'gym_available': True,
            'security_24_7': True
        },
        {
            'title': 'Jumeirah Beach Residence Villa',
            'description': 'Exquisite 4-bedroom villa located in the prestigious Jumeirah Beach Residence area. This magnificent property offers direct beach access, private garden, and panoramic ocean views. Ideal for families seeking beachfront luxury.',
            'property_type': 'Villa',
            'price_aed': Decimal('6500000'),
            'location': 'Jumeirah Beach Residence, Dubai',
            'area_sqft': Decimal('3200'),
            'bedrooms': 4,
            'bathrooms': 5,
            'listing_status': 'active',
            'features': {
                'beach_access': True,
                'private_garden': True,
                'ocean_view': True,
                'maid_room': True,
                'private_pool': True,
                'covered_parking': 3
            },
            'property_images': [
                'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800',
                'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800'
            ],
            'neighborhood_data': {
                'district': 'JBR',
                'proximity_to_metro': '10 minutes drive',
                'nearby_amenities': ['The Beach', 'Marina Walk', 'JBR Beach', 'The Walk JBR'],
                'schools_nearby': ['GEMS Wellington International School', 'American School of Dubai']
            },
            'furnishing_status': 'Furnished',
            'view_type': 'Ocean and Beach View',
            'parking_spaces': 3,
            'pool_available': True,
            'gym_available': True,
            'security_24_7': True,
            'pet_friendly': True
        },
        {
            'title': 'Business Bay Executive Studio',
            'description': 'Modern executive studio apartment perfect for young professionals. Located in the heart of Business Bay with easy access to DIFC and Downtown. Features contemporary design and premium amenities.',
            'property_type': 'Studio',
            'price_aed': Decimal('1200000'),
            'location': 'Business Bay, Dubai',
            'area_sqft': Decimal('650'),
            'bedrooms': 0,  # Studio
            'bathrooms': 1,
            'listing_status': 'active',
            'features': {
                'canal_view': True,
                'modern_design': True,
                'built_in_wardrobes': True,
                'kitchenette': True,
                'balcony': True,
                'covered_parking': 1
            },
            'property_images': [
                'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'
            ],
            'neighborhood_data': {
                'district': 'Business Bay',
                'proximity_to_metro': '3 minutes walk',
                'nearby_amenities': ['DIFC', 'Dubai Mall', 'Canal Walk', 'Business Bay Metro'],
                'schools_nearby': ['American University of Dubai', 'Hult International Business School']
            },
            'furnishing_status': 'Fully Furnished',
            'view_type': 'Canal View',
            'parking_spaces': 1,
            'pool_available': True,
            'gym_available': True,
            'security_24_7': True
        },
        {
            'title': 'Palm Jumeirah Beachfront Townhouse',
            'description': 'Rare opportunity to own a beachfront townhouse on the iconic Palm Jumeirah. This exclusive 3-bedroom property offers private beach access, stunning Atlantis views, and luxury living at its finest.',
            'property_type': 'Townhouse',
            'price_aed': Decimal('8900000'),
            'location': 'Palm Jumeirah, Dubai',
            'area_sqft': Decimal('2800'),
            'bedrooms': 3,
            'bathrooms': 4,
            'listing_status': 'active',
            'features': {
                'beachfront': True,
                'atlantis_view': True,
                'private_beach_access': True,
                'terrace': True,
                'premium_location': True,
                'covered_parking': 2
            },
            'property_images': [
                'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800',
                'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800'
            ],
            'neighborhood_data': {
                'district': 'Palm Jumeirah',
                'proximity_to_metro': '15 minutes drive',
                'nearby_amenities': ['Atlantis Hotel', 'Palm Jumeirah Boardwalk', 'Nakheel Mall', 'The Pointe'],
                'schools_nearby': ['Dubai International Academy', 'GEMS Wellington International School']
            },
            'furnishing_status': 'Unfurnished',
            'view_type': 'Beach and Atlantis View',
            'parking_spaces': 2,
            'pool_available': True,
            'gym_available': True,
            'security_24_7': True,
            'pet_friendly': True
        }
    ]
    
    created_listings = []
    
    for listing_data in mock_listings:
        # Check if listing already exists
        existing = db.query(EnhancedProperty).filter(
            EnhancedProperty.title == listing_data['title']
        ).first()
        
        if existing:
            print(f"⚠️ Listing already exists: {listing_data['title']}")
            created_listings.append(existing)
            continue
            
        # Create new property listing
        new_property = EnhancedProperty(
            title=listing_data['title'],
            description=listing_data['description'],
            property_type=listing_data['property_type'],
            price_aed=listing_data['price_aed'],
            location=listing_data['location'],
            area_sqft=listing_data['area_sqft'],
            bedrooms=listing_data['bedrooms'],
            bathrooms=listing_data['bathrooms'],
            listing_status=listing_data['listing_status'],
            features=listing_data['features'],
            property_images=listing_data['property_images'],
            neighborhood_data=listing_data['neighborhood_data'],
            agent_id=agent_user.id,
            created_by=agent_user.id,
            furnishing_status=listing_data['furnishing_status'],
            view_type=listing_data['view_type'],
            parking_spaces=listing_data['parking_spaces'],
            pool_available=listing_data['pool_available'],
            gym_available=listing_data['gym_available'],
            security_24_7=listing_data['security_24_7'],
            pet_friendly=listing_data.get('pet_friendly', False),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_property)
        created_listings.append(new_property)
        print(f"✅ Created listing: {listing_data['title']}")
    
    try:
        db.commit()
        print(f"✅ Successfully saved {len(created_listings)} property listings")
        
        # Display created listings summary
        print("\n" + "="*50)
        print("📋 CREATED PROPERTY LISTINGS SUMMARY")
        print("="*50)
        
        for prop in created_listings:
            empty_desc = "⚠️ EMPTY DESCRIPTION" if not prop.description else "✅ Has Description"
            print(f"ID: {prop.id} | {prop.title}")
            print(f"   📍 {prop.location}")
            print(f"   💰 AED {prop.price_aed:,.0f}")
            print(f"   🛏️ {prop.bedrooms} bed | 🛁 {prop.bathrooms} bath | 📐 {prop.area_sqft} sqft")
            print(f"   📝 {empty_desc}")
            print(f"   👤 Agent ID: {prop.agent_id}")
            print()
            
        return created_listings
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving listings: {e}")
        return []

def main():
    """Main seeder function"""
    print("🚀 AURA Property Listings Seeder")
    print("=" * 40)
    
    db = None
    try:
        # Create database session
        db = create_db_session()
        print("✅ Database connection established")
        
        # Get or create development user
        dev_user = get_or_create_dev_user(db)
        
        # Create mock property listings
        listings = create_mock_listings(db, dev_user)
        
        if listings:
            print(f"\n🎉 SUCCESS: Created {len(listings)} property listings!")
            print("\n📋 Next Steps:")
            print("1. Test brochure generation with: 'Create a brochure for Marina Heights Penthouse'")
            print("2. Test AI description autofill with: 'Generate brochure for Downtown Dubai Luxury Apartment'")
            print("3. Check database to verify listings are saved")
            print("\n💡 Tip: The Downtown Dubai apartment has an empty description to test AI autofill!")
        else:
            print("⚠️ No new listings were created (they may already exist)")
            
    except Exception as e:
        print(f"❌ Seeder failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if db:
            db.close()
    
    return 0

if __name__ == "__main__":
    exit(main())