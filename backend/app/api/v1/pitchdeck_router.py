"""
Pitch Deck Generation Router
============================

FastAPI router that provides AURA-style pitch deck presentation generation.

Features:
- Property pitch deck creation for buyers and investors
- Professional presentation layouts with data visualizations
- Market analysis and investment highlights
- Financial projections and ROI calculations
- Multi-format export (PDF, PowerPoint, Web)
- Customizable branding and styling
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

router = APIRouter(prefix="/api/v1/pitchdeck", tags=["Pitch Deck Generation"])

# Dependency injection for AI orchestrator
def get_orchestrator(db: Session = Depends(get_db)) -> AITaskOrchestrator:
    """Get AI task orchestrator instance"""
    return AITaskOrchestrator(lambda: db)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class PitchDeckRequest(BaseModel):
    """Request model for pitch deck generation"""

    property_id: int = Field(..., description="Property ID to create pitch deck for")
    target_audience: str = Field(
        "buyer",
        pattern="^(buyer|investor|developer|corporate)$",
        description="Target audience for the presentation",
    )
    include_sections: List[str] = Field(
        default=[
            "cover",
            "property_overview",
            "location",
            "market_analysis",
            "investment_highlights",
            "financials",
            "call_to_action",
        ],
        description="Sections to include in the pitch deck",
    )
    presentation_style: str = Field(
        "professional",
        pattern="^(professional|modern|luxury|minimalist)$",
        description="Visual style of the presentation",
    )
    include_financial_projections: bool = Field(
        False, description="Include detailed financial projections and ROI analysis"
    )
    include_comparable_properties: bool = Field(
        True, description="Include comparable properties analysis"
    )
    custom_branding: Optional[Dict[str, Any]] = Field(
        None, description="Custom branding (logo, colors, fonts)"
    )
    custom_message: Optional[str] = Field(
        None, max_length=500, description="Custom message or introduction"
    )
    output_formats: List[str] = Field(
        ["pdf"], description="Desired output formats: pdf, pptx, web"
    )


class PitchDeckResponse(BaseModel):
    """Response model for pitch deck generation"""

    task_id: str
    property_id: int
    property_title: str
    target_audience: str
    presentation_style: str
    status: str
    message: str
    estimated_completion: str
    check_status_url: str
    created_at: datetime


class PitchDeckStatusResponse(BaseModel):
    """Response model for pitch deck status check"""

    task_id: str
    status: str
    progress: int
    property_id: int
    property_title: str
    target_audience: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None
    download_urls: Optional[Dict[str, str]] = None
    error: Optional[str] = None


class PitchDeckTemplateResponse(BaseModel):
    """Response model for pitch deck templates"""

    id: str
    name: str
    description: str
    style: str
    preview_image_url: Optional[str]
    suitable_for: List[str]
    included_sections: List[str]


# =============================================================================
# PITCH DECK GENERATION ENDPOINTS
# =============================================================================


@router.post("/generate", response_model=PitchDeckResponse)
async def generate_pitch_deck(
    request: PitchDeckRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db),
):
    """
    Generate a professional property pitch deck presentation.

    This is the core AURA pitch deck endpoint that:
    1. Retrieves comprehensive property data
    2. Gathers market analysis and comparable properties
    3. Generates financial projections (if requested)
    4. Creates professional presentation slides
    5. Applies custom branding and styling
    6. Exports to requested formats (PDF, PowerPoint, Web)

    Pitch decks are customized for different audiences:
    - Buyer: Property features, lifestyle, neighborhood, financing options
    - Investor: ROI analysis, market trends, cash flow projections, exit strategies
    - Developer: Development potential, zoning, construction opportunities
    - Corporate: Commercial suitability, tenant mix, market positioning
    """
    try:
        # Validate output formats
        valid_formats = ["pdf", "pptx", "web"]
        invalid_formats = [f for f in request.output_formats if f not in valid_formats]
        if invalid_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid output formats: {invalid_formats}. Valid options: {valid_formats}",
            )

        # Validate sections
        valid_sections = [
            "cover",
            "property_overview",
            "location",
            "amenities",
            "market_analysis",
            "investment_highlights",
            "financials",
            "comparable_properties",
            "neighborhood",
            "call_to_action",
        ]
        invalid_sections = [
            s for s in request.include_sections if s not in valid_sections
        ]
        if invalid_sections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sections: {invalid_sections}. Valid options: {valid_sections}",
            )

        # Get property data
        from sqlalchemy import text

        property_query = """
            SELECT id, title, location, property_type, bedrooms, bathrooms,
                   area_sqft, price, price_per_sqft, status, description,
                   listing_type, year_built, parking_spaces, agent_id
            FROM properties
            WHERE id = :property_id
        """

        result = db.execute(text(property_query), {"property_id": request.property_id})
        property_row = result.fetchone()

        if not property_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property {request.property_id} not found",
            )

        # Check user access permissions
        if property_row.agent_id != current_user.id and current_user.role not in [
            "admin",
            "brokerage_owner",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this property",
            )

        property_data = {
            "id": property_row.id,
            "title": property_row.title,
            "location": property_row.location,
            "property_type": property_row.property_type,
            "bedrooms": property_row.bedrooms,
            "bathrooms": property_row.bathrooms,
            "area_sqft": property_row.area_sqft,
            "price": property_row.price,
            "price_per_sqft": property_row.price_per_sqft,
            "status": property_row.status,
            "description": property_row.description,
            "listing_type": property_row.listing_type
            if hasattr(property_row, "listing_type")
            else "sale",
            "year_built": property_row.year_built
            if hasattr(property_row, "year_built")
            else None,
            "parking_spaces": property_row.parking_spaces
            if hasattr(property_row, "parking_spaces")
            else None,
        }

        # Get market analysis data if section is included
        market_analysis = None
        if "market_analysis" in request.include_sections:
            market_query = """
                SELECT 
                    COUNT(*) as total_listings,
                    AVG(price) as avg_price,
                    AVG(price_per_sqft) as avg_price_psf,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    AVG(CASE WHEN status = 'sold' THEN days_on_market END) as avg_days_on_market
                FROM properties
                WHERE location ILIKE :location
                AND property_type = :property_type
                AND status IN ('active', 'live', 'sold')
            """

            result = db.execute(
                text(market_query),
                {
                    "location": f"%{property_data['location']}%",
                    "property_type": property_data["property_type"],
                },
            ).fetchone()

            if result:
                market_analysis = {
                    "total_listings": int(result.total_listings)
                    if result.total_listings
                    else 0,
                    "avg_price": float(result.avg_price) if result.avg_price else 0,
                    "avg_price_psf": float(result.avg_price_psf)
                    if result.avg_price_psf
                    else 0,
                    "min_price": float(result.min_price) if result.min_price else 0,
                    "max_price": float(result.max_price) if result.max_price else 0,
                    "avg_days_on_market": float(result.avg_days_on_market)
                    if result.avg_days_on_market
                    else 0,
                    "location": property_data["location"],
                }

        # Get comparable properties if requested
        comparable_properties = []
        if (
            request.include_comparable_properties
            and "comparable_properties" in request.include_sections
        ):
            comp_query = """
                SELECT id, title, location, property_type, bedrooms, bathrooms,
                       area_sqft, price, price_per_sqft, status
                FROM properties
                WHERE property_type = :property_type
                AND bedrooms = :bedrooms
                AND bathrooms = :bathrooms
                AND area_sqft BETWEEN :min_size AND :max_size
                AND id != :property_id
                AND status IN ('active', 'live', 'sold')
                ORDER BY ABS(area_sqft - :target_size)
                LIMIT 5
            """

            size_variance = property_data["area_sqft"] * 0.2  # 20% variance
            result = db.execute(
                text(comp_query),
                {
                    "property_type": property_data["property_type"],
                    "bedrooms": property_data["bedrooms"],
                    "bathrooms": property_data["bathrooms"],
                    "min_size": property_data["area_sqft"] - size_variance,
                    "max_size": property_data["area_sqft"] + size_variance,
                    "target_size": property_data["area_sqft"],
                    "property_id": request.property_id,
                },
            )

            for row in result.fetchall():
                comp_data = {
                    "id": row.id,
                    "title": row.title,
                    "location": row.location,
                    "property_type": row.property_type,
                    "bedrooms": row.bedrooms,
                    "bathrooms": row.bathrooms,
                    "area_sqft": row.area_sqft,
                    "price": row.price,
                    "price_per_sqft": row.price_per_sqft,
                    "status": row.status,
                }
                comparable_properties.append(comp_data)

        # Calculate financial projections if requested
        financial_projections = None
        if request.include_financial_projections and request.target_audience in [
            "investor",
            "developer",
        ]:
            # Basic ROI calculation (can be enhanced with more sophisticated models)
            annual_rental_income = (
                property_data["price"] * 0.05
            )  # Assume 5% rental yield
            annual_expenses = annual_rental_income * 0.25  # 25% for expenses
            net_annual_income = annual_rental_income - annual_expenses
            roi_percentage = (net_annual_income / property_data["price"]) * 100

            financial_projections = {
                "purchase_price": property_data["price"],
                "estimated_annual_rental_income": annual_rental_income,
                "estimated_annual_expenses": annual_expenses,
                "net_annual_income": net_annual_income,
                "estimated_roi_percentage": round(roi_percentage, 2),
                "cash_on_cash_return": round(roi_percentage, 2),  # Simplified
                "cap_rate": round(
                    (net_annual_income / property_data["price"]) * 100, 2
                ),
                "break_even_years": round(property_data["price"] / net_annual_income, 1)
                if net_annual_income > 0
                else None,
            }

        # Prepare task data for orchestrator
        task_data = {
            "property_id": request.property_id,
            "property_data": property_data,
            "target_audience": request.target_audience,
            "include_sections": request.include_sections,
            "presentation_style": request.presentation_style,
            "market_analysis": market_analysis,
            "comparable_properties": comparable_properties,
            "financial_projections": financial_projections,
            "custom_branding": request.custom_branding or {},
            "custom_message": request.custom_message,
            "output_formats": request.output_formats,
            "agent_id": current_user.id,
            "agent_name": current_user.full_name
            if hasattr(current_user, "full_name")
            else current_user.email,
            "agent_email": current_user.email,
            "agent_phone": current_user.phone
            if hasattr(current_user, "phone")
            else None,
        }

        # Submit pitch deck generation task
        task_id = await orchestrator.submit_task(
            task_type="pitchdeck_generation",
            task_data=task_data,
            user_id=current_user.id,
            priority="high",  # Pitch decks are typically time-sensitive
        )

        logger.info(
            f"Pitch deck generation task {task_id} submitted by user {current_user.id} "
            f"for property {request.property_id} ({property_data['title']})"
        )

        return PitchDeckResponse(
            task_id=task_id,
            property_id=request.property_id,
            property_title=property_data["title"],
            target_audience=request.target_audience,
            presentation_style=request.presentation_style,
            status="processing",
            message=f"Pitch deck generation started for '{property_data['title']}'. Creating {len(request.include_sections)} slides.",
            estimated_completion="3-5 minutes",
            check_status_url=f"/api/v1/pitchdeck/{task_id}/status",
            created_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate pitch deck: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate pitch deck: {str(e)}",
        )


@router.get("/{task_id}/status", response_model=PitchDeckStatusResponse)
async def get_pitch_deck_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Check the status of a pitch deck generation task.

    Returns:
    - Task progress and current status
    - Generated presentation content when complete
    - Download URLs for different formats (PDF, PPTX, Web)
    - Preview images of slides
    - Error details if generation failed
    """
    try:
        task_status = await orchestrator.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pitch deck task {task_id} not found",
            )

        # Verify user has access to this task
        if task_status.get("user_id") != current_user.id and current_user.role not in [
            "admin",
            "brokerage_owner",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this pitch deck task",
            )

        # Extract download URLs if task is complete
        download_urls = None
        if task_status.get("status") == "completed" and task_status.get("output"):
            output = task_status.get("output", {})
            download_urls = output.get("download_urls", {})

        return PitchDeckStatusResponse(
            task_id=task_id,
            status=task_status.get("status", "unknown"),
            progress=task_status.get("progress", 0),
            property_id=task_status.get("task_data", {}).get("property_id", 0),
            property_title=task_status.get("task_data", {})
            .get("property_data", {})
            .get("title", "Property"),
            target_audience=task_status.get("task_data", {}).get(
                "target_audience", "buyer"
            ),
            created_at=task_status.get("created_at", datetime.utcnow()),
            completed_at=task_status.get("completed_at"),
            output=task_status.get("output"),
            download_urls=download_urls,
            error=task_status.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pitch deck status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pitch deck status: {str(e)}",
        )


@router.get("/templates", response_model=List[PitchDeckTemplateResponse])
async def list_pitch_deck_templates(
    style: Optional[str] = None,
    target_audience: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    List available pitch deck templates.

    Templates are professionally designed presentation layouts optimized for:
    - Professional: Classic business presentation style
    - Modern: Contemporary design with bold typography
    - Luxury: High-end aesthetic for premium properties
    - Minimalist: Clean, simple design focused on content

    Each template is optimized for different target audiences and use cases.
    """
    try:
        # Define available templates
        templates = [
            {
                "id": "professional_buyer",
                "name": "Professional Buyer Presentation",
                "description": "Classic business presentation highlighting property features and lifestyle",
                "style": "professional",
                "preview_image_url": "/templates/previews/professional_buyer.png",
                "suitable_for": ["buyer"],
                "included_sections": [
                    "cover",
                    "property_overview",
                    "location",
                    "amenities",
                    "neighborhood",
                    "call_to_action",
                ],
            },
            {
                "id": "investor_analysis",
                "name": "Investor Analysis Deck",
                "description": "Data-driven presentation with financial projections and ROI analysis",
                "style": "professional",
                "preview_image_url": "/templates/previews/investor_analysis.png",
                "suitable_for": ["investor"],
                "included_sections": [
                    "cover",
                    "property_overview",
                    "market_analysis",
                    "investment_highlights",
                    "financials",
                    "comparable_properties",
                    "call_to_action",
                ],
            },
            {
                "id": "luxury_showcase",
                "name": "Luxury Property Showcase",
                "description": "Elegant presentation for high-end properties with stunning visuals",
                "style": "luxury",
                "preview_image_url": "/templates/previews/luxury_showcase.png",
                "suitable_for": ["buyer", "investor"],
                "included_sections": [
                    "cover",
                    "property_overview",
                    "location",
                    "amenities",
                    "investment_highlights",
                    "call_to_action",
                ],
            },
            {
                "id": "modern_investment",
                "name": "Modern Investment Pitch",
                "description": "Contemporary design focusing on market trends and opportunities",
                "style": "modern",
                "preview_image_url": "/templates/previews/modern_investment.png",
                "suitable_for": ["investor", "developer"],
                "included_sections": [
                    "cover",
                    "property_overview",
                    "market_analysis",
                    "investment_highlights",
                    "financials",
                    "call_to_action",
                ],
            },
            {
                "id": "developer_opportunity",
                "name": "Development Opportunity Deck",
                "description": "Detailed analysis for developers highlighting development potential",
                "style": "professional",
                "preview_image_url": "/templates/previews/developer_opportunity.png",
                "suitable_for": ["developer"],
                "included_sections": [
                    "cover",
                    "property_overview",
                    "location",
                    "market_analysis",
                    "investment_highlights",
                    "financials",
                    "call_to_action",
                ],
            },
            {
                "id": "minimalist_modern",
                "name": "Minimalist Modern",
                "description": "Clean, simple design letting the property speak for itself",
                "style": "minimalist",
                "preview_image_url": "/templates/previews/minimalist_modern.png",
                "suitable_for": ["buyer", "investor"],
                "included_sections": [
                    "cover",
                    "property_overview",
                    "location",
                    "amenities",
                    "call_to_action",
                ],
            },
        ]

        # Filter by style if specified
        if style:
            templates = [t for t in templates if t["style"] == style]

        # Filter by target audience if specified
        if target_audience:
            templates = [t for t in templates if target_audience in t["suitable_for"]]

        return [PitchDeckTemplateResponse(**t) for t in templates]

    except Exception as e:
        logger.error(f"Failed to list pitch deck templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}",
        )


@router.delete("/{task_id}")
async def cancel_pitch_deck_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Cancel a pitch deck generation task that is in progress.
    """
    try:
        task_status = await orchestrator.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pitch deck task {task_id} not found",
            )

        # Verify user has access
        if task_status.get("user_id") != current_user.id and current_user.role not in [
            "admin",
            "brokerage_owner",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this pitch deck task",
            )

        # Cancel the task
        await orchestrator.cancel_task(task_id)

        logger.info(f"Pitch deck task {task_id} cancelled by user {current_user.id}")

        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Pitch deck generation task cancelled successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel pitch deck task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}",
        )


# =============================================================================
# HEALTH CHECK
# =============================================================================


@router.get("/health")
async def pitchdeck_health_check():
    """Health check endpoint for pitch deck service"""
    return {
        "service": "Pitch Deck Generation",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
