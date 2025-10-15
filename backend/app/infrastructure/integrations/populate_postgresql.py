#!/usr/bin/env python3
"""
PostgreSQL Population Script for Dubai Real Estate RAG System
This script populates all PostgreSQL tables with sample data for intelligent assistant functionality
"""

import os
import sys
import json
from sqlalchemy import create_engine, text
from datetime import datetime, date
import logging
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


class PostgreSQLPopulator:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

        # Sample data for each table
        self.sample_data = {
            "properties": [
                {
                    "address": "Marina Gate 1, Dubai Marina",
                    "price": 2500000,
                    "bedrooms": 2,
                    "bathrooms": 2.5,
                    "square_feet": 1200,
                    "property_type": "apartment",
                    "description": "Luxury waterfront apartment with marina views",
                    "listing_status": "live",
                },
                {
                    "address": "Burj Vista 2, Downtown Dubai",
                    "price": 4500000,
                    "bedrooms": 3,
                    "bathrooms": 3.5,
                    "square_feet": 1800,
                    "property_type": "apartment",
                    "description": "Premium apartment with Burj Khalifa views",
                    "listing_status": "live",
                },
                {
                    "address": "Palm Tower, Palm Jumeirah",
                    "price": 8500000,
                    "bedrooms": 4,
                    "bathrooms": 4.5,
                    "square_feet": 2800,
                    "property_type": "penthouse",
                    "description": "Exclusive penthouse with panoramic sea views",
                    "listing_status": "live",
                },
                {
                    "address": "Binghatti Rose, Business Bay",
                    "price": 1800000,
                    "bedrooms": 1,
                    "bathrooms": 1.5,
                    "square_feet": 800,
                    "property_type": "apartment",
                    "description": "Modern apartment in emerging business district",
                    "listing_status": "live",
                },
                {
                    "address": "Villa 45, Emirates Hills",
                    "price": 12000000,
                    "bedrooms": 5,
                    "bathrooms": 6,
                    "square_feet": 4500,
                    "property_type": "villa",
                    "description": "Luxury villa with private garden and pool",
                    "listing_status": "live",
                },
            ],
            "market_data": [
                {
                    "area": "Dubai Marina",
                    "property_type": "apartment",
                    "avg_price": 2500,
                    "price_change_percentage": 15.5,
                    "transaction_volume": 1250,
                    "rental_yield": 6.8,
                    "market_trend": "rising",
                    "data_date": date(2024, 8, 1),
                },
                {
                    "area": "Downtown Dubai",
                    "property_type": "apartment",
                    "avg_price": 3200,
                    "price_change_percentage": 18.2,
                    "transaction_volume": 890,
                    "rental_yield": 5.2,
                    "market_trend": "rising",
                    "data_date": date(2024, 8, 1),
                },
                {
                    "area": "Palm Jumeirah",
                    "property_type": "villa",
                    "avg_price": 4500,
                    "price_change_percentage": 22.1,
                    "transaction_volume": 340,
                    "rental_yield": 4.5,
                    "market_trend": "rising",
                    "data_date": date(2024, 8, 1),
                },
                {
                    "area": "Business Bay",
                    "property_type": "apartment",
                    "avg_price": 1800,
                    "price_change_percentage": 12.8,
                    "transaction_volume": 670,
                    "rental_yield": 7.2,
                    "market_trend": "stable",
                    "data_date": date(2024, 8, 1),
                },
            ],
            "neighborhood_profiles": [
                {
                    "name": "Dubai Marina",
                    "description": "Luxury waterfront community with 200+ restaurants and world-class amenities",
                    "price_ranges": json.dumps(
                        {
                            "studio": "800K-1.2M",
                            "1BR": "1.2M-1.8M",
                            "2BR": "1.8M-3M",
                            "3BR": "3M-5M",
                        }
                    ),
                    "rental_yields": json.dumps(
                        {"studio": "6.5%", "1BR": "6.8%", "2BR": "7.0%", "3BR": "6.5%"}
                    ),
                    "amenities": json.dumps(
                        [
                            "Marina Walk",
                            "Dubai Marina Mall",
                            "Metro Station",
                            "Beach Access",
                            "5-star Hotels",
                        ]
                    ),
                    "pros": json.dumps(
                        [
                            "Waterfront location",
                            "High rental yields",
                            "Excellent amenities",
                            "Metro connectivity",
                        ]
                    ),
                    "cons": json.dumps(
                        [
                            "Traffic congestion",
                            "High service charges",
                            "Limited parking",
                        ]
                    ),
                    "source_file": "area_guide_dubai_marina",
                },
                {
                    "name": "Downtown Dubai",
                    "description": "Home to Burj Khalifa and Dubai Mall, ultra-luxury properties with iconic views",
                    "price_ranges": json.dumps(
                        {
                            "1BR": "2M-3M",
                            "2BR": "3M-5M",
                            "3BR": "5M-8M",
                            "Penthouse": "10M+",
                        }
                    ),
                    "rental_yields": json.dumps(
                        {
                            "1BR": "5.0%",
                            "2BR": "5.2%",
                            "3BR": "5.5%",
                            "Penthouse": "4.8%",
                        }
                    ),
                    "amenities": json.dumps(
                        [
                            "Burj Khalifa",
                            "Dubai Mall",
                            "Dubai Fountain",
                            "Metro Station",
                            "Luxury Hotels",
                        ]
                    ),
                    "pros": json.dumps(
                        [
                            "Iconic location",
                            "Luxury lifestyle",
                            "High appreciation",
                            "Tourist attraction",
                        ]
                    ),
                    "cons": json.dumps(
                        ["Very expensive", "Tourist crowds", "High maintenance costs"]
                    ),
                    "source_file": "area_guide_downtown",
                },
                {
                    "name": "Palm Jumeirah",
                    "description": "Exclusive island community with private beaches and luxury villas",
                    "price_ranges": json.dumps(
                        {
                            "Apartment": "3M-6M",
                            "Villa": "8M-25M",
                            "Penthouse": "15M-50M",
                        }
                    ),
                    "rental_yields": json.dumps(
                        {"Apartment": "4.8%", "Villa": "4.5%", "Penthouse": "4.2%"}
                    ),
                    "amenities": json.dumps(
                        [
                            "Private Beaches",
                            "Atlantis Hotel",
                            "Aquaventure",
                            "Beach Clubs",
                            "Fine Dining",
                        ]
                    ),
                    "pros": json.dumps(
                        [
                            "Exclusive location",
                            "Private beaches",
                            "High capital appreciation",
                            "Luxury lifestyle",
                        ]
                    ),
                    "cons": json.dumps(
                        ["Limited supply", "High prices", "Island access only"]
                    ),
                    "source_file": "area_guide_palm_jumeirah",
                },
            ],
            "developers": [
                {
                    "name": "Emaar Properties",
                    "market_share": 40.5,
                    "reputation_score": 9.2,
                    "key_projects": json.dumps(
                        [
                            "Burj Khalifa",
                            "Dubai Mall",
                            "Downtown Dubai",
                            "Dubai Marina",
                            "Emirates Hills",
                        ]
                    ),
                    "track_record": "Dubai's largest developer with excellent track record of on-time delivery and quality construction",
                    "contact_info": json.dumps(
                        {
                            "phone": "+971-4-366-8888",
                            "email": "info@emaar.ae",
                            "website": "www.emaar.ae",
                        }
                    ),
                },
                {
                    "name": "DAMAC Properties",
                    "market_share": 15.2,
                    "reputation_score": 8.5,
                    "key_projects": json.dumps(
                        [
                            "DAMAC Hills",
                            "AKOYA Oxygen",
                            "DAMAC Towers",
                            "DAMAC Bay",
                            "DAMAC Hills 2",
                        ]
                    ),
                    "track_record": "Luxury developer known for innovative designs and premium amenities",
                    "contact_info": json.dumps(
                        {
                            "phone": "+971-4-373-2000",
                            "email": "info@damacgroup.com",
                            "website": "www.damacgroup.com",
                        }
                    ),
                },
                {
                    "name": "Nakheel",
                    "market_share": 12.8,
                    "reputation_score": 8.8,
                    "key_projects": json.dumps(
                        [
                            "Palm Jumeirah",
                            "Palm Jebel Ali",
                            "Dubai Islands",
                            "Ibn Battuta Mall",
                            "Jumeirah Islands",
                        ]
                    ),
                    "track_record": "Government-owned developer with strong financial backing and large-scale project expertise",
                    "contact_info": json.dumps(
                        {
                            "phone": "+971-4-390-3333",
                            "email": "info@nakheel.com",
                            "website": "www.nakheel.com",
                        }
                    ),
                },
                {
                    "name": "Sobha Realty",
                    "market_share": 8.5,
                    "reputation_score": 8.9,
                    "key_projects": json.dumps(
                        [
                            "Sobha Hartland",
                            "Sobha Creek Vistas",
                            "Sobha Greens",
                            "Sobha Hartland 2",
                        ]
                    ),
                    "track_record": "Premium developer known for high-quality construction and attention to detail",
                    "contact_info": json.dumps(
                        {
                            "phone": "+971-4-378-8888",
                            "email": "info@sobha.com",
                            "website": "www.sobha.com",
                        }
                    ),
                },
            ],
            "investment_insights": [
                {
                    "title": "Dubai Real Estate Investment Strategy 2024",
                    "summary": "Focus on off-plan properties in emerging areas for maximum ROI",
                    "investment_type": "off_plan",
                    "expected_roi": 25.5,
                    "time_horizon": "3-5 years",
                    "risk_level": "medium",
                    "target_areas": json.dumps(
                        [
                            "Dubai South",
                            "Dubai Creek Harbour",
                            "Business Bay",
                            "Dubai Hills",
                        ]
                    ),
                    "key_factors": json.dumps(
                        [
                            "Golden Visa benefits",
                            "Strong market fundamentals",
                            "Government support",
                            "Infrastructure development",
                        ]
                    ),
                    "source": "Investment Analysis Report",
                },
                {
                    "title": "Rental Investment Analysis",
                    "summary": "Dubai Marina offers best rental yields while Downtown provides luxury appeal",
                    "investment_type": "rental",
                    "expected_roi": 6.8,
                    "time_horizon": "long_term",
                    "risk_level": "low",
                    "target_areas": json.dumps(
                        ["Dubai Marina", "Downtown Dubai", "Business Bay", "JBR"]
                    ),
                    "key_factors": json.dumps(
                        [
                            "High rental demand",
                            "Stable rental income",
                            "Property appreciation",
                            "Low vacancy rates",
                        ]
                    ),
                    "source": "Rental Market Report",
                },
                {
                    "title": "Luxury Property Investment Guide",
                    "summary": "Ultra-luxury segment showing strong growth with international buyer demand",
                    "investment_type": "luxury",
                    "expected_roi": 18.5,
                    "time_horizon": "5-10 years",
                    "risk_level": "high",
                    "target_areas": json.dumps(
                        [
                            "Palm Jumeirah",
                            "Emirates Hills",
                            "Downtown Dubai",
                            "Dubai Hills",
                        ]
                    ),
                    "key_factors": json.dumps(
                        [
                            "Limited supply",
                            "High net worth buyers",
                            "Status symbol",
                            "Capital appreciation",
                        ]
                    ),
                    "source": "Luxury Market Analysis",
                },
            ],
            "regulatory_updates": [
                {
                    "title": "Golden Visa Property Investment Requirements",
                    "description": "Updated requirements for property investment to qualify for Golden Visa",
                    "regulation_type": "visa_regulations",
                    "effective_date": date(2024, 1, 1),
                    "requirements": json.dumps(
                        [
                            "Minimum property value: AED 2M",
                            "Off-plan requires 50% down payment",
                            "RERA escrow account mandatory",
                            "Property must be completed within 2 years",
                        ]
                    ),
                    "impact_analysis": "Positive impact on foreign investment with simplified requirements and faster processing",
                    "source": "GDRFA Dubai",
                },
                {
                    "title": "RERA Agent Licensing Requirements",
                    "description": "Updated licensing requirements for real estate agents in Dubai",
                    "regulation_type": "agent_regulations",
                    "effective_date": date(2024, 3, 1),
                    "requirements": json.dumps(
                        [
                            "Mandatory licensing for all agents",
                            "Commission capped at 2% residential, 4% commercial",
                            "Mandatory disclosure of all fees",
                            "Professional indemnity insurance required",
                        ]
                    ),
                    "impact_analysis": "Improved professionalism and transparency in real estate transactions",
                    "source": "RERA",
                },
                {
                    "title": "DLD Transfer Fee Updates",
                    "description": "Updated transfer fees for property transactions in Dubai",
                    "regulation_type": "transaction_regulations",
                    "effective_date": date(2024, 6, 1),
                    "requirements": json.dumps(
                        [
                            "4% for first-time buyers",
                            "8% for investors",
                            "NOC required for off-plan resale",
                            "Mandatory registration within 60 days",
                        ]
                    ),
                    "impact_analysis": "Encourages first-time buyers while maintaining market stability",
                    "source": "Dubai Land Department",
                },
            ],
            "leads": [
                {
                    "agent_id": 3,  # agent1@dubai-estate.com
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@email.com",
                    "phone": "+971-50-123-4567",
                    "status": "new",
                    "source": "website",
                    "budget_min": 2000000,
                    "budget_max": 3500000,
                    "preferred_areas": json.dumps(["Dubai Marina", "Downtown Dubai"]),
                    "property_type": "apartment",
                    "last_contacted": datetime(2024, 8, 20, 10, 30),
                    "notes": "Interested in 2-3 bedroom apartments with marina views",
                },
                {
                    "agent_id": 3,
                    "name": "Ahmed Al Mansouri",
                    "email": "ahmed.mansouri@email.com",
                    "phone": "+971-55-987-6543",
                    "status": "contacted",
                    "source": "referral",
                    "budget_min": 5000000,
                    "budget_max": 8000000,
                    "preferred_areas": json.dumps(["Palm Jumeirah", "Emirates Hills"]),
                    "property_type": "villa",
                    "last_contacted": datetime(2024, 8, 22, 14, 15),
                    "notes": "Looking for luxury villa with private pool and garden",
                },
                {
                    "agent_id": 4,  # agent2@dubai-estate.com
                    "name": "Maria Rodriguez",
                    "email": "maria.rodriguez@email.com",
                    "phone": "+971-52-456-7890",
                    "status": "qualified",
                    "source": "social_media",
                    "budget_min": 1500000,
                    "budget_max": 2500000,
                    "preferred_areas": json.dumps(["Business Bay", "Dubai Hills"]),
                    "property_type": "apartment",
                    "last_contacted": datetime(2024, 8, 21, 16, 45),
                    "notes": "First-time buyer, needs guidance on mortgage options",
                },
                {
                    "agent_id": 4,
                    "name": "David Chen",
                    "email": "david.chen@email.com",
                    "phone": "+971-54-321-0987",
                    "status": "new",
                    "source": "website",
                    "budget_min": 3000000,
                    "budget_max": 5000000,
                    "preferred_areas": json.dumps(["Downtown Dubai", "Dubai Marina"]),
                    "property_type": "penthouse",
                    "last_contacted": None,
                    "notes": "Investor looking for high-end properties with rental potential",
                },
            ],
            "viewings": [
                {
                    "agent_id": 3,
                    "client_name": "Sarah Johnson",
                    "property_address": "Marina Gate 1, Dubai Marina",
                    "viewing_date": date(2024, 8, 23),
                    "viewing_time": "14:00:00",
                    "status": "completed",
                    "client_feedback": "Loved the marina views but concerned about service charges",
                    "follow_up_required": True,
                },
                {
                    "agent_id": 3,
                    "client_name": "Ahmed Al Mansouri",
                    "property_address": "Villa 45, Emirates Hills",
                    "viewing_date": date(2024, 8, 24),
                    "viewing_time": "10:00:00",
                    "status": "scheduled",
                    "client_feedback": None,
                    "follow_up_required": True,
                },
                {
                    "agent_id": 4,
                    "client_name": "Maria Rodriguez",
                    "property_address": "Binghatti Rose, Business Bay",
                    "viewing_date": date(2024, 8, 23),
                    "viewing_time": "16:00:00",
                    "status": "completed",
                    "client_feedback": "Property is perfect size but needs to check mortgage approval",
                    "follow_up_required": True,
                },
            ],
            "appointments": [
                {
                    "agent_id": 3,
                    "client_name": "Sarah Johnson",
                    "appointment_date": date(2024, 8, 25),
                    "appointment_time": "11:00:00",
                    "appointment_type": "contract_review",
                    "notes": "Review purchase contract for Marina Gate property",
                    "status": "scheduled",
                },
                {
                    "agent_id": 3,
                    "client_name": "Ahmed Al Mansouri",
                    "appointment_date": date(2024, 8, 25),
                    "appointment_time": "15:00:00",
                    "appointment_type": "property_viewing",
                    "notes": "View additional properties in Palm Jumeirah area",
                    "status": "scheduled",
                },
                {
                    "agent_id": 4,
                    "client_name": "Maria Rodriguez",
                    "appointment_date": date(2024, 8, 25),
                    "appointment_time": "13:00:00",
                    "appointment_type": "mortgage_consultation",
                    "notes": "Meet with mortgage advisor to discuss financing options",
                    "status": "scheduled",
                },
                {
                    "agent_id": 4,
                    "client_name": "David Chen",
                    "appointment_date": date(2024, 8, 25),
                    "appointment_time": "17:00:00",
                    "appointment_type": "initial_consultation",
                    "notes": "First meeting to understand investment requirements",
                    "status": "scheduled",
                },
            ],
            # Phase 1: New tables for granular data & security
            "property_confidential": [
                {
                    "property_id": 1,
                    "unit_number": "MG1-1501",
                    "plot_number": "DM-001-2024",
                    "floor": "15",
                    "owner_details": "Ahmed Al Rashid - Emirates ID: 784-1985-1234567-8",
                },
                {
                    "property_id": 2,
                    "unit_number": "BV2-2203",
                    "plot_number": "DD-002-2024",
                    "floor": "22",
                    "owner_details": "Fatima Al Zahra - Emirates ID: 784-1990-9876543-2",
                },
                {
                    "property_id": 3,
                    "unit_number": "PT-4501",
                    "plot_number": "PJ-003-2024",
                    "floor": "45",
                    "owner_details": "Mohammed Al Qasimi - Emirates ID: 784-1988-4567890-1",
                },
                {
                    "property_id": 4,
                    "unit_number": "BR-801",
                    "plot_number": "BB-004-2024",
                    "floor": "8",
                    "owner_details": "Aisha Al Mansouri - Emirates ID: 784-1992-3210987-6",
                },
                {
                    "property_id": 5,
                    "unit_number": "EH-V45",
                    "plot_number": "EH-005-2024",
                    "floor": "Ground",
                    "owner_details": "David Chen - Passport: H12345678",
                },
            ],
            "transactions": [
                {
                    "property_id": 1,
                    "agent_id": 3,
                    "transaction_date": date(2024, 6, 15),
                    "sale_price": 2500000,
                    "price_per_sqft": 2083.33,
                    "source_document_id": "TRX-2024-001",
                },
                {
                    "property_id": 2,
                    "agent_id": 3,
                    "transaction_date": date(2024, 7, 20),
                    "sale_price": 4500000,
                    "price_per_sqft": 2500.00,
                    "source_document_id": "TRX-2024-002",
                },
                {
                    "property_id": 3,
                    "agent_id": 4,
                    "transaction_date": date(2024, 5, 10),
                    "sale_price": 8500000,
                    "price_per_sqft": 3035.71,
                    "source_document_id": "TRX-2024-003",
                },
            ],
            "lead_history": [
                {
                    "lead_id": 1,
                    "status_from": "new",
                    "status_to": "contacted",
                    "changed_by_agent_id": 3,
                },
                {
                    "lead_id": 2,
                    "status_from": "new",
                    "status_to": "contacted",
                    "changed_by_agent_id": 3,
                },
                {
                    "lead_id": 2,
                    "status_from": "contacted",
                    "status_to": "qualified",
                    "changed_by_agent_id": 3,
                },
                {
                    "lead_id": 3,
                    "status_from": "new",
                    "status_to": "contacted",
                    "changed_by_agent_id": 4,
                },
                {
                    "lead_id": 3,
                    "status_from": "contacted",
                    "status_to": "qualified",
                    "changed_by_agent_id": 4,
                },
            ],
            "client_interactions": [
                {
                    "lead_id": 1,
                    "agent_id": 3,
                    "interaction_type": "call",
                    "notes": "Initial contact - client interested in marina properties",
                    "interaction_date": datetime(2024, 8, 20, 10, 30),
                },
                {
                    "lead_id": 1,
                    "agent_id": 3,
                    "interaction_type": "email",
                    "notes": "Sent property listings for Dubai Marina area",
                    "interaction_date": datetime(2024, 8, 21, 14, 15),
                },
                {
                    "lead_id": 2,
                    "agent_id": 3,
                    "interaction_type": "viewing_log",
                    "notes": "Property viewing scheduled for Villa 45 in Emirates Hills",
                    "interaction_date": datetime(2024, 8, 22, 16, 45),
                },
                {
                    "lead_id": 3,
                    "agent_id": 4,
                    "interaction_type": "call",
                    "notes": "Mortgage consultation call - client needs financing options",
                    "interaction_date": datetime(2024, 8, 21, 11, 20),
                },
            ],
            "listing_history": [
                {
                    "property_id": 1,
                    "event_type": "status_change",
                    "old_value": "draft",
                    "new_value": "live",
                    "changed_by_agent_id": 3,
                },
                {
                    "property_id": 2,
                    "event_type": "status_change",
                    "old_value": "draft",
                    "new_value": "live",
                    "changed_by_agent_id": 3,
                },
                {
                    "property_id": 3,
                    "event_type": "status_change",
                    "old_value": "draft",
                    "new_value": "live",
                    "changed_by_agent_id": 4,
                },
                {
                    "property_id": 4,
                    "event_type": "status_change",
                    "old_value": "draft",
                    "new_value": "live",
                    "changed_by_agent_id": 4,
                },
                {
                    "property_id": 5,
                    "event_type": "status_change",
                    "old_value": "draft",
                    "new_value": "live",
                    "changed_by_agent_id": 3,
                },
            ],
        }

    def create_tables_if_not_exist(self):
        """Create tables if they don't exist"""
        try:
            with self.engine.connect() as conn:
                # Create market_data table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS market_data (
                        id SERIAL PRIMARY KEY,
                        area VARCHAR(100),
                        property_type VARCHAR(50),
                        avg_price DECIMAL(12,2),
                        price_change_percentage DECIMAL(5,2),
                        transaction_volume INTEGER,
                        rental_yield DECIMAL(5,2),
                        market_trend VARCHAR(50),
                        data_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create neighborhood_profiles table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS neighborhood_profiles (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        description TEXT,
                        price_ranges JSONB,
                        rental_yields JSONB,
                        amenities JSONB,
                        pros JSONB,
                        cons JSONB,
                        source_file VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create developers table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS developers (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        market_share DECIMAL(5,2),
                        reputation_score DECIMAL(3,1),
                        key_projects JSONB,
                        track_record TEXT,
                        contact_info JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create investment_insights table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS investment_insights (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255),
                        summary TEXT,
                        investment_type VARCHAR(100),
                        expected_roi DECIMAL(5,2),
                        time_horizon VARCHAR(50),
                        risk_level VARCHAR(50),
                        target_areas JSONB,
                        key_factors JSONB,
                        source VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create regulatory_updates table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS regulatory_updates (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255),
                        description TEXT,
                        regulation_type VARCHAR(100),
                        effective_date DATE,
                        requirements JSONB,
                        impact_analysis TEXT,
                        source VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create leads table for daily briefing feature
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS leads (
                        id SERIAL PRIMARY KEY,
                        agent_id INTEGER REFERENCES users(id),
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255),
                        phone VARCHAR(50),
                        status VARCHAR(50) DEFAULT 'new',
                        source VARCHAR(100),
                        budget_min DECIMAL(12,2),
                        budget_max DECIMAL(12,2),
                        preferred_areas JSONB,
                        property_type VARCHAR(100),
                        last_contacted TIMESTAMP,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create viewings table for daily briefing feature
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS viewings (
                        id SERIAL PRIMARY KEY,
                        agent_id INTEGER REFERENCES users(id),
                        client_name VARCHAR(255) NOT NULL,
                        property_address TEXT NOT NULL,
                        viewing_date DATE NOT NULL,
                        viewing_time TIME,
                        status VARCHAR(50) DEFAULT 'scheduled',
                        client_feedback TEXT,
                        follow_up_required BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create appointments table for daily briefing feature
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS appointments (
                        id SERIAL PRIMARY KEY,
                        agent_id INTEGER REFERENCES users(id),
                        client_name VARCHAR(255) NOT NULL,
                        appointment_date DATE NOT NULL,
                        appointment_time TIME NOT NULL,
                        appointment_type VARCHAR(100),
                        notes TEXT,
                        status VARCHAR(50) DEFAULT 'scheduled',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # --- Phase 1: Granular Data & Security Foundation ---

                # 1. Alter Properties Table for Listing Status
                conn.execute(
                    text(
                        """
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='properties' AND column_name='listing_status') THEN
                            ALTER TABLE properties ADD COLUMN listing_status VARCHAR(20) DEFAULT 'draft';
                        END IF;
                    END $$;
                """
                    )
                )

                # 2. Create Confidential Data Table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS property_confidential (
                        id SERIAL PRIMARY KEY,
                        property_id INTEGER UNIQUE REFERENCES properties(id) ON DELETE CASCADE,
                        unit_number VARCHAR(50),
                        plot_number VARCHAR(50),
                        floor VARCHAR(20),
                        owner_details TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """
                    )
                )

                # 3. Create Transactions Table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        property_id INTEGER REFERENCES properties(id),
                        agent_id INTEGER REFERENCES users(id),
                        transaction_date DATE NOT NULL,
                        sale_price NUMERIC(15, 2) NOT NULL,
                        price_per_sqft NUMERIC(10, 2),
                        source_document_id VARCHAR(255),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """
                    )
                )

                # 4. Create Lead History Table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS lead_history (
                        id SERIAL PRIMARY KEY,
                        lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
                        status_from VARCHAR(50),
                        status_to VARCHAR(50),
                        change_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        changed_by_agent_id INTEGER REFERENCES users(id)
                    );
                """
                    )
                )

                # 5. Create Client Interactions Table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS client_interactions (
                        id SERIAL PRIMARY KEY,
                        lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
                        agent_id INTEGER REFERENCES users(id),
                        interaction_type VARCHAR(50), -- e.g., 'call', 'email', 'viewing_log'
                        notes TEXT,
                        interaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """
                    )
                )

                # 6. Create Listing History Table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS listing_history (
                        id SERIAL PRIMARY KEY,
                        property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
                        event_type VARCHAR(50), -- e.g., 'price_change', 'status_change'
                        old_value VARCHAR(255),
                        new_value VARCHAR(255),
                        change_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        changed_by_agent_id INTEGER REFERENCES users(id)
                    );
                """
                    )
                )

                conn.commit()
                logger.info("✅ All tables created successfully")

        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
            raise

    def create_default_users(self):
        """Create default admin and agent users"""
        try:
            with self.engine.connect() as conn:
                # Check if users table exists, if not create it
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        role VARCHAR(50) DEFAULT 'client',
                        is_active BOOLEAN DEFAULT TRUE,
                        email_verified BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Default users data with properly hashed passwords
                default_users = [
                    # Admin users
                    {
                        "email": "admin1@dubai-estate.com",
                        "password_hash": hash_password("Admin123!"),
                        "first_name": "Ahmed",
                        "last_name": "Al Mansouri",
                        "role": "admin",
                        "is_active": True,
                        "email_verified": True,
                    },
                    {
                        "email": "admin2@dubai-estate.com",
                        "password_hash": hash_password("Admin123!"),
                        "first_name": "Fatima",
                        "last_name": "Al Zahra",
                        "role": "admin",
                        "is_active": True,
                        "email_verified": True,
                    },
                    # Agent users
                    {
                        "email": "agent1@dubai-estate.com",
                        "password_hash": hash_password("Agent123!"),
                        "first_name": "Mohammed",
                        "last_name": "Al Rashid",
                        "role": "agent",
                        "is_active": True,
                        "email_verified": True,
                    },
                    {
                        "email": "agent2@dubai-estate.com",
                        "password_hash": hash_password("Agent123!"),
                        "first_name": "Aisha",
                        "last_name": "Al Qasimi",
                        "role": "agent",
                        "is_active": True,
                        "email_verified": True,
                    },
                ]

                # Insert default users
                for user in default_users:
                    # Check if user already exists
                    result = conn.execute(
                        text("SELECT id FROM users WHERE email = :email"),
                        {"email": user["email"]},
                    )
                    if not result.fetchone():
                        conn.execute(
                            text(
                                """
                            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, email_verified)
                            VALUES (:email, :password_hash, :first_name, :last_name, :role, :is_active, :email_verified)
                        """
                            ),
                            user,
                        )
                        logger.info(f"✅ Created user: {user['email']} ({user['role']})")
                    else:
                        logger.info(f"ℹ️ User already exists: {user['email']}")

                conn.commit()
                logger.info("✅ Default users created successfully")

        except Exception as e:
            logger.error(f"❌ Error creating default users: {e}")
            raise

    def populate_tables(self):
        """Populate all tables with sample data"""
        total_records = 0

        for table_name, records in self.sample_data.items():
            try:
                with self.engine.connect() as conn:
                    for record in records:
                        # Build dynamic INSERT statement
                        columns = list(record.keys())
                        values = list(record.values())
                        placeholders = [f":{col}" for col in columns]

                        sql = f"""
                            INSERT INTO {table_name} ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                        """

                        conn.execute(text(sql), record)

                    conn.commit()
                    total_records += len(records)
                    logger.info(f"✅ Added {len(records)} records to {table_name}")

            except Exception as e:
                logger.error(f"❌ Error populating table {table_name}: {e}")

        return total_records

    def verify_tables(self):
        """Verify that tables are populated"""
        verification_results = {}

        for table_name in self.sample_data.keys():
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    verification_results[table_name] = count
                    logger.info(f"📊 Table {table_name}: {count} records")
            except Exception as e:
                logger.error(f"❌ Error verifying table {table_name}: {e}")
                verification_results[table_name] = 0

        return verification_results

    def run_population(self):
        """Run complete PostgreSQL population process"""
        try:
            logger.info("🚀 Starting PostgreSQL population...")

            # Create tables
            self.create_tables_if_not_exist()

            # Create default users
            self.create_default_users()

            # Populate tables
            total_records = self.populate_tables()
            logger.info(f"✅ Added {total_records} total records")

            # Verify tables
            verification = self.verify_tables()

            logger.info("🎉 PostgreSQL population completed successfully!")
            return {"total_records": total_records, "verification": verification}

        except Exception as e:
            logger.error(f"❌ Error during PostgreSQL population: {e}")
            raise


def main():
    """Main function to run PostgreSQL population"""
    try:
        # Get the database URL from the environment variable
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("❌ DATABASE_URL environment variable not set.")
            sys.exit(1)

        # Pass the correct URL to the populator
        populator = PostgreSQLPopulator(db_url=db_url)
        results = populator.run_population()

        print("\n" + "=" * 60)
        print("🎉 POSTGRESQL POPULATION COMPLETED!")
        print("=" * 60)
        print(f"✅ Total records added: {results['total_records']}")
        print("\n📊 Table Verification:")
        for table, count in results["verification"].items():
            print(f"   - {table}: {count} records")
        print("\n👥 Default Users Created:")
        print("   - admin1@dubai-estate.com (Admin)")
        print("   - admin2@dubai-estate.com (Admin)")
        print("   - agent1@dubai-estate.com (Agent)")
        print("   - agent2@dubai-estate.com (Agent)")
        print("\n🔑 Default Passwords:")
        print("   - Admins: Admin123!")
        print("   - Agents: Agent123!")
        print("\nYour RAG system now has comprehensive database data!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"❌ Failed to populate PostgreSQL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
