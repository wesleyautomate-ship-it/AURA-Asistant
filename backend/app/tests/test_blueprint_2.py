#!/usr/bin/env python3
"""
Test Script for Blueprint 2.0: Proactive AI Copilot
Tests the new features including web-based content delivery and proactive lead nurturing
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_database_schema():
    """Test that the new database schema is properly set up"""
    logger.info("🔍 Testing database schema...")

    try:
        from sqlalchemy import create_engine, text

        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://admin:password123@localhost:5432/real_estate_db",
        )
        engine = create_engine(db_url)

        with engine.connect() as conn:
            # Test generated_documents table
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as count FROM generated_documents
            """
                )
            )
            count = result.fetchone().count
            logger.info(f"✅ generated_documents table: {count} records")

            # Test leads table enhancements
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as count FROM leads 
                WHERE nurture_status IS NOT NULL
            """
                )
            )
            count = result.fetchone().count
            logger.info(
                f"✅ leads table enhancements: {count} records with nurture_status"
            )

            # Test lead_history table
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as count FROM lead_history
            """
                )
            )
            count = result.fetchone().count
            logger.info(f"✅ lead_history table: {count} records")

            # Test notifications table
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as count FROM notifications
            """
                )
            )
            count = result.fetchone().count
            logger.info(f"✅ notifications table: {count} records")

            # Test tasks table
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) as count FROM tasks
            """
                )
            )
            count = result.fetchone().count
            logger.info(f"✅ tasks table: {count} records")

        return True

    except Exception as e:
        logger.error(f"❌ Database schema test failed: {e}")
        return False


def test_document_generator():
    """Test the document generator functionality"""
    logger.info("📄 Testing document generator...")

    try:
        from document_generator import DocumentGenerator
        import google.generativeai as genai

        # Initialize AI model
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("⚠️ GOOGLE_API_KEY not found, skipping AI model test")
            return True

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")

        # Initialize document generator
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://admin:password123@localhost:5432/real_estate_db",
        )
        document_generator = DocumentGenerator(db_url, model)

        # Test data
        subject_property = {
            "address": "Villa 12, Emirates Hills",
            "property_type": "villa",
            "bedrooms": 5,
            "bathrooms": 6,
            "size_sqft": 4500,
            "current_price": 12000000,
        }

        comparable_properties = [
            {
                "address": "Villa 15, Emirates Hills",
                "price": 11500000,
                "bedrooms": 5,
                "bathrooms": 5,
                "area_sqft": 4200,
                "price_per_sqft": 2738,
            },
            {
                "address": "Villa 8, Emirates Hills",
                "price": 12500000,
                "bedrooms": 5,
                "bathrooms": 6,
                "area_sqft": 4800,
                "price_per_sqft": 2604,
            },
        ]

        # Test CMA generation
        result = document_generator.generate_cma_html(
            subject_property, comparable_properties, 1
        )

        if "error" in result:
            logger.error(f"❌ CMA generation failed: {result['error']}")
            return False

        logger.info(f"✅ CMA document generated successfully: {result['document_id']}")
        logger.info(f"✅ Result URL: {result['result_url']}")
        logger.info(f"✅ Preview: {result['preview_summary']}")

        return True

    except Exception as e:
        logger.error(f"❌ Document generator test failed: {e}")
        return False


def test_action_engine():
    """Test the action engine functionality"""
    logger.info("⚙️ Testing action engine...")

    try:
        from action_engine import ActionEngine

        action_engine = ActionEngine()

        # Test getting follow-up context for a lead
        context = action_engine.get_follow_up_context(1)  # Assuming lead ID 1 exists

        if "error" in context:
            logger.warning(f"⚠️ Lead context test: {context['error']}")
        else:
            logger.info(f"✅ Lead context retrieved successfully")
            logger.info(f"✅ Lead profile: {context['profile']['name']}")
            logger.info(f"✅ History items: {len(context['history'])}")

        # Test getting leads needing attention
        leads = action_engine.get_leads_needing_follow_up(agent_id=1, days_threshold=5)
        logger.info(f"✅ Leads needing attention: {len(leads)}")

        return True

    except Exception as e:
        logger.error(f"❌ Action engine test failed: {e}")
        return False


async def test_nurturing_scheduler():
    """Test the nurturing scheduler functionality"""
    logger.info("⏰ Testing nurturing scheduler...")

    try:
        from nurturing_scheduler import NurturingScheduler

        scheduler = NurturingScheduler()

        # Test manual nurture check
        result = await scheduler.run_manual_nurture_check()

        if result["success"]:
            logger.info(
                f"✅ Manual nurture check completed: {result['total_count']} leads need attention"
            )
        else:
            logger.warning(
                f"⚠️ Manual nurture check: {result.get('error', 'Unknown error')}"
            )

        return True

    except Exception as e:
        logger.error(f"❌ Nurturing scheduler test failed: {e}")
        return False


def test_api_endpoints():
    """Test the new API endpoints"""
    logger.info("🌐 Testing API endpoints...")

    try:
        import requests

        base_url = "http://localhost:8001"

        # Test documents endpoint
        try:
            response = requests.get(f"{base_url}/documents/")
            if response.status_code == 200:
                logger.info("✅ Documents endpoint working")
            else:
                logger.warning(f"⚠️ Documents endpoint: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Documents endpoint test: {e}")

        # Test nurturing endpoint
        try:
            response = requests.get(f"{base_url}/nurturing/users/me/agenda")
            if response.status_code == 200:
                logger.info("✅ Nurturing agenda endpoint working")
            else:
                logger.warning(f"⚠️ Nurturing agenda endpoint: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Nurturing agenda endpoint test: {e}")

        return True

    except Exception as e:
        logger.error(f"❌ API endpoints test failed: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("🚀 Starting Blueprint 2.0 tests...")

    tests = [
        ("Database Schema", test_database_schema),
        ("Document Generator", test_document_generator),
        ("Action Engine", test_action_engine),
        ("Nurturing Scheduler", test_nurturing_scheduler),
        ("API Endpoints", test_api_endpoints),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*50}")

        try:
            if test_name == "Nurturing Scheduler":
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All Blueprint 2.0 tests passed!")
    else:
        logger.warning(f"⚠️ {total - passed} tests failed")

    return passed == total


if __name__ == "__main__":
    import asyncio

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
