
"""
Human Expertise Router
=====================

FastAPI router for human expertise endpoints including:
- Expert registration and profile management
- Expert availability and workload
- Human review submission
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from auth.database import get_db
from auth.middleware import get_current_user, require_roles
from auth.models import User
from services.human_expertise_service import HumanExpertiseService, ExpertiseArea, AvailabilityStatus
from services.ai_request_processing_service import AIRequestProcessingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/experts", tags=["Human Experts"])

# =====================================================
# PYDANTIC MODELS
# =====================================================

class HumanReviewSubmit(BaseModel):
    review_content: str = Field(..., description="Human expert review content")
    rating: int = Field(..., ge=1, le=5, description="Quality rating (1-5)")
    final_output: Optional[str] = Field(None, description="Final output content")

class ExpertRegistration(BaseModel):
    expertise_area: str = Field(..., description="Expertise area")
    specializations: List[str] = Field(..., description="List of specializations")
    languages: List[str] = Field(["English"], description="Languages spoken")
    timezone: str = Field("Asia/Dubai", description="Timezone")
    working_hours: Dict[str, str] = Field({"start": "09:00", "end": "18:00"}, description="Working hours")
    max_concurrent_tasks: int = Field(3, ge=1, le=10, description="Maximum concurrent tasks")

class ExpertAvailabilityUpdate(BaseModel):
    availability_status: str = Field(..., description="Availability status (available, busy, offline, on_break)")

# =====================================================
# HUMAN EXPERT ENDPOINTS
# =====================================================

@router.post("/register", response_model=Dict[str, Any])
async def register_expert(
    expert_data: ExpertRegistration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register as a human expert"""
    try:
        service = HumanExpertiseService(db)
        
        result = await service.register_expert(
            user_id=current_user.id,
            expertise_area=expert_data.expertise_area,
            specializations=expert_data.specializations,
            languages=expert_data.languages,
            timezone=expert_data.timezone,
            working_hours=expert_data.working_hours,
            max_concurrent_tasks=expert_data.max_concurrent_tasks
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error registering expert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register expert: {str(e)}"
        )

@router.get("/my-profile", response_model=Dict[str, Any])
async def get_my_expert_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's expert profile"""
    try:
        service = HumanExpertiseService(db)
        
        # Get expert profile
        expert = db.query(service.HumanExpert).filter(
            service.HumanExpert.user_id == current_user.id
        ).first()
        
        if not expert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expert profile not found"
            )
        
        # Get workload
        workload = await service.get_expert_workload(expert.id)
        
        return {
            "expert_profile": {
                "expert_id": expert.id,
                "expertise_area": expert.expertise_area,
                "specializations": expert.specializations,
                "languages": expert.languages,
                "availability_status": expert.availability_status,
                "rating": float(expert.rating),
                "completed_tasks": expert.completed_tasks,
                "max_concurrent_tasks": expert.max_concurrent_tasks,
                "is_active": expert.is_active
            },
            "workload": workload
        }
        
    except Exception as e:
        logger.error(f"Error getting expert profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expert profile: {str(e)}"
        )

@router.put("/availability", response_model=Dict[str, Any])
async def update_expert_availability(
    availability_data: ExpertAvailabilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update expert availability status"""
    try:
        service = HumanExpertiseService(db)
        
        # Get expert profile
        expert = db.query(service.HumanExpert).filter(
            service.HumanExpert.user_id == current_user.id
        ).first()
        
        if not expert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expert profile not found"
            )
        
        result = await service.update_expert_availability(
            expert_id=expert.id,
            user_id=current_user.id,
            availability_status=availability_data.availability_status
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating expert availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update availability: {str(e)}"
        )

@router.post("/reviews/{request_id}", response_model=Dict[str, Any])
async def submit_human_review(
    request_id: int,
    review_data: HumanReviewSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit human expert review for a request"""
    try:
        service = AIRequestProcessingService(db)
        
        result = await service.submit_human_review(
            request_id=request_id,
            expert_id=current_user.id,
            review_content=review_data.review_content,
            rating=review_data.rating,
            final_output=review_data.final_output
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error submitting human review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit review: {str(e)}"
        )
