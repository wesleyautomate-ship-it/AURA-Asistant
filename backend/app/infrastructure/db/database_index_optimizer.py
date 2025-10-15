#!/usr/bin/env python3
"""
Database Index Optimizer for Dubai Real Estate RAG System
Automatically creates and manages database indexes for optimal performance
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
class IndexDefinition:
    name: str
    table: str
    columns: List[str]
    index_type: str  # 'btree', 'gin', 'gist', 'hash'
    condition: Optional[str] = None
    priority: int = 1  # 1=high, 2=medium, 3=low


@dataclass
class IndexPerformance:
    index_name: str
    table_name: str
    index_size: str
    index_scans: int
    tuples_read: int
    tuples_fetched: int
    usage_efficiency: float


class DatabaseIndexOptimizer:
    """Database index optimization and management system"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.metadata = MetaData()

        # Define high-priority indexes for real estate system
        self.index_definitions = [
            # High Priority - Property Search Indexes
            IndexDefinition(
                name="idx_properties_location_type_price",
                table="properties",
                columns=["location", "property_type", "price_aed"],
                index_type="btree",
                condition="listing_status = 'live'",
                priority=1,
            ),
            IndexDefinition(
                name="idx_properties_price_bedrooms",
                table="properties",
                columns=["price_aed", "bedrooms"],
                index_type="btree",
                condition="listing_status = 'live' AND price_aed > 0",
                priority=1,
            ),
            IndexDefinition(
                name="idx_properties_area_type",
                table="properties",
                columns=["area_sqft", "property_type"],
                index_type="btree",
                condition="listing_status = 'live'",
                priority=1,
            ),
            # High Priority - Lead Management Indexes
            IndexDefinition(
                name="idx_leads_agent_status",
                table="leads",
                columns=["assigned_agent_id", "nurture_status"],
                index_type="btree",
                priority=1,
            ),
            IndexDefinition(
                name="idx_leads_status_created",
                table="leads",
                columns=["status", "created_at"],
                index_type="btree",
                priority=1,
            ),
            # High Priority - Conversation Indexes
            IndexDefinition(
                name="idx_conversations_user_active_created",
                table="conversations",
                columns=["user_id", "is_active", "created_at"],
                index_type="btree",
                priority=1,
            ),
            IndexDefinition(
                name="idx_messages_conversation_timestamp",
                table="messages",
                columns=["conversation_id", "created_at"],
                index_type="btree",
                priority=1,
            ),
            # High Priority - ML Analytics Indexes
            IndexDefinition(
                name="idx_ml_analytics_user_period_current",
                table="ml_performance_analytics",
                columns=["user_id", "period", "is_current"],
                index_type="btree",
                priority=1,
            ),
            IndexDefinition(
                name="idx_ml_notifications_user_status_priority",
                table="ml_smart_notifications",
                columns=["user_id", "status", "priority"],
                index_type="btree",
                priority=1,
            ),
            IndexDefinition(
                name="idx_ml_market_location_type_period",
                table="ml_market_intelligence",
                columns=["location", "property_type", "period"],
                index_type="btree",
                priority=1,
            ),
            # Medium Priority - JSONB GIN Indexes
            IndexDefinition(
                name="idx_properties_features_gin",
                table="properties",
                columns=["features"],
                index_type="gin",
                priority=2,
            ),
            IndexDefinition(
                name="idx_ml_reports_content_gin",
                table="ml_automated_reports",
                columns=["content"],
                index_type="gin",
                priority=2,
            ),
            IndexDefinition(
                name="idx_ml_analytics_metrics_gin",
                table="ml_performance_analytics",
                columns=["metrics"],
                index_type="gin",
                priority=2,
            ),
            IndexDefinition(
                name="idx_ml_market_trends_gin",
                table="ml_market_intelligence",
                columns=["trend_indicators"],
                index_type="gin",
                priority=2,
            ),
            IndexDefinition(
                name="idx_market_data_context_gin",
                table="market_data",
                columns=["market_context"],
                index_type="gin",
                priority=2,
            ),
            IndexDefinition(
                name="idx_neighborhood_amenities_gin",
                table="neighborhood_profiles",
                columns=["amenities"],
                index_type="gin",
                priority=2,
            ),
            # Medium Priority - User and Session Indexes
            IndexDefinition(
                name="idx_users_role_active",
                table="users",
                columns=["role", "is_active"],
                index_type="btree",
                priority=2,
            ),
            IndexDefinition(
                name="idx_user_sessions_expires",
                table="user_sessions",
                columns=["expires_at"],
                index_type="btree",
                priority=2,
            ),
            # Medium Priority - Entity and Context Indexes
            IndexDefinition(
                name="idx_entity_detections_type_confidence",
                table="entity_detections",
                columns=["entity_type", "confidence_score"],
                index_type="btree",
                priority=2,
            ),
            IndexDefinition(
                name="idx_context_cache_user_session",
                table="context_cache",
                columns=["user_id", "session_id"],
                index_type="btree",
                priority=2,
            ),
            # Low Priority - Maintenance Indexes
            IndexDefinition(
                name="idx_ml_insights_log_created_at",
                table="ml_insights_log",
                columns=["created_at"],
                index_type="btree",
                priority=3,
            ),
            IndexDefinition(
                name="idx_ml_analytics_period_start_retention",
                table="ml_performance_analytics",
                columns=["period_start"],
                index_type="btree",
                condition="is_current = false",
                priority=3,
            ),
        ]

    def optimize_database(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run complete database optimization"""
        logger.info("🚀 Starting database index optimization")

        results = {
            "start_time": datetime.now().isoformat(),
            "dry_run": dry_run,
            "indexes_created": [],
            "indexes_skipped": [],
            "errors": [],
            "performance_impact": {},
        }

        try:
            # Get current index status
            current_indexes = self._get_current_indexes()
            results["current_indexes"] = len(current_indexes)

            # Create indexes by priority
            for priority in [1, 2, 3]:
                priority_indexes = [
                    idx for idx in self.index_definitions if idx.priority == priority
                ]
                logger.info(
                    f"Creating {priority} priority indexes: {len(priority_indexes)} indexes"
                )

                for index_def in priority_indexes:
                    try:
                        if self._index_exists(index_def.name, current_indexes):
                            logger.info(
                                f"⏭️ Index {index_def.name} already exists, skipping"
                            )
                            results["indexes_skipped"].append(
                                {"name": index_def.name, "reason": "already_exists"}
                            )
                            continue

                        if not dry_run:
                            self._create_index(index_def)

                        results["indexes_created"].append(
                            {
                                "name": index_def.name,
                                "table": index_def.table,
                                "columns": index_def.columns,
                                "type": index_def.index_type,
                                "priority": index_def.priority,
                            }
                        )

                        logger.info(f"✅ Created index: {index_def.name}")

                    except Exception as e:
                        error_msg = f"Failed to create index {index_def.name}: {str(e)}"
                        logger.error(error_msg)
                        results["errors"].append(
                            {"index_name": index_def.name, "error": str(e)}
                        )

            # Update statistics
            if not dry_run:
                self._update_statistics()

            # Get performance metrics
            results["performance_impact"] = self._get_performance_impact()

            results["end_time"] = datetime.now().isoformat()
            results["success"] = len(results["errors"]) == 0

            logger.info(
                f"✅ Database optimization completed. Created {len(results['indexes_created'])} indexes"
            )

        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
            results["error"] = str(e)
            results["success"] = False

        return results

    def _get_current_indexes(self) -> List[Dict[str, Any]]:
        """Get list of current database indexes"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        indexdef
                    FROM pg_indexes 
                    WHERE schemaname = 'public'
                    ORDER BY tablename, indexname
                """
                    )
                )

                indexes = []
                for row in result:
                    indexes.append(
                        {
                            "schema": row.schemaname,
                            "table": row.tablename,
                            "name": row.indexname,
                            "definition": row.indexdef,
                        }
                    )

                return indexes

        except Exception as e:
            logger.error(f"Error getting current indexes: {e}")
            return []

    def _index_exists(
        self, index_name: str, current_indexes: List[Dict[str, Any]]
    ) -> bool:
        """Check if index already exists"""
        return any(idx["name"] == index_name for idx in current_indexes)

    def _create_index(self, index_def: IndexDefinition):
        """Create a database index"""
        try:
            # Build CREATE INDEX statement
            columns_str = ", ".join(index_def.columns)

            if index_def.index_type == "gin":
                index_sql = f"CREATE INDEX IF NOT EXISTS {index_def.name} ON {index_def.table} USING GIN ({columns_str})"
            elif index_def.index_type == "gist":
                index_sql = f"CREATE INDEX IF NOT EXISTS {index_def.name} ON {index_def.table} USING GIST ({columns_str})"
            elif index_def.index_type == "hash":
                index_sql = f"CREATE INDEX IF NOT EXISTS {index_def.name} ON {index_def.table} USING HASH ({columns_str})"
            else:  # btree (default)
                index_sql = f"CREATE INDEX IF NOT EXISTS {index_def.name} ON {index_def.table} ({columns_str})"

            # Add WHERE condition if specified
            if index_def.condition:
                index_sql += f" WHERE {index_def.condition}"

            # Execute the index creation
            with self.engine.connect() as conn:
                conn.execute(text(index_sql))
                conn.commit()

            logger.debug(f"Created index: {index_sql}")

        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error creating index {index_def.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating index {index_def.name}: {e}")
            raise

    def _update_statistics(self):
        """Update database statistics for query planner"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("ANALYZE"))
                conn.commit()
            logger.info("✅ Database statistics updated")
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")

    def _get_performance_impact(self) -> Dict[str, Any]:
        """Get performance impact metrics"""
        try:
            with self.engine.connect() as conn:
                # Get index usage statistics
                result = conn.execute(
                    text(
                        """
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    WHERE schemaname = 'public'
                    ORDER BY idx_scan DESC
                """
                    )
                )

                index_stats = []
                for row in result:
                    efficiency = 0
                    if row.idx_tup_read > 0:
                        efficiency = (row.idx_tup_fetch / row.idx_tup_read) * 100

                    index_stats.append(
                        {
                            "table": row.tablename,
                            "index": row.indexname,
                            "scans": row.idx_scan,
                            "tuples_read": row.idx_tup_read,
                            "tuples_fetched": row.idx_tup_fetch,
                            "efficiency": round(efficiency, 2),
                        }
                    )

                # Get table statistics
                result = conn.execute(
                    text(
                        """
                    SELECT 
                        schemaname,
                        tablename,
                        seq_scan,
                        seq_tup_read,
                        idx_scan,
                        idx_tup_fetch,
                        n_live_tup,
                        n_dead_tup
                    FROM pg_stat_user_tables 
                    WHERE schemaname = 'public'
                    ORDER BY n_live_tup DESC
                """
                    )
                )

                table_stats = []
                for row in result:
                    table_stats.append(
                        {
                            "table": row.tablename,
                            "sequential_scans": row.seq_scan,
                            "sequential_tuples_read": row.seq_tup_read,
                            "index_scans": row.idx_scan,
                            "index_tuples_fetched": row.idx_tup_fetch,
                            "live_tuples": row.n_live_tup,
                            "dead_tuples": row.n_dead_tup,
                        }
                    )

                return {
                    "index_statistics": index_stats,
                    "table_statistics": table_stats,
                    "total_indexes": len(index_stats),
                    "total_tables": len(table_stats),
                }

        except Exception as e:
            logger.error(f"Error getting performance impact: {e}")
            return {"error": str(e)}

    def analyze_query_performance(self, query: str) -> Dict[str, Any]:
        """Analyze performance of a specific query"""
        try:
            with self.engine.connect() as conn:
                # Get query execution plan
                explain_result = conn.execute(
                    text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
                )
                plan = explain_result.fetchone()[0]

                return {
                    "query": query,
                    "execution_plan": plan,
                    "analysis_timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {"error": str(e)}

    def get_index_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for additional indexes based on query patterns"""
        recommendations = []

        try:
            with self.engine.connect() as conn:
                # Check for tables with high sequential scan ratios
                result = conn.execute(
                    text(
                        """
                    SELECT 
                        schemaname,
                        tablename,
                        seq_scan,
                        seq_tup_read,
                        idx_scan,
                        idx_tup_fetch,
                        n_live_tup
                    FROM pg_stat_user_tables 
                    WHERE schemaname = 'public'
                    AND seq_scan > idx_scan * 2
                    AND n_live_tup > 1000
                    ORDER BY seq_tup_read DESC
                """
                    )
                )

                for row in result:
                    if row.seq_scan > 0:
                        recommendations.append(
                            {
                                "type": "sequential_scan_optimization",
                                "table": row.tablename,
                                "priority": "high",
                                "reason": f"High sequential scan ratio: {row.seq_scan} seq scans vs {row.idx_scan} index scans",
                                "suggestion": f"Consider adding indexes for frequently queried columns in {row.tablename}",
                            }
                        )

                # Check for unused indexes
                result = conn.execute(
                    text(
                        """
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan
                    FROM pg_stat_user_indexes 
                    WHERE schemaname = 'public'
                    AND idx_scan = 0
                    ORDER BY tablename, indexname
                """
                    )
                )

                for row in result:
                    recommendations.append(
                        {
                            "type": "unused_index",
                            "table": row.tablename,
                            "index": row.indexname,
                            "priority": "low",
                            "reason": "Index has never been used",
                            "suggestion": f"Consider dropping unused index {row.indexname} on {row.tablename}",
                        }
                    )

        except Exception as e:
            logger.error(f"Error getting index recommendations: {e}")

        return recommendations

    def export_optimization_report(self, filepath: str, results: Dict[str, Any]):
        """Export optimization results to JSON file"""
        try:
            report = {
                "optimization_report": results,
                "recommendations": self.get_index_recommendations(),
                "generated_at": datetime.now().isoformat(),
                "system_info": {
                    "database_url": self.engine.url.database,
                    "host": self.engine.url.host,
                    "port": self.engine.url.port,
                },
            }

            with open(filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"✅ Optimization report exported to {filepath}")

        except Exception as e:
            logger.error(f"Error exporting optimization report: {e}")


def main():
    """Main function for running database optimization"""
    import argparse

    parser = argparse.ArgumentParser(description="Database Index Optimizer")
    parser.add_argument("--database-url", required=True, help="Database connection URL")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--export-report", help="Export optimization report to file")

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run optimization
    optimizer = DatabaseIndexOptimizer(args.database_url)
    results = optimizer.optimize_database(dry_run=args.dry_run)

    # Print results
    print(f"\n{'='*60}")
    print("DATABASE OPTIMIZATION RESULTS")
    print(f"{'='*60}")
    print(f"Success: {results.get('success', False)}")
    print(f"Indexes Created: {len(results.get('indexes_created', []))}")
    print(f"Indexes Skipped: {len(results.get('indexes_skipped', []))}")
    print(f"Errors: {len(results.get('errors', []))}")

    if results.get("errors"):
        print("\nErrors:")
        for error in results["errors"]:
            print(f"  - {error['index_name']}: {error['error']}")

    # Export report if requested
    if args.export_report:
        optimizer.export_optimization_report(args.export_report, results)


if __name__ == "__main__":
    main()
