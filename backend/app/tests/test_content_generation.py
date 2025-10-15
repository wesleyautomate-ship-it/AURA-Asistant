#!/usr/bin/env python3
"""
Test script for the new content generation capabilities in ai_manager.py

This script demonstrates how to use the new content generation functions
with sample data to generate various types of content.
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the AI manager
from ai_manager import AIEnhancementManager

# Mock Google Gemini model for testing
class MockGeminiModel:
    def generate_content(self, prompt):
        class MockResponse:
            def __init__(self, text):
                self.text = text

        return MockResponse(
            f"[MOCK AI RESPONSE] Generated content for prompt: {prompt[:100]}..."
        )


def test_content_generation():
    """Test all content generation functions"""

    # Initialize the AI manager with mock model
    mock_model = MockGeminiModel()
    db_url = "postgresql://user:pass@localhost/testdb"  # Mock DB URL
    ai_manager = AIEnhancementManager(db_url, mock_model)

    print("🧪 Testing Content Generation Capabilities")
    print("=" * 50)

    # Test 1: Daily Briefing
    print("\n📊 Test 1: Daily Briefing Generation")
    print("-" * 30)

    market_summary = {
        "trend": "Bullish",
        "price_change_pct": 2.5,
        "hotspot_area": "Dubai Marina",
    }

    new_listings = [
        {"bedrooms": 2, "type": "Apartment", "area": "Dubai Marina", "price": 1500000},
        {"bedrooms": 3, "type": "Villa", "area": "Palm Jumeirah", "price": 4500000},
    ]

    new_leads = [
        {"name": "Sarah Johnson", "interest": "2BR apartments in Dubai Marina"},
        {"name": "Ahmed Al Mansouri", "interest": "Luxury villas in Palm Jumeirah"},
    ]

    briefing = ai_manager.generate_daily_briefing(
        "Alex Smith", market_summary, new_listings, new_leads
    )
    print(f"Generated Briefing:\n{briefing}")

    # Test 2: Social Media Post
    print("\n📱 Test 2: Social Media Post Generation")
    print("-" * 30)

    social_post = ai_manager.generate_social_media_post(
        platform="Instagram",
        topic="New Luxury Villa in Palm Jumeirah",
        key_points=[
            "5-bedroom luxury villa",
            "Private beach access",
            "AED 12M price tag",
            "Exclusive community",
        ],
        audience="High-net-worth investors",
        call_to_action="Schedule a private viewing",
    )
    print(f"Generated Social Media Post:\n{social_post}")

    # Test 3: Follow-up Email
    print("\n📧 Test 3: Follow-up Email Generation")
    print("-" * 30)

    email = ai_manager.draft_follow_up_email(
        client_name="Sarah Johnson",
        client_context="Viewed 2BR apartment in Dubai Marina last week, showed interest but concerned about price",
        email_goal="Follow up on viewing and address price concerns",
        listings_to_mention=[
            {
                "bedrooms": 2,
                "type": "Apartment",
                "area": "Dubai Marina",
                "price": 1500000,
            },
            {"bedrooms": 2, "type": "Apartment", "area": "JBR", "price": 1200000},
        ],
    )
    print(f"Generated Email:\n{email}")

    # Test 4: Market Report
    print("\n📈 Test 4: Market Report Generation")
    print("-" * 30)

    market_data = {
        "avg_price_aed": 2500000,
        "price_change_percentage": 15.5,
        "sales_volume": 1250,
        "rental_yield": 6.8,
    }

    market_report = ai_manager.generate_market_report(
        neighborhood="Dubai Marina",
        property_type="Apartments",
        time_period="Q1 2024",
        market_data=market_data,
    )
    print(f"Generated Market Report:\n{market_report}")

    # Test 5: Property Brochure
    print("\n🏠 Test 5: Property Brochure Generation")
    print("-" * 30)

    property_details = {
        "type": "Luxury Apartment",
        "address": "Marina Gate 1, Dubai Marina",
        "price_aed": 3500000,
        "bedrooms": 3,
        "bathrooms": 3,
        "size_sqft": 2200,
        "features": "Sea view, private balcony, gym access, 24/7 security, swimming pool",
    }

    brochure = ai_manager.build_property_brochure(property_details)
    print(f"Generated Property Brochure:\n{brochure}")

    # Test 6: CMA Content
    print("\n📊 Test 6: CMA Content Generation")
    print("-" * 30)

    subject_property = {
        "address": "Marina Gate 1, Dubai Marina",
        "size_sqft": 2200,
        "features": "3BR, sea view, luxury amenities",
    }

    comparable_properties = [
        {
            "address": "Marina Gate 2, Dubai Marina",
            "sold_price_aed": 3400000,
            "size_sqft": 2100,
        },
        {
            "address": "Marina Heights, Dubai Marina",
            "sold_price_aed": 3600000,
            "size_sqft": 2300,
        },
        {
            "address": "Marina Promenade, Dubai Marina",
            "sold_price_aed": 3200000,
            "size_sqft": 2000,
        },
    ]

    cma_content = ai_manager.generate_cma_content(
        subject_property, comparable_properties
    )
    print(f"Generated CMA Content:\n{cma_content}")

    # Test 7: Universal Content Generator
    print("\n🔄 Test 7: Universal Content Generator")
    print("-" * 30)

    # Test using the universal function
    universal_briefing = ai_manager.generate_content_by_type(
        "daily_briefing",
        agent_name="Test Agent",
        market_summary=market_summary,
        new_listings=new_listings,
        new_leads=new_leads,
    )
    print(f"Universal Generator - Daily Briefing:\n{universal_briefing}")

    # Test available content types
    print("\n📋 Available Content Types:")
    print("-" * 30)
    available_types = ai_manager.get_available_content_types()
    for content_type in available_types:
        print(f"• {content_type}")

    print("\n✅ All content generation tests completed successfully!")


if __name__ == "__main__":
    try:
        test_content_generation()
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
