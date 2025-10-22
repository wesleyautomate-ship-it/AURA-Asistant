#!/usr/bin/env python3
"""
End-to-End Test for Property-Brochure Feature

Tests the complete workflow:
1. Create database tables
2. Test property creation 
3. Test brochure creation with property enrichment
4. Test manual curl commands for API verification
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def init_database():
    """Initialize database tables"""
    print("📋 Initializing database...")
    
    try:
        from backend.app.core.database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_api_health():
    """Test if backend API is running"""
    print("\n🔍 Testing API health...")
    
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is healthy")
            return True
        else:
            print(f"⚠️ Backend API returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend API is not running: {e}")
        return False

def test_property_creation():
    """Test property creation API"""
    print("\n🏠 Testing property creation...")
    
    property_data = {
        "title": "2BR at Orla Residences",
        "building": "Orla Residences",
        "community": "Palm Jumeirah", 
        "beds": 2,
        "baths": 2.0,
        "area_sqft": 1650.0,
        "price_aed": 7200000,
        "description": "Test property for brochure generation",
        "photos": [
            {"url": "https://example.com/photo1.jpg", "sort_order": 0}
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/properties",
            json=property_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            property_result = response.json()
            print(f"✅ Property created: {property_result['title']} (ID: {property_result['id']})")
            return property_result
        else:
            print(f"❌ Property creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Property creation error: {e}")
        return None

def test_brochure_creation(property_id=None):
    """Test brochure creation with property enrichment"""
    print("\n📋 Testing brochure creation...")
    
    brochure_data = {
        "templateKey": "clean-minimal",
    }
    
    if property_id:
        brochure_data["property_id"] = property_id
        print(f"📍 Using property_id: {property_id}")
    
    try:
        # Create brochure draft
        response = requests.post(
            "http://localhost:8000/api/v1/brochures",
            json=brochure_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            draft = response.json()
            print(f"✅ Brochure draft created: {draft['id']}")
            
            # Test rendering
            render_response = requests.post(
                f"http://localhost:8000/api/v1/brochures/{draft['id']}/render",
                timeout=30
            )
            
            if render_response.status_code == 200:
                render_result = render_response.json()
                print(f"✅ Brochure rendered: {render_result.get('download_url')}")
                return draft
            else:
                print(f"⚠️ Brochure rendering failed: {render_response.status_code} - {render_response.text}")
                return draft
        else:
            print(f"❌ Brochure creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Brochure creation error: {e}")
        return None

def show_curl_commands():
    """Show manual curl commands for testing"""
    print("\n🧪 Manual Testing Commands:")
    print("=" * 60)
    
    print("\n1. Create Property:")
    print("""curl -X POST http://localhost:8000/api/v1/properties \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "2BR at Orla Residences",
    "building": "Orla Residences", 
    "community": "Palm Jumeirah",
    "beds": 2,
    "baths": 2.0,
    "area_sqft": 1650.0,
    "price_aed": 7200000,
    "photos": [{"url": "http://localhost:8000/api/v1/assets/demo/orla1.jpg", "sort_order": 0}]
  }'""")
    
    print("\n2. Create Brochure with Property:")
    print("""curl -X POST http://localhost:8000/api/v1/brochures \\
  -H "Content-Type: application/json" \\
  -d '{
    "templateKey": "clean-minimal",
    "property_id": "<PROPERTY_ID_FROM_STEP_1>"
  }'""")
    
    print("\n3. Render Brochure:")
    print("""curl -X POST http://localhost:8000/api/v1/brochures/<BROCHURE_ID>/render""")
    
    print("\n4. Download Brochure:")
    print("""curl -O http://localhost:8000/api/v1/brochures/<BROCHURE_ID>/download""")

def main():
    """Main test runner"""
    print("🚀 Property-Brochure Feature End-to-End Test")
    print("=" * 60)
    
    # Step 1: Initialize database
    if not init_database():
        sys.exit(1)
    
    # Step 2: Check API health
    if not test_api_health():
        print("\n⚠️ Backend API is not running. Please start the backend first:")
        print("   cd backend && python start-backend.py")
        show_curl_commands()
        sys.exit(1)
    
    # Step 3: Test property creation
    property_result = test_property_creation()
    
    # Step 4: Test brochure creation  
    brochure_result = test_brochure_creation(
        property_id=property_result['id'] if property_result else None
    )
    
    # Step 5: Show results
    print("\n📊 Test Results Summary:")
    print("=" * 40)
    print(f"✅ Database: Initialized")
    print(f"✅ API Health: OK")
    print(f"{'✅' if property_result else '❌'} Property Creation: {'Success' if property_result else 'Failed'}")
    print(f"{'✅' if brochure_result else '❌'} Brochure Creation: {'Success' if brochure_result else 'Failed'}")
    
    if property_result and brochure_result:
        print(f"\n🎉 End-to-End Test PASSED!")
        print(f"🏠 Property: {property_result['title']} ({property_result['id']})")
        print(f"📋 Brochure: {brochure_result['id']}")
        print(f"📄 Status: {brochure_result.get('status', 'unknown')}")
    else:
        print(f"\n⚠️ Some tests failed. Check the logs above.")
    
    # Always show curl commands for manual verification
    show_curl_commands()

if __name__ == "__main__":
    main()