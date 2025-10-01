"""
Workflow Automation Service
===========================

This service provides comprehensive workflow automation capabilities including:
- Task automation management
- Intelligent workflow optimization
- Automation rule creation and execution
- Workflow performance tracking
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from fastapi import HTTPException, status
import json

from app.domain.listings.brokerage_models import WorkflowAutomation, WorkflowEfficiencyMetric, Brokerage
from auth.models import User

logger = logging.getLogger(__name__)

class WorkflowAutomationService:
    """Service for workflow automation management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================
    # WORKFLOW AUTOMATION CRUD OPERATIONS
    # =====================================================
    
    async def create_workflow(
        self, 
        brokerage_id: int, 
        workflow_data: Dict[str, Any], 
        created_by: int
    ) -> WorkflowAutomation:
        """Create a new workflow automation"""
        try:
            # Validate required fields
            required_fields = ['name', 'trigger_type']
            for field in required_fields:
                if not workflow_data.get(field):
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
            
            # Validate trigger type
            valid_triggers = ['manual', 'scheduled', 'event_based']
            if workflow_data['trigger_type'] not in valid_triggers:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid trigger type. Must be one of: {', '.join(valid_triggers)}"
                )
            
            # Create workflow
            workflow = WorkflowAutomation(
                brokerage_id=brokerage_id,
                name=workflow_data['name'],
                description=workflow_data.get('description'),
                trigger_type=workflow_data['trigger_type'],
                conditions=json.dumps(workflow_data.get('conditions', {})),
                actions=json.dumps(workflow_data.get('actions', {})),
                is_active=workflow_data.get('is_active', True),
                created_by=created_by
            )
            
            self.db.add(workflow)
            self.db.commit()
            self.db.refresh(workflow)
            
            logger.info(f"Created workflow: {workflow.name} (ID: {workflow.id})")
            return workflow
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating workflow: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create workflow: {str(e)}"
            )
    
    async def get_workflow(self, workflow_id: int, brokerage_id: int) -> WorkflowAutomation:
        """Get workflow by ID"""
        try:
            workflow = self.db.query(WorkflowAutomation).filter(
                WorkflowAutomation.id == workflow_id,
                WorkflowAutomation.brokerage_id == brokerage_id,
                WorkflowAutomation.is_active == True
            ).first()
            
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workflow not found"
                )
            
            return workflow
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting workflow {workflow_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get workflow: {str(e)}"
            )
    
    async def update_workflow(
        self, 
        workflow_id: int, 
        brokerage_id: int, 
        update_data: Dict[str, Any]
    ) -> WorkflowAutomation:
        """Update workflow automation"""
        try:
            workflow = await self.get_workflow(workflow_id, brokerage_id)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(workflow, field):
                    if field in ['conditions', 'actions'] and isinstance(value, dict):
                        setattr(workflow, field, json.dumps(value))
                    else:
                        setattr(workflow, field, value)
            
            workflow.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(workflow)
            
            logger.info(f"Updated workflow: {workflow.name} (ID: {workflow.id})")
            return workflow
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating workflow {workflow_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update workflow: {str(e)}"
            )
    
    async def delete_workflow(self, workflow_id: int, brokerage_id: int) -> bool:
        """Soft delete workflow (set is_active to False)"""
        try:
            workflow = await self.get_workflow(workflow_id, brokerage_id)
            
            workflow.is_active = False
            workflow.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted workflow: {workflow.name} (ID: {workflow.id})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting workflow {workflow_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete workflow: {str(e)}"
            )
    
    async def list_workflows(
        self, 
        brokerage_id: int, 
        trigger_type: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[WorkflowAutomation]:
        """List workflows with filtering"""
        try:
            query = self.db.query(WorkflowAutomation).filter(
                WorkflowAutomation.brokerage_id == brokerage_id
            )
            
            if active_only:
                query = query.filter(WorkflowAutomation.is_active == True)
            
            if trigger_type:
                query = query.filter(WorkflowAutomation.trigger_type == trigger_type)
            
            workflows = query.order_by(WorkflowAutomation.updated_at.desc()).offset(skip).limit(limit).all()
            return workflows
            
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list workflows: {str(e)}"
            )
    
    # =====================================================
    # WORKFLOW EXECUTION
    # =====================================================
    
    async def execute_workflow(self, workflow_id: int, brokerage_id: int, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow automation"""
        try:
            workflow = await self.get_workflow(workflow_id, brokerage_id)
            
            # Check if workflow is active
            if not workflow.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Workflow is not active"
                )
            
            # Get workflow conditions and actions
            conditions = workflow.conditions_dict
            actions = workflow.actions_dict
            
            # Evaluate conditions
            conditions_met = await self._evaluate_conditions(conditions, context or {})
            
            if not conditions_met:
                return {
                    "workflow_id": workflow_id,
                    "executed": False,
                    "reason": "Conditions not met",
                    "executed_at": datetime.utcnow().isoformat()
                }
            
            # Execute actions
            execution_result = await self._execute_actions(actions, context or {})
            
            # Record execution
            await self._record_workflow_execution(workflow_id, execution_result)
            
            logger.info(f"Executed workflow: {workflow.name} (ID: {workflow.id})")
            
            return {
                "workflow_id": workflow_id,
                "executed": True,
                "result": execution_result,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute workflow: {str(e)}"
            )
    
    async def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate workflow conditions"""
        try:
            # Simple condition evaluation logic
            # In a real implementation, this would be more sophisticated
            
            if not conditions:
                return True
            
            # Check if all required context variables are present
            required_vars = conditions.get('required_variables', [])
            for var in required_vars:
                if var not in context:
                    return False
            
            # Check value conditions
            value_conditions = conditions.get('value_conditions', [])
            for condition in value_conditions:
                var_name = condition.get('variable')
                expected_value = condition.get('value')
                operator = condition.get('operator', 'equals')
                
                if var_name not in context:
                    return False
                
                actual_value = context[var_name]
                
                if operator == 'equals' and actual_value != expected_value:
                    return False
                elif operator == 'not_equals' and actual_value == expected_value:
                    return False
                elif operator == 'greater_than' and actual_value <= expected_value:
                    return False
                elif operator == 'less_than' and actual_value >= expected_value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            return False
    
    async def _execute_actions(self, actions: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow actions"""
        try:
            results = {}
            
            # Execute each action
            action_list = actions.get('actions', [])
            for action in action_list:
                action_type = action.get('type')
                action_params = action.get('parameters', {})
                
                if action_type == 'send_notification':
                    result = await self._send_notification(action_params, context)
                elif action_type == 'update_status':
                    result = await self._update_status(action_params, context)
                elif action_type == 'create_task':
                    result = await self._create_task(action_params, context)
                elif action_type == 'send_email':
                    result = await self._send_email(action_params, context)
                else:
                    result = {"status": "skipped", "reason": f"Unknown action type: {action_type}"}
                
                results[action.get('name', action_type)] = result
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing actions: {e}")
            return {"error": str(e)}
    
    async def _send_notification(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification action"""
        # Placeholder implementation
        return {"status": "success", "message": "Notification sent"}
    
    async def _update_status(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Update status action"""
        # Placeholder implementation
        return {"status": "success", "message": "Status updated"}
    
    async def _create_task(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create task action"""
        # Placeholder implementation
        return {"status": "success", "message": "Task created"}
    
    async def _send_email(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send email action"""
        # Placeholder implementation
        return {"status": "success", "message": "Email sent"}
    
    async def _record_workflow_execution(self, workflow_id: int, result: Dict[str, Any]):
        """Record workflow execution for analytics"""
        try:
            # This would typically record execution metrics
            # For now, we'll just log it
            logger.info(f"Recorded execution for workflow {workflow_id}: {result}")
        except Exception as e:
            logger.error(f"Error recording workflow execution: {e}")
    
    # =====================================================
    # WORKFLOW ANALYTICS
    # =====================================================
    
    async def get_workflow_analytics(self, brokerage_id: int) -> Dict[str, Any]:
        """Get workflow automation analytics"""
        try:
            # Get workflow counts
            total_workflows = self.db.query(WorkflowAutomation).filter(
                WorkflowAutomation.brokerage_id == brokerage_id,
                WorkflowAutomation.is_active == True
            ).count()
            
            # Get workflows by trigger type
            workflows_by_trigger = self.db.query(
                WorkflowAutomation.trigger_type,
                func.count(WorkflowAutomation.id).label('count')
            ).filter(
                WorkflowAutomation.brokerage_id == brokerage_id,
                WorkflowAutomation.is_active == True
            ).group_by(WorkflowAutomation.trigger_type).all()
            
            # Get recent workflows (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_workflows = self.db.query(WorkflowAutomation).filter(
                WorkflowAutomation.brokerage_id == brokerage_id,
                WorkflowAutomation.is_active == True,
                WorkflowAutomation.created_at >= thirty_days_ago
            ).count()
            
            # Get efficiency metrics
            efficiency_metrics = self.db.query(WorkflowEfficiencyMetric).filter(
                WorkflowEfficiencyMetric.brokerage_id == brokerage_id
            ).all()
            
            avg_efficiency = 0
            if efficiency_metrics:
                avg_efficiency = sum(float(m.efficiency_score or 0) for m in efficiency_metrics) / len(efficiency_metrics)
            
            analytics = {
                "brokerage_id": brokerage_id,
                "total_workflows": total_workflows,
                "recent_workflows_30_days": recent_workflows,
                "workflows_by_trigger": [
                    {"trigger_type": w.trigger_type, "count": w.count}
                    for w in workflows_by_trigger
                ],
                "average_efficiency_score": round(avg_efficiency, 2),
                "efficiency_metrics_count": len(efficiency_metrics),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting workflow analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get workflow analytics: {str(e)}"
            )
    
    async def add_efficiency_metric(
        self, 
        brokerage_id: int, 
        workflow_id: int, 
        efficiency_data: Dict[str, Any]
    ) -> WorkflowEfficiencyMetric:
        """Add workflow efficiency metric"""
        try:
            # Verify workflow exists
            await self.get_workflow(workflow_id, brokerage_id)
            
            efficiency_metric = WorkflowEfficiencyMetric(
                brokerage_id=brokerage_id,
                workflow_id=workflow_id,
                efficiency_score=efficiency_data.get('efficiency_score'),
                time_saved=efficiency_data.get('time_saved'),
                automation_rate=efficiency_data.get('automation_rate'),
                period_start=efficiency_data.get('period_start'),
                period_end=efficiency_data.get('period_end'),
                metadata=json.dumps(efficiency_data.get('metadata', {}))
            )
            
            self.db.add(efficiency_metric)
            self.db.commit()
            self.db.refresh(efficiency_metric)
            
            logger.info(f"Added efficiency metric for workflow {workflow_id}")
            return efficiency_metric
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding efficiency metric: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add efficiency metric: {str(e)}"
            )
