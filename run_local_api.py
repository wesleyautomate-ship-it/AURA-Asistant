#!/usr/bin/env python3
"""
Local API Runner for Task Management Testing
============================================

This script runs a simplified version of the PropertyPro AI API
locally for testing our task management features without Docker.
"""

import os
import sys
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json
import uuid

# Set environment variables for development
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "true"
os.environ["DISABLE_AUTH"] = "true"  # Bypass authentication for testing

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    print("⚠️ FastAPI not available. Creating simple HTTP server instead.")
    HAS_FASTAPI = False

# Simple task data structures
@dataclass
class Task:
    id: str
    title: str
    description: Optional[str] = None
    status: str = 'open'  # open, in_progress, completed, archived
    priority: str = 'medium'  # low, medium, high, urgent
    due_date: Optional[str] = None
    order_index: int = 0
    property_id: Optional[str] = None
    client_id: Optional[str] = None
    created_by: str = 'dev-user'
    assigned_to: List[str] = None
    created_at: str = None
    updated_at: str = None
    is_overdue: bool = False
    
    def __post_init__(self):
        if self.assigned_to is None:
            self.assigned_to = [self.created_by]
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.due_date and self.status != 'completed':
            try:
                due = datetime.fromisoformat(self.due_date.replace('Z', '+00:00'))
                self.is_overdue = due.date() < date.today()
            except:
                self.is_overdue = False

# In-memory task storage
tasks_db: Dict[str, Task] = {}

# Initialize with sample tasks
def init_sample_tasks():
    global tasks_db
    if not tasks_db:
        sample_tasks = [
            Task(
                id="1",
                title="Follow up with client about listing contract",
                description="Client expressed interest in listing their Downtown property",
                priority="high",
                due_date="2025-10-08",
                order_index=1
            ),
            Task(
                id="2", 
                title="Prepare CMA for Marina apartment",
                description="Comparative market analysis for 2BR unit in Dubai Marina",
                status="in_progress",
                priority="medium",
                due_date="2025-10-10",
                order_index=2
            ),
            Task(
                id="3",
                title="Schedule property viewing", 
                description="Arrange viewing for Palm Jumeirah villa with potential buyer",
                priority="urgent",
                due_date="2025-10-06",
                order_index=3
            )
        ]
        
        for task in sample_tasks:
            tasks_db[task.id] = task
            
        print(f"✅ Initialized {len(sample_tasks)} sample tasks")

if HAS_FASTAPI:
    # FastAPI implementation
    app = FastAPI(title="PropertyPro AI - Task Management API", version="1.0.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In development, allow all origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class TaskResponse(BaseModel):
        id: str
        title: str
        description: Optional[str] = None
        status: str
        priority: str
        due_date: Optional[str] = None
        order_index: int = 0
        property_id: Optional[str] = None
        client_id: Optional[str] = None
        created_by: str
        assigned_to: List[str] = []
        created_at: str
        updated_at: str
        is_overdue: bool = False

    class TaskCreateRequest(BaseModel):
        title: str = Field(..., min_length=1, max_length=255)
        description: Optional[str] = Field(None, max_length=2000)
        due_date: Optional[str] = None
        priority: str = Field(default='medium', pattern='^(low|medium|high|urgent)$')
        property_id: Optional[str] = None
        client_id: Optional[str] = None

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "service": "PropertyPro AI Task API (Local)",
            "tasks_count": len(tasks_db)
        }

    @app.get("/api/v1/tasks")
    async def list_tasks(
        status: Optional[str] = Query(None),
        priority: Optional[str] = Query(None),
        q: Optional[str] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100)
    ):
        """List all tasks with filtering and pagination"""
        init_sample_tasks()
        
        filtered_tasks = list(tasks_db.values())
        
        # Apply filters
        if status:
            filtered_tasks = [t for t in filtered_tasks if t.status == status]
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
        if q:
            query = q.lower()
            filtered_tasks = [
                t for t in filtered_tasks 
                if query in t.title.lower() or (t.description and query in t.description.lower())
            ]
        
        # Sort tasks
        filtered_tasks.sort(key=lambda x: (
            x.status == 'completed',  # Incomplete first
            -{'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.priority, 0),  # Priority desc
            x.order_index  # Order index asc
        ))
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_tasks = filtered_tasks[start:end]
        
        return {
            "tasks": [TaskResponse(**asdict(t)) for t in paginated_tasks],
            "total": len(filtered_tasks),
            "page": page,
            "page_size": page_size,
            "has_next": end < len(filtered_tasks),
            "has_prev": page > 1
        }

    @app.get("/api/v1/tasks/{task_id}")
    async def get_task(task_id: str):
        """Get a specific task by ID"""
        init_sample_tasks()
        
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = tasks_db[task_id]
        return TaskResponse(**asdict(task))

    @app.post("/api/v1/tasks")
    async def create_task(task_data: TaskCreateRequest):
        """Create a new task"""
        init_sample_tasks()
        
        # Generate new task ID
        task_id = str(uuid.uuid4())[:8]
        
        # Calculate next order index
        max_order = max([t.order_index for t in tasks_db.values()], default=0)
        
        new_task = Task(
            id=task_id,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            priority=task_data.priority,
            property_id=task_data.property_id,
            client_id=task_data.client_id,
            order_index=max_order + 1
        )
        
        tasks_db[task_id] = new_task
        
        print(f"✅ Created task: {new_task.title}")
        return TaskResponse(**asdict(new_task))

    @app.patch("/api/v1/tasks/{task_id}")
    async def update_task(task_id: str, updates: dict):
        """Update an existing task"""
        init_sample_tasks()
        
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = tasks_db[task_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        
        task.updated_at = datetime.now().isoformat()
        
        # Recalculate overdue status
        if task.due_date and task.status != 'completed':
            try:
                due = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                task.is_overdue = due.date() < date.today()
            except:
                task.is_overdue = False
        
        print(f"✅ Updated task: {task.title}")
        return TaskResponse(**asdict(task))

    @app.patch("/api/v1/tasks/{task_id}/complete")
    async def toggle_task_completion(task_id: str):
        """Toggle task completion status"""
        init_sample_tasks()
        
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = tasks_db[task_id]
        task.status = 'completed' if task.status != 'completed' else 'open'
        task.updated_at = datetime.now().isoformat()
        task.is_overdue = False  # Completed tasks are not overdue
        
        print(f"✅ Toggled completion for task: {task.title} -> {task.status}")
        return TaskResponse(**asdict(task))

    @app.delete("/api/v1/tasks/{task_id}")
    async def delete_task(task_id: str):
        """Delete a task"""
        init_sample_tasks()
        
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = tasks_db[task_id]
        del tasks_db[task_id]
        
        print(f"✅ Deleted task: {task.title}")
        return {"message": "Task deleted successfully"}

    def run_server():
        print("🚀 Starting PropertyPro AI Task Management API...")
        print("📍 http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
        print("💾 Health Check: http://localhost:8000/health")
        print("\n🔧 Available endpoints:")
        print("  GET    /api/v1/tasks           - List tasks")
        print("  POST   /api/v1/tasks           - Create task")  
        print("  GET    /api/v1/tasks/{id}      - Get specific task")
        print("  PATCH  /api/v1/tasks/{id}      - Update task")
        print("  PATCH  /api/v1/tasks/{id}/complete - Toggle completion")
        print("  DELETE /api/v1/tasks/{id}      - Delete task")
        print("\n✨ Features enabled:")
        print("  ✅ CORS enabled for frontend")
        print("  ✅ Authentication disabled")
        print("  ✅ Sample tasks loaded")
        print("  ✅ In-memory storage")
        print("\nPress Ctrl+C to stop the server\n")
        
        try:
            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
        except KeyboardInterrupt:
            print("\n👋 Server stopped!")

else:
    # Simple HTTP server fallback
    def run_server():
        print("⚠️ FastAPI not available. Please install FastAPI to run the full API:")
        print("pip install fastapi uvicorn")
        print("\nAlternatively, you can test the task management UI in the demo HTML file.")

if __name__ == "__main__":
    run_server()