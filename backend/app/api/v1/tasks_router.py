"""
Task Management Router
======================

FastAPI router that provides task management functionality for PropertyPro AI.

Endpoints:
- GET /api/v1/tasks - List tasks with filtering and pagination
- GET /api/v1/tasks/{task_id} - Get task details
- POST /api/v1/tasks - Create new task
- PATCH /api/v1/tasks/{task_id} - Update task
- PATCH /api/v1/tasks/{task_id}/complete - Toggle task completion
- DELETE /api/v1/tasks/{task_id} - Delete task (soft delete)
- POST /api/v1/tasks/reorder - Reorder tasks by priority
- POST /api/v1/tasks/{task_id}/assign - Assign task to user
- DELETE /api/v1/tasks/{task_id}/assign/{user_id} - Unassign task from user
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from pydantic import BaseModel, Field, validator

from app.core.database import get_db
from app.core.middleware import get_current_user, require_roles
from app.core.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskCreateRequest(BaseModel):
    """Request model for creating a new task"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    property_id: Optional[str] = None
    client_id: Optional[str] = None
    assigned_to: Optional[List[str]] = None  # List of user IDs

    @validator('due_date')
    def due_date_not_past(cls, v):
        if v and v < date.today():
            raise ValueError('Due date cannot be in the past')
        return v

class TaskUpdateRequest(BaseModel):
    """Request model for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    property_id: Optional[str] = None
    client_id: Optional[str] = None

    @validator('due_date')
    def due_date_not_past(cls, v):
        if v and v < date.today():
            raise ValueError('Due date cannot be in the past')
        return v

class TaskReorderRequest(BaseModel):
    """Request model for reordering tasks"""
    task_orders: List[Dict[str, Any]] = Field(..., description="Array of {id, order_index}")

    @validator('task_orders')
    def validate_task_orders(cls, v):
        if not v:
            raise ValueError('Task orders cannot be empty')
        for item in v:
            if 'id' not in item or 'order_index' not in item:
                raise ValueError('Each item must have id and order_index')
        return v

class TaskAssignRequest(BaseModel):
    """Request model for assigning a task"""
    user_id: str = Field(..., min_length=1)

class TaskResponse(BaseModel):
    """Response model for task data"""
    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[date] = None
    order_index: int = 0
    property_id: Optional[str] = None
    client_id: Optional[str] = None
    created_by: str
    assigned_to: List[str] = []  # List of user IDs
    created_at: datetime
    updated_at: datetime
    is_overdue: bool = False

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """Response model for task list"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

# =============================================================================
# TEMPORARY IN-MEMORY STORAGE (Replace with proper database models)
# =============================================================================

# This will be replaced with proper SQLAlchemy models
_tasks_storage = {}
_task_counter = 1

class TaskEntity:
    def __init__(self, **kwargs):
        global _task_counter
        self.id = str(_task_counter)
        _task_counter += 1
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description')
        self.status = kwargs.get('status', TaskStatus.OPEN)
        self.priority = kwargs.get('priority', TaskPriority.MEDIUM)
        self.due_date = kwargs.get('due_date')
        self.order_index = kwargs.get('order_index', 0)
        self.property_id = kwargs.get('property_id')
        self.client_id = kwargs.get('client_id')
        self.created_by = kwargs.get('created_by')
        self.assigned_to = kwargs.get('assigned_to', [])
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.deleted_at = None

    def to_dict(self):
        is_overdue = (
            self.due_date and 
            self.status != TaskStatus.COMPLETED and 
            self.due_date < date.today()
        )
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date,
            'order_index': self.order_index,
            'property_id': self.property_id,
            'client_id': self.client_id,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_overdue': is_overdue
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.now()

# Initialize some sample tasks
def init_sample_tasks(user_id: str):
    if not _tasks_storage:
        sample_tasks = [
            TaskEntity(
                title="Follow up with client about listing contract",
                description="Client expressed interest in listing their Downtown property",
                status=TaskStatus.OPEN,
                priority=TaskPriority.HIGH,
                due_date=date(2025, 10, 8),
                created_by=user_id,
                assigned_to=[user_id],
                order_index=1
            ),
            TaskEntity(
                title="Prepare CMA for Marina apartment",
                description="Comparative market analysis for 2BR unit in Dubai Marina",
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.MEDIUM,
                due_date=date(2025, 10, 10),
                created_by=user_id,
                assigned_to=[user_id],
                order_index=2
            ),
            TaskEntity(
                title="Schedule property viewing",
                description="Arrange viewing for Palm Jumeirah villa with potential buyer",
                status=TaskStatus.OPEN,
                priority=TaskPriority.MEDIUM,
                due_date=date(2025, 10, 7),
                created_by=user_id,
                assigned_to=[user_id],
                order_index=3
            )
        ]
        
        for task in sample_tasks:
            _tasks_storage[task.id] = task

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_user_tasks(user_id: str, filters: dict = None, sort_by: str = "order_index", sort_order: str = "asc") -> List[TaskEntity]:
    """Get tasks for a specific user with filters and sorting"""
    init_sample_tasks(user_id)  # Initialize sample data if needed
    
    user_tasks = []
    for task in _tasks_storage.values():
        if task.deleted_at is not None:
            continue
            
        # Check if user has access to this task
        if task.created_by == user_id or user_id in task.assigned_to:
            user_tasks.append(task)
    
    # Apply filters
    if filters:
        if 'status' in filters and filters['status']:
            user_tasks = [t for t in user_tasks if t.status == filters['status']]
        
        if 'priority' in filters and filters['priority']:
            user_tasks = [t for t in user_tasks if t.priority == filters['priority']]
        
        if 'property_id' in filters and filters['property_id']:
            user_tasks = [t for t in user_tasks if t.property_id == filters['property_id']]
        
        if 'client_id' in filters and filters['client_id']:
            user_tasks = [t for t in user_tasks if t.client_id == filters['client_id']]
        
        if 'assigned_to' in filters and filters['assigned_to']:
            user_tasks = [t for t in user_tasks if filters['assigned_to'] in t.assigned_to]
        
        if 'q' in filters and filters['q']:
            query = filters['q'].lower()
            user_tasks = [
                t for t in user_tasks 
                if query in t.title.lower() or (t.description and query in t.description.lower())
            ]
    
    # Apply sorting
    reverse = sort_order == "desc"
    if sort_by == "due_date":
        user_tasks.sort(key=lambda x: x.due_date or date.max, reverse=reverse)
    elif sort_by == "priority":
        priority_order = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
        user_tasks.sort(key=lambda x: priority_order.get(x.priority, 0), reverse=reverse)
    elif sort_by == "created_at":
        user_tasks.sort(key=lambda x: x.created_at, reverse=reverse)
    elif sort_by == "updated_at":
        user_tasks.sort(key=lambda x: x.updated_at, reverse=reverse)
    else:  # default to order_index
        user_tasks.sort(key=lambda x: x.order_index, reverse=reverse)
    
    return user_tasks

def paginate_tasks(tasks: List[TaskEntity], page: int = 1, page_size: int = 50):
    """Paginate task list"""
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        'tasks': tasks[start:end],
        'total': len(tasks),
        'page': page,
        'page_size': page_size,
        'has_next': end < len(tasks),
        'has_prev': page > 1
    }

# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/test")
async def test_tasks_endpoint():
    """Public test endpoint to verify tasks router is working"""
    import os
    return {
        "message": "Tasks API is working!",
        "environment": {
            "DISABLE_AUTH": os.getenv("DISABLE_AUTH", "not set"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "not set"),
            "DEBUG": os.getenv("DEBUG", "not set")
        },
        "endpoints": [
            "GET /api/v1/tasks - List tasks (requires auth)",
            "POST /api/v1/tasks - Create task (requires auth)",
            "GET /api/v1/tasks/test - This test endpoint (no auth)"
        ]
    }

@router.get("/dev", response_model=TaskListResponse)
async def list_tasks_dev():
    """
    Development endpoint to list tasks without authentication.
    Only available when DISABLE_AUTH is true.
    """
    import os
    if os.getenv("DISABLE_AUTH", "false").lower() != "true":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development endpoint not available"
        )
    
    try:
        # Use a fixed dev user ID
        dev_user_id = "1"
        filters = {}
        
        tasks = get_user_tasks(dev_user_id, filters, "order_index", "asc")
        paginated = paginate_tasks(tasks, 1, 50)
        
        return TaskListResponse(
            tasks=[TaskResponse(**task.to_dict()) for task in paginated['tasks']],
            total=paginated['total'],
            page=paginated['page'],
            page_size=paginated['page_size'],
            has_next=paginated['has_next'],
            has_prev=paginated['has_prev']
        )
        
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks"
        )

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    current_user: User = Depends(get_current_user),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user ID"),
    property_id: Optional[str] = Query(None, description="Filter by property ID"),
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    q: Optional[str] = Query(None, description="Search in title and description"),
    sort: Optional[str] = Query("order_index", description="Sort by field"),
    order: Optional[str] = Query("asc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size")
):
    """
    List tasks for the authenticated user with filtering and pagination.
    
    Supports filtering by status, priority, assigned user, property, client,
    and text search. Results can be sorted by various fields.
    """
    try:
        filters = {
            'status': status,
            'priority': priority,
            'assigned_to': assigned_to,
            'property_id': property_id,
            'client_id': client_id,
            'q': q
        }
        
        tasks = get_user_tasks(current_user.id, filters, sort, order)
        paginated = paginate_tasks(tasks, page, page_size)
        
        return TaskListResponse(
            tasks=[TaskResponse(**task.to_dict()) for task in paginated['tasks']],
            total=paginated['total'],
            page=paginated['page'],
            page_size=paginated['page_size'],
            has_next=paginated['has_next'],
            has_prev=paginated['has_prev']
        )
        
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks"
        )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID"""
    try:
        task = _tasks_storage.get(task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check access permission
        if task.created_by != current_user.id and current_user.id not in task.assigned_to:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this task"
            )
        
        return TaskResponse(**task.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task"
        )

@router.post("", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    try:
        # Calculate next order index
        user_tasks = get_user_tasks(current_user.id)
        next_order = max([t.order_index for t in user_tasks], default=0) + 1
        
        task = TaskEntity(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            due_date=task_data.due_date,
            property_id=task_data.property_id,
            client_id=task_data.client_id,
            created_by=current_user.id,
            assigned_to=task_data.assigned_to or [current_user.id],
            order_index=next_order
        )
        
        _tasks_storage[task.id] = task
        
        logger.info(f"Task {task.id} created by user {current_user.id}")
        return TaskResponse(**task.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a task"""
    try:
        task = _tasks_storage.get(task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check access permission
        if task.created_by != current_user.id and current_user.id not in task.assigned_to:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this task"
            )
        
        # Update task fields
        update_data = task_data.dict(exclude_unset=True)
        task.update(**update_data)
        
        logger.info(f"Task {task.id} updated by user {current_user.id}")
        return TaskResponse(**task.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )

@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Toggle task completion status"""
    try:
        task = _tasks_storage.get(task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check access permission
        if task.created_by != current_user.id and current_user.id not in task.assigned_to:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this task"
            )
        
        # Toggle completion status
        if task.status == TaskStatus.COMPLETED:
            task.status = TaskStatus.OPEN
        else:
            task.status = TaskStatus.COMPLETED
        
        task.updated_at = datetime.now()
        
        logger.info(f"Task {task.id} completion toggled by user {current_user.id}")
        return TaskResponse(**task.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle task completion {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task completion"
        )

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a task (soft delete)"""
    try:
        task = _tasks_storage.get(task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check access permission (only creator can delete)
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only task creator can delete this task"
            )
        
        # Soft delete
        task.deleted_at = datetime.now()
        task.updated_at = datetime.now()
        
        logger.info(f"Task {task.id} deleted by user {current_user.id}")
        return {"message": "Task deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )

@router.post("/reorder")
async def reorder_tasks(
    reorder_data: TaskReorderRequest,
    current_user: User = Depends(get_current_user)
):
    """Reorder tasks by updating their order indices"""
    try:
        # Validate all tasks exist and user has access
        for item in reorder_data.task_orders:
            task = _tasks_storage.get(item['id'])
            if not task or task.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {item['id']} not found"
                )
            
            if task.created_by != current_user.id and current_user.id not in task.assigned_to:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to task {item['id']}"
                )
        
        # Update order indices
        for item in reorder_data.task_orders:
            task = _tasks_storage[item['id']]
            task.order_index = item['order_index']
            task.updated_at = datetime.now()
        
        logger.info(f"Tasks reordered by user {current_user.id}")
        return {"message": "Tasks reordered successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reorder tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder tasks"
        )

@router.post("/{task_id}/assign")
async def assign_task(
    task_id: str,
    assign_data: TaskAssignRequest,
    current_user: User = Depends(get_current_user)
):
    """Assign a task to a user"""
    try:
        task = _tasks_storage.get(task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check access permission (only creator can assign)
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only task creator can assign this task"
            )
        
        # Add user to assigned list if not already assigned
        if assign_data.user_id not in task.assigned_to:
            task.assigned_to.append(assign_data.user_id)
            task.updated_at = datetime.now()
        
        logger.info(f"Task {task.id} assigned to user {assign_data.user_id} by {current_user.id}")
        return {"message": "Task assigned successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign task"
        )

@router.delete("/{task_id}/assign/{user_id}")
async def unassign_task(
    task_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unassign a task from a user"""
    try:
        task = _tasks_storage.get(task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check access permission (only creator can unassign)
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only task creator can unassign this task"
            )
        
        # Remove user from assigned list
        if user_id in task.assigned_to:
            task.assigned_to.remove(user_id)
            task.updated_at = datetime.now()
        
        logger.info(f"Task {task.id} unassigned from user {user_id} by {current_user.id}")
        return {"message": "Task unassigned successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unassign task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unassign task"
        )