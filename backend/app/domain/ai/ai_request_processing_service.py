"""
AI Request Processing Service
============================

This service handles AI request processing with human expertise integration:
- Request intake and processing
- AI response generation
- Human expert assignment and review
- Content delivery and quality assurance
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from fastapi import HTTPException, status
import json
import asyncio
from enum import Enum

from app.domain.listings.ai_assistant_models import (
    AIRequest,
    HumanExpert,
    ContentDeliverable,
    VoiceRequest,
)
from app.domain.listings.brokerage_models import Brokerage
from auth.models import User

logger = logging.getLogger(__name__)

class RequestType(str, Enum):
    """AI request types"""
    CMA = "cma"
    PRESENTATION = "presentation"
    MARKETING = "marketing"
    COMPLIANCE = "compliance"
    GENERAL = "general"
    FOLLOW_UP = "follow_up"
    REPORT = "report"
    SOCIAL_MEDIA = "social_media"

class RequestStatus(str, Enum):
    """AI request status"""
    PENDING = "pending"
    PROCESSING = "processing"
    AI_COMPLETE = "ai_complete"
    HUMAN_REVIEW = "human_review"
    COMPLETED = "completed"
    FAILED = "failed"

class RequestPriority(str, Enum):
    """Request priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class AIRequestProcessingService:
    """Service for AI request processing with human expertise"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================
    # REQUEST CREATION AND MANAGEMENT
    # =====================================================
    
    async def create_ai_request(
        self,
        agent_id: int,
        brokerage_id: int,
        request_type: str,
        request_content: str,
        request_metadata: Optional[Dict[str, Any]] = None,
        priority: str = RequestPriority.NORMAL,
        output_format: str = "text"
    ) -> Dict[str, Any]:
        """Create a new AI request"""
        try:
            # Validate request type
            if request_type not in [rt.value for rt in RequestType]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid request type: {request_type}"
                )
            
            # Create AI request
            ai_request = AIRequest(
                agent_id=agent_id,
                brokerage_id=brokerage_id,
                request_type=request_type,
                request_content=request_content,
                request_metadata=request_metadata or {},
                priority=priority,
                output_format=output_format,
                status=RequestStatus.PENDING,
                estimated_completion=self._calculate_estimated_completion(request_type, priority)
            )
            
            self.db.add(ai_request)
            self.db.commit()
            self.db.refresh(ai_request)
            
            # Start processing
            await self._start_processing(ai_request.id)
            
            logger.info(f"Created AI request {ai_request.id} for agent {agent_id}")
            
            return {
                "request_id": ai_request.id,
                "status": ai_request.status,
                "estimated_completion": ai_request.estimated_completion,
                "message": "Request created successfully and processing started"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating AI request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create AI request: {str(e)}"
            )
    
    async def create_voice_request(
        self,
        agent_id: int,
        brokerage_id: int,
        audio_file_path: str,
        audio_duration: Optional[int] = None,
        audio_format: Optional[str] = None,
        file_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a voice request from audio file"""
        try:
            # Create voice request
            voice_request = VoiceRequest(
                agent_id=agent_id,
                brokerage_id=brokerage_id,
                audio_file_path=audio_file_path,
                audio_duration=audio_duration,
                audio_format=audio_format,
                file_size=file_size,
                processing_status="pending"
            )
            
            self.db.add(voice_request)
            self.db.commit()
            self.db.refresh(voice_request)
            
            # Start voice processing
            await self._process_voice_request(voice_request.id)
            
            logger.info(f"Created voice request {voice_request.id} for agent {agent_id}")
            
            return {
                "voice_request_id": voice_request.id,
                "status": voice_request.processing_status,
                "message": "Voice request created and processing started"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating voice request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create voice request: {str(e)}"
            )
    
    # =====================================================
    # REQUEST PROCESSING
    # =====================================================
    
    async def _start_processing(self, request_id: int) -> None:
        """Start processing an AI request"""
        try:
            request = self.db.query(AIRequest).filter(AIRequest.id == request_id).first()
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="AI request not found"
                )
            
            # Update status to processing
            request.status = RequestStatus.PROCESSING
            self.db.commit()
            
            # Generate AI response
            ai_response = await self._generate_ai_response(request)
            
            # Update request with AI response
            request.ai_response = ai_response["content"]
            request.ai_confidence = ai_response["confidence"]
            
            # Check if this is a contract-related request that needs human review
            if self._requires_human_review(request):
                request.status = RequestStatus.AI_COMPLETE
                self.db.commit()
                # Assign human expert for contract review
                await self._assign_human_expert(request_id)
            else:
                # For all other content, mark as completed directly
                request.status = RequestStatus.COMPLETED
                request.actual_completion = datetime.utcnow()
                self.db.commit()
                logger.info(f"AI content generated and completed directly for request {request_id}")
            
            logger.info(f"AI processing completed for request {request_id}")
            
        except Exception as e:
            logger.error(f"Error processing AI request {request_id}: {e}")
            # Update status to failed
            request = self.db.query(AIRequest).filter(AIRequest.id == request_id).first()
            if request:
                request.status = RequestStatus.FAILED
                self.db.commit()
    
    async def _generate_ai_response(self, request: AIRequest) -> Dict[str, Any]:
        """Generate AI response for the request"""
        try:
            # This would integrate with your AI service (Google Gemini, etc.)
            # For now, we'll simulate the response
            
            response_templates = {
                RequestType.CMA: {
                    "content": f"Comparative Market Analysis for {request.request_content}:\n\nBased on recent market data, here's a comprehensive CMA...",
                    "confidence": 0.85
                },
                RequestType.PRESENTATION: {
                    "content": f"Listing Presentation for {request.request_content}:\n\nProfessional presentation slides with market insights...",
                    "confidence": 0.90
                },
                RequestType.MARKETING: {
                    "content": f"Marketing Content for {request.request_content}:\n\nEngaging marketing materials tailored for your target audience...",
                    "confidence": 0.88
                },
                RequestType.COMPLIANCE: {
                    "content": f"Compliance Documentation for {request.request_content}:\n\nRERA-compliant documents and regulatory requirements...",
                    "confidence": 0.92
                },
                RequestType.GENERAL: {
                    "content": f"Response to: {request.request_content}\n\nHere's a comprehensive response to your inquiry...",
                    "confidence": 0.80
                }
            }
            
            template = response_templates.get(request.request_type, response_templates[RequestType.GENERAL])
            
            return {
                "content": template["content"],
                "confidence": template["confidence"]
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "content": "I apologize, but I encountered an error processing your request. Please try again or contact support.",
                "confidence": 0.0
            }
    
    def _requires_human_review(self, request: AIRequest) -> bool:
        """Determine if a request requires human review (only for contracts)"""
        # Only contract-related requests need human review
        contract_keywords = [
            'contract', 'agreement', 'lease', 'purchase', 'sale', 
            'legal', 'terms', 'conditions', 'clause', 'liability',
            'warranty', 'indemnity', 'breach', 'termination'
        ]
        
        # Check request content for contract-related keywords
        request_text = (request.request_content or "").lower()
        if any(keyword in request_text for keyword in contract_keywords):
            return True
            
        # Check request type - compliance might include contracts
        if request.request_type == RequestType.COMPLIANCE:
            return True
            
        return False
    
    async def _assign_human_expert(self, request_id: int) -> None:
        """Assign a human expert for review"""
        try:
            request = self.db.query(AIRequest).filter(AIRequest.id == request_id).first()
            if not request:
                return
            
            # Find available expert based on expertise area
            expertise_mapping = {
                RequestType.CMA: "market_analysis",
                RequestType.PRESENTATION: "presentations",
                RequestType.MARKETING: "marketing",
                RequestType.COMPLIANCE: "compliance",
                RequestType.GENERAL: "general"
            }
            
            required_expertise = expertise_mapping.get(request.request_type, "general")
            
            # Find available expert
            expert = self.db.query(HumanExpert).filter(
                and_(
                    HumanExpert.expertise_area == required_expertise,
                    HumanExpert.availability_status == "available",
                    HumanExpert.is_active == True
                )
            ).first()
            
            if expert:
                request.human_expert_id = expert.user_id
                request.status = RequestStatus.HUMAN_REVIEW
                self.db.commit()
                
                logger.info(f"Assigned expert {expert.user_id} to request {request_id}")
            else:
                # No expert available, mark as completed with AI response only
                request.status = RequestStatus.COMPLETED
                request.actual_completion = datetime.utcnow()
                self.db.commit()
                
                logger.warning(f"No expert available for request {request_id}, completed with AI response only")
            
        except Exception as e:
            logger.error(f"Error assigning human expert for request {request_id}: {e}")
    
    async def _process_voice_request(self, voice_request_id: int) -> None:
        """Process voice request (transcription and request creation)"""
        try:
            voice_request = self.db.query(VoiceRequest).filter(VoiceRequest.id == voice_request_id).first()
            if not voice_request:
                return
            
            # Update status to transcribing
            voice_request.processing_status = "transcribing"
            self.db.commit()
            
            # Simulate voice-to-text transcription
            # In real implementation, this would use a speech-to-text service
            transcription = f"Transcribed content from audio file: {voice_request.audio_file_path}"
            processed_request = f"Processed request: Create a CMA for the property mentioned in the audio"
            
            voice_request.transcription = transcription
            voice_request.processed_request = processed_request
            voice_request.transcription_confidence = 0.85
            voice_request.processing_status = "processed"
            self.db.commit()
            
            # Create AI request from processed voice request
            await self.create_ai_request(
                agent_id=voice_request.agent_id,
                brokerage_id=voice_request.brokerage_id,
                request_type=RequestType.CMA,
                request_content=processed_request,
                request_metadata={
                    "voice_request_id": voice_request_id,
                    "transcription": transcription,
                    "audio_duration": voice_request.audio_duration
                }
            )
            
            logger.info(f"Voice request {voice_request_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing voice request {voice_request_id}: {e}")
            voice_request = self.db.query(VoiceRequest).filter(VoiceRequest.id == voice_request_id).first()
            if voice_request:
                voice_request.processing_status = "failed"
                voice_request.error_message = str(e)
                self.db.commit()
    
    # =====================================================
    # HUMAN EXPERT REVIEW
    # =====================================================
    
    async def submit_human_review(
        self,
        request_id: int,
        expert_id: int,
        review_content: str,
        rating: int,
        final_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit human expert review"""
        try:
            request = self.db.query(AIRequest).filter(
                and_(
                    AIRequest.id == request_id,
                    AIRequest.human_expert_id == expert_id
                )
            ).first()
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found or not assigned to this expert"
                )
            
            # Update request with human review
            request.human_review = review_content
            request.human_rating = rating
            request.final_output = final_output or request.ai_response
            request.status = RequestStatus.COMPLETED
            request.actual_completion = datetime.utcnow()
            self.db.commit()
            
            # Update expert statistics
            expert = self.db.query(HumanExpert).filter(HumanExpert.user_id == expert_id).first()
            if expert:
                expert.completed_tasks += 1
                # Update rating (simple average for now)
                if expert.rating:
                    expert.rating = (expert.rating + rating) / 2
                else:
                    expert.rating = rating
                self.db.commit()
            
            # Create content deliverable
            await self._create_content_deliverable(request_id)
            
            logger.info(f"Human review submitted for request {request_id}")
            
            return {
                "request_id": request_id,
                "status": request.status,
                "message": "Review submitted successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error submitting human review: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to submit review: {str(e)}"
            )
    
    async def _create_content_deliverable(self, request_id: int) -> None:
        """Create content deliverable from completed request"""
        try:
            request = self.db.query(AIRequest).filter(AIRequest.id == request_id).first()
            if not request:
                return
            
            # Determine content type based on request type
            content_type_mapping = {
                RequestType.CMA: "cma",
                RequestType.PRESENTATION: "presentation",
                RequestType.MARKETING: "marketing",
                RequestType.COMPLIANCE: "document",
                RequestType.GENERAL: "document"
            }
            
            content_type = content_type_mapping.get(request.request_type, "document")
            
            # Create deliverable
            deliverable = ContentDeliverable(
                request_id=request_id,
                content_type=content_type,
                content_data=request.final_output,
                mime_type="text/plain",
                branding_applied=False,  # Would be applied based on brokerage settings
                quality_score=request.human_rating / 5.0 if request.human_rating else 0.8
            )
            
            self.db.add(deliverable)
            self.db.commit()
            
            logger.info(f"Content deliverable created for request {request_id}")
            
        except Exception as e:
            logger.error(f"Error creating content deliverable: {e}")
    
    # =====================================================
    # REQUEST RETRIEVAL AND STATUS
    # =====================================================
    
    async def get_request_status(self, request_id: int, agent_id: int) -> Dict[str, Any]:
        """Get request status and details"""
        try:
            request = self.db.query(AIRequest).filter(
                and_(
                    AIRequest.id == request_id,
                    AIRequest.agent_id == agent_id
                )
            ).first()
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found"
                )
            
            return {
                "request_id": request.id,
                "request_type": request.request_type,
                "status": request.status,
                "priority": request.priority,
                "created_at": request.created_at,
                "estimated_completion": request.estimated_completion,
                "actual_completion": request.actual_completion,
                "ai_confidence": float(request.ai_confidence) if request.ai_confidence else None,
                "human_rating": request.human_rating,
                "has_deliverable": len(request.content_deliverables) > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting request status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get request status: {str(e)}"
            )
    
    async def get_agent_requests(
        self,
        agent_id: int,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get agent's AI requests"""
        try:
            query = self.db.query(AIRequest).filter(AIRequest.agent_id == agent_id)
            
            if status:
                query = query.filter(AIRequest.status == status)
            
            total = query.count()
            requests = query.order_by(desc(AIRequest.created_at)).offset(offset).limit(limit).all()
            
            return {
                "requests": [
                    {
                        "request_id": req.id,
                        "request_type": req.request_type,
                        "status": req.status,
                        "priority": req.priority,
                        "created_at": req.created_at,
                        "estimated_completion": req.estimated_completion,
                        "actual_completion": req.actual_completion,
                        "ai_confidence": float(req.ai_confidence) if req.ai_confidence else None,
                        "human_rating": req.human_rating
                    }
                    for req in requests
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting agent requests: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get agent requests: {str(e)}"
            )
    
    async def get_deliverable_content(self, request_id: int, agent_id: int) -> Dict[str, Any]:
        """Get deliverable content for a request"""
        try:
            request = self.db.query(AIRequest).filter(
                and_(
                    AIRequest.id == request_id,
                    AIRequest.agent_id == agent_id,
                    AIRequest.status == RequestStatus.COMPLETED
                )
            ).first()
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found or not completed"
                )
            
            deliverable = request.content_deliverables[0] if request.content_deliverables else None
            
            if not deliverable:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No deliverable found for this request"
                )
            
            # Update download count
            deliverable.download_count += 1
            self.db.commit()
            
            return {
                "request_id": request_id,
                "content_type": deliverable.content_type,
                "content_data": deliverable.content_data,
                "mime_type": deliverable.mime_type,
                "quality_score": float(deliverable.quality_score) if deliverable.quality_score else None,
                "created_at": deliverable.created_at,
                "download_count": deliverable.download_count
            }
            
        except Exception as e:
            logger.error(f"Error getting deliverable content: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get deliverable content: {str(e)}"
            )
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    def _calculate_estimated_completion(self, request_type: str, priority: str) -> datetime:
        """Calculate estimated completion time"""
        base_times = {
            RequestType.CMA: timedelta(hours=2),
            RequestType.PRESENTATION: timedelta(hours=4),
            RequestType.MARKETING: timedelta(hours=1),
            RequestType.COMPLIANCE: timedelta(hours=3),
            RequestType.GENERAL: timedelta(hours=1)
        }
        
        priority_multipliers = {
            RequestPriority.URGENT: 0.5,
            RequestPriority.HIGH: 0.75,
            RequestPriority.NORMAL: 1.0,
            RequestPriority.LOW: 1.5
        }
        
        base_time = base_times.get(request_type, timedelta(hours=1))
        multiplier = priority_multipliers.get(priority, 1.0)
        
        return datetime.utcnow() + (base_time * multiplier)
    
    async def get_brokerage_analytics(self, brokerage_id: int) -> Dict[str, Any]:
        """Get analytics for a brokerage"""
        try:
            # Get request statistics
            total_requests = self.db.query(AIRequest).filter(
                AIRequest.brokerage_id == brokerage_id
            ).count()
            
            completed_requests = self.db.query(AIRequest).filter(
                and_(
                    AIRequest.brokerage_id == brokerage_id,
                    AIRequest.status == RequestStatus.COMPLETED
                )
            ).count()
            
            avg_rating = self.db.query(func.avg(AIRequest.human_rating)).filter(
                and_(
                    AIRequest.brokerage_id == brokerage_id,
                    AIRequest.human_rating.isnot(None)
                )
            ).scalar() or 0
            
            # Get request types breakdown
            type_breakdown = self.db.query(
                AIRequest.request_type,
                func.count(AIRequest.id).label('count')
            ).filter(
                AIRequest.brokerage_id == brokerage_id
            ).group_by(AIRequest.request_type).all()
            
            return {
                "total_requests": total_requests,
                "completed_requests": completed_requests,
                "completion_rate": (completed_requests / total_requests * 100) if total_requests > 0 else 0,
                "average_rating": float(avg_rating),
                "request_types": {item.request_type: item.count for item in type_breakdown}
            }
            
        except Exception as e:
            logger.error(f"Error getting brokerage analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get analytics: {str(e)}"
            )
