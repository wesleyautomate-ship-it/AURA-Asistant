#!/usr/bin/env python3
"""
Search Optimization Router for Dubai Real Estate RAG System
Provides API endpoints for hybrid search, performance monitoring, and database optimization
"""

import os
import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio

from hybrid_search_engine import get_hybrid_search_engine, SearchParams, SearchType
from performance_monitor import get_performance_monitor
from database_index_optimizer import DatabaseIndexOptimizer
from cache_manager import cache_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/optimization", tags=["Search Optimization"])

# Pydantic models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    search_type: str = Field(
        "hybrid", description="Search type: vector_only, structured_only, hybrid"
    )
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    location: Optional[str] = Field(None, description="Location filter")
    property_type: Optional[str] = Field(None, description="Property type filter")
    budget_min: Optional[float] = Field(None, ge=0, description="Minimum budget in AED")
    budget_max: Optional[float] = Field(None, ge=0, description="Maximum budget in AED")
    bedrooms: Optional[int] = Field(
        None, ge=0, description="Minimum number of bedrooms"
    )
    bathrooms: Optional[float] = Field(
        None, ge=0, description="Minimum number of bathrooms"
    )
    intent: Optional[str] = Field(None, description="Query intent")


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_results: int
    search_type: str
    execution_time: float
    cache_hit: bool
    metadata: Dict[str, Any]


class PerformanceMetricsResponse(BaseModel):
    system_info: Dict[str, Any]
    current_metrics: Dict[str, float]
    health_status: Optional[Dict[str, Any]]
    performance_trends: Dict[str, Any]
    alerts: List[Dict[str, Any]]


class DatabaseOptimizationRequest(BaseModel):
    dry_run: bool = Field(
        False, description="Show what would be done without making changes"
    )
    priority: Optional[int] = Field(
        None, ge=1, le=3, description="Priority level (1=high, 2=medium, 3=low)"
    )


class DatabaseOptimizationResponse(BaseModel):
    success: bool
    indexes_created: List[Dict[str, Any]]
    indexes_skipped: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    performance_impact: Dict[str, Any]
    execution_time: float


class CacheStatsResponse(BaseModel):
    status: str
    total_keys: int
    memory_usage: str
    connected_clients: int
    uptime: int
    cache_patterns: Dict[str, int]
    ping_time_ms: float


# Dependency functions
def get_search_engine():
    return get_hybrid_search_engine()


def get_performance_monitor_instance():
    return get_performance_monitor()


def get_database_optimizer():
    return DatabaseIndexOptimizer(database_url=os.getenv("DATABASE_URL"))


# API Endpoints


@router.post("/search", response_model=SearchResponse)
async def hybrid_search(
    request: SearchRequest, search_engine=Depends(get_search_engine)
):
    """Perform hybrid search combining vector and structured search"""
    try:
        # Convert search type string to enum
        search_type_map = {
            "vector_only": SearchType.VECTOR_ONLY,
            "structured_only": SearchType.STRUCTURED_ONLY,
            "hybrid": SearchType.HYBRID,
        }

        search_type = search_type_map.get(request.search_type, SearchType.HYBRID)

        # Create search parameters
        search_params = SearchParams(
            query=request.query,
            search_type=search_type,
            max_results=request.max_results,
            location=request.location,
            property_type=request.property_type,
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            intent=request.intent,
        )

        # Perform search
        start_time = datetime.now()
        results = search_engine.search(search_params)
        execution_time = (datetime.now() - start_time).total_seconds()

        # Convert results to dict format
        results_dict = []
        for result in results:
            results_dict.append(
                {
                    "content": result.content,
                    "source": result.source,
                    "relevance_score": result.relevance_score,
                    "metadata": result.metadata,
                    "search_type": result.search_type.value,
                    "execution_time": result.execution_time,
                }
            )

        return SearchResponse(
            results=results_dict,
            total_results=len(results_dict),
            search_type=request.search_type,
            execution_time=execution_time,
            cache_hit=False,  # This would be determined by the search engine
            metadata={
                "search_params": request.dict(),
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    performance_monitor=Depends(get_performance_monitor_instance),
):
    """Get current performance metrics and system health"""
    try:
        summary = performance_monitor.get_performance_summary()

        return PerformanceMetricsResponse(
            system_info=summary["system_info"],
            current_metrics=summary["current_metrics"],
            health_status=summary["health_status"],
            performance_trends=summary["performance_trends"],
            alerts=summary["alerts"],
        )

    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/health")
async def get_system_health(
    search_engine=Depends(get_search_engine),
    performance_monitor=Depends(get_performance_monitor_instance),
):
    """Get comprehensive system health status"""
    try:
        # Get search engine health
        search_health = search_engine.health_check()

        # Get performance monitor health
        perf_summary = performance_monitor.get_performance_summary()

        # Get cache health
        cache_health = cache_manager.health_check()

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy"
            if all(
                [
                    search_health["status"] == "healthy",
                    cache_health["status"] == "healthy",
                    perf_summary["health_status"]["overall_status"] == "healthy",
                ]
            )
            else "degraded",
            "components": {
                "search_engine": search_health,
                "cache": cache_health,
                "performance_monitor": perf_summary["health_status"],
            },
            "alerts": perf_summary["alerts"],
        }

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/database/optimize", response_model=DatabaseOptimizationResponse)
async def optimize_database(
    request: DatabaseOptimizationRequest,
    background_tasks: BackgroundTasks,
    optimizer=Depends(get_database_optimizer),
):
    """Optimize database indexes for better performance"""
    try:
        start_time = datetime.now()

        # Run optimization
        results = optimizer.optimize_database(dry_run=request.dry_run)

        execution_time = (datetime.now() - start_time).total_seconds()

        # Add execution time to results
        results["execution_time"] = execution_time

        return DatabaseOptimizationResponse(**results)

    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/recommendations")
async def get_database_recommendations(optimizer=Depends(get_database_optimizer)):
    """Get recommendations for database optimization"""
    try:
        recommendations = optimizer.get_index_recommendations()

        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting database recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_statistics():
    """Get cache statistics and performance metrics"""
    try:
        stats = cache_manager.get_cache_stats()
        health = cache_manager.health_check()

        return CacheStatsResponse(
            status=stats["status"],
            total_keys=stats.get("total_keys", 0),
            memory_usage=stats.get("memory_usage", "N/A"),
            connected_clients=stats.get("connected_clients", 0),
            uptime=stats.get("uptime", 0),
            cache_patterns=stats.get("cache_patterns", {}),
            ping_time_ms=health.get("ping_time_ms", 0),
        )

    except Exception as e:
        logger.error(f"Error getting cache statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache():
    """Clear all cache entries"""
    try:
        success = cache_manager.clear_all_cache()

        return {
            "success": success,
            "message": "Cache cleared successfully"
            if success
            else "Failed to clear cache",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/metrics")
async def get_search_metrics(search_engine=Depends(get_search_engine)):
    """Get search engine performance metrics"""
    try:
        metrics = search_engine.get_search_metrics()

        return {"metrics": metrics, "timestamp": datetime.now().isoformat()}

    except Exception as e:
        logger.error(f"Error getting search metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance/start-monitoring")
async def start_performance_monitoring(
    background_tasks: BackgroundTasks,
    performance_monitor=Depends(get_performance_monitor_instance),
):
    """Start continuous performance monitoring"""
    try:
        # Start monitoring in background
        background_tasks.add_task(performance_monitor.start_monitoring)

        return {
            "success": True,
            "message": "Performance monitoring started",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error starting performance monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/export")
async def export_performance_data(
    performance_monitor=Depends(get_performance_monitor_instance),
):
    """Export performance data to file"""
    try:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_export_{timestamp}.json"
        filepath = f"logs/{filename}"

        # Export data
        performance_monitor.export_metrics(filepath)

        return {
            "success": True,
            "filename": filename,
            "filepath": filepath,
            "message": "Performance data exported successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error exporting performance data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_optimization_status():
    """Get overall optimization system status"""
    try:
        # Get status from all components
        search_engine = get_hybrid_search_engine()
        performance_monitor = get_performance_monitor_instance()

        search_health = search_engine.health_check()
        cache_health = cache_manager.health_check()
        perf_summary = performance_monitor.get_performance_summary()

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "operational",
            "components": {
                "hybrid_search_engine": {
                    "status": search_health["status"],
                    "postgres": search_health["postgres"],
                    "chromadb": search_health["chromadb"],
                },
                "cache_manager": {
                    "status": cache_health["status"],
                    "memory_usage": cache_health.get("memory_usage", "N/A"),
                },
                "performance_monitor": {
                    "status": "active",
                    "metrics_collected": perf_summary["system_info"][
                        "total_metrics_collected"
                    ],
                },
            },
            "optimization_features": {
                "hybrid_search": True,
                "performance_monitoring": True,
                "database_optimization": True,
                "intelligent_caching": True,
            },
        }

    except Exception as e:
        logger.error(f"Error getting optimization status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
