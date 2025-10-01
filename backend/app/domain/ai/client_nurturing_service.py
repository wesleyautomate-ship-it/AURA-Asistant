"""
Client Nurturing Service
========================

This service provides comprehensive client nurturing capabilities including:
- Automated follow-up sequence management
- Lead nurturing automation
- Communication sequence templates
- Nurturing performance tracking
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from fastapi import HTTPException, status
import json

from app.domain.listings.brokerage_models import ClientNurturing, Brokerage
from auth.models import User

logger = logging.getLogger(__name__)

class ClientNurturingService:
    """Service for client nurturing and lead management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================
    # NURTURING SEQUENCE CRUD OPERATIONS
    # =====================================================
    
    async def create_nurturing_sequence(
        self, 
        brokerage_id: int, 
        sequence_data: Dict[str, Any], 
        created_by: int
    ) -> ClientNurturing:
        """Create a new client nurturing sequence"""
        try:
            # Validate required fields
            required_fields = ['sequence_name']
            for field in required_fields:
                if not sequence_data.get(field):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Field '{field}' is required"
                    )
            
            # Verify brokerage exists
            brokerage = self.db.query(Brokerage).filter(
                Brokerage.id == brokerage_id,
                Brokerage.is_active == True
            ).first()
            
            if not brokerage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brokerage not found"
                )
            
            # Validate sequence structure
            steps = sequence_data.get('steps', [])
            if not steps:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one step is required in the nurturing sequence"
                )
            
            # Create nurturing sequence
            nurturing_sequence = ClientNurturing(
                brokerage_id=brokerage_id,
                sequence_name=sequence_data['sequence_name'],
                description=sequence_data.get('description'),
                steps=json.dumps(steps),
                triggers=json.dumps(sequence_data.get('triggers', {})),
                is_active=sequence_data.get('is_active', True),
                created_by=created_by
            )
            
            self.db.add(nurturing_sequence)
            self.db.commit()
            self.db.refresh(nurturing_sequence)
            
            logger.info(f"Created nurturing sequence: {nurturing_sequence.sequence_name} (ID: {nurturing_sequence.id})")
            return nurturing_sequence
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating nurturing sequence: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create nurturing sequence: {str(e)}"
            )
    
    async def get_nurturing_sequence(self, sequence_id: int, brokerage_id: int) -> ClientNurturing:
        """Get nurturing sequence by ID"""
        try:
            sequence = self.db.query(ClientNurturing).filter(
                ClientNurturing.id == sequence_id,
                ClientNurturing.brokerage_id == brokerage_id,
                ClientNurturing.is_active == True
            ).first()
            
            if not sequence:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nurturing sequence not found"
                )
            
            return sequence
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting nurturing sequence {sequence_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get nurturing sequence: {str(e)}"
            )
    
    async def update_nurturing_sequence(
        self, 
        sequence_id: int, 
        brokerage_id: int, 
        update_data: Dict[str, Any]
    ) -> ClientNurturing:
        """Update nurturing sequence"""
        try:
            sequence = await self.get_nurturing_sequence(sequence_id, brokerage_id)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(sequence, field):
                    if field in ['steps', 'triggers'] and isinstance(value, (list, dict)):
                        setattr(sequence, field, json.dumps(value))
                    else:
                        setattr(sequence, field, value)
            
            sequence.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(sequence)
            
            logger.info(f"Updated nurturing sequence: {sequence.sequence_name} (ID: {sequence.id})")
            return sequence
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating nurturing sequence {sequence_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update nurturing sequence: {str(e)}"
            )
    
    async def delete_nurturing_sequence(self, sequence_id: int, brokerage_id: int) -> bool:
        """Soft delete nurturing sequence (set is_active to False)"""
        try:
            sequence = await self.get_nurturing_sequence(sequence_id, brokerage_id)
            
            sequence.is_active = False
            sequence.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted nurturing sequence: {sequence.sequence_name} (ID: {sequence.id})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting nurturing sequence {sequence_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete nurturing sequence: {str(e)}"
            )
    
    async def list_nurturing_sequences(
        self, 
        brokerage_id: int, 
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ClientNurturing]:
        """List nurturing sequences"""
        try:
            query = self.db.query(ClientNurturing).filter(
                ClientNurturing.brokerage_id == brokerage_id
            )
            
            if active_only:
                query = query.filter(ClientNurturing.is_active == True)
            
            sequences = query.order_by(ClientNurturing.updated_at.desc()).offset(skip).limit(limit).all()
            return sequences
            
        except Exception as e:
            logger.error(f"Error listing nurturing sequences: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list nurturing sequences: {str(e)}"
            )
    
    # =====================================================
    # NURTURING SEQUENCE EXECUTION
    # =====================================================
    
    async def start_nurturing_sequence(
        self, 
        sequence_id: int, 
        brokerage_id: int, 
        lead_id: int,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Start a nurturing sequence for a lead"""
        try:
            sequence = await self.get_nurturing_sequence(sequence_id, brokerage_id)
            
            # Check if sequence is active
            if not sequence.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nurturing sequence is not active"
                )
            
            # Get sequence steps
            steps = sequence.steps_list
            
            if not steps:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nurturing sequence has no steps"
                )
            
            # Start with the first step
            first_step = steps[0]
            execution_result = await self._execute_nurturing_step(
                first_step, 
                lead_id, 
                context or {}
            )
            
            # Record sequence start
            await self._record_sequence_start(sequence_id, lead_id, context or {})
            
            logger.info(f"Started nurturing sequence {sequence_id} for lead {lead_id}")
            
            return {
                "sequence_id": sequence_id,
                "lead_id": lead_id,
                "started": True,
                "current_step": 0,
                "total_steps": len(steps),
                "first_step_result": execution_result,
                "started_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting nurturing sequence {sequence_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start nurturing sequence: {str(e)}"
            )
    
    async def execute_next_step(
        self, 
        sequence_id: int, 
        brokerage_id: int, 
        lead_id: int,
        current_step: int,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute the next step in a nurturing sequence"""
        try:
            sequence = await self.get_nurturing_sequence(sequence_id, brokerage_id)
            steps = sequence.steps_list
            
            if current_step >= len(steps):
                return {
                    "sequence_id": sequence_id,
                    "lead_id": lead_id,
                    "completed": True,
                    "message": "All steps completed",
                    "completed_at": datetime.utcnow().isoformat()
                }
            
            # Execute current step
            step = steps[current_step]
            execution_result = await self._execute_nurturing_step(
                step, 
                lead_id, 
                context or {}
            )
            
            # Determine next step
            next_step = current_step + 1
            if next_step < len(steps):
                next_step_data = steps[next_step]
            else:
                next_step_data = None
            
            logger.info(f"Executed step {current_step} of sequence {sequence_id} for lead {lead_id}")
            
            return {
                "sequence_id": sequence_id,
                "lead_id": lead_id,
                "current_step": current_step,
                "next_step": next_step,
                "total_steps": len(steps),
                "step_result": execution_result,
                "next_step_data": next_step_data,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error executing next step: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute next step: {str(e)}"
            )
    
    async def _execute_nurturing_step(
        self, 
        step: Dict[str, Any], 
        lead_id: int, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single nurturing step"""
        try:
            step_type = step.get('type')
            step_params = step.get('parameters', {})
            
            if step_type == 'send_email':
                result = await self._send_nurturing_email(step_params, lead_id, context)
            elif step_type == 'send_sms':
                result = await self._send_nurturing_sms(step_params, lead_id, context)
            elif step_type == 'schedule_call':
                result = await self._schedule_nurturing_call(step_params, lead_id, context)
            elif step_type == 'send_document':
                result = await self._send_nurturing_document(step_params, lead_id, context)
            elif step_type == 'wait':
                result = await self._wait_step(step_params, lead_id, context)
            else:
                result = {"status": "skipped", "reason": f"Unknown step type: {step_type}"}
            
            return {
                "step_type": step_type,
                "step_name": step.get('name', step_type),
                "result": result,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing nurturing step: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _send_nurturing_email(self, params: Dict[str, Any], lead_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send nurturing email"""
        # Placeholder implementation
        return {"status": "success", "message": "Email sent", "email_id": f"email_{lead_id}_{datetime.utcnow().timestamp()}"}
    
    async def _send_nurturing_sms(self, params: Dict[str, Any], lead_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send nurturing SMS"""
        # Placeholder implementation
        return {"status": "success", "message": "SMS sent", "sms_id": f"sms_{lead_id}_{datetime.utcnow().timestamp()}"}
    
    async def _schedule_nurturing_call(self, params: Dict[str, Any], lead_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule nurturing call"""
        # Placeholder implementation
        return {"status": "success", "message": "Call scheduled", "call_id": f"call_{lead_id}_{datetime.utcnow().timestamp()}"}
    
    async def _send_nurturing_document(self, params: Dict[str, Any], lead_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send nurturing document"""
        # Placeholder implementation
        return {"status": "success", "message": "Document sent", "document_id": f"doc_{lead_id}_{datetime.utcnow().timestamp()}"}
    
    async def _wait_step(self, params: Dict[str, Any], lead_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wait step implementation"""
        wait_duration = params.get('duration', 24)  # Default 24 hours
        return {"status": "success", "message": f"Waiting {wait_duration} hours", "wait_until": (datetime.utcnow() + timedelta(hours=wait_duration)).isoformat()}
    
    async def _record_sequence_start(self, sequence_id: int, lead_id: int, context: Dict[str, Any]):
        """Record sequence start for analytics"""
        try:
            # This would typically record in a sequence_executions table
            logger.info(f"Recorded sequence start: sequence {sequence_id}, lead {lead_id}")
        except Exception as e:
            logger.error(f"Error recording sequence start: {e}")
    
    # =====================================================
    # NURTURING ANALYTICS
    # =====================================================
    
    async def get_nurturing_analytics(self, brokerage_id: int) -> Dict[str, Any]:
        """Get client nurturing analytics"""
        try:
            # Get sequence counts
            total_sequences = self.db.query(ClientNurturing).filter(
                ClientNurturing.brokerage_id == brokerage_id,
                ClientNurturing.is_active == True
            ).count()
            
            # Get recent sequences (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_sequences = self.db.query(ClientNurturing).filter(
                ClientNurturing.brokerage_id == brokerage_id,
                ClientNurturing.is_active == True,
                ClientNurturing.created_at >= thirty_days_ago
            ).count()
            
            # Get average steps per sequence
            sequences = await self.list_nurturing_sequences(brokerage_id)
            avg_steps = 0
            if sequences:
                total_steps = sum(len(seq.steps_list) for seq in sequences)
                avg_steps = total_steps / len(sequences)
            
            analytics = {
                "brokerage_id": brokerage_id,
                "total_sequences": total_sequences,
                "recent_sequences_30_days": recent_sequences,
                "average_steps_per_sequence": round(avg_steps, 2),
                "active_sequences": len([s for s in sequences if s.is_active]),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting nurturing analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get nurturing analytics: {str(e)}"
            )
    
    # =====================================================
    # TEMPLATE MANAGEMENT
    # =====================================================
    
    async def create_nurturing_template(
        self, 
        brokerage_id: int, 
        template_data: Dict[str, Any], 
        created_by: int
    ) -> ClientNurturing:
        """Create a nurturing sequence template"""
        try:
            # Add template indicator to the sequence
            template_data['description'] = f"[TEMPLATE] {template_data.get('description', '')}"
            
            # Create the sequence
            sequence = await self.create_nurturing_sequence(brokerage_id, template_data, created_by)
            
            logger.info(f"Created nurturing template: {sequence.sequence_name} (ID: {sequence.id})")
            return sequence
            
        except Exception as e:
            logger.error(f"Error creating nurturing template: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create nurturing template: {str(e)}"
            )
    
    async def get_nurturing_templates(self, brokerage_id: int) -> List[ClientNurturing]:
        """Get all nurturing sequence templates"""
        try:
            templates = self.db.query(ClientNurturing).filter(
                ClientNurturing.brokerage_id == brokerage_id,
                ClientNurturing.is_active == True,
                ClientNurturing.description.like('[TEMPLATE]%')
            ).all()
            
            return templates
            
        except Exception as e:
            logger.error(f"Error getting nurturing templates: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get nurturing templates: {str(e)}"
            )
