#!/usr/bin/env python3
"""
Data Migration Script for Schema Enhancement
Handles migration of existing data to new schema structure
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json
import random

logger = logging.getLogger(__name__)


class DataMigrationManager:
    """Manages data migration for schema enhancements"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()

        # Migration statistics
        self.migration_stats = {
            "properties_updated": 0,
            "leads_updated": 0,
            "clients_updated": 0,
            "sample_data_created": 0,
            "errors": [],
        }

    def run_migration(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run complete data migration"""
        logger.info("🚀 Starting data migration for schema enhancement")

        try:
            if not dry_run:
                # 1. Migrate existing properties data
                self._migrate_properties_data()

                # 2. Migrate existing leads data
                self._migrate_leads_data()

                # 3. Migrate existing clients data
                self._migrate_clients_data()

                # 4. Create sample market data
                self._create_sample_market_data()

                # 5. Create sample neighborhood profiles
                self._create_sample_neighborhood_profiles()

                # 6. Create sample transactions
                self._create_sample_transactions()

                # 7. Update statistics
                self._update_database_statistics()

            logger.info("✅ Data migration completed successfully")
            return {
                "success": True,
                "dry_run": dry_run,
                "statistics": self.migration_stats,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Data migration failed: {e}")
            self.migration_stats["errors"].append(str(e))
            return {
                "success": False,
                "error": str(e),
                "statistics": self.migration_stats,
                "timestamp": datetime.now().isoformat(),
            }

    def _migrate_properties_data(self):
        """Migrate existing properties data to new schema"""
        logger.info("📊 Migrating properties data...")

        with self.engine.connect() as conn:
            # Update price field to price_aed
            result = conn.execute(
                text(
                    """
                UPDATE properties 
                SET price_aed = price 
                WHERE price_aed IS NULL AND price IS NOT NULL
            """
                )
            )

            # Set default listing status for existing properties
            result = conn.execute(
                text(
                    """
                UPDATE properties 
                SET listing_status = 'live' 
                WHERE listing_status IS NULL
            """
                )
            )

            # Set default agent_id to 1 if not set (assuming admin user exists)
            result = conn.execute(
                text(
                    """
                UPDATE properties 
                SET agent_id = 1 
                WHERE agent_id IS NULL
            """
                )
            )

            # Add sample features for existing properties
            result = conn.execute(
                text(
                    """
                UPDATE properties 
                SET features = '{"amenities": ["parking", "balcony", "gym"], "furnishing": "semi_furnished", "view": "city_view"}'::jsonb
                WHERE features = '{}'::jsonb OR features IS NULL
            """
                )
            )

            # Add sample neighborhood data
            result = conn.execute(
                text(
                    """
                UPDATE properties 
                SET neighborhood_data = '{"area_type": "residential", "nearby_amenities": ["schools", "hospitals", "shopping"], "transportation": "metro_accessible"}'::jsonb
                WHERE neighborhood_data = '{}'::jsonb OR neighborhood_data IS NULL
            """
                )
            )

            conn.commit()

            # Count updated properties
            result = conn.execute(
                text("SELECT COUNT(*) FROM properties WHERE price_aed IS NOT NULL")
            )
            self.migration_stats["properties_updated"] = result.fetchone()[0]

            logger.info(
                f"✅ Updated {self.migration_stats['properties_updated']} properties"
            )

    def _migrate_leads_data(self):
        """Migrate existing leads data to new schema"""
        logger.info("👥 Migrating leads data...")

        with self.engine.connect() as conn:
            # Check if leads table exists
            result = conn.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'leads'
                )
            """
                )
            )
            leads_table_exists = result.fetchone()[0]

            if not leads_table_exists:
                logger.info("⚠️ Leads table does not exist, skipping leads migration")
                self.migration_stats["leads_updated"] = 0
                return

            # Set default nurture status
            result = conn.execute(
                text(
                    """
                UPDATE leads 
                SET nurture_status = 'new' 
                WHERE nurture_status IS NULL
            """
                )
            )

            # Set assigned_agent_id to agent_id if not set
            result = conn.execute(
                text(
                    """
                UPDATE leads 
                SET assigned_agent_id = agent_id 
                WHERE assigned_agent_id IS NULL AND agent_id IS NOT NULL
            """
                )
            )

            # Set last_contacted_at based on created_at
            result = conn.execute(
                text(
                    """
                UPDATE leads 
                SET last_contacted_at = created_at 
                WHERE last_contacted_at IS NULL
            """
                )
            )

            # Set next_follow_up_at (7 days from last contact)
            result = conn.execute(
                text(
                    """
                UPDATE leads 
                SET next_follow_up_at = last_contacted_at + INTERVAL '7 days' 
                WHERE next_follow_up_at IS NULL
            """
                )
            )

            # Calculate lead scores based on budget and contact info
            result = conn.execute(
                text(
                    """
                UPDATE leads 
                SET lead_score = CASE 
                    WHEN email IS NOT NULL AND phone IS NOT NULL AND budget_max > 1000000 THEN 80
                    WHEN email IS NOT NULL AND phone IS NOT NULL AND budget_max > 500000 THEN 70
                    WHEN email IS NOT NULL OR phone IS NOT NULL THEN 50
                    ELSE 30
                END
                WHERE lead_score = 0
            """
                )
            )

            # Add sample source details
            result = conn.execute(
                text(
                    """
                UPDATE leads 
                SET source_details = '{"campaign": "website", "medium": "organic", "content": "homepage"}'::jsonb
                WHERE source_details = '{}'::jsonb OR source_details IS NULL
            """
                )
            )

            conn.commit()

            # Count updated leads
            result = conn.execute(
                text("SELECT COUNT(*) FROM leads WHERE nurture_status IS NOT NULL")
            )
            self.migration_stats["leads_updated"] = result.fetchone()[0]

            logger.info(f"✅ Updated {self.migration_stats['leads_updated']} leads")

    def _migrate_clients_data(self):
        """Migrate existing clients data to new schema"""
        logger.info("🏢 Migrating clients data...")

        with self.engine.connect() as conn:
            # Check if clients table exists
            result = conn.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'clients'
                )
            """
                )
            )
            clients_table_exists = result.fetchone()[0]

            if not clients_table_exists:
                logger.info(
                    "⚠️ Clients table does not exist, skipping clients migration"
                )
                self.migration_stats["clients_updated"] = 0
                return

            # Set default client type
            result = conn.execute(
                text(
                    """
                UPDATE clients 
                SET client_type = 'buyer' 
                WHERE client_type IS NULL
            """
                )
            )

            # Set default client status
            result = conn.execute(
                text(
                    """
                UPDATE clients 
                SET client_status = 'active' 
                WHERE client_status IS NULL
            """
                )
            )

            # Set relationship start date to created_at
            result = conn.execute(
                text(
                    """
                UPDATE clients 
                SET relationship_start_date = created_at::date 
                WHERE relationship_start_date IS NULL
            """
                )
            )

            # Add sample preferences
            result = conn.execute(
                text(
                    """
                UPDATE clients 
                SET preferences = '{"communication": "email", "language": "en", "timezone": "Asia/Dubai"}'::jsonb
                WHERE preferences = '{}'::jsonb OR preferences IS NULL
            """
                )
            )

            conn.commit()

            # Count updated clients
            result = conn.execute(
                text("SELECT COUNT(*) FROM clients WHERE client_type IS NOT NULL")
            )
            self.migration_stats["clients_updated"] = result.fetchone()[0]

            logger.info(f"✅ Updated {self.migration_stats['clients_updated']} clients")

    def _create_sample_market_data(self):
        """Create sample market data for Dubai areas"""
        logger.info("📈 Creating sample market data...")

        dubai_areas = [
            "Dubai Marina",
            "Palm Jumeirah",
            "Downtown Dubai",
            "Jumeirah",
            "Business Bay",
            "DIFC",
            "JBR",
            "Arabian Ranches",
            "Emirates Hills",
            "The Springs",
            "Discovery Gardens",
            "International City",
            "Dubai Silicon Oasis",
            "Dubai Sports City",
            "Dubai Investment Park",
            "Dubai Production City",
            "Dubai Studio City",
            "Dubai Media City",
        ]

        property_types = ["apartment", "villa", "townhouse", "penthouse", "studio"]
        market_trends = ["rising", "stable", "declining"]

        with self.engine.connect() as conn:
            for area in dubai_areas:
                for prop_type in property_types:
                    # Generate realistic market data
                    base_price = self._get_base_price(area, prop_type)
                    price_per_sqft = base_price * random.uniform(0.8, 1.2)
                    market_trend = random.choice(market_trends)

                    # Insert market data
                    conn.execute(
                        text(
                            """
                        INSERT INTO market_data (area, property_type, avg_price, price_per_sqft, market_trend, data_date, source)
                        VALUES (:area, :prop_type, :avg_price, :price_per_sqft, :market_trend, :data_date, 'DLD')
                        ON CONFLICT (area, property_type, data_date) DO NOTHING
                    """
                        ),
                        {
                            "area": area,
                            "prop_type": prop_type,
                            "avg_price": base_price,
                            "price_per_sqft": price_per_sqft,
                            "market_trend": market_trend,
                            "data_date": datetime.now().date(),
                        },
                    )

            conn.commit()
            self.migration_stats["sample_data_created"] += len(dubai_areas) * len(
                property_types
            )
            logger.info(
                f"✅ Created market data for {len(dubai_areas)} areas and {len(property_types)} property types"
            )

    def _create_sample_neighborhood_profiles(self):
        """Create sample neighborhood profiles for Dubai areas"""
        logger.info("🏘️ Creating sample neighborhood profiles...")

        neighborhood_data = [
            {
                "area_name": "Dubai Marina",
                "amenities": {
                    "beach": True,
                    "marina": True,
                    "restaurants": True,
                    "shopping": True,
                    "gym": True,
                },
                "demographics": {"expat_ratio": 0.85, "average_age": 32.5},
                "transportation_score": 9,
                "safety_rating": 8,
                "investment_potential": "high",
                "average_rental_yield": 6.5,
                "population_density": 12000,
                "family_friendly_score": 7,
                "nightlife_score": 9,
                "shopping_score": 9,
            },
            {
                "area_name": "Palm Jumeirah",
                "amenities": {
                    "beach": True,
                    "luxury_resorts": True,
                    "restaurants": True,
                    "spa": True,
                },
                "demographics": {"expat_ratio": 0.90, "average_age": 35.2},
                "transportation_score": 7,
                "safety_rating": 9,
                "investment_potential": "high",
                "average_rental_yield": 5.8,
                "population_density": 8000,
                "family_friendly_score": 8,
                "nightlife_score": 8,
                "shopping_score": 7,
            },
            {
                "area_name": "Downtown Dubai",
                "amenities": {
                    "burj_khalifa": True,
                    "dubai_mall": True,
                    "restaurants": True,
                    "entertainment": True,
                },
                "demographics": {"expat_ratio": 0.80, "average_age": 33.8},
                "transportation_score": 10,
                "safety_rating": 9,
                "investment_potential": "high",
                "average_rental_yield": 6.2,
                "population_density": 15000,
                "family_friendly_score": 6,
                "nightlife_score": 9,
                "shopping_score": 10,
            },
            {
                "area_name": "Jumeirah",
                "amenities": {
                    "beach": True,
                    "parks": True,
                    "schools": True,
                    "hospitals": True,
                },
                "demographics": {"expat_ratio": 0.70, "average_age": 38.5},
                "transportation_score": 8,
                "safety_rating": 9,
                "investment_potential": "medium",
                "average_rental_yield": 5.5,
                "population_density": 6000,
                "family_friendly_score": 9,
                "nightlife_score": 6,
                "shopping_score": 7,
            },
            {
                "area_name": "Business Bay",
                "amenities": {
                    "business_district": True,
                    "restaurants": True,
                    "gym": True,
                    "shopping": True,
                },
                "demographics": {"expat_ratio": 0.75, "average_age": 31.2},
                "transportation_score": 9,
                "safety_rating": 8,
                "investment_potential": "high",
                "average_rental_yield": 6.8,
                "population_density": 18000,
                "family_friendly_score": 5,
                "nightlife_score": 7,
                "shopping_score": 8,
            },
        ]

        with self.engine.connect() as conn:
            for neighborhood in neighborhood_data:
                # Convert dictionaries to JSON strings for JSONB columns
                neighborhood_copy = neighborhood.copy()
                neighborhood_copy["amenities"] = json.dumps(neighborhood["amenities"])
                neighborhood_copy["demographics"] = json.dumps(
                    neighborhood["demographics"]
                )

                conn.execute(
                    text(
                        """
                    INSERT INTO neighborhood_profiles (
                        area_name, amenities, demographics, transportation_score, safety_rating,
                        investment_potential, average_rental_yield, population_density,
                        family_friendly_score, nightlife_score, shopping_score
                    ) VALUES (
                        :area_name, :amenities, :demographics, :transportation_score, :safety_rating,
                        :investment_potential, :average_rental_yield, :population_density,
                        :family_friendly_score, :nightlife_score, :shopping_score
                    ) ON CONFLICT (area_name) DO NOTHING
                """
                    ),
                    neighborhood_copy,
                )

            conn.commit()
            self.migration_stats["sample_data_created"] += len(neighborhood_data)
            logger.info(f"✅ Created {len(neighborhood_data)} neighborhood profiles")

    def _create_sample_transactions(self):
        """Create sample transactions for existing properties and clients"""
        logger.info("💰 Creating sample transactions...")

        with self.engine.connect() as conn:
            # Get existing properties and clients
            properties_result = conn.execute(
                text(
                    "SELECT id, price_aed, agent_id FROM properties WHERE price_aed IS NOT NULL LIMIT 10"
                )
            )
            properties = properties_result.fetchall()

            clients_result = conn.execute(text("SELECT id FROM clients LIMIT 20"))
            clients = clients_result.fetchall()

            if not properties or not clients:
                logger.warning(
                    "⚠️ No properties or clients found for transaction creation"
                )
                return

            transaction_types = ["sale", "rental", "lease"]
            transaction_statuses = ["completed", "in_progress", "pending"]

            for i, property_row in enumerate(properties):
                if i >= len(clients):
                    break

                property_id, price_aed, agent_id = property_row
                client_id = clients[i % len(clients)][0]

                transaction_type = random.choice(transaction_types)
                transaction_status = random.choice(transaction_statuses)

                # Calculate transaction values
                if transaction_type == "sale":
                    offer_price = float(price_aed) * random.uniform(0.95, 1.05)
                    final_price = offer_price * random.uniform(0.98, 1.02)
                else:  # rental or lease
                    offer_price = (
                        float(price_aed) * 0.05 * random.uniform(0.8, 1.2)
                    )  # 5% of property value
                    final_price = offer_price

                commission_rate = random.uniform(2.0, 4.0)
                commission_amount = final_price * (commission_rate / 100)

                # Insert transaction
                conn.execute(
                    text(
                        """
                    INSERT INTO transactions (
                        property_id, buyer_id, agent_id, transaction_type, transaction_status,
                        offer_price, final_price, commission_rate, commission_amount,
                        transaction_date, closing_date
                    ) VALUES (
                        :property_id, :buyer_id, :agent_id, :transaction_type, :transaction_status,
                        :offer_price, :final_price, :commission_rate, :commission_amount,
                        :transaction_date, :closing_date
                    )
                """
                    ),
                    {
                        "property_id": property_id,
                        "buyer_id": client_id,
                        "agent_id": agent_id,
                        "transaction_type": transaction_type,
                        "transaction_status": transaction_status,
                        "offer_price": offer_price,
                        "final_price": final_price,
                        "commission_rate": commission_rate,
                        "commission_amount": commission_amount,
                        "transaction_date": datetime.now()
                        - timedelta(days=random.randint(1, 30)),
                        "closing_date": datetime.now()
                        + timedelta(days=random.randint(1, 60))
                        if transaction_status == "in_progress"
                        else None,
                    },
                )

            conn.commit()
            self.migration_stats["sample_data_created"] += len(properties)
            logger.info(f"✅ Created {len(properties)} sample transactions")

    def _get_base_price(self, area: str, property_type: str) -> float:
        """Get base price for area and property type"""
        base_prices = {
            "Dubai Marina": {
                "apartment": 1200000,
                "villa": 3500000,
                "townhouse": 2800000,
                "penthouse": 5000000,
                "studio": 600000,
            },
            "Palm Jumeirah": {
                "apartment": 1500000,
                "villa": 4500000,
                "townhouse": 3500000,
                "penthouse": 8000000,
                "studio": 800000,
            },
            "Downtown Dubai": {
                "apartment": 1800000,
                "villa": 4000000,
                "townhouse": 3200000,
                "penthouse": 6000000,
                "studio": 700000,
            },
            "Jumeirah": {
                "apartment": 1000000,
                "villa": 3000000,
                "townhouse": 2500000,
                "penthouse": 4000000,
                "studio": 500000,
            },
            "Business Bay": {
                "apartment": 1100000,
                "villa": 3200000,
                "townhouse": 2600000,
                "penthouse": 4500000,
                "studio": 550000,
            },
        }

        return base_prices.get(area, {}).get(property_type, 1000000)

    def _update_database_statistics(self):
        """Update database statistics after migration"""
        logger.info("📊 Updating database statistics...")

        with self.engine.connect() as conn:
            conn.execute(text("ANALYZE"))
            conn.commit()

        logger.info("✅ Database statistics updated")

    def get_migration_report(self) -> Dict[str, Any]:
        """Get detailed migration report"""
        with self.engine.connect() as conn:
            # Get table counts
            tables = [
                "properties",
                "leads",
                "clients",
                "market_data",
                "neighborhood_profiles",
                "transactions",
            ]
            table_counts = {}

            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    table_counts[table] = result.fetchone()[0]
                except Exception as e:
                    table_counts[table] = f"Error: {e}"

            return {
                "migration_statistics": self.migration_stats,
                "table_counts": table_counts,
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """Main function for running data migration"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Data Migration for Schema Enhancement"
    )
    parser.add_argument("--database-url", required=True, help="Database connection URL")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate migration report"
    )

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run migration
    migration_manager = DataMigrationManager(args.database_url)

    if args.report:
        report = migration_manager.get_migration_report()
        print(f"\n{'='*60}")
        print("MIGRATION REPORT")
        print(f"{'='*60}")
        print(f"Migration Statistics: {report['migration_statistics']}")
        print(f"Table Counts: {report['table_counts']}")
        print(f"Generated at: {report['timestamp']}")
    else:
        results = migration_manager.run_migration(dry_run=args.dry_run)

        print(f"\n{'='*60}")
        print("DATA MIGRATION RESULTS")
        print(f"{'='*60}")
        print(f"Success: {results['success']}")
        print(f"Dry Run: {results['dry_run']}")
        print(f"Statistics: {results['statistics']}")

        if not results["success"]:
            print(f"Error: {results['error']}")


if __name__ == "__main__":
    main()
