#!/usr/bin/env python3
"""
Property Brochure Generation Test
================================

Test script to validate the property brochure generation functionality.
Tests both mock and real mode content generation for Marina Heights Penthouse.
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv('.env.development')

from app.core.ai_content_generator import (
    AIContentGenerator, 
    extract_property_query,
    serialize_property_for_brochure
)
from app.schemas.intelligence import ContentType
from app.domain.ai.task_orchestrator import AITaskOrchestrator
from app.domain.listings.enhanced_real_estate_models import EnhancedProperty
from app.core.database import get_db

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./propertypro_dev.db')

def create_db_session():
    """Create database session"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

async def test_extract_property_query():
    """Test property query extraction from user text"""
    print("\n🧪 Testing property query extraction:")
    
    test_cases = [
        "Create a brochure for Marina Heights Penthouse",
        "Generate brochure for Downtown Dubai Luxury Apartment",
        "Make a property brochure for Palm Jumeirah Villa",
        "Create brochure",
        "Marina Heights Penthouse brochure please"
    ]
    
    for test_input in test_cases:
        extracted = extract_property_query(test_input)
        print(f"  Input: '{test_input}' → Extract: '{extracted}'")
        
        # Test that Marina Heights is correctly extracted
        if "Marina Heights" in test_input:
            assert "Marina Heights" in extracted, f"Failed to extract Marina Heights from: {test_input}"
    
    print("✅ Property query extraction tests passed")

async def test_property_serialization():
    """Test property serialization for AI"""
    print("\n🧪 Testing property serialization:")
    
    db = create_db_session()
    try:
        # Find Marina Heights Penthouse
        property_obj = db.query(EnhancedProperty).filter(
            EnhancedProperty.title.ilike("%Marina Heights%")
        ).first()
        
        if not property_obj:
            print("❌ Marina Heights Penthouse not found in database")
            return False
            
        print(f"  Found property: {property_obj.title} (ID: {property_obj.id})")
        
        # Serialize property
        serialized = serialize_property_for_brochure(property_obj)
        
        print(f"  Serialized property:")
        print(f"    - Title: {serialized['title']}")
        print(f"    - Price: AED {serialized['specs']['price_aed']:,.0f}")
        print(f"    - Bedrooms: {serialized['specs']['bedrooms']}")
        print(f"    - Bathrooms: {serialized['specs']['bathrooms']}")
        print(f"    - Area: {serialized['specs']['area_sqft']} sqft")
        print(f"    - Agent: {serialized['contact']['agent_name']}")
        
        # Validate required fields
        assert serialized['id'] == property_obj.id
        assert serialized['title'] == property_obj.title
        assert 'specs' in serialized
        assert 'contact' in serialized
        
        print("✅ Property serialization tests passed")
        return True
        
    finally:
        db.close()

async def test_content_type_detection():
    """Test content type detection for brochures"""
    print("\n🧪 Testing content type detection:")
    
    generator = AIContentGenerator()
    
    test_cases = [
        ("Create a brochure for my property", ContentType.PROPERTY_BROCHURE),
        ("Generate a property brochure", ContentType.PROPERTY_BROCHURE),
        ("Make a flyer for Marina Heights", ContentType.PROPERTY_BROCHURE),
        ("Create a CMA report", ContentType.CMA_REPORT),
        ("Social media post needed", ContentType.SOCIAL_POST),
        ("Generate general content", ContentType.GENERAL)
    ]
    
    for test_input, expected_type in test_cases:
        detected = generator._detect_content_type(test_input)
        print(f"  Input: '{test_input}' → Detected: {detected.value}")
        assert detected == expected_type, f"Expected {expected_type}, got {detected}"
    
    print("✅ Content type detection tests passed")

async def test_mock_brochure_generation():
    """Test mock brochure content generation"""
    print("\n🧪 Testing mock brochure generation:")
    
    # Force mock mode
    generator = AIContentGenerator()
    generator.mock_mode = True
    
    db = create_db_session()
    try:
        # Find Marina Heights Penthouse
        property_obj = db.query(EnhancedProperty).filter(
            EnhancedProperty.title.ilike("%Marina Heights%")
        ).first()
        
        if not property_obj:
            print("❌ Marina Heights Penthouse not found in database")
            return False
        
        # Serialize property for context
        property_payload = serialize_property_for_brochure(property_obj)
        
        # Generate brochure content
        content = await generator.generate_content(
            user_input="Create a brochure for Marina Heights Penthouse",
            content_type=ContentType.PROPERTY_BROCHURE,
            context={'property': property_payload}
        )
        
        print(f"  Generated content:")
        print(f"    - Content ID: {content.content_id}")
        print(f"    - Title: {content.title}")
        print(f"    - Content Type: {content.content_type.value}")
        print(f"    - Mock Origin: {content.metadata.mock_origin}")
        print(f"    - Quality Score: {content.quality_scores.overall_score}")
        
        # Validate brochure structure
        structured = content.generated_content.structured
        print(f"    - Brochure Type: {structured.get('type', 'N/A')}")
        print(f"    - Property Title: {structured.get('title', 'N/A')}")
        print(f"    - Price: {structured.get('specs', {}).get('price_aed', 'N/A')}")
        
        # Validate required brochure fields
        assert content.content_type == ContentType.PROPERTY_BROCHURE
        assert structured.get('type') == 'property_brochure'
        assert 'title' in structured
        assert 'specs' in structured
        assert 'contact' in structured
        
        print("✅ Mock brochure generation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Mock brochure generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

async def test_task_orchestrator_integration():
    """Test task orchestrator with brochure request"""
    print("\n🧪 Testing task orchestrator integration:")
    
    def db_factory():
        return create_db_session()
    
    orchestrator = AITaskOrchestrator(db_factory)
    
    try:
        # Submit brochure generation task
        task_id = await orchestrator.submit_intelligence_task(
            user_input="Create a brochure for Marina Heights Penthouse",
            content_type=None,  # Let it auto-detect
            user_id=1,
            context={'user_id': 1}
        )
        
        print(f"  Submitted task: {task_id}")
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Check task status
        status = await orchestrator.get_task_status(task_id)
        print(f"  Task status: {status.status.value}")
        print(f"  Progress: {status.progress}%")
        
        if status.error_message:
            print(f"  Error: {status.error_message}")
        
        if status.output_data:
            print(f"  Output: {status.output_data}")
            
        print("✅ Task orchestrator integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Task orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all brochure generation tests"""
    print("🚀 Property Brochure Generation Tests")
    print("=" * 50)
    
    results = []
    
    # Test 1: Property query extraction
    try:
        await test_extract_property_query()
        results.append(("Property Query Extraction", True))
    except Exception as e:
        print(f"❌ Property query extraction failed: {e}")
        results.append(("Property Query Extraction", False))
    
    # Test 2: Property serialization
    try:
        success = await test_property_serialization()
        results.append(("Property Serialization", success))
    except Exception as e:
        print(f"❌ Property serialization failed: {e}")
        results.append(("Property Serialization", False))
    
    # Test 3: Content type detection
    try:
        await test_content_type_detection()
        results.append(("Content Type Detection", True))
    except Exception as e:
        print(f"❌ Content type detection failed: {e}")
        results.append(("Content Type Detection", False))
    
    # Test 4: Mock brochure generation
    try:
        success = await test_mock_brochure_generation()
        results.append(("Mock Brochure Generation", success))
    except Exception as e:
        print(f"❌ Mock brochure generation failed: {e}")
        results.append(("Mock Brochure Generation", False))
    
    # Test 5: Task orchestrator integration
    try:
        success = await test_task_orchestrator_integration()
        results.append(("Task Orchestrator Integration", success))
    except Exception as e:
        print(f"❌ Task orchestrator integration failed: {e}")
        results.append(("Task Orchestrator Integration", False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Property brochure generation is ready.")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check implementation.")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))