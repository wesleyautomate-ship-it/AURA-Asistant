"""
Team Management Router
======================

This router provides API endpoints for team management, performance tracking,
and team analytics within the brokerage-centric architecture.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from auth.database import get_db
from auth.token_manager import get_current_user
from auth.models import User
from services.brokerage_management_service import BrokerageManagementService
from app.domain.listings.brokerage_models import TeamPerformance, AgentConsistencyMetric

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/team", tags=["Team Management"])
security = HTTPBearer()

# =====================================================
# PYDANTIC MODELS
# =====================================================

class TeamMemberResponse(BaseModel):
    """Response model for team member information"""
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeamPerformanceRequest(BaseModel):
    """Request model for team performance data"""
    agent_id: int
    metric_name: str
    metric_value: float
    period_start: datetime
    period_end: datetime
    metadata: Optional[Dict[str, Any]] = {}

class TeamPerformanceResponse(BaseModel):
    """Response model for team performance data"""
    id: int
    agent_id: int
    metric_name: str
    metric_value: float
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeamAnalyticsResponse(BaseModel):
    """Response model for team analytics"""
    brokerage_id: int
    total_agents: int
    active_agents: int
    average_consistency_score: float
    performance_metrics_count: int
    agent_consistency_scores: List[float]
    generated_at: str

class AddTeamMemberRequest(BaseModel):
    """Request model for adding team member"""
    user_id: int

# =====================================================
# TEAM MEMBER MANAGEMENT
# =====================================================

@router.get("/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    brokerage_id: int = Query(..., description="Brokerage ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all team members for a brokerage"""
    try:
        # Verify user has access to this brokerage
        if current_user.brokerage_id != brokerage_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage"
            )
        
        service = BrokerageManagementService(db)
        team_members = await service.get_team_members(brokerage_id)
        
        return team_members
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get team members: {str(e)}"
        )

@router.post("/members/add")
async def add_team_member(
    brokerage_id: int,
    request: AddTeamMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a user to the brokerage team"""
    try:
        # Verify user has permission to add team members
        if current_user.role not in ['brokerage_owner', 'admin']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to add team members"
            )
        
        # Verify user has access to this brokerage
        if current_user.brokerage_id != brokerage_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage"
            )
        
        service = BrokerageManagementService(db)
        success = await service.add_team_member(brokerage_id, request.user_id)
        
        if success:
            return {
                "message": "Team member added successfully",
                "user_id": request.user_id,
                "brokerage_id": brokerage_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add team member"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding team member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add team member: {str(e)}"
        )

@router.delete("/members/{user_id}")
async def remove_team_member(
    brokerage_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a user from the brokerage team"""
    try:
        # Verify user has permission to remove team members
        if current_user.role not in ['brokerage_owner', 'admin']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to remove team members"
            )
        
        # Verify user has access to this brokerage
        if current_user.brokerage_id != brokerage_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage"
            )
        
        service = BrokerageManagementService(db)
        success = await service.remove_team_member(brokerage_id, user_id)
        
        if success:
            return {
                "message": "Team member removed successfully",
                "user_id": user_id,
                "brokerage_id": brokerage_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to remove team member"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing team member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove team member: {str(e)}"
        )

# =====================================================
# TEAM PERFORMANCE TRACKING
# =====================================================

@router.post("/performance", response_model=TeamPerformanceResponse)
async def add_team_performance(
    brokerage_id: int,
    request: TeamPerformanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add team performance metrics"""
    try:
        # Verify user has permission to add performance metrics
        if current_user.role not in ['brokerage_owner', 'admin', 'agent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to add performance metrics"
            )
        
        # Verify user has access to this brokerage
        if current_user.brokerage_id != brokerage_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage"
            )
        
        # Create performance record
        performance = TeamPerformance(
            brokerage_id=brokerage_id,
            agent_id=request.agent_id,
            metric_name=request.metric_name,
            metric_value=request.metric_value,
            period_start=request.period_start.date(),
            period_end=request.period_end.date(),
            metadata=request.metadata
        )
        
        db.add(performance)
        db.commit()
        db.refresh(performance)
        
        logger.info(f"Added performance metric for agent {request.agent_id}: {request.metric_name}")
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding team performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add team performance: {str(e)}"
        )

@router.get("/performance", response_model=List[TeamPerformanceResponse])
async def get_team_performance(
    brokerage_id: int = Query(..., description="Brokerage ID"),
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    period_days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team performance metrics"""
    try:
        # Verify user has access to this brokerage
        if current_user.brokerage_id != brokerage_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage"
            )
        
        # Build query
        query = db.query(TeamPerformance).filter(
            TeamPerformance.brokerage_id == brokerage_id
        )
        
        # Apply filters
        if agent_id:
            query = query.filter(TeamPerformance.agent_id == agent_id)
        
        if metric_name:
            query = query.filter(TeamPerformance.metric_name == metric_name)
        
        # Date filter
        start_date = datetime.utcnow() - timedelta(days=period_days)
        query = query.filter(TeamPerformance.period_start >= start_date.date())
        
        # Order by most recent
        query = query.order_by(TeamPerformance.created_at.desc())
        
        performance_metrics = query.all()
        return performance_metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get team performance: {str(e)}"
        )

# =====================================================
# TEAM ANALYTICS
# =====================================================

@router.get("/analytics", response_model=TeamAnalyticsResponse)
async def get_team_analytics(
    brokerage_id: int = Query(..., description="Brokerage ID"),
    period_days: int = Query(30, description="Number of days for analytics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive team analytics"""
    try:
        # Verify user has access to this brokerage
        if current_user.brokerage_id != brokerage_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage"
            )
        
        service = BrokerageManagementService(db)
        analytics = await service.get_team_performance_summary(brokerage_id, period_days)
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get team analytics: {str(e)}"
        )

@router.get("/consistency-metrics")
async def get_agent_consistency_metrics(
    brokerage_id: int = Query(..., description="Brokerage ID"),
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    period: str = Query("monthly", description="Period: daily, weekly, monthly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get agent consistency metrics"""
    try:
        # Verify user has access to this brokerage
        if current_user.brokerage_id != brokerage_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage"
            )
        
        # Build query
        query = db.query(AgentConsistencyMetric).filter(
            AgentConsistencyMetric.brokerage_id == brokerage_id,
            AgentConsistencyMetric.period == period
        )
        
        if agent_id:
            query = query.filter(AgentConsistencyMetric.agent_id == agent_id)
        
        # Order by most recent
        query = query.order_by(AgentConsistencyMetric.calculated_at.desc())
        
        metrics = query.all()
        
        return {
            "brokerage_id": brokerage_id,
            "period": period,
            "metrics": [
                {
                    "id": m.id,
                    "agent_id": m.agent_id,
                    "consistency_score": float(m.consistency_score),
                    "metrics": m.metrics_dict,
                    "calculated_at": m.calculated_at.isoformat()
                }
                for m in metrics
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent consistency metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent consistency metrics: {str(e)}"
        )

# =====================================================
# TEAM DASHBOARD DATA
# =====================================================

@router.get("/dashboard")
async def get_team_dashboard(
    brokerage_id: int = Query(..., description="Brokerage ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team dashboard data"""
    try:
        # Verify user has access to this brokerage
        if current_user.brokerage_id != brokerage_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage"
            )
        
        service = BrokerageManagementService(db)
        
        # Get various dashboard data
        team_members = await service.get_team_members(brokerage_id)
        performance_summary = await service.get_team_performance_summary(brokerage_id)
        analytics = await service.get_brokerage_analytics(brokerage_id)
        
        # Calculate additional metrics
        active_agents = len([m for m in team_members if m.role in ['agent', 'brokerage_owner']])
        recent_performance = performance_summary.get('average_consistency_score', 0)
        
        dashboard_data = {
            "brokerage_id": brokerage_id,
            "team_overview": {
                "total_members": len(team_members),
                "active_agents": active_agents,
                "average_consistency_score": recent_performance
            },
            "performance_summary": performance_summary,
            "analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get team dashboard: {str(e)}"
        )
