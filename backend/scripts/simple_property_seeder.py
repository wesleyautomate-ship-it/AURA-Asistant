#!/usr/bin/env python3
"""
Simple Property Listings Seeder
===============================

Creates sample property listings using direct SQL to avoid complex model dependencies.
"""

import sqlite3
import json
import os
from datetime import datetime
from decimal import Decimal

# Database path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'propertypro_dev.db')

def create_properties():
    """Create sample property listings"""
    
    # Sample properties data
    properties = [
        {
            'title': 'Marina Heights Penthouse',
            'description': 'Stunning 3-bedroom penthouse with breathtaking views of Dubai Marina. Features include a private terrace, premium finishes, and access to world-class amenities. Perfect for luxury living in the heart of Dubai.',
            'property_type': 'Penthouse',
            'price_aed': '4200000.00',
            'location': 'Dubai Marina, UAE',
            'area_sqft': '2500.00',
            'bedrooms': 3,
            'bathrooms': 4,
            'listing_status': 'active',
            'features': json.dumps({
                'private_terrace': True,
                'marina_view': True,
                'premium_finishes': True,
                'built_in_wardrobes': True,
                'smart_home_system': True,
                'covered_parking': 2
            }),
            'property_images': json.dumps([
                'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800',
                'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'
            ]),
            'neighborhood_data': json.dumps({
                'district': 'Dubai Marina',
                'proximity_to_metro': '5 minutes walk',
                'nearby_amenities': ['Marina Mall', 'Beach', 'Restaurants', 'Marina Walk'],
                'schools_nearby': ['GEMS Wellington International School', 'Dubai International Academy']
            }),
            'furnishing_status': 'Unfurnished',
            'view_type': 'Marina and Sea View',
            'parking_spaces': 2,
            'pool_available': 1,
            'gym_available': 1,
            'security_24_7': 1
        },
        {
            'title': 'Downtown Dubai Luxury Apartment',
            'description': '',  # Empty for AI testing
            'property_type': 'Apartment',
            'price_aed': '2800000.00',
            'location': 'Downtown Dubai, UAE',
            'area_sqft': '1800.00',
            'bedrooms': 2,
            'bathrooms': 3,
            'listing_status': 'active',
            'features': json.dumps({
                'burj_khalifa_view': True,
                'high_floor': True,
                'premium_finishes': True,
                'built_in_kitchen': True,
                'balcony': True,
                'covered_parking': 1
            }),
            'property_images': json.dumps([
                'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800'
            ]),
            'neighborhood_data': json.dumps({
                'district': 'Downtown Dubai',
                'proximity_to_metro': '2 minutes walk',
                'nearby_amenities': ['Dubai Mall', 'Burj Khalifa', 'Dubai Opera', 'DIFC'],
                'schools_nearby': ['Repton School Dubai', 'Dubai International Academy']
            }),
            'furnishing_status': 'Semi-furnished',
            'view_type': 'Burj Khalifa and City View',
            'parking_spaces': 1,
            'pool_available': 1,
            'gym_available': 1,
            'security_24_7': 1
        },
        {
            'title': 'Jumeirah Beach Residence Villa',
            'description': 'Exquisite 4-bedroom villa located in the prestigious Jumeirah Beach Residence area. This magnificent property offers direct beach access, private garden, and panoramic ocean views. Ideal for families seeking beachfront luxury.',
            'property_type': 'Villa',
            'price_aed': '6500000.00',
            'location': 'Jumeirah Beach Residence, Dubai',
            'area_sqft': '3200.00',
            'bedrooms': 4,
            'bathrooms': 5,
            'listing_status': 'active',
            'features': json.dumps({
                'beach_access': True,
                'private_garden': True,
                'ocean_view': True,
                'maid_room': True,
                'private_pool': True,
                'covered_parking': 3
            }),
            'property_images': json.dumps([
                'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800',
                'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800'
            ]),
            'neighborhood_data': json.dumps({
                'district': 'JBR',
                'proximity_to_metro': '10 minutes drive',
                'nearby_amenities': ['The Beach', 'Marina Walk', 'JBR Beach', 'The Walk JBR'],
                'schools_nearby': ['GEMS Wellington International School', 'American School of Dubai']
            }),
            'furnishing_status': 'Furnished',
            'view_type': 'Ocean and Beach View',
            'parking_spaces': 3,
            'pool_available': 1,
            'gym_available': 1,
            'security_24_7': 1,
            'pet_friendly': 1
        },
        {
            'title': 'Business Bay Executive Studio',
            'description': 'Modern executive studio apartment perfect for young professionals. Located in the heart of Business Bay with easy access to DIFC and Downtown. Features contemporary design and premium amenities.',
            'property_type': 'Studio',
            'price_aed': '1200000.00',
            'location': 'Business Bay, Dubai',
            'area_sqft': '650.00',
            'bedrooms': 0,
            'bathrooms': 1,
            'listing_status': 'active',
            'features': json.dumps({
                'canal_view': True,
                'modern_design': True,
                'built_in_wardrobes': True,
                'kitchenette': True,
                'balcony': True,
                'covered_parking': 1
            }),
            'property_images': json.dumps([
                'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'
            ]),
            'neighborhood_data': json.dumps({
                'district': 'Business Bay',
                'proximity_to_metro': '3 minutes walk',
                'nearby_amenities': ['DIFC', 'Dubai Mall', 'Canal Walk', 'Business Bay Metro'],
                'schools_nearby': ['American University of Dubai', 'Hult International Business School']
            }),
            'furnishing_status': 'Fully Furnished',
            'view_type': 'Canal View',
            'parking_spaces': 1,
            'pool_available': 1,
            'gym_available': 1,
            'security_24_7': 1
        },
        {
            'title': 'Palm Jumeirah Beachfront Townhouse',
            'description': 'Rare opportunity to own a beachfront townhouse on the iconic Palm Jumeirah. This exclusive 3-bedroom property offers private beach access, stunning Atlantis views, and luxury living at its finest.',
            'property_type': 'Townhouse',
            'price_aed': '8900000.00',
            'location': 'Palm Jumeirah, Dubai',
            'area_sqft': '2800.00',
            'bedrooms': 3,
            'bathrooms': 4,
            'listing_status': 'active',
            'features': json.dumps({
                'beachfront': True,
                'atlantis_view': True,
                'private_beach_access': True,
                'terrace': True,
                'premium_location': True,
                'covered_parking': 2
            }),
            'property_images': json.dumps([
                'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800',
                'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800'
            ]),
            'neighborhood_data': json.dumps({
                'district': 'Palm Jumeirah',
                'proximity_to_metro': '15 minutes drive',
                'nearby_amenities': ['Atlantis Hotel', 'Palm Jumeirah Boardwalk', 'Nakheel Mall', 'The Pointe'],
                'schools_nearby': ['Dubai International Academy', 'GEMS Wellington International School']
            }),
            'furnishing_status': 'Unfurnished',
            'view_type': 'Beach and Atlantis View',
            'parking_spaces': 2,
            'pool_available': 1,
            'gym_available': 1,
            'security_24_7': 1,
            'pet_friendly': 1
        }
    ]
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get or create agent user (assume ID = 1 for simplicity)
    agent_id = 1
    created_count = 0
    
    for prop in properties:
        try:
            # Check if property already exists
            cursor.execute("SELECT id FROM properties WHERE title = ?", (prop['title'],))
            if cursor.fetchone():
                print(f"⚠️ Property already exists: {prop['title']}")
                continue
            
            # Insert property
            cursor.execute("""
                INSERT INTO properties (
                    title, description, property_type, price_aed, location, area_sqft,
                    bedrooms, bathrooms, listing_status, features, property_images, 
                    neighborhood_data, agent_id, created_by, furnishing_status, view_type,
                    parking_spaces, pool_available, gym_available, security_24_7, 
                    pet_friendly, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prop['title'], prop['description'], prop['property_type'], prop['price_aed'],
                prop['location'], prop['area_sqft'], prop['bedrooms'], prop['bathrooms'],
                prop['listing_status'], prop['features'], prop['property_images'],
                prop['neighborhood_data'], agent_id, agent_id, prop['furnishing_status'],
                prop['view_type'], prop['parking_spaces'], prop['pool_available'],
                prop['gym_available'], prop['security_24_7'], prop.get('pet_friendly', 0),
                datetime.utcnow().isoformat(), datetime.utcnow().isoformat()
            ))
            
            created_count += 1
            print(f"✅ Created property: {prop['title']}")
            
        except Exception as e:
            print(f"❌ Error creating {prop['title']}: {e}")
    
    conn.commit()
    conn.close()
    
    return created_count

def main():
    """Main seeder function"""
    print("🚀 Simple Property Listings Seeder")
    print("=" * 40)
    
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database not found at: {DATABASE_PATH}")
        print("Please ensure the backend has been started at least once to create the database.")
        return 1
    
    try:
        created_count = create_properties()
        
        if created_count > 0:
            print(f"\n🎉 SUCCESS: Created {created_count} property listings!")
            print("\n📋 Next Steps:")
            print("1. Test: 'Create a brochure for Marina Heights Penthouse'")
            print("2. Test AI autofill: 'Generate brochure for Downtown Dubai Luxury Apartment'")
            print("\n💡 The Downtown apartment has no description to test AI generation!")
        else:
            print("⚠️ No new properties were created (they may already exist)")
            
    except Exception as e:
        print(f"❌ Seeder failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())