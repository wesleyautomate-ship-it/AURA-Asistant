#!/usr/bin/env python3
"""
Database Enhancement Router for Dubai Real Estate RAG System
Provides API endpoints for database schema enhancement and optimization
"""

import os
import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime

from database_enhancement_optimizer import DatabaseEnhancementOptimizer
from database_index_optimizer import DatabaseIndexOptimizer
from migrations.data_migration_script import DataMigrationManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/database", tags=["Database Enhancement"])

# Pydantic models
class DatabaseEnhancementRequest(BaseModel):
    dry_run: bool = Field(
        False, description="Show what would be done without making changes"
    )
    include_sample_data: bool = Field(True, description="Include sample data creation")


class DatabaseEnhancementResponse(BaseModel):
    success: bool
    execution_time: float
    enhancement_results: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    timestamp: str


class DataMigrationRequest(BaseModel):
    dry_run: bool = Field(
        False, description="Show what would be done without making changes"
    )


class DataMigrationResponse(BaseModel):
    success: bool
    statistics: Dict[str, Any]
    timestamp: str


class IndexOptimizationRequest(BaseModel):
    dry_run: bool = Field(
        False, description="Show what would be done without making changes"
    )
    priority: Optional[int] = Field(
        None, ge=1, le=3, description="Priority level (1=high, 2=medium, 3=low)"
    )


class IndexOptimizationResponse(BaseModel):
    success: bool
    indexes_created: List[Dict[str, Any]]
    indexes_skipped: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    performance_impact: Dict[str, Any]
    execution_time: float


class DatabaseStatusResponse(BaseModel):
    schema_status: Dict[str, Any]
    data_status: Dict[str, Any]
    performance_status: Dict[str, Any]
    enhancement_status: Dict[str, Any]
    timestamp: str


# Dependency functions
def get_database_enhancement_optimizer():
    return DatabaseEnhancementOptimizer(database_url=os.getenv("DATABASE_URL"))


def get_database_index_optimizer():
    return DatabaseIndexOptimizer(database_url=os.getenv("DATABASE_URL"))


def get_data_migration_manager():
    return DataMigrationManager(database_url=os.getenv("DATABASE_URL"))


# API Endpoints


@router.post("/enhance", response_model=DatabaseEnhancementResponse)
async def enhance_database(
    request: DatabaseEnhancementRequest,
    background_tasks: BackgroundTasks,
    optimizer=Depends(get_database_enhancement_optimizer),
):
    """Run comprehensive database enhancement including schema updates, data migration, and optimization"""
    try:
        # Run enhancement
        results = optimizer.run_complete_enhancement(dry_run=request.dry_run)

        return DatabaseEnhancementResponse(
            success=results["success"],
            execution_time=results["execution_time"],
            enhancement_results=results["enhancement_results"],
            performance_metrics=results["performance_metrics"],
            timestamp=results["timestamp"],
        )

    except Exception as e:
        logger.error(f"Error in database enhancement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/migrate-data", response_model=DataMigrationResponse)
async def migrate_data(
    request: DataMigrationRequest, migration_manager=Depends(get_data_migration_manager)
):
    """Migrate existing data to enhanced schema"""
    try:
        # Run data migration
        results = migration_manager.run_migration(dry_run=request.dry_run)

        return DataMigrationResponse(
            success=results["success"],
            statistics=results["statistics"],
            timestamp=results["timestamp"],
        )

    except Exception as e:
        logger.error(f"Error in data migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-indexes", response_model=IndexOptimizationResponse)
async def optimize_indexes(
    request: IndexOptimizationRequest, optimizer=Depends(get_database_index_optimizer)
):
    """Optimize database indexes for enhanced schema"""
    try:
        # Run index optimization
        results = optimizer.optimize_database(dry_run=request.dry_run)

        return IndexOptimizationResponse(
            success=results["success"],
            indexes_created=results["indexes_created"],
            indexes_skipped=results["indexes_skipped"],
            errors=results["errors"],
            performance_impact=results["performance_impact"],
            execution_time=results["execution_time"],
        )

    except Exception as e:
        logger.error(f"Error in index optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=DatabaseStatusResponse)
async def get_database_status(
    optimizer=Depends(get_database_enhancement_optimizer),
    index_optimizer=Depends(get_database_index_optimizer),
    migration_manager=Depends(get_data_migration_manager),
):
    """Get comprehensive database status including schema, data, and performance metrics"""
    try:
        # Get schema status
        schema_status = await _get_schema_status()

        # Get data status
        data_status = await _get_data_status()

        # Get performance status
        performance_status = await _get_performance_status()

        # Get enhancement status
        enhancement_status = await _get_enhancement_status(optimizer)

        return DatabaseStatusResponse(
            schema_status=schema_status,
            data_status=data_status,
            performance_status=performance_status,
            enhancement_status=enhancement_status,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/analysis")
async def analyze_schema():
    """Analyze current database schema and provide recommendations"""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(os.getenv("DATABASE_URL"))

        with engine.connect() as conn:
            # Get table information
            tables_result = conn.execute(
                text(
                    """
                SELECT 
                    table_name,
                    table_type,
                    is_insertable_into
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
                )
            )

            tables = [
                {"name": row[0], "type": row[1], "insertable": row[2]}
                for row in tables_result
            ]

            # Get column information
            columns_result = conn.execute(
                text(
                    """
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """
                )
            )

            columns = [
                {
                    "table": row[0],
                    "column": row[1],
                    "type": row[2],
                    "nullable": row[3],
                    "default": row[4],
                }
                for row in columns_result
            ]

            # Get index information
            indexes_result = conn.execute(
                text(
                    """
                SELECT 
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """
                )
            )

            indexes = [
                {"table": row[0], "name": row[1], "definition": row[2]}
                for row in indexes_result
            ]

            # Get foreign key information
            foreign_keys_result = conn.execute(
                text(
                    """
                SELECT 
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.column_name
            """
                )
            )

            foreign_keys = [
                {
                    "table": row[0],
                    "column": row[1],
                    "foreign_table": row[2],
                    "foreign_column": row[3],
                }
                for row in foreign_keys_result
            ]

        return {
            "tables": tables,
            "columns": columns,
            "indexes": indexes,
            "foreign_keys": foreign_keys,
            "analysis_timestamp": datetime.now().isoformat(),
            "recommendations": _generate_schema_recommendations(
                tables, columns, indexes
            ),
        }

    except Exception as e:
        logger.error(f"Error analyzing schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/validation")
async def validate_data_integrity():
    """Validate data integrity across all tables"""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(os.getenv("DATABASE_URL"))
        validation_results = {}

        with engine.connect() as conn:
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

            # Check data consistency
            consistency_checks = [
                (
                    "Properties with price_aed",
                    "SELECT COUNT(*) FROM properties WHERE price_aed IS NOT NULL",
                ),
                (
                    "Leads with nurture_status",
                    "SELECT COUNT(*) FROM leads WHERE nurture_status IS NOT NULL",
                ),
                (
                    "Clients with client_type",
                    "SELECT COUNT(*) FROM clients WHERE client_type IS NOT NULL",
                ),
                (
                    "Orphaned property agents",
                    "SELECT COUNT(*) FROM properties p LEFT JOIN users u ON p.agent_id = u.id WHERE p.agent_id IS NOT NULL AND u.id IS NULL",
                ),
                (
                    "Orphaned lead agents",
                    "SELECT COUNT(*) FROM leads l LEFT JOIN users u ON l.assigned_agent_id = u.id WHERE l.assigned_agent_id IS NOT NULL AND u.id IS NULL",
                ),
            ]

            for check_name, query in consistency_checks:
                try:
                    result = conn.execute(text(query))
                    count = result.fetchone()[0]
                    validation_results[check_name.lower().replace(" ", "_")] = count
                except Exception as e:
                    validation_results[
                        f"{check_name.lower().replace(' ', '_')}_error"
                    ] = str(e)

        return {
            "validation_results": validation_results,
            "validation_timestamp": datetime.now().isoformat(),
            "overall_status": "healthy"
            if not any("error" in str(v) for v in validation_results.values())
            else "issues_detected",
        }

    except Exception as e:
        logger.error(f"Error validating data integrity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/metrics")
async def get_performance_metrics():
    """Get database performance metrics"""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(os.getenv("DATABASE_URL"))

        with engine.connect() as conn:
            # Get table statistics
            table_stats_result = conn.execute(
                text(
                    """
                SELECT 
                    schemaname,
                    tablename,
                    seq_scan,
                    seq_tup_read,
                    idx_scan,
                    idx_tup_fetch,
                    n_tup_ins,
                    n_tup_upd,
                    n_tup_del,
                    n_live_tup,
                    n_dead_tup
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY n_live_tup DESC
            """
                )
            )

            table_stats = []
            for row in table_stats_result:
                table_stats.append(
                    {
                        "table": row[1],
                        "sequential_scans": row[2],
                        "sequential_tuples_read": row[3],
                        "index_scans": row[4],
                        "index_tuples_fetched": row[5],
                        "inserts": row[6],
                        "updates": row[7],
                        "deletes": row[8],
                        "live_tuples": row[9],
                        "dead_tuples": row[10],
                    }
                )

            # Get index statistics
            index_stats_result = conn.execute(
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
            for row in index_stats_result:
                index_stats.append(
                    {
                        "table": row[1],
                        "index": row[2],
                        "scans": row[3],
                        "tuples_read": row[4],
                        "tuples_fetched": row[5],
                    }
                )

        return {
            "table_statistics": table_stats,
            "index_statistics": index_stats,
            "metrics_timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def _get_schema_status():
    """Get schema status information"""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(os.getenv("DATABASE_URL"))

        with engine.connect() as conn:
            # Check if enhanced tables exist
            enhanced_tables = [
                "market_data",
                "neighborhood_profiles",
                "transactions",
                "property_viewings",
                "appointments",
                "rera_compliance",
                "document_management",
            ]

            existing_tables = []
            for table in enhanced_tables:
                result = conn.execute(
                    text(
                        f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table}')"
                    )
                )
                exists = result.fetchone()[0]
                existing_tables.append({"table": table, "exists": exists})

            # Check enhanced columns
            enhanced_columns = [
                ("properties", "price_aed"),
                ("properties", "listing_status"),
                ("properties", "features"),
                ("leads", "nurture_status"),
                ("leads", "assigned_agent_id"),
                ("clients", "client_type"),
            ]

            existing_columns = []
            for table, column in enhanced_columns:
                result = conn.execute(
                    text(
                        f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{table}' AND column_name = '{column}')"
                    )
                )
                exists = result.fetchone()[0]
                existing_columns.append(
                    {"table": table, "column": column, "exists": exists}
                )

        return {
            "enhanced_tables": existing_tables,
            "enhanced_columns": existing_columns,
            "schema_enhancement_complete": all(
                col["exists"] for col in existing_columns
            ),
        }

    except Exception as e:
        return {"error": str(e)}


async def _get_data_status():
    """Get data status information"""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(os.getenv("DATABASE_URL"))

        with engine.connect() as conn:
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
                    count = result.fetchone()[0]
                    table_counts[table] = count
                except Exception as e:
                    table_counts[table] = f"Error: {e}"

        return {
            "table_counts": table_counts,
            "data_migration_complete": all(
                isinstance(count, int) for count in table_counts.values()
            ),
        }

    except Exception as e:
        return {"error": str(e)}


async def _get_performance_status():
    """Get performance status information"""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(os.getenv("DATABASE_URL"))

        with engine.connect() as conn:
            # Get index count
            result = conn.execute(
                text("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'")
            )
            index_count = result.fetchone()[0]

            # Get unused indexes
            result = conn.execute(
                text(
                    "SELECT COUNT(*) FROM pg_stat_user_indexes WHERE schemaname = 'public' AND idx_scan = 0"
                )
            )
            unused_indexes = result.fetchone()[0]

        return {
            "total_indexes": index_count,
            "unused_indexes": unused_indexes,
            "index_optimization_complete": index_count
            > 20,  # Assuming we should have many indexes
        }

    except Exception as e:
        return {"error": str(e)}


async def _get_enhancement_status(optimizer):
    """Get enhancement status information"""
    try:
        report = optimizer.get_enhancement_report()
        return {
            "overall_success": report["overall_success"],
            "total_enhancements": report["total_enhancements"],
            "successful_enhancements": report["successful_enhancements"],
            "failed_enhancements": report["failed_enhancements"],
        }
    except Exception as e:
        return {"error": str(e)}


def _generate_schema_recommendations(tables, columns, indexes):
    """Generate schema recommendations based on analysis"""
    recommendations = []

    # Check for missing enhanced tables
    enhanced_tables = [
        "market_data",
        "neighborhood_profiles",
        "transactions",
        "property_viewings",
        "appointments",
        "rera_compliance",
        "document_management",
    ]
    existing_table_names = [table["name"] for table in tables]

    for table in enhanced_tables:
        if table not in existing_table_names:
            recommendations.append(
                {
                    "type": "missing_table",
                    "priority": "high",
                    "message": f"Missing enhanced table: {table}",
                    "action": f"Create {table} table for enhanced functionality",
                }
            )

    # Check for missing enhanced columns
    enhanced_columns = [
        ("properties", "price_aed"),
        ("properties", "listing_status"),
        ("properties", "features"),
        ("leads", "nurture_status"),
        ("leads", "assigned_agent_id"),
        ("clients", "client_type"),
    ]

    for table, column in enhanced_columns:
        if not any(
            col["table"] == table and col["column"] == column for col in columns
        ):
            recommendations.append(
                {
                    "type": "missing_column",
                    "priority": "high",
                    "message": f"Missing enhanced column: {table}.{column}",
                    "action": f"Add {column} column to {table} table",
                }
            )

    # Check for missing indexes
    if len(indexes) < 20:
        recommendations.append(
            {
                "type": "missing_indexes",
                "priority": "medium",
                "message": "Insufficient database indexes",
                "action": "Create additional indexes for better performance",
            }
        )

    return recommendations
