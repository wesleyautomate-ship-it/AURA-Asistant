#!/usr/bin/env python3
"""
Task Manager for Asynchronous Document Processing
Handles task creation, status tracking, and result storage
"""

import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import threading
import time

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingTask:
    task_id: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    instructions: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    execution_plan: Optional[Dict[str, Any]] = None
    storage_summary: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class TaskManager:
    """Manages asynchronous processing tasks"""

    def __init__(self):
        self.tasks: Dict[str, ProcessingTask] = {}
        self._lock = threading.Lock()

    def create_task(
        self, file_path: str, file_type: str, instructions: str = ""
    ) -> str:
        """Create a new processing task"""
        task_id = str(uuid.uuid4())

        task = ProcessingTask(
            task_id=task_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            file_path=file_path,
            file_type=file_type,
            instructions=instructions,
        )

        with self._lock:
            self.tasks[task_id] = task

        logger.info(f"Created task {task_id} for file {file_path}")
        return task_id

    def get_task(self, task_id: str) -> Optional[ProcessingTask]:
        """Get task by ID"""
        with self._lock:
            return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus, **kwargs):
        """Update task status and optional fields"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = status

                if status == TaskStatus.PROCESSING and not task.started_at:
                    task.started_at = datetime.now()
                elif (
                    status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                    and not task.completed_at
                ):
                    task.completed_at = datetime.now()

                # Update any additional fields
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)

                logger.info(f"Updated task {task_id} status to {status}")

    def set_task_result(self, task_id: str, result: Dict[str, Any]):
        """Set the final result for a completed task"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                logger.info(f"Set result for task {task_id}")

    def set_task_error(self, task_id: str, error_message: str):
        """Set error message for a failed task"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.error_message = error_message
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                logger.error(f"Task {task_id} failed: {error_message}")

    def update_progress(self, task_id: str, progress: float):
        """Update task progress (0.0 to 1.0)"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].progress = min(1.0, max(0.0, progress))

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up tasks older than specified hours"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        with self._lock:
            tasks_to_remove = [
                task_id
                for task_id, task in self.tasks.items()
                if task.created_at.timestamp() < cutoff_time
            ]

            for task_id in tasks_to_remove:
                del self.tasks[task_id]

            if tasks_to_remove:
                logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")

    def get_task_summary(self, task_id: str) -> Dict[str, Any]:
        """Get a summary of task for API response"""
        task = self.get_task(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "progress": task.progress,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "result": task.result,
            "error_message": task.error_message,
            "execution_plan": task.execution_plan,
            "storage_summary": task.storage_summary,
            "performance_metrics": task.performance_metrics,
        }


# Global task manager instance
task_manager = TaskManager()
