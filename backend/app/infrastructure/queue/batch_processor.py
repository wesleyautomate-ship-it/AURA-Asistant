#!/usr/bin/env python3
"""
Batch Processor for Dubai Real Estate RAG System
Handles efficient processing of large datasets with progress tracking and async operations
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable, Generator
from datetime import datetime, timedelta
import json
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
from enum import Enum
import threading
from queue import Queue
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """Represents a batch processing job"""

    job_id: str
    job_type: str
    data: List[Dict[str, Any]]
    status: BatchStatus
    progress: float = 0.0
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class BatchProcessor:
    """Batch processor for efficient data processing"""

    def __init__(self, max_workers: int = 4, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.active_jobs: Dict[str, BatchJob] = {}
        self.job_history: List[BatchJob] = []
        self.progress_callbacks: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        logger.info(
            f"Batch processor initialized with {max_workers} workers, batch size: {batch_size}"
        )

    def create_batch_job(
        self, job_type: str, data: List[Dict[str, Any]], metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new batch processing job"""
        job_id = f"{job_type}_{int(time.time())}_{len(self.active_jobs)}"

        job = BatchJob(
            job_id=job_id,
            job_type=job_type,
            data=data,
            status=BatchStatus.PENDING,
            total_items=len(data),
            metadata=metadata or {},
        )

        with self._lock:
            self.active_jobs[job_id] = job

        logger.info(f"Created batch job {job_id}: {job_type} with {len(data)} items")
        return job_id

    def process_batch_async(
        self,
        job_id: str,
        processor_func: Callable,
        progress_callback: Optional[Callable] = None,
    ) -> None:
        """Process batch asynchronously"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")

        job = self.active_jobs[job_id]
        job.status = BatchStatus.PROCESSING
        job.start_time = datetime.now()

        if progress_callback:
            self.progress_callbacks[job_id] = progress_callback

        # Submit to thread pool
        future = self._executor.submit(self._process_batch_sync, job_id, processor_func)
        future.add_done_callback(lambda f: self._job_completed(job_id, f))

        logger.info(f"Started async processing for job {job_id}")

    def _process_batch_sync(self, job_id: str, processor_func: Callable) -> None:
        """Process batch synchronously in worker thread"""
        job = self.active_jobs[job_id]

        try:
            # Process data in batches
            for i in range(0, len(job.data), self.batch_size):
                batch = job.data[i : i + self.batch_size]

                # Process batch
                for item in batch:
                    try:
                        processor_func(item)
                        job.processed_items += 1
                    except Exception as e:
                        job.failed_items += 1
                        logger.error(f"Error processing item in job {job_id}: {e}")

                # Update progress
                job.progress = (
                    job.processed_items + job.failed_items
                ) / job.total_items
                self._update_progress(job_id)

                # Check if job was cancelled
                if job.status == BatchStatus.CANCELLED:
                    return

            # Mark as completed
            job.status = BatchStatus.COMPLETED
            job.end_time = datetime.now()

        except Exception as e:
            job.status = BatchStatus.FAILED
            job.error_message = str(e)
            job.end_time = datetime.now()
            logger.error(f"Batch job {job_id} failed: {e}")

    def _update_progress(self, job_id: str) -> None:
        """Update progress for a job"""
        if job_id in self.progress_callbacks:
            try:
                job = self.active_jobs[job_id]
                self.progress_callbacks[job_id](job)
            except Exception as e:
                logger.error(f"Error in progress callback for job {job_id}: {e}")

    def _job_completed(self, job_id: str, future) -> None:
        """Handle job completion"""
        try:
            future.result()  # This will raise any exceptions
        except Exception as e:
            logger.error(f"Job {job_id} completed with error: {e}")

        # Clean up
        if job_id in self.progress_callbacks:
            del self.progress_callbacks[job_id]

    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get current status of a job"""
        return self.active_jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id not in self.active_jobs:
            return False

        job = self.active_jobs[job_id]
        if job.status == BatchStatus.PROCESSING:
            job.status = BatchStatus.CANCELLED
            logger.info(f"Cancelled job {job_id}")
            return True

        return False

    def get_all_jobs(self) -> List[BatchJob]:
        """Get all active jobs"""
        with self._lock:
            return list(self.active_jobs.values())

    def cleanup_completed_jobs(self, max_history: int = 100) -> None:
        """Clean up completed jobs and maintain history"""
        with self._lock:
            completed_jobs = []
            active_jobs = {}

            for job_id, job in self.active_jobs.items():
                if job.status in [
                    BatchStatus.COMPLETED,
                    BatchStatus.FAILED,
                    BatchStatus.CANCELLED,
                ]:
                    completed_jobs.append(job)
                else:
                    active_jobs[job_id] = job

            # Add to history
            self.job_history.extend(completed_jobs)

            # Maintain history size
            if len(self.job_history) > max_history:
                self.job_history = self.job_history[-max_history:]

            # Update active jobs
            self.active_jobs = active_jobs

            logger.info(f"Cleaned up {len(completed_jobs)} completed jobs")


class DataIngestionBatchProcessor:
    """Specialized batch processor for data ingestion"""

    def __init__(self, db_engine, chroma_client, batch_size: int = 50):
        self.batch_processor = BatchProcessor(max_workers=2, batch_size=batch_size)
        self.db_engine = db_engine
        self.chroma_client = chroma_client

    def ingest_properties_batch(
        self,
        properties: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """Ingest properties in batches"""
        job_id = self.batch_processor.create_batch_job("property_ingestion", properties)

        def process_property(property_data: Dict[str, Any]) -> None:
            # Process individual property
            # This would include database insertion and ChromaDB indexing
            pass

        self.batch_processor.process_batch_async(
            job_id, process_property, progress_callback
        )
        return job_id

    def ingest_documents_batch(
        self,
        documents: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """Ingest documents in batches"""
        job_id = self.batch_processor.create_batch_job("document_ingestion", documents)

        def process_document(doc_data: Dict[str, Any]) -> None:
            # Process individual document
            # This would include text extraction, chunking, and embedding
            pass

        self.batch_processor.process_batch_async(
            job_id, process_document, progress_callback
        )
        return job_id


class AsyncDataProcessor:
    """Async data processor for non-blocking operations"""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.processing_queue = asyncio.Queue()
        self.results = {}

    async def process_data_async(
        self, data_items: List[Dict[str, Any]], processor_func: Callable
    ) -> List[Any]:
        """Process data items asynchronously"""
        tasks = []

        for item in data_items:
            task = asyncio.create_task(self._process_item(item, processor_func))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def _process_item(
        self, item: Dict[str, Any], processor_func: Callable
    ) -> Any:
        """Process a single item with semaphore control"""
        async with self.semaphore:
            try:
                return await asyncio.to_thread(processor_func, item)
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                return None

    async def stream_process(
        self, data_items: List[Dict[str, Any]], processor_func: Callable
    ) -> Generator[Any, None, None]:
        """Stream process data items"""
        for item in data_items:
            async with self.semaphore:
                try:
                    result = await asyncio.to_thread(processor_func, item)
                    yield result
                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    yield None


class PerformanceMonitor:
    """Monitor batch processing performance"""

    def __init__(self):
        self.metrics = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "total_processing_time": 0,
            "average_processing_time": 0,
            "peak_memory_usage": 0,
            "cache_hit_rate": 0,
        }
        self._lock = threading.Lock()

    def record_job_completion(self, job: BatchJob) -> None:
        """Record job completion metrics"""
        with self._lock:
            self.metrics["total_jobs"] += 1

            if job.status == BatchStatus.COMPLETED:
                self.metrics["completed_jobs"] += 1
            elif job.status == BatchStatus.FAILED:
                self.metrics["failed_jobs"] += 1

            if job.start_time and job.end_time:
                processing_time = (job.end_time - job.start_time).total_seconds()
                self.metrics["total_processing_time"] += processing_time
                self.metrics["average_processing_time"] = (
                    self.metrics["total_processing_time"] / self.metrics["total_jobs"]
                )

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        with self._lock:
            success_rate = (
                self.metrics["completed_jobs"] / self.metrics["total_jobs"]
                if self.metrics["total_jobs"] > 0
                else 0
            )

            return {
                **self.metrics,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat(),
            }

    def reset_metrics(self) -> None:
        """Reset performance metrics"""
        with self._lock:
            self.metrics = {
                "total_jobs": 0,
                "completed_jobs": 0,
                "failed_jobs": 0,
                "total_processing_time": 0,
                "average_processing_time": 0,
                "peak_memory_usage": 0,
                "cache_hit_rate": 0,
            }
