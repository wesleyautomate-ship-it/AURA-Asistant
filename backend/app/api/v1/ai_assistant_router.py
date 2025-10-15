"""
AI Assistant Router
==================

FastAPI router for AI assistant endpoints including:
- AI request processing
- Voice request handling
- Human expertise management
- Content delivery
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from auth.database import get_db
from auth.middleware import get_current_user, require_roles
from auth.models import User
from services.ai_request_processing_service import (
    AIRequestProcessingService,
    RequestType,
    RequestPriority,
)
from services.human_expertise_service import (
    HumanExpertiseService,
    ExpertiseArea,
    AvailabilityStatus,
)
from services.voice_processing_service import VoiceProcessingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai-assistant", tags=["AI Assistant"])

# =====================================================
# PYDANTIC MODELS
# =====================================================


class AIRequestCreate(BaseModel):
    request_type: str = Field(
        ...,
        description="Type of request (cma, presentation, marketing, compliance, general)",
    )
    request_content: str = Field(..., description="Content of the request")
    request_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional request metadata"
    )
    priority: str = Field(
        "normal", description="Request priority (low, normal, high, urgent)"
    )
    output_format: str = Field(
        "text", description="Output format (text, pdf, presentation, email, social)"
    )


class VoiceRequestResponse(BaseModel):
    voice_request_id: int
    processing_status: str
    transcription: Optional[str] = None
    transcription_confidence: Optional[float] = None
    processed_request: Optional[str] = None
    language_detected: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime


class AIRequestResponse(BaseModel):
    request_id: int
    request_type: str
    status: str
    priority: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    ai_confidence: Optional[float] = None
    human_rating: Optional[int] = None
    has_deliverable: bool = False


class HumanReviewSubmit(BaseModel):
    review_content: str = Field(..., description="Human expert review content")
    rating: int = Field(..., ge=1, le=5, description="Quality rating (1-5)")
    final_output: Optional[str] = Field(None, description="Final output content")


class ExpertRegistration(BaseModel):
    expertise_area: str = Field(..., description="Expertise area")
    specializations: List[str] = Field(..., description="List of specializations")
    languages: List[str] = Field(["English"], description="Languages spoken")
    timezone: str = Field("Asia/Dubai", description="Timezone")
    working_hours: Dict[str, str] = Field(
        {"start": "09:00", "end": "18:00"}, description="Working hours"
    )
    max_concurrent_tasks: int = Field(
        3, ge=1, le=10, description="Maximum concurrent tasks"
    )


class ExpertAvailabilityUpdate(BaseModel):
    availability_status: str = Field(
        ..., description="Availability status (available, busy, offline, on_break)"
    )


# =====================================================
# AI REQUEST ENDPOINTS
# =====================================================


@router.post("/requests", response_model=Dict[str, Any])
async def create_ai_request(
    request_data: AIRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new AI request"""
    try:
        # Check if user has brokerage
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage",
            )

        service = AIRequestProcessingService(db)

        result = await service.create_ai_request(
            agent_id=current_user.id,
            brokerage_id=current_user.brokerage_id,
            request_type=request_data.request_type,
            request_content=request_data.request_content,
            request_metadata=request_data.request_metadata,
            priority=request_data.priority,
            output_format=request_data.output_format,
        )

        return result

    except Exception as e:
        logger.error(f"Error creating AI request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI request: {str(e)}",
        )


@router.get("/requests", response_model=Dict[str, Any])
async def get_agent_requests(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get agent's AI requests"""
    try:
        service = AIRequestProcessingService(db)

        result = await service.get_agent_requests(
            agent_id=current_user.id, status=status, limit=limit, offset=offset
        )

        return result

    except Exception as e:
        logger.error(f"Error getting agent requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent requests: {str(e)}",
        )


@router.get("/requests/{request_id}", response_model=Dict[str, Any])
async def get_request_status(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get request status and details"""
    try:
        service = AIRequestProcessingService(db)

        result = await service.get_request_status(
            request_id=request_id, agent_id=current_user.id
        )

        return result

    except Exception as e:
        logger.error(f"Error getting request status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get request status: {str(e)}",
        )


@router.get("/requests/{request_id}/content", response_model=Dict[str, Any])
async def get_deliverable_content(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get deliverable content for a completed request"""
    try:
        service = AIRequestProcessingService(db)

        result = await service.get_deliverable_content(
            request_id=request_id, agent_id=current_user.id
        )

        return result

    except Exception as e:
        logger.error(f"Error getting deliverable content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deliverable content: {str(e)}",
        )


# =====================================================
# VOICE REQUEST ENDPOINTS
# =====================================================


@router.post("/voice-requests", response_model=Dict[str, Any])
async def upload_voice_request(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload voice request and start processing"""
    try:
        # Check if user has brokerage
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage",
            )

        service = VoiceProcessingService(db)

        result = await service.upload_audio_file(
            agent_id=current_user.id,
            brokerage_id=current_user.brokerage_id,
            audio_file=audio_file,
        )

        return result

    except Exception as e:
        logger.error(f"Error uploading voice request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload voice request: {str(e)}",
        )


@router.get("/voice-requests", response_model=Dict[str, Any])
async def get_voice_requests(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get agent's voice requests"""
    try:
        service = VoiceProcessingService(db)

        result = await service.get_agent_voice_requests(
            agent_id=current_user.id, status=status, limit=limit, offset=offset
        )

        return result

    except Exception as e:
        logger.error(f"Error getting voice requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voice requests: {str(e)}",
        )


@router.get("/voice-requests/{voice_request_id}", response_model=Dict[str, Any])
async def get_voice_request_status(
    voice_request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get voice request status"""
    try:
        service = VoiceProcessingService(db)

        result = await service.get_voice_request_status(
            voice_request_id=voice_request_id, agent_id=current_user.id
        )

        return result

    except Exception as e:
        logger.error(f"Error getting voice request status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voice request status: {str(e)}",
        )


# =====================================================
# HUMAN EXPERT ENDPOINTS
# =====================================================


@router.post("/experts/register", response_model=Dict[str, Any])
async def register_expert(
    expert_data: ExpertRegistration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
            max_concurrent_tasks=expert_data.max_concurrent_tasks,
        )

        return result

    except Exception as e:
        logger.error(f"Error registering expert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register expert: {str(e)}",
        )


@router.get("/experts/my-profile", response_model=Dict[str, Any])
async def get_my_expert_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's expert profile"""
    try:
        service = HumanExpertiseService(db)

        # Get expert profile
        expert = (
            db.query(service.HumanExpert)
            .filter(service.HumanExpert.user_id == current_user.id)
            .first()
        )

        if not expert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Expert profile not found"
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
                "is_active": expert.is_active,
            },
            "workload": workload,
        }

    except Exception as e:
        logger.error(f"Error getting expert profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expert profile: {str(e)}",
        )


@router.put("/experts/availability", response_model=Dict[str, Any])
async def update_expert_availability(
    availability_data: ExpertAvailabilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update expert availability status"""
    try:
        service = HumanExpertiseService(db)

        # Get expert profile
        expert = (
            db.query(service.HumanExpert)
            .filter(service.HumanExpert.user_id == current_user.id)
            .first()
        )

        if not expert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Expert profile not found"
            )

        result = await service.update_expert_availability(
            expert_id=expert.id,
            user_id=current_user.id,
            availability_status=availability_data.availability_status,
        )

        return result

    except Exception as e:
        logger.error(f"Error updating expert availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update availability: {str(e)}",
        )


@router.post("/requests/{request_id}/review", response_model=Dict[str, Any])
async def submit_human_review(
    request_id: int,
    review_data: HumanReviewSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit human expert review for a request"""
    try:
        service = AIRequestProcessingService(db)

        result = await service.submit_human_review(
            request_id=request_id,
            expert_id=current_user.id,
            review_content=review_data.review_content,
            rating=review_data.rating,
            final_output=review_data.final_output,
        )

        return result

    except Exception as e:
        logger.error(f"Error submitting human review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit review: {str(e)}",
        )


# =====================================================
# ADMIN ENDPOINTS
# =====================================================


@router.get("/experts", response_model=Dict[str, Any])
async def get_all_experts(
    expertise_area: Optional[str] = None,
    availability_status: Optional[str] = None,
    is_active: bool = True,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_roles(["admin", "brokerage_owner"])),
    db: Session = Depends(get_db),
):
    """Get all experts (admin/brokerage owner only)"""
    try:
        service = HumanExpertiseService(db)

        result = await service.get_all_experts(
            expertise_area=expertise_area,
            availability_status=availability_status,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

        return result

    except Exception as e:
        logger.error(f"Error getting all experts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get experts: {str(e)}",
        )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_ai_assistant_analytics(
    current_user: User = Depends(require_roles(["admin", "brokerage_owner"])),
    db: Session = Depends(get_db),
):
    """Get AI assistant analytics (admin/brokerage owner only)"""
    try:
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage",
            )

        ai_service = AIRequestProcessingService(db)
        voice_service = VoiceProcessingService(db)
        expert_service = HumanExpertiseService(db)

        # Get AI request analytics
        ai_analytics = await ai_service.get_brokerage_analytics(
            current_user.brokerage_id
        )

        # Get voice processing analytics
        voice_analytics = await voice_service.get_voice_processing_analytics(
            brokerage_id=current_user.brokerage_id
        )

        # Get expertise area statistics
        expert_stats = await expert_service.get_expertise_area_statistics()

        return {
            "ai_requests": ai_analytics,
            "voice_processing": voice_analytics,
            "expert_statistics": expert_stats,
            "brokerage_id": current_user.brokerage_id,
        }

    except Exception as e:
        logger.error(f"Error getting AI assistant analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}",
        )


# =====================================================
# UTILITY ENDPOINTS
# =====================================================


@router.get("/request-types", response_model=List[str])
async def get_request_types():
    """Get available request types"""
    return [rt.value for rt in RequestType]


@router.get("/expertise-areas", response_model=List[str])
async def get_expertise_areas():
    """Get available expertise areas"""
    return [ea.value for ea in ExpertiseArea]


@router.get("/availability-statuses", response_model=List[str])
async def get_availability_statuses():
    """Get available statuses"""
    return [status.value for status in AvailabilityStatus]


@router.get("/priorities", response_model=List[str])
async def get_priorities():
    """Get available priorities"""
    return [priority.value for priority in RequestPriority]


# =====================================================
# HEALTH CHECK
# =====================================================


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Assistant",
        "timestamp": datetime.utcnow(),
    }
