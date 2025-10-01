"""
Human Expertise Management Service
=================================

This service manages the network of human experts who review and refine AI output:
- Expert registration and management
- Expertise area assignment
- Workload balancing
- Quality tracking and performance metrics
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from fastapi import HTTPException, status
import json

from app.domain.listings.ai_assistant_models import HumanExpert, AIRequest
from auth.models import User
from app.domain.listings.brokerage_models import Brokerage

logger = logging.getLogger(__name__)

class ExpertiseArea(str, Enum):
    """Expertise areas for human experts"""
    MARKET_ANALYSIS = "market_analysis"
    PRESENTATIONS = "presentations"
    COMPLIANCE = "compliance"
    MARKETING = "marketing"
    GENERAL = "general"
    LEGAL = "legal"
    FINANCIAL = "financial"
    TECHNICAL = "technical"

class AvailabilityStatus(str, Enum):
    """Expert availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ON_BREAK = "on_break"

class HumanExpertiseService:
    """Service for managing human experts and their expertise"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================
    # EXPERT REGISTRATION AND MANAGEMENT
    # =====================================================
    
    async def register_expert(
        self,
        user_id: int,
        expertise_area: str,
        specializations: List[str],
        languages: List[str] = None,
        timezone: str = "Asia/Dubai",
        working_hours: Dict[str, str] = None,
        max_concurrent_tasks: int = 3
    ) -> Dict[str, Any]:
        """Register a new human expert"""
        try:
            # Check if user already has expert profile
            existing_expert = self.db.query(HumanExpert).filter(
                HumanExpert.user_id == user_id
            ).first()
            
            if existing_expert:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has an expert profile"
                )
            
            # Validate expertise area
            if expertise_area not in [ea.value for ea in ExpertiseArea]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid expertise area: {expertise_area}"
                )
            
            # Create expert profile
            expert = HumanExpert(
                user_id=user_id,
                expertise_area=expertise_area,
                specializations=specializations,
                languages=languages or ["English"],
                timezone=timezone,
                working_hours=working_hours or {"start": "09:00", "end": "18:00"},
                max_concurrent_tasks=max_concurrent_tasks,
                availability_status=AvailabilityStatus.AVAILABLE,
                rating=5.00,  # Default rating for new experts
                is_active=True
            )
            
            self.db.add(expert)
            self.db.commit()
            self.db.refresh(expert)
            
            logger.info(f"Registered new expert {user_id} with expertise {expertise_area}")
            
            return {
                "expert_id": expert.id,
                "user_id": expert.user_id,
                "expertise_area": expert.expertise_area,
                "availability_status": expert.availability_status,
                "message": "Expert registered successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error registering expert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register expert: {str(e)}"
            )
    
    async def update_expert_profile(
        self,
        expert_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update expert profile"""
        try:
            expert = self.db.query(HumanExpert).filter(
                and_(
                    HumanExpert.id == expert_id,
                    HumanExpert.user_id == user_id
                )
            ).first()
            
            if not expert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expert profile not found"
                )
            
            # Update allowed fields
            allowed_fields = [
                'expertise_area', 'specializations', 'languages', 'timezone',
                'working_hours', 'max_concurrent_tasks', 'availability_status'
            ]
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(expert, field):
                    setattr(expert, field, value)
            
            expert.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated expert profile {expert_id}")
            
            return {
                "expert_id": expert.id,
                "message": "Expert profile updated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating expert profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update expert profile: {str(e)}"
            )
    
    async def deactivate_expert(self, expert_id: int, user_id: int) -> Dict[str, Any]:
        """Deactivate expert profile"""
        try:
            expert = self.db.query(HumanExpert).filter(
                and_(
                    HumanExpert.id == expert_id,
                    HumanExpert.user_id == user_id
                )
            ).first()
            
            if not expert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expert profile not found"
                )
            
            expert.is_active = False
            expert.availability_status = AvailabilityStatus.OFFLINE
            self.db.commit()
            
            logger.info(f"Deactivated expert {expert_id}")
            
            return {
                "expert_id": expert.id,
                "message": "Expert deactivated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating expert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to deactivate expert: {str(e)}"
            )
    
    # =====================================================
    # EXPERT DISCOVERY AND ASSIGNMENT
    # =====================================================
    
    async def find_available_expert(
        self,
        expertise_area: str,
        required_specializations: List[str] = None,
        language: str = "English",
        exclude_expert_ids: List[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Find an available expert for a specific task"""
        try:
            query = self.db.query(HumanExpert).filter(
                and_(
                    HumanExpert.expertise_area == expertise_area,
                    HumanExpert.availability_status == AvailabilityStatus.AVAILABLE,
                    HumanExpert.is_active == True
                )
            )
            
            # Filter by specializations if required
            if required_specializations:
                query = query.filter(
                    or_(*[
                        func.array_to_string(HumanExpert.specializations, ',').ilike(f'%{spec}%')
                        for spec in required_specializations
                    ])
                )
            
            # Filter by language
            query = query.filter(
                func.array_to_string(HumanExpert.languages, ',').ilike(f'%{language}%')
            )
            
            # Exclude specific experts
            if exclude_expert_ids:
                query = query.filter(~HumanExpert.id.in_(exclude_expert_ids))
            
            # Order by rating and current workload
            experts = query.order_by(
                desc(HumanExpert.rating),
                HumanExpert.completed_tasks
            ).all()
            
            # Find expert with capacity
            for expert in experts:
                current_tasks = self.db.query(AIRequest).filter(
                    and_(
                        AIRequest.human_expert_id == expert.user_id,
                        AIRequest.status.in_(["processing", "human_review"])
                    )
                ).count()
                
                if current_tasks < expert.max_concurrent_tasks:
                    return {
                        "expert_id": expert.id,
                        "user_id": expert.user_id,
                        "expertise_area": expert.expertise_area,
                        "rating": float(expert.rating),
                        "specializations": expert.specializations,
                        "languages": expert.languages,
                        "current_tasks": current_tasks,
                        "max_tasks": expert.max_concurrent_tasks
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding available expert: {e}")
            return None
    
    async def assign_expert_to_request(
        self,
        request_id: int,
        expert_id: int
    ) -> Dict[str, Any]:
        """Assign expert to a specific request"""
        try:
            # Get request
            request = self.db.query(AIRequest).filter(AIRequest.id == request_id).first()
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found"
                )
            
            # Get expert
            expert = self.db.query(HumanExpert).filter(HumanExpert.id == expert_id).first()
            if not expert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expert not found"
                )
            
            # Check if expert is available
            if expert.availability_status != AvailabilityStatus.AVAILABLE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Expert is not available"
                )
            
            # Check expert capacity
            current_tasks = self.db.query(AIRequest).filter(
                and_(
                    AIRequest.human_expert_id == expert.user_id,
                    AIRequest.status.in_(["processing", "human_review"])
                )
            ).count()
            
            if current_tasks >= expert.max_concurrent_tasks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Expert has reached maximum concurrent tasks"
                )
            
            # Assign expert
            request.human_expert_id = expert.user_id
            request.status = "human_review"
            self.db.commit()
            
            logger.info(f"Assigned expert {expert_id} to request {request_id}")
            
            return {
                "request_id": request_id,
                "expert_id": expert_id,
                "expert_name": expert.user.full_name if expert.user else "Unknown",
                "message": "Expert assigned successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning expert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to assign expert: {str(e)}"
            )
    
    # =====================================================
    # EXPERT WORKLOAD AND PERFORMANCE
    # =====================================================
    
    async def get_expert_workload(self, expert_id: int) -> Dict[str, Any]:
        """Get expert's current workload"""
        try:
            expert = self.db.query(HumanExpert).filter(HumanExpert.id == expert_id).first()
            if not expert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expert not found"
                )
            
            # Get current tasks
            current_tasks = self.db.query(AIRequest).filter(
                and_(
                    AIRequest.human_expert_id == expert.user_id,
                    AIRequest.status.in_(["processing", "human_review"])
                )
            ).all()
            
            # Get recent completed tasks
            recent_completed = self.db.query(AIRequest).filter(
                and_(
                    AIRequest.human_expert_id == expert.user_id,
                    AIRequest.status == "completed",
                    AIRequest.actual_completion >= datetime.utcnow() - timedelta(days=7)
                )
            ).count()
            
            return {
                "expert_id": expert.id,
                "user_id": expert.user_id,
                "availability_status": expert.availability_status,
                "current_tasks": len(current_tasks),
                "max_concurrent_tasks": expert.max_concurrent_tasks,
                "capacity_utilization": (len(current_tasks) / expert.max_concurrent_tasks) * 100,
                "recent_completed": recent_completed,
                "total_completed": expert.completed_tasks,
                "rating": float(expert.rating),
                "tasks": [
                    {
                        "request_id": task.id,
                        "request_type": task.request_type,
                        "priority": task.priority,
                        "status": task.status,
                        "created_at": task.created_at
                    }
                    for task in current_tasks
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting expert workload: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get expert workload: {str(e)}"
            )
    
    async def update_expert_availability(
        self,
        expert_id: int,
        user_id: int,
        availability_status: str
    ) -> Dict[str, Any]:
        """Update expert availability status"""
        try:
            if availability_status not in [status.value for status in AvailabilityStatus]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid availability status: {availability_status}"
                )
            
            expert = self.db.query(HumanExpert).filter(
                and_(
                    HumanExpert.id == expert_id,
                    HumanExpert.user_id == user_id
                )
            ).first()
            
            if not expert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expert not found"
                )
            
            expert.availability_status = availability_status
            expert.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated expert {expert_id} availability to {availability_status}")
            
            return {
                "expert_id": expert.id,
                "availability_status": expert.availability_status,
                "message": "Availability updated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating expert availability: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update availability: {str(e)}"
            )
    
    # =====================================================
    # EXPERT ANALYTICS AND REPORTING
    # =====================================================
    
    async def get_expert_performance_metrics(
        self,
        expert_id: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get expert performance metrics"""
        try:
            expert = self.db.query(HumanExpert).filter(HumanExpert.id == expert_id).first()
            if not expert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Expert not found"
                )
            
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            # Get completed tasks in period
            completed_tasks = self.db.query(AIRequest).filter(
                and_(
                    AIRequest.human_expert_id == expert.user_id,
                    AIRequest.status == "completed",
                    AIRequest.actual_completion >= start_date
                )
            ).all()
            
            # Calculate metrics
            total_tasks = len(completed_tasks)
            avg_rating = sum(task.human_rating for task in completed_tasks if task.human_rating) / total_tasks if total_tasks > 0 else 0
            
            # Calculate average completion time
            completion_times = []
            for task in completed_tasks:
                if task.actual_completion and task.created_at:
                    completion_time = (task.actual_completion - task.created_at).total_seconds() / 3600  # hours
                    completion_times.append(completion_time)
            
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            
            # Get task type breakdown
            type_breakdown = {}
            for task in completed_tasks:
                task_type = task.request_type
                type_breakdown[task_type] = type_breakdown.get(task_type, 0) + 1
            
            return {
                "expert_id": expert.id,
                "period_days": period_days,
                "total_tasks": total_tasks,
                "average_rating": float(avg_rating),
                "average_completion_time_hours": round(avg_completion_time, 2),
                "task_type_breakdown": type_breakdown,
                "overall_rating": float(expert.rating),
                "total_completed_all_time": expert.completed_tasks,
                "specializations": expert.specializations,
                "languages": expert.languages
            }
            
        except Exception as e:
            logger.error(f"Error getting expert performance metrics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get performance metrics: {str(e)}"
            )
    
    async def get_all_experts(
        self,
        expertise_area: Optional[str] = None,
        availability_status: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get all experts with filtering"""
        try:
            query = self.db.query(HumanExpert)
            
            if expertise_area:
                query = query.filter(HumanExpert.expertise_area == expertise_area)
            
            if availability_status:
                query = query.filter(HumanExpert.availability_status == availability_status)
            
            if is_active is not None:
                query = query.filter(HumanExpert.is_active == is_active)
            
            total = query.count()
            experts = query.order_by(desc(HumanExpert.rating)).offset(offset).limit(limit).all()
            
            return {
                "experts": [
                    {
                        "expert_id": expert.id,
                        "user_id": expert.user_id,
                        "expertise_area": expert.expertise_area,
                        "specializations": expert.specializations,
                        "languages": expert.languages,
                        "availability_status": expert.availability_status,
                        "rating": float(expert.rating),
                        "completed_tasks": expert.completed_tasks,
                        "max_concurrent_tasks": expert.max_concurrent_tasks,
                        "is_active": expert.is_active,
                        "created_at": expert.created_at
                    }
                    for expert in experts
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting all experts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get experts: {str(e)}"
            )
    
    async def get_expertise_area_statistics(self) -> Dict[str, Any]:
        """Get statistics by expertise area"""
        try:
            # Get expert count by expertise area
            area_stats = self.db.query(
                HumanExpert.expertise_area,
                func.count(HumanExpert.id).label('expert_count'),
                func.avg(HumanExpert.rating).label('avg_rating'),
                func.sum(HumanExpert.completed_tasks).label('total_tasks')
            ).filter(
                HumanExpert.is_active == True
            ).group_by(HumanExpert.expertise_area).all()
            
            # Get availability breakdown
            availability_stats = self.db.query(
                HumanExpert.availability_status,
                func.count(HumanExpert.id).label('count')
            ).filter(
                HumanExpert.is_active == True
            ).group_by(HumanExpert.availability_status).all()
            
            return {
                "expertise_areas": {
                    stat.expertise_area: {
                        "expert_count": stat.expert_count,
                        "average_rating": float(stat.avg_rating) if stat.avg_rating else 0,
                        "total_tasks": stat.total_tasks or 0
                    }
                    for stat in area_stats
                },
                "availability_breakdown": {
                    stat.availability_status: stat.count
                    for stat in availability_stats
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting expertise area statistics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get statistics: {str(e)}"
            )
