"""
Brand Management Service
========================

This service provides comprehensive brand management capabilities including:
- Logo management and upload
- Template system management
- Branding guidelines enforcement
- Brand asset organization
"""

import logging
import os
import shutil
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from fastapi import HTTPException, status, UploadFile
import json
import uuid

from app.domain.listings.brokerage_models import BrandAsset, Brokerage
from auth.models import User

logger = logging.getLogger(__name__)

class BrandManagementService:
    """Service for brand management and asset organization"""
    
    def __init__(self, db: Session, upload_dir: str = "uploads/brand_assets"):
        self.db = db
        self.upload_dir = upload_dir
        self._ensure_upload_directory()
    
    def _ensure_upload_directory(self):
        """Ensure upload directory exists"""
        try:
            os.makedirs(self.upload_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating upload directory: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create upload directory"
            )
    
    # =====================================================
    # BRAND ASSET MANAGEMENT
    # =====================================================
    
    async def upload_brand_asset(
        self, 
        brokerage_id: int, 
        asset_type: str, 
        asset_name: str,
        file: UploadFile,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BrandAsset:
        """Upload a new brand asset"""
        try:
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
            
            # Validate asset type
            valid_types = ['logo', 'template', 'color_scheme', 'font', 'image', 'document']
            if asset_type not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid asset type. Must be one of: {', '.join(valid_types)}"
                )
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ''
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create brokerage-specific directory
            brokerage_dir = os.path.join(self.upload_dir, str(brokerage_id))
            os.makedirs(brokerage_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(brokerage_dir, unique_filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create database record
            brand_asset = BrandAsset(
                brokerage_id=brokerage_id,
                asset_type=asset_type,
                asset_name=asset_name,
                file_path=file_path,
                metadata=json.dumps(metadata or {}),
                is_active=True
            )
            
            self.db.add(brand_asset)
            self.db.commit()
            self.db.refresh(brand_asset)
            
            logger.info(f"Uploaded brand asset: {asset_name} (ID: {brand_asset.id})")
            return brand_asset
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error uploading brand asset: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload brand asset: {str(e)}"
            )
    
    async def get_brand_assets(
        self, 
        brokerage_id: int, 
        asset_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[BrandAsset]:
        """Get brand assets for a brokerage"""
        try:
            query = self.db.query(BrandAsset).filter(
                BrandAsset.brokerage_id == brokerage_id
            )
            
            if active_only:
                query = query.filter(BrandAsset.is_active == True)
            
            if asset_type:
                query = query.filter(BrandAsset.asset_type == asset_type)
            
            assets = query.order_by(BrandAsset.created_at.desc()).all()
            return assets
            
        except Exception as e:
            logger.error(f"Error getting brand assets: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get brand assets: {str(e)}"
            )
    
    async def get_brand_asset(self, asset_id: int, brokerage_id: int) -> BrandAsset:
        """Get specific brand asset"""
        try:
            asset = self.db.query(BrandAsset).filter(
                BrandAsset.id == asset_id,
                BrandAsset.brokerage_id == brokerage_id,
                BrandAsset.is_active == True
            ).first()
            
            if not asset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brand asset not found"
                )
            
            return asset
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting brand asset {asset_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get brand asset: {str(e)}"
            )
    
    async def update_brand_asset(
        self, 
        asset_id: int, 
        brokerage_id: int, 
        update_data: Dict[str, Any]
    ) -> BrandAsset:
        """Update brand asset information"""
        try:
            asset = await self.get_brand_asset(asset_id, brokerage_id)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(asset, field) and field not in ['id', 'brokerage_id', 'created_at']:
                    if field == 'metadata' and isinstance(value, dict):
                        setattr(asset, field, json.dumps(value))
                    else:
                        setattr(asset, field, value)
            
            self.db.commit()
            self.db.refresh(asset)
            
            logger.info(f"Updated brand asset: {asset.asset_name} (ID: {asset.id})")
            return asset
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating brand asset {asset_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update brand asset: {str(e)}"
            )
    
    async def delete_brand_asset(self, asset_id: int, brokerage_id: int) -> bool:
        """Delete brand asset (soft delete)"""
        try:
            asset = await self.get_brand_asset(asset_id, brokerage_id)
            
            # Soft delete
            asset.is_active = False
            self.db.commit()
            
            # Optionally delete physical file
            if asset.file_path and os.path.exists(asset.file_path):
                try:
                    os.remove(asset.file_path)
                except Exception as e:
                    logger.warning(f"Could not delete physical file {asset.file_path}: {e}")
            
            logger.info(f"Deleted brand asset: {asset.asset_name} (ID: {asset.id})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting brand asset {asset_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete brand asset: {str(e)}"
            )
    
    # =====================================================
    # BRANDING CONFIGURATION
    # =====================================================
    
    async def update_branding_config(
        self, 
        brokerage_id: int, 
        branding_config: Dict[str, Any]
    ) -> Brokerage:
        """Update brokerage branding configuration"""
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
            
            # Merge with existing branding config
            current_config = brokerage.branding_config_dict
            current_config.update(branding_config)
            
            brokerage.branding_config = json.dumps(current_config)
            brokerage.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(brokerage)
            
            logger.info(f"Updated branding config for brokerage {brokerage_id}")
            return brokerage
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating branding config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update branding config: {str(e)}"
            )
    
    async def get_branding_config(self, brokerage_id: int) -> Dict[str, Any]:
        """Get brokerage branding configuration"""
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
            
            return brokerage.branding_config_dict
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting branding config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get branding config: {str(e)}"
            )
    
    # =====================================================
    # TEMPLATE MANAGEMENT
    # =====================================================
    
    async def get_templates(self, brokerage_id: int) -> List[BrandAsset]:
        """Get all templates for a brokerage"""
        try:
            templates = await self.get_brand_assets(brokerage_id, asset_type='template')
            return templates
            
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get templates: {str(e)}"
            )
    
    async def create_template(
        self, 
        brokerage_id: int, 
        template_name: str,
        template_content: str,
        template_type: str = "document",
        metadata: Optional[Dict[str, Any]] = None
    ) -> BrandAsset:
        """Create a new template"""
        try:
            # Save template content to file
            template_filename = f"{uuid.uuid4()}.txt"
            brokerage_dir = os.path.join(self.upload_dir, str(brokerage_id))
            os.makedirs(brokerage_dir, exist_ok=True)
            
            file_path = os.path.join(brokerage_dir, template_filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(template_content)
            
            # Create database record
            template_metadata = metadata or {}
            template_metadata.update({
                "template_type": template_type,
                "content_length": len(template_content)
            })
            
            brand_asset = BrandAsset(
                brokerage_id=brokerage_id,
                asset_type='template',
                asset_name=template_name,
                file_path=file_path,
                metadata=json.dumps(template_metadata),
                is_active=True
            )
            
            self.db.add(brand_asset)
            self.db.commit()
            self.db.refresh(brand_asset)
            
            logger.info(f"Created template: {template_name} (ID: {brand_asset.id})")
            return brand_asset
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating template: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create template: {str(e)}"
            )
    
    async def get_template_content(self, template_id: int, brokerage_id: int) -> str:
        """Get template content"""
        try:
            template = await self.get_brand_asset(template_id, brokerage_id)
            
            if template.asset_type != 'template':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Asset is not a template"
                )
            
            if not os.path.exists(template.file_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template file not found"
                )
            
            with open(template.file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return content
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting template content: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get template content: {str(e)}"
            )
    
    # =====================================================
    # LOGO MANAGEMENT
    # =====================================================
    
    async def set_primary_logo(self, brokerage_id: int, logo_asset_id: int) -> Brokerage:
        """Set primary logo for brokerage"""
        try:
            # Verify logo asset exists
            logo_asset = await self.get_brand_asset(logo_asset_id, brokerage_id)
            
            if logo_asset.asset_type != 'logo':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Asset is not a logo"
                )
            
            # Update brokerage branding config
            branding_config = {
                "primary_logo_id": logo_asset_id,
                "primary_logo_path": logo_asset.file_path,
                "logo_updated_at": datetime.utcnow().isoformat()
            }
            
            brokerage = await self.update_branding_config(brokerage_id, branding_config)
            
            logger.info(f"Set primary logo for brokerage {brokerage_id}")
            return brokerage
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error setting primary logo: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set primary logo: {str(e)}"
            )
    
    async def get_primary_logo(self, brokerage_id: int) -> Optional[BrandAsset]:
        """Get primary logo for brokerage"""
        try:
            branding_config = await self.get_branding_config(brokerage_id)
            primary_logo_id = branding_config.get('primary_logo_id')
            
            if not primary_logo_id:
                return None
            
            return await self.get_brand_asset(primary_logo_id, brokerage_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting primary logo: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get primary logo: {str(e)}"
            )
    
    # =====================================================
    # ANALYTICS AND INSIGHTS
    # =====================================================
    
    async def get_brand_analytics(self, brokerage_id: int) -> Dict[str, Any]:
        """Get brand management analytics"""
        try:
            # Get asset counts by type
            asset_counts = self.db.query(
                BrandAsset.asset_type,
                func.count(BrandAsset.id).label('count')
            ).filter(
                BrandAsset.brokerage_id == brokerage_id,
                BrandAsset.is_active == True
            ).group_by(BrandAsset.asset_type).all()
            
            # Get total assets
            total_assets = sum(count.count for count in asset_counts)
            
            # Get recent uploads (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_uploads = self.db.query(BrandAsset).filter(
                BrandAsset.brokerage_id == brokerage_id,
                BrandAsset.is_active == True,
                BrandAsset.created_at >= thirty_days_ago
            ).count()
            
            # Get branding config status
            branding_config = await self.get_branding_config(brokerage_id)
            has_primary_logo = 'primary_logo_id' in branding_config
            has_color_scheme = 'primary_color' in branding_config
            
            analytics = {
                "brokerage_id": brokerage_id,
                "total_assets": total_assets,
                "recent_uploads_30_days": recent_uploads,
                "asset_counts_by_type": [
                    {"type": count.asset_type, "count": count.count}
                    for count in asset_counts
                ],
                "branding_status": {
                    "has_primary_logo": has_primary_logo,
                    "has_color_scheme": has_color_scheme,
                    "config_completeness": self._calculate_config_completeness(branding_config)
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting brand analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get brand analytics: {str(e)}"
            )
    
    def _calculate_config_completeness(self, branding_config: Dict[str, Any]) -> float:
        """Calculate branding configuration completeness percentage"""
        required_fields = [
            'primary_color', 'secondary_color', 'primary_logo_id',
            'font_family', 'brand_name'
        ]
        
        completed_fields = sum(1 for field in required_fields if field in branding_config)
        return (completed_fields / len(required_fields)) * 100
