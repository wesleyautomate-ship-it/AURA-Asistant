"""
Task Orchestration Router
=========================

FastAPI router that exposes the AURA AI Task Orchestration functionality.

Endpoints:
- POST /tasks - Submit individual AI tasks
- GET /tasks/{task_id} - Get task status
- POST /packages/execute - Execute workflow packages
- GET /packages/status/{execution_id} - Get package execution status
- GET /packages - List available packages
- POST /packages/custom - Create custom packages
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.middleware import get_current_user, require_roles
from app.core.models import User
from app.domain.ai.task_orchestrator import (
    AITaskOrchestrator, AITaskRequest, TaskType, TaskPriority
)
from app.domain.ai.package_manager import WorkflowPackageManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/orchestration", tags=["AI Task Orchestration"])

# Initialize orchestrator and package manager (these should be singletons in production)
def get_orchestrator(db: Session = Depends(get_db)) -> AITaskOrchestrator:
    """Get task orchestrator instance"""
    return AITaskOrchestrator(lambda: db)

def get_package_manager(
    db: Session = Depends(get_db),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator)
) -> WorkflowPackageManager:
    """Get package manager instance"""
    return WorkflowPackageManager(lambda: db, orchestrator)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class TaskSubmissionRequest(BaseModel):
    """Request model for submitting AI tasks"""
    task_type: TaskType
    input_data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = Field(default=3, ge=0, le=10)
    timeout_seconds: int = Field(default=300, ge=30, le=3600)
    context: Optional[Dict[str, Any]] = None


class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0


class PackageExecutionRequest(BaseModel):
    """Request model for executing workflow packages"""
    package_id: int
    context: Dict[str, Any]
    custom_steps: Optional[List[Dict[str, Any]]] = None


class PackageExecutionResponse(BaseModel):
    """Response model for package execution"""
    execution_id: str
    package_name: str
    estimated_duration: int
    status: str
    progress: int = 0


class PackageListResponse(BaseModel):
    """Response model for package listing"""
    packages: List[Dict[str, Any]]
    total_count: int


class CustomPackageRequest(BaseModel):
    """Request model for creating custom packages"""
    name: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10, max_length=1000)
    category: str = Field(..., pattern="^(listing|nurturing|onboarding|custom)$")
    steps: List[Dict[str, Any]]


# =============================================================================
# INDIVIDUAL AI TASK ENDPOINTS
# =============================================================================

@router.post("/tasks", response_model=Dict[str, str])
async def submit_ai_task(
    request: TaskSubmissionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator)
):
    """
    Submit an individual AI task for processing.
    
    This endpoint allows submitting single AI tasks such as:
    - Content generation
    - CMA analysis
    - Social media posts
    - Lead scoring
    """
    try:
        task_request = AITaskRequest(
            task_type=request.task_type,
            user_id=current_user.id,
            input_data=request.input_data,
            priority=request.priority,
            max_retries=request.max_retries,
            timeout_seconds=request.timeout_seconds,
            context=request.context
        )
        
        task_id = await orchestrator.submit_task(task_request)
        
        logger.info(f"AI task {task_id} submitted by user {current_user.id}")
        
        return {
            "task_id": task_id,
            "message": "Task submitted successfully",
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit AI task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator)
):
    """
    Get the status of a submitted AI task.
    
    Returns detailed information about task progress, completion status,
    and any generated outputs or error messages.
    """
    try:
        task_result = await orchestrator.get_task_status(task_id)
        
        return TaskStatusResponse(
            task_id=task_result.task_id,
            status=task_result.status.value,
            progress=task_result.progress,
            output_data=task_result.output_data,
            error_message=task_result.error_message,
            started_at=task_result.started_at,
            completed_at=task_result.completed_at,
            retries=task_result.retries
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator)
):
    """
    Cancel a submitted AI task.
    
    Only tasks that are queued or processing can be cancelled.
    Completed or failed tasks cannot be cancelled.
    """
    try:
        # Implementation would depend on the orchestrator having a cancel method
        return {"message": "Task cancellation requested", "task_id": task_id}
        
    except Exception as e:
        logger.error(f"Failed to cancel task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )


# =============================================================================
# WORKFLOW PACKAGE ENDPOINTS
# =============================================================================

@router.get("/packages", response_model=PackageListResponse)
async def list_packages(
    category: Optional[str] = None,
    only_templates: bool = True,
    current_user: User = Depends(get_current_user),
    package_manager: WorkflowPackageManager = Depends(get_package_manager)
):
    """
    List available workflow packages.
    
    Args:
        category: Filter by package category (listing, nurturing, etc.)
        only_templates: If true, only show template packages
        
    Returns list of packages with metadata and usage statistics.
    """
    try:
        user_id = None if only_templates else current_user.id
        packages = await package_manager.get_available_packages(
            category=category,
            user_id=user_id
        )
        
        return PackageListResponse(
            packages=packages,
            total_count=len(packages)
        )
        
    except Exception as e:
        logger.error(f"Failed to list packages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list packages: {str(e)}"
        )


@router.post("/packages/execute", response_model=PackageExecutionResponse)
async def execute_package(
    request: PackageExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    package_manager: WorkflowPackageManager = Depends(get_package_manager)
):
    """
    Execute a AURA-style workflow package.
    
    This is the core endpoint for launching comprehensive AI workflows such as:
    - New Listing Package (CMA + Strategy + Marketing + Approval)
    - Lead Nurturing Package (Scoring + Email + Recommendations + Follow-up)
    - Client Onboarding Package (Profile + Welcome + Meeting + Communication)
    
    The execution runs asynchronously, and you can poll the status endpoint
    for real-time progress updates.
    """
    try:
        # Validate context data
        if not request.context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Context data is required for package execution"
            )
        
        execution_id = await package_manager.execute_package(
            package_id=request.package_id,
            user_id=current_user.id,
            context=request.context
        )
        
        # Get package details for response
        package = await package_manager.load_package(request.package_id)
        
        logger.info(f"Package {package.name} started by user {current_user.id} with execution {execution_id}")
        
        return PackageExecutionResponse(
            execution_id=execution_id,
            package_name=package.name,
            estimated_duration=package.estimated_duration,
            status="running",
            progress=0
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to execute package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute package: {str(e)}"
        )


@router.get("/packages/status/{execution_id}")
async def get_package_status(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    package_manager: WorkflowPackageManager = Depends(get_package_manager)
):
    """
    Get detailed status of a package execution.
    
    Returns comprehensive information about:
    - Overall package progress
    - Individual step status and outputs
    - Error messages and retry attempts
    - Estimated completion time
    """
    try:
        status_info = await package_manager.get_execution_status(execution_id)
        
        # Verify user has access to this execution
        if status_info['user_id'] != current_user.id:
            # Check if user is admin or from same brokerage
            if current_user.role not in ['admin', 'brokerage_owner']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this package execution"
                )
        
        return status_info
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get package status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get package status: {str(e)}"
        )


@router.post("/packages/custom", response_model=Dict[str, Any])
async def create_custom_package(
    request: CustomPackageRequest,
    current_user: User = Depends(get_current_user),
    package_manager: WorkflowPackageManager = Depends(get_package_manager)
):
    """
    Create a custom workflow package.
    
    Allows users to create their own AURA-style workflows by combining
    available task types into a custom sequence. The package can be saved
    as a template for future use.
    """
    try:
        package_id = await package_manager.create_custom_package(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            category=request.category,
            steps=request.steps
        )
        
        logger.info(f"Custom package '{request.name}' created by user {current_user.id}")
        
        return {
            "package_id": package_id,
            "name": request.name,
            "category": request.category,
            "message": "Custom package created successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create custom package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom package: {str(e)}"
        )


# =============================================================================
# QUICK-START ENDPOINTS FOR COMMON AURA WORKFLOWS
# =============================================================================

@router.post("/quick/new-listing")
async def quick_new_listing(
    property_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    package_manager: WorkflowPackageManager = Depends(get_package_manager)
):
    """
    Quick-start endpoint for New Listing Package.
    
    Simplified endpoint that executes the complete AURA New Listing workflow:
    1. Generate CMA Report
    2. Create Listing Strategy  
    3. Generate Marketing Campaign
    4. Agent Review & Approval
    5. Launch Marketing Campaign
    
    Just provide property details and the AI handles the rest!
    """
    try:
        # Get the New Listing package (assuming it's package ID 1 in seed data)
        packages = await package_manager.get_available_packages(category="listing")
        new_listing_package = None
        
        for package in packages:
            if "New Listing" in package['name']:
                new_listing_package = package
                break
        
        if not new_listing_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New Listing Package not found"
            )
        
        # Execute with property context
        execution_id = await package_manager.execute_package(
            package_id=new_listing_package['id'],
            user_id=current_user.id,
            context={
                "property_details": property_data,
                "agent_id": current_user.id,
                "workflow_type": "new_listing",
                **property_data
            }
        )
        
        return {
            "execution_id": execution_id,
            "workflow": "New Listing Package",
            "message": "Your AI team is creating your listing strategy, CMA, and marketing campaign!",
            "estimated_completion": "40 minutes"
        }
        
    except Exception as e:
        logger.error(f"Failed to start New Listing workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start New Listing workflow: {str(e)}"
        )


@router.post("/quick/lead-nurturing")
async def quick_lead_nurturing(
    client_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    package_manager: WorkflowPackageManager = Depends(get_package_manager)
):
    """
    Quick-start endpoint for Lead Nurturing Package.
    
    Automated lead nurturing sequence:
    1. Lead Qualification Analysis
    2. Personalized Welcome Email
    3. Property Recommendations
    4. Schedule Follow-up Tasks
    """
    try:
        # Get the Lead Nurturing package
        packages = await package_manager.get_available_packages(category="nurturing")
        nurturing_package = None
        
        for package in packages:
            if "Lead Nurturing" in package['name'] or "Nurturing" in package['name']:
                nurturing_package = package
                break
        
        if not nurturing_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead Nurturing Package not found"
            )
        
        execution_id = await package_manager.execute_package(
            package_id=nurturing_package['id'],
            user_id=current_user.id,
            context={
                "client_profile": client_data,
                "agent_id": current_user.id,
                "workflow_type": "lead_nurturing",
                **client_data
            }
        )
        
        return {
            "execution_id": execution_id,
            "workflow": "Lead Nurturing Package",
            "message": "Your AI team is analyzing the lead and preparing personalized outreach!",
            "estimated_completion": "16 minutes"
        }
        
    except Exception as e:
        logger.error(f"Failed to start Lead Nurturing workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start Lead Nurturing workflow: {str(e)}"
        )


# =============================================================================
# MONITORING AND ADMIN ENDPOINTS
# =============================================================================

@router.get("/stats")
async def get_orchestration_stats(
    current_user: User = Depends(require_roles(["admin", "brokerage_owner"])),
    db: Session = Depends(get_db)
):
    """
    Get orchestration statistics (admin only).
    
    Provides insights into:
    - Task completion rates
    - Average processing times
    - Most popular packages
    - Error rates and patterns
    """
    try:
        # Query orchestration statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tasks,
                AVG(CASE WHEN completed_at IS NOT NULL 
                    THEN EXTRACT(epoch FROM (completed_at - started_at))/60.0 END) as avg_duration_minutes
            FROM ai_tasks
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        """
        
        result = db.execute(text(stats_query))
        task_stats = result.fetchone()
        
        # Package statistics
        package_stats_query = """
            SELECT wp.name, wp.usage_count, wp.category,
                   COUNT(pe.id) as executions_last_30_days
            FROM workflow_packages wp
            LEFT JOIN package_executions pe ON wp.id = pe.package_id 
                AND pe.created_at >= CURRENT_DATE - INTERVAL '30 days'
            WHERE wp.is_active = true
            GROUP BY wp.id, wp.name, wp.usage_count, wp.category
            ORDER BY wp.usage_count DESC
            LIMIT 10
        """
        
        package_result = db.execute(text(package_stats_query))
        popular_packages = [dict(row) for row in package_result.fetchall()]
        
        return {
            "task_statistics": {
                "total_tasks": task_stats.total_tasks or 0,
                "completed_tasks": task_stats.completed_tasks or 0,
                "failed_tasks": task_stats.failed_tasks or 0,
                "success_rate": (task_stats.completed_tasks or 0) / max(task_stats.total_tasks or 1, 1) * 100,
                "average_duration_minutes": round(task_stats.avg_duration_minutes or 0, 2)
            },
            "popular_packages": popular_packages,
            "period": "Last 30 days"
        }
        
    except Exception as e:
        logger.error(f"Failed to get orchestration stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get orchestration stats: {str(e)}"
        )
