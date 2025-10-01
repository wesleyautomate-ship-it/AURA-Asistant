"""
Brokerage Management Service
============================

This service provides comprehensive brokerage management capabilities including:
- Brokerage CRUD operations
- Team management
- Branding controls
- Performance analytics
- Compliance monitoring
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from fastapi import HTTPException, status
import json

from app.domain.listings.brokerage_models import (
    Brokerage, TeamPerformance, KnowledgeBase, BrandAsset,
    WorkflowAutomation, ClientNurturing, ComplianceRule,
    AgentConsistencyMetric, LeadRetentionAnalytic, WorkflowEfficiencyMetric
)
from auth.models import User

logger = logging.getLogger(__name__)

class BrokerageManagementService:
    """Service for comprehensive brokerage management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================
    # BROKERAGE CRUD OPERATIONS
    # =====================================================
    
    async def create_brokerage(self, brokerage_data: Dict[str, Any], created_by: int) -> Brokerage:
        """Create a new brokerage"""
        try:
            # Validate required fields
            required_fields = ['name', 'license_number', 'email']
            for field in required_fields:
                if not brokerage_data.get(field):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Field '{field}' is required"
                    )
            
            # Check if license number already exists
            existing_brokerage = self.db.query(Brokerage).filter(
                Brokerage.license_number == brokerage_data['license_number']
            ).first()
            
            if existing_brokerage:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Brokerage with this license number already exists"
                )
            
            # Create brokerage
            brokerage = Brokerage(
                name=brokerage_data['name'],
                license_number=brokerage_data['license_number'],
                address=brokerage_data.get('address'),
                phone=brokerage_data.get('phone'),
                email=brokerage_data['email'],
                website=brokerage_data.get('website'),
                logo_url=brokerage_data.get('logo_url'),
                branding_config=json.dumps(brokerage_data.get('branding_config', {})),
                is_active=brokerage_data.get('is_active', True)
            )
            
            self.db.add(brokerage)
            self.db.commit()
            self.db.refresh(brokerage)
            
            logger.info(f"Created brokerage: {brokerage.name} (ID: {brokerage.id})")
            return brokerage
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating brokerage: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create brokerage: {str(e)}"
            )
    
    async def get_brokerage(self, brokerage_id: int) -> Optional[Brokerage]:
        """Get brokerage by ID"""
        try:
            brokerage = self.db.query(Brokerage).filter(
                Brokerage.id == brokerage_id,
                Brokerage.is_active == True
            ).first()
            
            if not brokerage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brokerage not found"
                )
            
            return brokerage
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting brokerage {brokerage_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get brokerage: {str(e)}"
            )
    
    async def update_brokerage(self, brokerage_id: int, update_data: Dict[str, Any]) -> Brokerage:
        """Update brokerage information"""
        try:
            brokerage = await self.get_brokerage(brokerage_id)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(brokerage, field):
                    if field == 'branding_config' and isinstance(value, dict):
                        setattr(brokerage, field, json.dumps(value))
                    else:
                        setattr(brokerage, field, value)
            
            brokerage.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(brokerage)
            
            logger.info(f"Updated brokerage: {brokerage.name} (ID: {brokerage.id})")
            return brokerage
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating brokerage {brokerage_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update brokerage: {str(e)}"
            )
    
    async def delete_brokerage(self, brokerage_id: int) -> bool:
        """Soft delete brokerage (set is_active to False)"""
        try:
            brokerage = await self.get_brokerage(brokerage_id)
            
            brokerage.is_active = False
            brokerage.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted brokerage: {brokerage.name} (ID: {brokerage.id})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting brokerage {brokerage_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete brokerage: {str(e)}"
            )
    
    async def list_brokerages(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Brokerage]:
        """List all brokerages with pagination"""
        try:
            query = self.db.query(Brokerage)
            
            if active_only:
                query = query.filter(Brokerage.is_active == True)
            
            brokerages = query.offset(skip).limit(limit).all()
            return brokerages
            
        except Exception as e:
            logger.error(f"Error listing brokerages: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list brokerages: {str(e)}"
            )
    
    # =====================================================
    # TEAM MANAGEMENT
    # =====================================================
    
    async def get_team_members(self, brokerage_id: int) -> List[User]:
        """Get all team members for a brokerage"""
        try:
            team_members = self.db.query(User).filter(
                User.brokerage_id == brokerage_id,
                User.is_active == True
            ).all()
            
            return team_members
            
        except Exception as e:
            logger.error(f"Error getting team members for brokerage {brokerage_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get team members: {str(e)}"
            )
    
    async def add_team_member(self, brokerage_id: int, user_id: int) -> bool:
        """Add user to brokerage team"""
        try:
            # Verify brokerage exists
            await self.get_brokerage(brokerage_id)
            
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update user's brokerage
            user.brokerage_id = brokerage_id
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Added user {user_id} to brokerage {brokerage_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding team member: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add team member: {str(e)}"
            )
    
    async def remove_team_member(self, brokerage_id: int, user_id: int) -> bool:
        """Remove user from brokerage team"""
        try:
            user = self.db.query(User).filter(
                User.id == user_id,
                User.brokerage_id == brokerage_id
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in this brokerage"
                )
            
            # Remove user from brokerage
            user.brokerage_id = None
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Removed user {user_id} from brokerage {brokerage_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing team member: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove team member: {str(e)}"
            )
    
    # =====================================================
    # BRANDING MANAGEMENT
    # =====================================================
    
    async def update_branding(self, brokerage_id: int, branding_config: Dict[str, Any]) -> Brokerage:
        """Update brokerage branding configuration"""
        try:
            brokerage = await self.get_brokerage(brokerage_id)
            
            # Merge with existing branding config
            current_config = brokerage.branding_config_dict
            current_config.update(branding_config)
            
            brokerage.branding_config = json.dumps(current_config)
            brokerage.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(brokerage)
            
            logger.info(f"Updated branding for brokerage {brokerage_id}")
            return brokerage
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating branding for brokerage {brokerage_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update branding: {str(e)}"
            )
    
    async def upload_brand_asset(self, brokerage_id: int, asset_data: Dict[str, Any]) -> BrandAsset:
        """Upload a new brand asset"""
        try:
            await self.get_brokerage(brokerage_id)  # Verify brokerage exists
            
            brand_asset = BrandAsset(
                brokerage_id=brokerage_id,
                asset_type=asset_data['asset_type'],
                asset_name=asset_data['asset_name'],
                file_path=asset_data.get('file_path'),
                metadata=json.dumps(asset_data.get('metadata', {})),
                is_active=True
            )
            
            self.db.add(brand_asset)
            self.db.commit()
            self.db.refresh(brand_asset)
            
            logger.info(f"Uploaded brand asset: {brand_asset.asset_name} for brokerage {brokerage_id}")
            return brand_asset
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error uploading brand asset: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload brand asset: {str(e)}"
            )
    
    async def get_brand_assets(self, brokerage_id: int, asset_type: Optional[str] = None) -> List[BrandAsset]:
        """Get brand assets for a brokerage"""
        try:
            query = self.db.query(BrandAsset).filter(
                BrandAsset.brokerage_id == brokerage_id,
                BrandAsset.is_active == True
            )
            
            if asset_type:
                query = query.filter(BrandAsset.asset_type == asset_type)
            
            assets = query.all()
            return assets
            
        except Exception as e:
            logger.error(f"Error getting brand assets for brokerage {brokerage_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get brand assets: {str(e)}"
            )
    
    # =====================================================
    # PERFORMANCE ANALYTICS
    # =====================================================
    
    async def get_team_performance_summary(self, brokerage_id: int, period_days: int = 30) -> Dict[str, Any]:
        """Get team performance summary for a brokerage"""
        try:
            await self.get_brokerage(brokerage_id)  # Verify brokerage exists
            
            # Get team members
            team_members = await self.get_team_members(brokerage_id)
            
            # Get performance metrics
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            performance_metrics = self.db.query(TeamPerformance).filter(
                TeamPerformance.brokerage_id == brokerage_id,
                TeamPerformance.period_start >= start_date
            ).all()
            
            # Calculate summary statistics
            total_agents = len(team_members)
            active_agents = len([m for m in team_members if m.role in ['agent', 'brokerage_owner']])
            
            # Group metrics by agent
            agent_metrics = {}
            for metric in performance_metrics:
                agent_id = metric.agent_id
                if agent_id not in agent_metrics:
                    agent_metrics[agent_id] = []
                agent_metrics[agent_id].append(metric)
            
            # Calculate consistency scores
            consistency_scores = []
            for agent_id, metrics in agent_metrics.items():
                if metrics:
                    avg_score = sum(float(m.metric_value or 0) for m in metrics) / len(metrics)
                    consistency_scores.append(avg_score)
            
            avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
            
            summary = {
                'brokerage_id': brokerage_id,
                'period_days': period_days,
                'total_agents': total_agents,
                'active_agents': active_agents,
                'average_consistency_score': round(avg_consistency, 2),
                'performance_metrics_count': len(performance_metrics),
                'agent_consistency_scores': consistency_scores,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return summary
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting team performance summary for brokerage {brokerage_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get team performance summary: {str(e)}"
            )
    
    async def get_brokerage_analytics(self, brokerage_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a brokerage"""
        try:
            await self.get_brokerage(brokerage_id)  # Verify brokerage exists
            
            # Get various metrics
            team_members = await self.get_team_members(brokerage_id)
            knowledge_items = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True
            ).count()
            
            workflows = self.db.query(WorkflowAutomation).filter(
                WorkflowAutomation.brokerage_id == brokerage_id,
                WorkflowAutomation.is_active == True
            ).count()
            
            nurturing_sequences = self.db.query(ClientNurturing).filter(
                ClientNurturing.brokerage_id == brokerage_id,
                ClientNurturing.is_active == True
            ).count()
            
            compliance_rules = self.db.query(ComplianceRule).filter(
                ComplianceRule.brokerage_id == brokerage_id,
                ComplianceRule.is_active == True
            ).count()
            
            # Get performance summary
            performance_summary = await self.get_team_performance_summary(brokerage_id)
            
            analytics = {
                'brokerage_id': brokerage_id,
                'team_size': len(team_members),
                'knowledge_base_items': knowledge_items,
                'active_workflows': workflows,
                'nurturing_sequences': nurturing_sequences,
                'compliance_rules': compliance_rules,
                'performance_summary': performance_summary,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting brokerage analytics for brokerage {brokerage_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get brokerage analytics: {str(e)}"
            )
