"""
Feedback Router - FastAPI Router for User Feedback System Endpoints

This router handles all feedback-related endpoints migrated from main.py
to maintain frontend compatibility while following the secure architecture
patterns of main_secure.py.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

# Initialize router
router = APIRouter(prefix="/feedback", tags=["User Feedback"])

# Pydantic Models
class FeedbackRequest(BaseModel):
    """Feedback request model"""

    session_id: str
    query: str
    response: str
    feedback_type: str  # "thumbs_up", "thumbs_down", "rating"
    rating: Optional[int] = None
    text_feedback: Optional[str] = ""
    category: str = "accuracy"  # accuracy, relevance, completeness, clarity, speed, data_quality, user_experience


class FeedbackSubmitResponse(BaseModel):
    """Feedback submit response model"""

    success: bool
    message: str


class FeedbackSummaryResponse(BaseModel):
    """Feedback summary response model"""

    total_feedback: int
    average_rating: float
    feedback_by_category: Dict[str, int]
    feedback_by_type: Dict[str, int]
    recent_feedback: List[Dict[str, Any]]
    quality_metrics: Dict[str, float]


class FeedbackRecommendationsResponse(BaseModel):
    """Feedback recommendations response model"""

    recommendations: List[str]


# Router Endpoints


@router.post("/submit", response_model=FeedbackSubmitResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for quality improvement"""
    try:
        from quality.feedback_system import (
            get_feedback_system,
            FeedbackEntry,
            FeedbackType,
            FeedbackCategory,
        )

        feedback_system = get_feedback_system()

        # Create feedback entry
        feedback = FeedbackEntry(
            session_id=request.session_id,
            user_id="user_id",  # TODO: Get from session
            user_role="client",  # TODO: Get from session
            query=request.query,
            response=request.response,
            feedback_type=FeedbackType(request.feedback_type),
            rating=request.rating,
            text_feedback=request.text_feedback,
            category=FeedbackCategory(request.category),
            created_at=datetime.now(),
        )

        # Submit feedback
        success = await feedback_system.submit_feedback(feedback)

        if success:
            return FeedbackSubmitResponse(
                success=True, message="Feedback submitted successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to submit feedback")

    except Exception as e:
        print(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=FeedbackSummaryResponse)
async def get_feedback_summary(
    days: int = Query(30, description="Number of days to include in summary")
):
    """Get feedback summary for quality analysis"""
    try:
        from quality.feedback_system import get_feedback_system

        feedback_system = get_feedback_system()
        summary = await feedback_system.get_feedback_summary(days)

        return FeedbackSummaryResponse(**summary)

    except Exception as e:
        print(f"Error getting feedback summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=FeedbackRecommendationsResponse)
async def get_improvement_recommendations():
    """Get improvement recommendations based on feedback"""
    try:
        from quality.feedback_system import get_feedback_system

        feedback_system = get_feedback_system()
        recommendations = await feedback_system.get_improvement_recommendations()

        return FeedbackRecommendationsResponse(recommendations=recommendations)

    except Exception as e:
        print(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
