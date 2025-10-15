"""
Newsletter Generation Router
============================

FastAPI router that provides AURA-style newsletter generation functionality.

Features:
- Real estate newsletter creation with market insights
- Multi-format output (HTML, PDF, plain text)
- Property showcase integration
- Market data and trends inclusion
- Client segmentation and personalization
- Template management and customization
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.middleware import get_current_user, require_roles
from app.core.models import User
from app.domain.ai.task_orchestrator import AITaskOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/newsletter", tags=["Newsletter Generation"])

# Dependency injection for AI orchestrator
def get_orchestrator(db: Session = Depends(get_db)) -> AITaskOrchestrator:
    """Get AI task orchestrator instance"""
    return AITaskOrchestrator(lambda: db)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class NewsletterRequest(BaseModel):
    """Request model for newsletter generation"""

    title: str = Field(
        ..., min_length=1, max_length=200, description="Newsletter title"
    )
    content_type: str = Field(
        "market_update",
        pattern="^(market_update|property_showcase|monthly_digest|investment_insights)$",
        description="Type of newsletter content",
    )
    target_audience: str = Field(
        "all_clients",
        pattern="^(all_clients|buyers|sellers|investors|renters)$",
        description="Target audience segment",
    )
    include_market_data: bool = Field(
        True, description="Include market statistics and trends"
    )
    include_featured_listings: bool = Field(
        True, description="Include featured property listings"
    )
    featured_property_ids: Optional[List[int]] = Field(
        None, description="Specific properties to feature"
    )
    custom_message: Optional[str] = Field(
        None, max_length=1000, description="Custom message from agent"
    )
    location_focus: Optional[str] = Field(
        None, description="Geographic area to focus on"
    )
    output_formats: List[str] = Field(
        ["html"], description="Desired output formats: html, pdf, plain_text"
    )
    branding: Optional[Dict[str, Any]] = Field(
        None, description="Custom branding settings"
    )


class NewsletterResponse(BaseModel):
    """Response model for newsletter generation"""

    task_id: str
    title: str
    content_type: str
    target_audience: str
    status: str
    message: str
    estimated_completion: str
    check_status_url: str
    created_at: datetime


class NewsletterStatusResponse(BaseModel):
    """Response model for newsletter status check"""

    task_id: str
    status: str
    progress: int
    title: str
    content_type: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class NewsletterTemplateResponse(BaseModel):
    """Response model for newsletter templates"""

    id: str
    name: str
    description: str
    content_type: str
    preview_image_url: Optional[str]
    suitable_for: List[str]


# =============================================================================
# NEWSLETTER GENERATION ENDPOINTS
# =============================================================================


@router.post("/generate", response_model=NewsletterResponse)
async def generate_newsletter(
    request: NewsletterRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db),
):
    """
    Generate a real estate newsletter with market updates and property listings.

    This is the core AURA newsletter endpoint that:
    1. Gathers relevant market data for the specified location
    2. Selects and formats featured properties
    3. Generates AI-powered content with market insights
    4. Creates professional newsletter layouts
    5. Exports to requested formats (HTML, PDF, plain text)

    Newsletters can be customized for different audiences:
    - Buyers: New listings, market opportunities, buying tips
    - Sellers: Market activity, pricing trends, selling strategies
    - Investors: ROI analysis, market forecasts, investment opportunities
    - All Clients: Comprehensive market overview and featured properties
    """
    try:
        # Validate output formats
        valid_formats = ["html", "pdf", "plain_text"]
        invalid_formats = [f for f in request.output_formats if f not in valid_formats]
        if invalid_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid output formats: {invalid_formats}. Valid options: {valid_formats}",
            )

        # Get featured properties if specified
        featured_properties = []
        if request.featured_property_ids:
            from sqlalchemy import text

            properties_query = """
                SELECT id, title, location, property_type, bedrooms, bathrooms,
                       area_sqft, price, status, description, image_url
                FROM properties
                WHERE id = ANY(:property_ids)
                AND status IN ('active', 'live')
            """

            result = db.execute(
                text(properties_query), {"property_ids": request.featured_property_ids}
            )

            for row in result.fetchall():
                # Check access permissions
                property_data = {
                    "id": row.id,
                    "title": row.title,
                    "location": row.location,
                    "property_type": row.property_type,
                    "bedrooms": row.bedrooms,
                    "bathrooms": row.bathrooms,
                    "area_sqft": row.area_sqft,
                    "price": row.price,
                    "status": row.status,
                    "description": row.description,
                    "image_url": row.image_url,
                }
                featured_properties.append(property_data)

        # If no specific properties but feature listings requested, get recent ones
        elif request.include_featured_listings:
            from sqlalchemy import text

            recent_query = """
                SELECT id, title, location, property_type, bedrooms, bathrooms,
                       area_sqft, price, status, description, image_url
                FROM properties
                WHERE status IN ('active', 'live')
                AND agent_id = :agent_id
                ORDER BY created_at DESC
                LIMIT 5
            """

            result = db.execute(text(recent_query), {"agent_id": current_user.id})

            for row in result.fetchall():
                property_data = {
                    "id": row.id,
                    "title": row.title,
                    "location": row.location,
                    "property_type": row.property_type,
                    "bedrooms": row.bedrooms,
                    "bathrooms": row.bathrooms,
                    "area_sqft": row.area_sqft,
                    "price": row.price,
                    "status": row.status,
                    "description": row.description,
                    "image_url": row.image_url if hasattr(row, "image_url") else None,
                }
                featured_properties.append(property_data)

        # Get market data if requested
        market_data = None
        if request.include_market_data and request.location_focus:
            from sqlalchemy import text

            market_query = """
                SELECT 
                    COUNT(*) as total_listings,
                    AVG(price) as avg_price,
                    AVG(price_per_sqft) as avg_price_psf,
                    MIN(price) as min_price,
                    MAX(price) as max_price
                FROM properties
                WHERE location ILIKE :location
                AND status IN ('active', 'live')
            """

            result = db.execute(
                text(market_query), {"location": f"%{request.location_focus}%"}
            ).fetchone()

            if result:
                market_data = {
                    "total_listings": int(result.total_listings)
                    if result.total_listings
                    else 0,
                    "avg_price": float(result.avg_price) if result.avg_price else 0,
                    "avg_price_psf": float(result.avg_price_psf)
                    if result.avg_price_psf
                    else 0,
                    "min_price": float(result.min_price) if result.min_price else 0,
                    "max_price": float(result.max_price) if result.max_price else 0,
                    "location": request.location_focus,
                }

        # Prepare task data for orchestrator
        task_data = {
            "title": request.title,
            "content_type": request.content_type,
            "target_audience": request.target_audience,
            "include_market_data": request.include_market_data,
            "include_featured_listings": request.include_featured_listings,
            "featured_properties": featured_properties,
            "market_data": market_data,
            "custom_message": request.custom_message,
            "location_focus": request.location_focus,
            "output_formats": request.output_formats,
            "branding": request.branding or {},
            "agent_id": current_user.id,
            "agent_name": current_user.full_name
            if hasattr(current_user, "full_name")
            else current_user.email,
            "agent_email": current_user.email,
        }

        # Submit newsletter generation task
        task_id = await orchestrator.submit_task(
            task_type="newsletter_generation",
            task_data=task_data,
            user_id=current_user.id,
            priority="medium",
        )

        logger.info(
            f"Newsletter generation task {task_id} submitted by user {current_user.id} "
            f"for '{request.title}' ({request.content_type})"
        )

        return NewsletterResponse(
            task_id=task_id,
            title=request.title,
            content_type=request.content_type,
            target_audience=request.target_audience,
            status="processing",
            message=f"Newsletter '{request.title}' generation started. Processing {len(featured_properties)} properties.",
            estimated_completion="5-8 minutes",
            check_status_url=f"/api/v1/newsletter/{task_id}/status",
            created_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate newsletter: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate newsletter: {str(e)}",
        )


@router.get("/{task_id}/status", response_model=NewsletterStatusResponse)
async def get_newsletter_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Check the status of a newsletter generation task.

    Returns:
    - Task progress and current status
    - Generated newsletter content when complete
    - Download URLs for different formats
    - Error details if generation failed
    """
    try:
        task_status = await orchestrator.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Newsletter task {task_id} not found",
            )

        # Verify user has access to this task
        if task_status.get("user_id") != current_user.id and current_user.role not in [
            "admin",
            "brokerage_owner",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this newsletter task",
            )

        return NewsletterStatusResponse(
            task_id=task_id,
            status=task_status.get("status", "unknown"),
            progress=task_status.get("progress", 0),
            title=task_status.get("task_data", {}).get("title", "Newsletter"),
            content_type=task_status.get("task_data", {}).get(
                "content_type", "market_update"
            ),
            created_at=task_status.get("created_at", datetime.utcnow()),
            completed_at=task_status.get("completed_at"),
            output=task_status.get("output"),
            error=task_status.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get newsletter status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get newsletter status: {str(e)}",
        )


@router.get("/templates", response_model=List[NewsletterTemplateResponse])
async def list_newsletter_templates(
    content_type: Optional[str] = None, current_user: User = Depends(get_current_user)
):
    """
    List available newsletter templates.

    Templates are pre-designed layouts optimized for different content types:
    - Market Update: Market trends, statistics, and analysis
    - Property Showcase: Featured listings with detailed descriptions
    - Monthly Digest: Comprehensive monthly market overview
    - Investment Insights: Investment opportunities and ROI analysis
    """
    try:
        # Define available templates
        templates = [
            {
                "id": "market_update_professional",
                "name": "Professional Market Update",
                "description": "Clean, data-driven layout perfect for market statistics and trends",
                "content_type": "market_update",
                "preview_image_url": "/templates/previews/market_update_pro.png",
                "suitable_for": ["buyers", "sellers", "investors", "all_clients"],
            },
            {
                "id": "property_showcase_luxury",
                "name": "Luxury Property Showcase",
                "description": "Elegant layout highlighting premium properties with large images",
                "content_type": "property_showcase",
                "preview_image_url": "/templates/previews/property_showcase_lux.png",
                "suitable_for": ["buyers", "investors"],
            },
            {
                "id": "monthly_digest_comprehensive",
                "name": "Comprehensive Monthly Digest",
                "description": "Full-featured template combining market data and property listings",
                "content_type": "monthly_digest",
                "preview_image_url": "/templates/previews/monthly_digest_comp.png",
                "suitable_for": ["all_clients"],
            },
            {
                "id": "investment_insights_analytical",
                "name": "Investment Analysis Report",
                "description": "Data-heavy layout focused on ROI, forecasts, and opportunities",
                "content_type": "investment_insights",
                "preview_image_url": "/templates/previews/investment_insights_ana.png",
                "suitable_for": ["investors"],
            },
        ]

        # Filter by content type if specified
        if content_type:
            templates = [t for t in templates if t["content_type"] == content_type]

        return [NewsletterTemplateResponse(**t) for t in templates]

    except Exception as e:
        logger.error(f"Failed to list newsletter templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}",
        )


@router.delete("/{task_id}")
async def cancel_newsletter_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Cancel a newsletter generation task that is in progress.
    """
    try:
        task_status = await orchestrator.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Newsletter task {task_id} not found",
            )

        # Verify user has access
        if task_status.get("user_id") != current_user.id and current_user.role not in [
            "admin",
            "brokerage_owner",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this newsletter task",
            )

        # Cancel the task
        await orchestrator.cancel_task(task_id)

        logger.info(f"Newsletter task {task_id} cancelled by user {current_user.id}")

        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Newsletter generation task cancelled successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel newsletter task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}",
        )


# =============================================================================
# HEALTH CHECK
# =============================================================================


@router.get("/health")
async def newsletter_health_check():
    """Health check endpoint for newsletter service"""
    return {
        "service": "Newsletter Generation",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
