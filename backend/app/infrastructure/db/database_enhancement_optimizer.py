#!/usr/bin/env python3
"""
Database Enhancement Optimizer for Dubai Real Estate RAG System
Comprehensive database optimization including schema enhancements and performance improvements
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
import json
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EnhancementResult:
    success: bool
    message: str
    execution_time: float
    details: Dict[str, Any]


class DatabaseEnhancementOptimizer:
    """Comprehensive database enhancement and optimization system"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.metadata = MetaData()

        # Enhancement results tracking
        self.enhancement_results = []

        # Performance metrics
        self.performance_metrics = {
            "start_time": datetime.now(),
            "enhancements_completed": 0,
            "errors_encountered": 0,
            "total_execution_time": 0.0,
        }

    def run_complete_enhancement(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run complete database enhancement process"""
        logger.info("🚀 Starting comprehensive database enhancement")

        start_time = time.time()

        try:
            # 1. Schema Enhancement
            schema_result = self._enhance_database_schema(dry_run)
            self.enhancement_results.append(schema_result)

            # 2. Data Migration
            if not dry_run and schema_result.success:
                migration_result = self._migrate_existing_data()
                self.enhancement_results.append(migration_result)

            # 3. Performance Optimization
            if not dry_run:
                performance_result = self._optimize_performance()
                self.enhancement_results.append(performance_result)

            # 4. Index Creation
            if not dry_run:
                index_result = self._create_enhanced_indexes()
                self.enhancement_results.append(index_result)

            # 5. Data Validation
            if not dry_run:
                validation_result = self._validate_data_integrity()
                self.enhancement_results.append(validation_result)

            # 6. Sample Data Creation
            if not dry_run:
                sample_data_result = self._create_sample_data()
                self.enhancement_results.append(sample_data_result)

            # Calculate total execution time
            total_time = time.time() - start_time
            self.performance_metrics["total_execution_time"] = total_time

            # Determine overall success
            overall_success = all(result.success for result in self.enhancement_results)

            logger.info(f"✅ Database enhancement completed in {total_time:.2f} seconds")

            return {
                "success": overall_success,
                "dry_run": dry_run,
                "execution_time": total_time,
                "enhancement_results": [
                    result.__dict__ for result in self.enhancement_results
                ],
                "performance_metrics": self.performance_metrics,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Database enhancement failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "enhancement_results": [
                    result.__dict__ for result in self.enhancement_results
                ],
                "timestamp": datetime.now().isoformat(),
            }

    def _enhance_database_schema(self, dry_run: bool = False) -> EnhancementResult:
        """Enhance database schema with new tables and fields"""
        start_time = time.time()

        try:
            if dry_run:
                return EnhancementResult(
                    success=True,
                    message="Schema enhancement dry run completed",
                    execution_time=time.time() - start_time,
                    details={
                        "dry_run": True,
                        "changes_planned": "Schema enhancement migration",
                    },
                )

            # Read and execute schema enhancement migration
            migration_file = "backend/migrations/schema_enhancement_migration.sql"

            if os.path.exists(migration_file):
                with open(migration_file, "r") as f:
                    migration_sql = f.read()

                with self.engine.connect() as conn:
                    # Execute migration in chunks to handle large scripts
                    statements = migration_sql.split(";")
                    for statement in statements:
                        statement = statement.strip()
                        if statement and not statement.startswith("--"):
                            try:
                                conn.execute(text(statement))
                            except Exception as e:
                                logger.warning(f"Statement execution warning: {e}")

                    conn.commit()

                self.performance_metrics["enhancements_completed"] += 1

                return EnhancementResult(
                    success=True,
                    message="Database schema enhanced successfully",
                    execution_time=time.time() - start_time,
                    details={
                        "migration_file": migration_file,
                        "statements_executed": len(
                            [
                                s
                                for s in statements
                                if s.strip() and not s.strip().startswith("--")
                            ]
                        ),
                    },
                )
            else:
                raise FileNotFoundError(f"Migration file not found: {migration_file}")

        except Exception as e:
            self.performance_metrics["errors_encountered"] += 1
            logger.error(f"Schema enhancement failed: {e}")
            return EnhancementResult(
                success=False,
                message=f"Schema enhancement failed: {str(e)}",
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    def _migrate_existing_data(self) -> EnhancementResult:
        """Migrate existing data to new schema"""
        start_time = time.time()

        try:
            # Import and run data migration
            from backend.migrations.data_migration_script import DataMigrationManager

            migration_manager = DataMigrationManager(self.engine.url)
            migration_result = migration_manager.run_migration(dry_run=False)

            self.performance_metrics["enhancements_completed"] += 1

            return EnhancementResult(
                success=migration_result["success"],
                message="Data migration completed"
                if migration_result["success"]
                else "Data migration failed",
                execution_time=time.time() - start_time,
                details=migration_result["statistics"],
            )

        except Exception as e:
            self.performance_metrics["errors_encountered"] += 1
            logger.error(f"Data migration failed: {e}")
            return EnhancementResult(
                success=False,
                message=f"Data migration failed: {str(e)}",
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    def _optimize_performance(self) -> EnhancementResult:
        """Optimize database performance"""
        start_time = time.time()

        try:
            with self.engine.connect() as conn:
                # Update statistics
                conn.execute(text("ANALYZE"))

                # Vacuum tables
                conn.execute(text("VACUUM ANALYZE"))

                # Optimize autovacuum settings
                conn.execute(
                    text(
                        """
                    ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;
                    ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.05;
                    ALTER SYSTEM SET autovacuum_vacuum_cost_limit = 2000;
                    ALTER SYSTEM SET autovacuum_vacuum_cost_delay = 20ms;
                """
                    )
                )

                conn.commit()

            self.performance_metrics["enhancements_completed"] += 1

            return EnhancementResult(
                success=True,
                message="Performance optimization completed",
                execution_time=time.time() - start_time,
                details={
                    "statistics_updated": True,
                    "vacuum_completed": True,
                    "autovacuum_optimized": True,
                },
            )

        except Exception as e:
            self.performance_metrics["errors_encountered"] += 1
            logger.error(f"Performance optimization failed: {e}")
            return EnhancementResult(
                success=False,
                message=f"Performance optimization failed: {str(e)}",
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    def _create_enhanced_indexes(self) -> EnhancementResult:
        """Create enhanced indexes for new schema"""
        start_time = time.time()

        try:
            # Import and run index optimization
            from backend.database_index_optimizer import DatabaseIndexOptimizer

            index_optimizer = DatabaseIndexOptimizer(self.engine.url)
            optimization_result = index_optimizer.optimize_database(dry_run=False)

            self.performance_metrics["enhancements_completed"] += 1

            return EnhancementResult(
                success=optimization_result["success"],
                message="Enhanced indexes created successfully"
                if optimization_result["success"]
                else "Index creation failed",
                execution_time=time.time() - start_time,
                details={
                    "indexes_created": len(
                        optimization_result.get("indexes_created", [])
                    ),
                    "indexes_skipped": len(
                        optimization_result.get("indexes_skipped", [])
                    ),
                    "errors": len(optimization_result.get("errors", [])),
                },
            )

        except Exception as e:
            self.performance_metrics["errors_encountered"] += 1
            logger.error(f"Index creation failed: {e}")
            return EnhancementResult(
                success=False,
                message=f"Index creation failed: {str(e)}",
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    def _validate_data_integrity(self) -> EnhancementResult:
        """Validate data integrity after enhancements"""
        start_time = time.time()

        try:
            validation_results = {}

            with self.engine.connect() as conn:
                # Check table counts
                tables = [
                    "properties",
                    "leads",
                    "clients",
                    "market_data",
                    "neighborhood_profiles",
                    "transactions",
                ]

                for table in tables:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.fetchone()[0]
                        validation_results[f"{table}_count"] = count
                    except Exception as e:
                        validation_results[f"{table}_error"] = str(e)

                # Check for data consistency
                # Properties with price_aed
                result = conn.execute(
                    text("SELECT COUNT(*) FROM properties WHERE price_aed IS NOT NULL")
                )
                validation_results["properties_with_price_aed"] = result.fetchone()[0]

                # Leads with nurture_status
                result = conn.execute(
                    text("SELECT COUNT(*) FROM leads WHERE nurture_status IS NOT NULL")
                )
                validation_results["leads_with_nurture_status"] = result.fetchone()[0]

                # Clients with client_type
                result = conn.execute(
                    text("SELECT COUNT(*) FROM clients WHERE client_type IS NOT NULL")
                )
                validation_results["clients_with_client_type"] = result.fetchone()[0]

                # Check foreign key integrity
                result = conn.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM properties p 
                    LEFT JOIN users u ON p.agent_id = u.id 
                    WHERE p.agent_id IS NOT NULL AND u.id IS NULL
                """
                    )
                )
                validation_results["orphaned_property_agents"] = result.fetchone()[0]

            self.performance_metrics["enhancements_completed"] += 1

            return EnhancementResult(
                success=True,
                message="Data integrity validation completed",
                execution_time=time.time() - start_time,
                details=validation_results,
            )

        except Exception as e:
            self.performance_metrics["errors_encountered"] += 1
            logger.error(f"Data validation failed: {e}")
            return EnhancementResult(
                success=False,
                message=f"Data validation failed: {str(e)}",
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    def _create_sample_data(self) -> EnhancementResult:
        """Create sample data for testing and demonstration"""
        start_time = time.time()

        try:
            sample_data_created = 0

            with self.engine.connect() as conn:
                # Create sample properties if none exist
                result = conn.execute(text("SELECT COUNT(*) FROM properties"))
                property_count = result.fetchone()[0]

                if property_count == 0:
                    # Insert sample properties
                    sample_properties = [
                        {
                            "title": "Luxury Apartment in Dubai Marina",
                            "description": "Stunning 2-bedroom apartment with marina views",
                            "property_type": "apartment",
                            "price_aed": 1200000,
                            "location": "Dubai Marina",
                            "area_sqft": 1200,
                            "bedrooms": 2,
                            "bathrooms": 2,
                            "listing_status": "live",
                            "features": '{"amenities": ["parking", "balcony", "gym", "pool"], "furnishing": "semi_furnished", "view": "marina_view"}',
                            "rera_number": "RERA-001",
                            "developer_name": "Emaar Properties",
                        },
                        {
                            "title": "Villa in Palm Jumeirah",
                            "description": "Exclusive 4-bedroom villa with private beach access",
                            "property_type": "villa",
                            "price_aed": 3500000,
                            "location": "Palm Jumeirah",
                            "area_sqft": 3500,
                            "bedrooms": 4,
                            "bathrooms": 5,
                            "listing_status": "live",
                            "features": '{"amenities": ["private_beach", "garden", "pool", "gym"], "furnishing": "fully_furnished", "view": "sea_view"}',
                            "rera_number": "RERA-002",
                            "developer_name": "Nakheel Properties",
                        },
                    ]

                    for prop in sample_properties:
                        conn.execute(
                            text(
                                """
                            INSERT INTO properties (title, description, property_type, price_aed, location, area_sqft, bedrooms, bathrooms, listing_status, features, rera_number, developer_name)
                            VALUES (:title, :description, :property_type, :price_aed, :location, :area_sqft, :bedrooms, :bathrooms, :listing_status, :features, :rera_number, :developer_name)
                        """
                            ),
                            prop,
                        )

                    sample_data_created += len(sample_properties)

                # Create sample leads if none exist
                result = conn.execute(text("SELECT COUNT(*) FROM leads"))
                lead_count = result.fetchone()[0]

                if lead_count == 0:
                    sample_leads = [
                        {
                            "name": "John Smith",
                            "email": "john.smith@email.com",
                            "phone": "+971501234567",
                            "status": "new",
                            "nurture_status": "hot",
                            "budget_min": 1000000,
                            "budget_max": 1500000,
                            "property_type": "apartment",
                            "preferred_areas": '["Dubai Marina", "Downtown Dubai"]',
                            "lead_score": 85,
                            "urgency_level": "high",
                        },
                        {
                            "name": "Sarah Johnson",
                            "email": "sarah.johnson@email.com",
                            "phone": "+971507654321",
                            "status": "new",
                            "nurture_status": "warm",
                            "budget_min": 2000000,
                            "budget_max": 3000000,
                            "property_type": "villa",
                            "preferred_areas": '["Palm Jumeirah", "Jumeirah"]',
                            "lead_score": 70,
                            "urgency_level": "normal",
                        },
                    ]

                    for lead in sample_leads:
                        conn.execute(
                            text(
                                """
                            INSERT INTO leads (name, email, phone, status, nurture_status, budget_min, budget_max, property_type, preferred_areas, lead_score, urgency_level)
                            VALUES (:name, :email, :phone, :status, :nurture_status, :budget_min, :budget_max, :property_type, :preferred_areas, :lead_score, :urgency_level)
                        """
                            ),
                            lead,
                        )

                    sample_data_created += len(sample_leads)

                conn.commit()

            self.performance_metrics["enhancements_completed"] += 1

            return EnhancementResult(
                success=True,
                message="Sample data creation completed",
                execution_time=time.time() - start_time,
                details={
                    "sample_data_created": sample_data_created,
                    "properties_created": property_count == 0,
                    "leads_created": lead_count == 0,
                },
            )

        except Exception as e:
            self.performance_metrics["errors_encountered"] += 1
            logger.error(f"Sample data creation failed: {e}")
            return EnhancementResult(
                success=False,
                message=f"Sample data creation failed: {str(e)}",
                execution_time=time.time() - start_time,
                details={"error": str(e)},
            )

    def get_enhancement_report(self) -> Dict[str, Any]:
        """Get comprehensive enhancement report"""
        return {
            "enhancement_results": [
                result.__dict__ for result in self.enhancement_results
            ],
            "performance_metrics": self.performance_metrics,
            "overall_success": all(
                result.success for result in self.enhancement_results
            ),
            "total_enhancements": len(self.enhancement_results),
            "successful_enhancements": sum(
                1 for result in self.enhancement_results if result.success
            ),
            "failed_enhancements": sum(
                1 for result in self.enhancement_results if not result.success
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def export_enhancement_report(self, filepath: str):
        """Export enhancement report to JSON file"""
        try:
            report = self.get_enhancement_report()

            with open(filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"✅ Enhancement report exported to {filepath}")

        except Exception as e:
            logger.error(f"Error exporting enhancement report: {e}")


def main():
    """Main function for running database enhancement"""
    import argparse

    parser = argparse.ArgumentParser(description="Database Enhancement Optimizer")
    parser.add_argument("--database-url", required=True, help="Database connection URL")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--export-report", help="Export enhancement report to file")

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run enhancement
    optimizer = DatabaseEnhancementOptimizer(args.database_url)
    results = optimizer.run_complete_enhancement(dry_run=args.dry_run)

    # Print results
    print(f"\n{'='*60}")
    print("DATABASE ENHANCEMENT RESULTS")
    print(f"{'='*60}")
    print(f"Success: {results.get('success', False)}")
    print(f"Execution Time: {results.get('execution_time', 0):.2f} seconds")
    print(f"Enhancements Completed: {len(results.get('enhancement_results', []))}")

    for i, result in enumerate(results.get("enhancement_results", []), 1):
        status = "✅" if result["success"] else "❌"
        print(f"{status} {i}. {result['message']} ({result['execution_time']:.2f}s)")

    # Export report if requested
    if args.export_report:
        optimizer.export_enhancement_report(args.export_report)


if __name__ == "__main__":
    main()
