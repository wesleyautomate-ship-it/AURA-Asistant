"""
Performance Router - FastAPI Router for Performance Monitoring and Analytics Endpoints

This router handles all performance monitoring and analytics endpoints migrated from main.py
to maintain frontend compatibility while following the secure architecture
patterns of main_secure.py.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Import dependencies
from app.core.settings import REDIS_URL

# Import performance services
from cache_manager import CacheManager
from batch_processor import BatchProcessor, PerformanceMonitor

# Initialize performance services
# Parse REDIS_URL to get host, port, db
from urllib.parse import urlparse

try:
    redis_parts = urlparse(REDIS_URL)
    cache_manager = CacheManager(
        redis_host=redis_parts.hostname or "localhost",
        redis_port=redis_parts.port or 6379,
        redis_db=int(redis_parts.path.lstrip("/")) if redis_parts.path else 0,
    )
except Exception as e:
    print(f"Warning: Could not initialize Redis cache: {e}")
    cache_manager = None
batch_processor = BatchProcessor(max_workers=4, batch_size=50)
performance_monitor = PerformanceMonitor()

# Initialize router
router = APIRouter(prefix="/performance", tags=["Performance Monitoring"])

# Pydantic Models
class CacheStatsResponse(BaseModel):
    """Cache statistics response model"""

    total_keys: int
    memory_usage: str
    hit_rate: float
    miss_rate: float
    evictions: int
    expired_keys: int


class CacheHealthResponse(BaseModel):
    """Cache health response model"""

    status: str
    connected: bool
    memory_usage: str
    total_keys: int
    last_check: str


class BatchJobResponse(BaseModel):
    """Batch job response model"""

    job_id: str
    job_type: str
    status: str
    progress: float
    total_items: int
    processed_items: int
    failed_items: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class BatchJobsResponse(BaseModel):
    """Batch jobs list response model"""

    active_jobs: int
    jobs: List[BatchJobResponse]


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response model"""

    response_time: float
    throughput: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    active_connections: int
    cache_hit_rate: float


class CacheClearResponse(BaseModel):
    """Cache clear response model"""

    success: bool
    message: str


class JobCancelResponse(BaseModel):
    """Job cancel response model"""

    success: bool
    message: str


class PerformanceAnalyticsResponse(BaseModel):
    """Performance analytics response model"""

    total_chat_sessions: int
    average_response_time: float
    average_query_length: int
    average_user_satisfaction: float
    total_feedback_received: int
    average_feedback_rating: float
    total_ingested_documents: int
    average_ingestion_time: float
    total_processed_documents: int
    average_processing_time: float
    total_generated_responses: int
    average_response_length: int
    total_generated_insights: int
    average_insight_length: int
    total_generated_recommendations: int
    average_recommendation_length: int
    total_generated_property_listings: int
    average_property_listing_length: int
    total_generated_agent_profiles: int
    average_agent_profile_length: int
    total_generated_developer_profiles: int
    average_developer_profile_length: int
    total_generated_general_documents: int
    average_general_document_length: int
    total_generated_legal_documents: int
    average_legal_document_length: int
    total_generated_transaction_records: int
    average_transaction_record_length: int


class PerformanceReportResponse(BaseModel):
    """Performance report response model"""

    system_health: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    recommendations: List[str]
    generated_at: str


# Router Endpoints


@router.get("/cache-stats", response_model=CacheStatsResponse)
def get_cache_stats():
    """Get cache performance statistics"""
    try:
        if cache_manager is None:
            return CacheStatsResponse(
                total_keys=0,
                memory_usage="0B",
                hit_rate=0.0,
                miss_rate=0.0,
                evictions=0,
                expired_keys=0,
            )
        stats = cache_manager.get_cache_stats()
        return CacheStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache stats: {str(e)}"
        )


@router.get("/cache-health", response_model=CacheHealthResponse)
def get_cache_health():
    """Get cache health status"""
    try:
        if cache_manager is None:
            return CacheHealthResponse(
                status="disabled",
                connected=False,
                memory_usage="0B",
                total_keys=0,
                last_check=datetime.now().isoformat(),
            )
        health = cache_manager.health_check()
        return CacheHealthResponse(**health)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache health: {str(e)}"
        )


@router.get("/batch-jobs", response_model=BatchJobsResponse)
def get_batch_jobs():
    """Get all active batch jobs"""
    try:
        jobs = batch_processor.get_all_jobs()
        job_responses = []

        for job in jobs:
            job_responses.append(
                BatchJobResponse(
                    job_id=job.job_id,
                    job_type=job.job_type,
                    status=job.status.value,
                    progress=job.progress,
                    total_items=job.total_items,
                    processed_items=job.processed_items,
                    failed_items=job.failed_items,
                    start_time=job.start_time.isoformat() if job.start_time else None,
                    end_time=job.end_time.isoformat() if job.end_time else None,
                )
            )

        return BatchJobsResponse(active_jobs=len(jobs), jobs=job_responses)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get batch jobs: {str(e)}"
        )


@router.get("/metrics", response_model=PerformanceMetricsResponse)
def get_performance_metrics():
    """Get overall performance metrics"""
    try:
        metrics = performance_monitor.get_performance_report()
        return PerformanceMetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.post("/clear-cache", response_model=CacheClearResponse)
def clear_cache():
    """Clear all cache entries"""
    try:
        if cache_manager is None:
            return CacheClearResponse(success=False, message="Cache is disabled")
        success = cache_manager.clear_all_cache()
        return CacheClearResponse(
            success=success,
            message="Cache cleared" if success else "Failed to clear cache",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.delete("/cancel-job/{job_id}", response_model=JobCancelResponse)
def cancel_batch_job(job_id: str):
    """Cancel a running batch job"""
    try:
        success = batch_processor.cancel_job(job_id)
        return JobCancelResponse(
            success=success,
            message=f"Job {job_id} cancelled" if success else "Failed to cancel job",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")


@router.get(
    "/analytics",
    response_model=PerformanceAnalyticsResponse,
    tags=["Performance Analytics"],
)
async def get_performance_analytics():
    """Get performance analytics for the system"""
    try:
        # This is a placeholder function. In a real application, you would fetch this data from a database or a monitoring tool.
        performance = {
            "total_chat_sessions": 100,
            "average_response_time": 15.2,
            "average_query_length": 50,
            "average_user_satisfaction": 85,
            "total_feedback_received": 200,
            "average_feedback_rating": 4.5,
            "total_ingested_documents": 100,
            "average_ingestion_time": 60.5,
            "total_processed_documents": 95,
            "average_processing_time": 45.2,
            "total_generated_responses": 1000,
            "average_response_length": 200,
            "total_generated_insights": 50,
            "average_insight_length": 150,
            "total_generated_recommendations": 100,
            "average_recommendation_length": 100,
            "total_generated_property_listings": 50,
            "average_property_listing_length": 150,
            "total_generated_agent_profiles": 20,
            "average_agent_profile_length": 100,
            "total_generated_developer_profiles": 10,
            "average_developer_profile_length": 100,
            "total_generated_general_documents": 30,
            "average_general_document_length": 100,
            "total_generated_legal_documents": 10,
            "average_legal_document_length": 100,
            "total_generated_transaction_records": 50,
            "average_transaction_record_length": 100,
        }

        return PerformanceAnalyticsResponse(**performance)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get performance analytics: {str(e)}"
        )


@router.get("/report", response_model=PerformanceReportResponse)
async def get_performance_report():
    """Get performance and cost metrics"""
    try:
        from performance.optimization_manager import get_performance_optimizer

        performance_optimizer = get_performance_optimizer()
        report = performance_optimizer.get_performance_report()

        # Add timestamp to the report
        report["generated_at"] = datetime.now().isoformat()

        return PerformanceReportResponse(**report)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get performance report: {str(e)}"
        )
