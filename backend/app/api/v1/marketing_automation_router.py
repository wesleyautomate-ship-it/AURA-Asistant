"""
Marketing Automation Router
===========================

FastAPI router that provides AURA-style marketing automation endpoints.

Features:
- Template management and selection
- Campaign creation and management
- Approval workflow (Draft → Review → Approved → Distributed)
- Asset generation (PDFs, images, HTML)
- Multi-channel campaign creation
- Campaign analytics and reporting
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.middleware import get_current_user, require_roles
from app.core.models import User
from app.domain.marketing.campaign_engine import MarketingCampaignEngine
from app.domain.ai.task_orchestrator import AITaskOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/marketing", tags=["Marketing Automation"])

# Dependency injection for AI orchestrator
def get_orchestrator(db: Session = Depends(get_db)) -> AITaskOrchestrator:
    """Get AI task orchestrator instance"""
    return AITaskOrchestrator(lambda: db)


# Dependency injection for marketing engine
def get_marketing_engine(
    db: Session = Depends(get_db),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
) -> MarketingCampaignEngine:
    """Get marketing campaign engine instance"""
    return MarketingCampaignEngine(lambda: db, orchestrator)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class CampaignCreateRequest(BaseModel):
    """Request model for creating marketing campaigns"""

    property_id: int
    campaign_type: str = Field(
        ..., pattern="^(postcard|email_blast|social_campaign|flyer)$"
    )
    template_id: Optional[int] = None
    custom_content: Optional[Dict[str, Any]] = None
    auto_generate_content: bool = True


class FullMarketingPackageRequest(BaseModel):
    """Request model for creating complete marketing packages"""

    property_id: int
    include_postcards: bool = True
    include_email: bool = True
    include_social: bool = True
    include_flyers: bool = False
    custom_message: Optional[str] = None


class CampaignUpdateRequest(BaseModel):
    """Request model for updating campaigns"""

    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class CampaignApprovalRequest(BaseModel):
    """Request model for campaign approval"""

    action: str = Field(..., pattern="^(approve|reject)$")
    approved_content: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None


class CampaignResponse(BaseModel):
    """Response model for campaign details"""

    id: int
    title: str
    property_id: int
    property_title: Optional[str]
    campaign_type: str
    status: str
    content: Dict[str, Any]
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    assets: List[Dict[str, Any]] = []


class TemplateResponse(BaseModel):
    """Response model for templates"""

    id: int
    name: str
    category: str
    type: str
    description: Optional[str]
    dubai_specific: bool


# =============================================================================
# TEMPLATE MANAGEMENT ENDPOINTS
# =============================================================================


@router.get("/templates", response_model=List[TemplateResponse])
async def list_marketing_templates(
    category: Optional[str] = None,
    template_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    List available marketing templates.

    Templates are the foundation of AURA marketing automation:
    - Postcards: Just Listed, Open House, Price Reduction, Sold
    - Emails: Announcements, Follow-ups, Market Updates
    - Social Media: Instagram, Facebook, LinkedIn posts
    - Flyers: Property details, feature sheets

    All templates are Dubai-specific and RERA-compliant.
    """
    try:
        templates = await marketing_engine.get_available_templates(
            category=category, template_type=template_type
        )

        return [TemplateResponse(**template) for template in templates]

    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates: {str(e)}",
        )


@router.get("/templates/{template_id}/preview")
async def preview_template(
    template_id: int,
    property_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    Preview a marketing template with sample or real property data.

    Shows how the template will look when populated with actual property
    information. If property_id is provided, uses real property data;
    otherwise uses sample data for preview.
    """
    try:
        template = await marketing_engine.load_template(template_id)

        # Use sample data if no property specified
        if property_id:
            property_data = await marketing_engine._get_property_data(property_id)
            agent_data = await marketing_engine._get_agent_data(current_user.id)
        else:
            property_data = {
                "property_title": "Luxury Marina Apartment",
                "location": "Dubai Marina",
                "price": 2500000,
                "bedrooms": 2,
                "bathrooms": 2,
                "area_sqft": 1200,
                "property_type": "apartment",
            }
            agent_data = {
                "agent_name": "Sample Agent",
                "agent_email": "agent@propertypro.ae",
                "agent_phone": "+971-50-123-4567",
                "brokerage_name": "PropertyPro Real Estate",
                "brokerage_license": "RERA-12345",
            }

        # Generate preview content
        preview_content = template.generate_content(
            property_data,
            agent_data,
            {
                "description": "This stunning apartment offers breathtaking marina views...",
                "highlights": ["Marina Views", "Premium Finishes", "Prime Location"],
                "hashtags": ["#DubaiRealEstate", "#LuxuryLiving", "#PropertyPro"],
            },
        )

        return {
            "template_id": template_id,
            "template_name": template.name,
            "preview_content": preview_content,
            "property_data_used": property_data,
            "agent_data_used": agent_data,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to preview template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview template: {str(e)}",
        )


# =============================================================================
# CAMPAIGN CREATION ENDPOINTS
# =============================================================================


@router.post("/campaigns", response_model=Dict[str, Any])
async def create_marketing_campaign(
    request: CampaignCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    Create a new marketing campaign for a property.

    This is the core AURA marketing endpoint that:
    1. Loads the specified template
    2. Generates AI content if requested
    3. Populates template with property data
    4. Creates campaign in draft status
    5. Optionally generates initial assets

    The campaign enters the approval workflow and can be reviewed
    before distribution.
    """
    try:
        campaign_id = await marketing_engine.create_campaign(
            property_id=request.property_id,
            agent_id=current_user.id,
            campaign_type=request.campaign_type,
            template_id=request.template_id,
            custom_content=request.custom_content,
        )

        # Generate assets in the background if requested
        if request.auto_generate_content:
            background_tasks.add_task(
                marketing_engine.generate_campaign_assets, campaign_id
            )

        campaign = await marketing_engine.get_campaign_details(campaign_id)

        logger.info(f"Campaign {campaign_id} created by user {current_user.id}")

        return {
            "campaign_id": campaign_id,
            "status": "created",
            "message": "Marketing campaign created successfully",
            "campaign": campaign,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}",
        )


@router.post("/campaigns/full-package", response_model=Dict[str, Any])
async def create_full_marketing_package(
    request: FullMarketingPackageRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    Create a complete AURA marketing package with multiple channels.

    This endpoint creates a comprehensive marketing package that includes:
    - Just Listed postcard (print-ready PDF)
    - Email announcement (HTML + text versions)
    - Social media posts (Instagram, Facebook, LinkedIn)
    - Optional property flyer

    All campaigns are created in draft status and enter the approval workflow.
    This is equivalent to the "Marketing Campaign" step in the New Listing Package.
    """
    try:
        marketing_package = await marketing_engine.create_full_marketing_package(
            property_id=request.property_id, agent_id=current_user.id
        )

        # Generate assets for all campaigns in the background
        for campaign_type, campaign_id in marketing_package["campaigns"].items():
            background_tasks.add_task(
                marketing_engine.generate_campaign_assets, campaign_id
            )

        logger.info(
            f"Full marketing package created for property {request.property_id} by user {current_user.id}"
        )

        return {
            "package_id": f"pkg_{request.property_id}_{int(datetime.utcnow().timestamp())}",
            "message": "Complete marketing package created successfully!",
            "package": marketing_package,
            "next_steps": "Review and approve campaigns in the Requests Board",
        }

    except Exception as e:
        logger.error(f"Failed to create full marketing package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create marketing package: {str(e)}",
        )


# =============================================================================
# CAMPAIGN MANAGEMENT ENDPOINTS
# =============================================================================


@router.get("/campaigns", response_model=List[Dict[str, Any]])
async def list_campaigns(
    property_id: Optional[int] = None,
    status: Optional[str] = None,
    campaign_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List marketing campaigns with filtering options.

    Provides a comprehensive view of all campaigns with status tracking:
    - Draft: Campaign created, ready for review
    - Review: Submitted for approval
    - Approved: Ready for distribution
    - Distributed: Campaign has been sent/published
    - Archived: Campaign completed or cancelled
    """
    try:
        from sqlalchemy import text

        query = """
            SELECT mc.id, mc.title, mc.property_id, mc.campaign_type, mc.status,
                   mc.created_at, mc.approved_at, mc.distributed_at,
                   p.title as property_title, p.location as property_location
            FROM marketing_campaigns mc
            LEFT JOIN properties p ON mc.property_id = p.id
            WHERE mc.agent_id = :agent_id
        """

        params = {"agent_id": current_user.id}

        if property_id:
            query += " AND mc.property_id = :property_id"
            params["property_id"] = property_id

        if status:
            query += " AND mc.status = :status"
            params["status"] = status

        if campaign_type:
            query += " AND mc.campaign_type = :campaign_type"
            params["campaign_type"] = campaign_type

        query += " ORDER BY mc.created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        result = db.execute(text(query), params)
        campaigns = []

        for row in result.fetchall():
            campaigns.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "property_id": row.property_id,
                    "property_title": row.property_title,
                    "property_location": row.property_location,
                    "campaign_type": row.campaign_type,
                    "status": row.status,
                    "created_at": row.created_at,
                    "approved_at": row.approved_at,
                    "distributed_at": row.distributed_at,
                }
            )

        return campaigns

    except Exception as e:
        logger.error(f"Failed to list campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}",
        )


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign_details(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    Get detailed information about a specific campaign.

    Returns comprehensive campaign data including:
    - Campaign content and configuration
    - Approval status and history
    - Generated assets (PDFs, images, HTML)
    - Performance metrics (if distributed)
    """
    try:
        campaign = await marketing_engine.get_campaign_details(campaign_id)

        # Verify user has access to this campaign
        if campaign["agent_id"] != current_user.id and current_user.role not in [
            "admin",
            "brokerage_owner",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this campaign",
            )

        return CampaignResponse(**campaign)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get campaign details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign details: {str(e)}",
        )


@router.patch("/campaigns/{campaign_id}", response_model=Dict[str, Any])
async def update_campaign(
    campaign_id: int,
    request: CampaignUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a marketing campaign.

    Allows modification of campaign content, title, and status.
    Note: Approved campaigns cannot be modified without creating a new revision.
    """
    try:
        # Verify campaign exists and user has access
        campaign = await get_campaign_details(
            campaign_id, current_user, MarketingCampaignEngine(lambda: db)
        )

        if campaign.status == "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approved campaigns cannot be modified. Create a new campaign instead.",
            )

        # Build update query
        update_fields = []
        params = {"campaign_id": campaign_id, "updated_at": datetime.utcnow()}

        if request.title:
            update_fields.append("title = :title")
            params["title"] = request.title

        if request.content:
            update_fields.append("content = :content")
            params["content"] = json.dumps(request.content)

        if request.status:
            update_fields.append("status = :status")
            params["status"] = request.status

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
            )

        update_fields.append("updated_at = :updated_at")

        query = f"""
            UPDATE marketing_campaigns 
            SET {', '.join(update_fields)}
            WHERE id = :campaign_id
        """

        from sqlalchemy import text

        db.execute(text(query), params)
        db.commit()

        logger.info(f"Campaign {campaign_id} updated by user {current_user.id}")

        return {
            "campaign_id": campaign_id,
            "status": "updated",
            "message": "Campaign updated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}",
        )


# =============================================================================
# APPROVAL WORKFLOW ENDPOINTS
# =============================================================================


@router.post("/campaigns/{campaign_id}/approval", response_model=Dict[str, Any])
async def handle_campaign_approval(
    campaign_id: int,
    request: CampaignApprovalRequest,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    Approve or reject a marketing campaign.

    This is the core approval workflow endpoint that agents use to:
    - Approve campaigns for distribution
    - Reject campaigns with feedback for revision
    - Modify content during approval process

    Part of the AURA approval workflow where human oversight
    ensures quality before campaign distribution.
    """
    try:
        workflow = marketing_engine.approval_workflow

        if request.action == "approve":
            success = await workflow.approve_campaign(
                campaign_id=campaign_id,
                approver_id=current_user.id,
                approved_content=request.approved_content,
            )

            if success:
                return {
                    "campaign_id": campaign_id,
                    "status": "approved",
                    "message": "Campaign approved successfully! Ready for distribution.",
                    "approved_by": current_user.id,
                    "approved_at": datetime.utcnow().isoformat(),
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to approve campaign",
                )

        elif request.action == "reject":
            if not request.rejection_reason:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rejection reason is required",
                )

            success = await workflow.reject_campaign(
                campaign_id=campaign_id,
                approver_id=current_user.id,
                rejection_reason=request.rejection_reason,
            )

            if success:
                return {
                    "campaign_id": campaign_id,
                    "status": "rejected",
                    "message": "Campaign rejected. Feedback has been added for revision.",
                    "rejection_reason": request.rejection_reason,
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to reject campaign",
                )

    except Exception as e:
        logger.error(f"Failed to handle campaign approval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process approval: {str(e)}",
        )


@router.post("/campaigns/{campaign_id}/submit-for-approval")
async def submit_campaign_for_approval(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    Submit a campaign for approval review.

    Moves campaign from 'draft' to 'review' status, indicating
    it's ready for agent approval. This triggers the approval workflow.
    """
    try:
        workflow = marketing_engine.approval_workflow

        approval_id = await workflow.create_approval_request(
            campaign_id=campaign_id, agent_id=current_user.id
        )

        return {
            "campaign_id": campaign_id,
            "approval_id": approval_id,
            "status": "submitted_for_approval",
            "message": "Campaign submitted for review. Check the Requests Board for approval.",
        }

    except Exception as e:
        logger.error(f"Failed to submit campaign for approval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit for approval: {str(e)}",
        )


# =============================================================================
# ASSET GENERATION ENDPOINTS
# =============================================================================


@router.post("/campaigns/{campaign_id}/assets/generate")
async def generate_campaign_assets(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    Generate marketing assets for a campaign.

    Creates print-ready and digital assets based on campaign type:
    - Postcards: High-resolution PDFs for printing
    - Emails: HTML and text versions
    - Social Media: Platform-optimized images
    - Flyers: Property detail sheets

    Asset generation runs in the background and updates are
    available through the campaign details endpoint.
    """
    try:
        # Verify campaign exists and user has access
        campaign = await marketing_engine.get_campaign_details(campaign_id)

        if campaign["agent_id"] != current_user.id and current_user.role not in [
            "admin",
            "brokerage_owner",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this campaign",
            )

        # Generate assets in background
        background_tasks.add_task(
            marketing_engine.generate_campaign_assets, campaign_id
        )

        return {
            "campaign_id": campaign_id,
            "status": "generating",
            "message": "Asset generation started. Check back shortly for completed assets.",
            "estimated_completion": "2-5 minutes",
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate campaign assets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate assets: {str(e)}",
        )


@router.get("/campaigns/{campaign_id}/assets")
async def list_campaign_assets(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    marketing_engine: MarketingCampaignEngine = Depends(get_marketing_engine),
):
    """
    List all assets generated for a campaign.

    Returns metadata about generated assets including:
    - File paths and download URLs
    - Asset types and formats
    - Generation timestamps
    - File sizes and metadata
    """
    try:
        campaign = await marketing_engine.get_campaign_details(campaign_id)

        if campaign["agent_id"] != current_user.id and current_user.role not in [
            "admin",
            "brokerage_owner",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this campaign",
            )

        return {
            "campaign_id": campaign_id,
            "assets": campaign.get("assets", []),
            "total_assets": len(campaign.get("assets", [])),
            "last_generated": max(
                [asset.get("created_at") for asset in campaign.get("assets", [])],
                default=None,
            ),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list campaign assets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list assets: {str(e)}",
        )


# =============================================================================
# ANALYTICS AND REPORTING ENDPOINTS
# =============================================================================


@router.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get performance metrics for a distributed campaign.

    Provides analytics on campaign effectiveness:
    - Distribution metrics (emails sent, postcards mailed)
    - Engagement metrics (opens, clicks, shares)
    - Lead generation metrics
    - ROI calculations (future feature)
    """
    # Placeholder for future analytics implementation
    return {
        "campaign_id": campaign_id,
        "status": "analytics_coming_soon",
        "message": "Campaign performance analytics will be available in the next release",
        "available_metrics": [
            "Distribution metrics",
            "Email open rates",
            "Social media engagement",
            "Lead generation tracking",
            "ROI calculations",
        ],
    }


@router.get("/analytics/summary")
async def get_marketing_analytics_summary(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get marketing analytics summary for the current user.

    Provides high-level metrics including:
    - Campaigns created and distributed
    - Most popular templates
    - Approval rates and times
    - Asset generation statistics
    """
    try:
        from sqlalchemy import text

        # Get campaign statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_campaigns,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_campaigns,
                COUNT(CASE WHEN status = 'distributed' THEN 1 END) as distributed_campaigns,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_campaigns
            FROM marketing_campaigns
            WHERE agent_id = :agent_id 
                AND created_at >= CURRENT_DATE - INTERVAL :days DAY
        """

        result = db.execute(
            text(stats_query), {"agent_id": current_user.id, "days": days}
        )
        stats = result.fetchone()

        # Get popular templates
        template_stats_query = """
            SELECT mt.name, mt.category, COUNT(*) as usage_count
            FROM marketing_campaigns mc
            JOIN marketing_templates mt ON mc.template_id = mt.id
            WHERE mc.agent_id = :agent_id 
                AND mc.created_at >= CURRENT_DATE - INTERVAL :days DAY
            GROUP BY mt.id, mt.name, mt.category
            ORDER BY usage_count DESC
            LIMIT 5
        """

        template_result = db.execute(
            text(template_stats_query), {"agent_id": current_user.id, "days": days}
        )
        popular_templates = [dict(row) for row in template_result.fetchall()]

        return {
            "period": f"Last {days} days",
            "campaign_statistics": {
                "total_campaigns": stats.total_campaigns or 0,
                "approved_campaigns": stats.approved_campaigns or 0,
                "distributed_campaigns": stats.distributed_campaigns or 0,
                "draft_campaigns": stats.draft_campaigns or 0,
                "approval_rate": (stats.approved_campaigns or 0)
                / max(stats.total_campaigns or 1, 1)
                * 100,
            },
            "popular_templates": popular_templates,
            "next_steps": [
                "Create more campaigns to improve your marketing reach",
                "Review draft campaigns and submit them for approval",
                "Analyze campaign performance to optimize future efforts",
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get marketing analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}",
        )
