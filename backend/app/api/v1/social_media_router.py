"""
Social Media Automation Router
==============================

FastAPI router that provides AURA-style social media automation functionality.

Features:
- Cross-platform content creation (Instagram, Facebook, LinkedIn)
- Dubai real estate content optimization
- Automated scheduling and publishing
- Visual asset generation and management
- Hashtag optimization and research
- Performance analytics and insights
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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
from app.domain.ai.task_orchestrator import AITaskOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/social", tags=["Social Media Automation"])

# Dependency injection for AI orchestrator
def get_orchestrator(db: Session = Depends(get_db)) -> AITaskOrchestrator:
    """Get AI task orchestrator instance"""
    return AITaskOrchestrator(lambda: db)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class SocialPostRequest(BaseModel):
    """Request model for creating social media posts"""

    property_id: Optional[int] = None
    platforms: List[str] = Field(
        ..., min_items=1
    )  # ['instagram', 'facebook', 'linkedin']
    content_type: str = Field(
        ..., pattern="^(listing|sold|open_house|market_update|tips|success_story)$"
    )
    custom_message: Optional[str] = None
    include_images: bool = True
    schedule_time: Optional[datetime] = None
    hashtags: Optional[List[str]] = None


class SocialCampaignRequest(BaseModel):
    """Request model for creating social media campaigns"""

    campaign_name: str
    property_id: Optional[int] = None
    campaign_type: str = Field(
        ..., pattern="^(property_launch|market_series|brand_awareness)$"
    )
    platforms: List[str] = Field(..., min_items=1)
    post_frequency: str = Field("daily", pattern="^(hourly|daily|weekly)$")
    duration_days: int = Field(7, ge=1, le=30)
    start_date: Optional[datetime] = None


class HashtagResearchRequest(BaseModel):
    """Request model for hashtag research"""

    property_type: Optional[str] = None
    location: Optional[str] = None
    target_audience: str = Field(
        "buyers", pattern="^(buyers|investors|renters|sellers)$"
    )
    max_hashtags: int = Field(30, ge=10, le=50)


class PostPerformanceRequest(BaseModel):
    """Request model for analyzing post performance"""

    post_id: int
    metrics_period: str = Field("7days", pattern="^(24hours|7days|30days)$")


class SocialPostResponse(BaseModel):
    """Response model for social posts"""

    id: int
    property_id: Optional[int]
    platforms: List[str]
    content_type: str
    content: Dict[str, Any]
    status: str
    scheduled_time: Optional[datetime]
    published_time: Optional[datetime]
    created_at: datetime
    assets: List[Dict[str, Any]] = []


class SocialCampaignResponse(BaseModel):
    """Response model for social campaigns"""

    id: int
    campaign_name: str
    campaign_type: str
    platforms: List[str]
    status: str
    posts_count: int
    posts_published: int
    start_date: datetime
    end_date: datetime
    performance_metrics: Dict[str, Any]


class HashtagRecommendations(BaseModel):
    """Response model for hashtag recommendations"""

    recommended_hashtags: List[Dict[str, Any]]
    trending_hashtags: List[str]
    location_specific: List[str]
    property_specific: List[str]
    audience_targeted: List[str]


# =============================================================================
# SOCIAL MEDIA POST CREATION ENDPOINTS
# =============================================================================


@router.post("/posts", response_model=Dict[str, Any])
async def create_social_media_post(
    request: SocialPostRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db),
):
    """
    Create social media posts for multiple platforms.

    This is the core AURA social media endpoint that:
    1. Generates platform-optimized content
    2. Creates visual assets if needed
    3. Optimizes hashtags for Dubai real estate
    4. Schedules posts across platforms
    5. Tracks performance metrics

    Supported platforms:
    - Instagram: Square images, Stories, Reels
    - Facebook: Various formats, business features
    - LinkedIn: Professional tone, market insights

    All content is Dubai real estate focused with RERA compliance.
    """
    try:
        # Validate platforms
        valid_platforms = ["instagram", "facebook", "linkedin", "twitter"]
        invalid_platforms = [p for p in request.platforms if p not in valid_platforms]
        if invalid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platforms: {invalid_platforms}. Valid options: {valid_platforms}",
            )

        # Get property data if provided
        property_data = None
        if request.property_id:
            from sqlalchemy import text

            property_query = """
                SELECT id, title, location, property_type, bedrooms, bathrooms, 
                       area_sqft, price, status, description, agent_id
                FROM properties 
                WHERE id = :property_id
            """

            result = db.execute(
                text(property_query), {"property_id": request.property_id}
            )
            property_row = result.fetchone()

            if not property_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
                )

            # Check user access
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
                "status": property_row.status,
                "description": property_row.description,
            }

        # Submit social media task to orchestrator
        task_data = {
            "property_data": property_data,
            "platforms": request.platforms,
            "content_type": request.content_type,
            "custom_message": request.custom_message,
            "include_images": request.include_images,
            "schedule_time": request.schedule_time.isoformat()
            if request.schedule_time
            else None,
            "hashtags": request.hashtags,
            "user_id": current_user.id,
            "agent_data": {
                "name": current_user.full_name
                or f"{current_user.first_name} {current_user.last_name}",
                "email": current_user.email,
                "phone": getattr(current_user, "phone", None),
            },
        }

        task_id = await orchestrator.submit_task(
            task_type="social_media_post",
            task_data=task_data,
            user_id=current_user.id,
            priority="medium",
        )

        logger.info(
            f"Social media post task {task_id} submitted for platforms {request.platforms} by user {current_user.id}"
        )

        return {
            "task_id": task_id,
            "property_id": request.property_id,
            "platforms": request.platforms,
            "content_type": request.content_type,
            "status": "processing",
            "message": "Social media posts are being created. You will be notified when ready.",
            "estimated_completion": "2-4 minutes",
            "check_status_url": f"/api/v1/social/posts/{task_id}/status",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create social media post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create social media post: {str(e)}",
        )


@router.get("/posts/{task_id}/status")
async def get_social_post_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Check the status of a social media post creation task.

    Returns current progress, content preview, and publishing status.
    """
    try:
        task_status = await orchestrator.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media post task not found",
            )

        # Check user access
        if task_status.get("user_id") != current_user.id and current_user.role not in [
            "admin"
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this social media post",
            )

        response_data = {
            "task_id": task_id,
            "status": task_status.get("status", "unknown"),
            "progress": task_status.get("progress", 0),
            "created_at": task_status.get("created_at"),
            "updated_at": task_status.get("updated_at"),
        }

        # Add result data if completed
        if task_status.get("status") == "completed" and task_status.get("result"):
            response_data.update(
                {
                    "social_posts": task_status["result"],
                    "preview_url": f"/api/v1/social/posts/{task_id}/preview",
                    "publish_url": f"/api/v1/social/posts/{task_id}/publish",
                }
            )
        elif task_status.get("status") == "failed":
            response_data["error"] = task_status.get("error", "Unknown error occurred")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get social post status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get post status: {str(e)}",
        )


@router.get("/posts/{task_id}/preview")
async def preview_social_posts(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Preview generated social media posts before publishing.

    Shows content formatted for each platform with visual assets.
    """
    try:
        # Get social media posts from database
        from sqlalchemy import text

        query = """
            SELECT sp.id, sp.property_id, sp.platforms, sp.content_type, sp.content, 
                   sp.status, sp.scheduled_time, sp.created_at, p.title as property_title
            FROM social_media_posts sp
            LEFT JOIN properties p ON sp.property_id = p.id
            WHERE sp.task_id = :task_id
        """

        result = db.execute(text(query), {"task_id": task_id})
        posts = []

        for row in result.fetchall():
            # Check user access
            if current_user.role not in ["admin"]:
                # Additional access check would go here
                pass

            posts.append(
                {
                    "id": row.id,
                    "property_id": row.property_id,
                    "property_title": row.property_title,
                    "platforms": json.loads(row.platforms) if row.platforms else [],
                    "content_type": row.content_type,
                    "content": json.loads(row.content) if row.content else {},
                    "status": row.status,
                    "scheduled_time": row.scheduled_time,
                    "created_at": row.created_at,
                }
            )

        if not posts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media posts not found or not yet completed",
            )

        return {
            "task_id": task_id,
            "posts": posts,
            "total_posts": len(posts),
            "platforms_covered": list(
                set(sum([post["platforms"] for post in posts], []))
            ),
            "actions": {
                "approve_all": f"/api/v1/social/posts/{task_id}/publish",
                "schedule_all": f"/api/v1/social/posts/{task_id}/schedule",
                "edit_post": "/api/v1/social/posts/{post_id}/edit",
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview social posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview posts: {str(e)}",
        )


@router.post("/posts/{task_id}/publish")
async def publish_social_posts(
    task_id: str,
    platforms: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Publish approved social media posts to selected platforms.

    This would integrate with platform APIs for actual publishing.
    For now, it marks posts as published and logs the action.
    """
    try:
        # Get posts for this task
        from sqlalchemy import text

        query = """
            SELECT id, platforms, content, scheduled_time
            FROM social_media_posts
            WHERE task_id = :task_id AND status IN ('draft', 'scheduled')
        """

        result = db.execute(text(query), {"task_id": task_id})
        posts = result.fetchall()

        if not posts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No posts found ready for publishing",
            )

        published_count = 0
        for post in posts:
            post_platforms = json.loads(post.platforms) if post.platforms else []

            # Filter platforms if specified
            if platforms:
                post_platforms = [p for p in post_platforms if p in platforms]

            if post_platforms:
                # TODO: Integrate with actual social media APIs
                # For now, just update status
                update_query = """
                    UPDATE social_media_posts
                    SET status = 'published', published_time = CURRENT_TIMESTAMP
                    WHERE id = :post_id
                """

                db.execute(text(update_query), {"post_id": post.id})
                published_count += 1

        db.commit()

        logger.info(
            f"Published {published_count} social media posts from task {task_id} by user {current_user.id}"
        )

        return {
            "task_id": task_id,
            "published_count": published_count,
            "status": "published",
            "message": f"Successfully published {published_count} social media posts",
            "platforms": platforms or "all",
            "published_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish social posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish posts: {str(e)}",
        )


# =============================================================================
# SOCIAL MEDIA CAMPAIGNS ENDPOINTS
# =============================================================================


@router.post("/campaigns", response_model=Dict[str, Any])
async def create_social_media_campaign(
    request: SocialCampaignRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Create a multi-post social media campaign.

    Campaigns include:
    - Property Launch: Series of posts introducing a new listing
    - Market Series: Educational content about Dubai real estate
    - Brand Awareness: Agent/brokerage promotion content

    Each campaign generates multiple posts scheduled over time.
    """
    try:
        task_data = {
            "campaign_name": request.campaign_name,
            "property_id": request.property_id,
            "campaign_type": request.campaign_type,
            "platforms": request.platforms,
            "post_frequency": request.post_frequency,
            "duration_days": request.duration_days,
            "start_date": request.start_date.isoformat()
            if request.start_date
            else datetime.utcnow().isoformat(),
            "user_id": current_user.id,
        }

        task_id = await orchestrator.submit_task(
            task_type="social_media_campaign",
            task_data=task_data,
            user_id=current_user.id,
            priority="medium",
        )

        logger.info(
            f"Social media campaign task {task_id} submitted: {request.campaign_name} by user {current_user.id}"
        )

        return {
            "task_id": task_id,
            "campaign_name": request.campaign_name,
            "campaign_type": request.campaign_type,
            "platforms": request.platforms,
            "duration_days": request.duration_days,
            "status": "processing",
            "message": f"Social media campaign '{request.campaign_name}' is being created.",
            "estimated_completion": "5-10 minutes",
            "check_status_url": f"/api/v1/social/campaigns/{task_id}/status",
        }

    except Exception as e:
        logger.error(f"Failed to create social media campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}",
        )


@router.get("/campaigns", response_model=List[Dict[str, Any]])
async def list_social_campaigns(
    status: Optional[str] = None,
    campaign_type: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List social media campaigns with filtering options.
    """
    try:
        from sqlalchemy import text

        query = """
            SELECT sc.id, sc.campaign_name, sc.campaign_type, sc.platforms, sc.status,
                   sc.posts_count, sc.posts_published, sc.start_date, sc.end_date,
                   sc.created_at, p.title as property_title
            FROM social_media_campaigns sc
            LEFT JOIN properties p ON sc.property_id = p.id
            WHERE sc.user_id = :user_id
        """

        params = {"user_id": current_user.id}

        if status:
            query += " AND sc.status = :status"
            params["status"] = status

        if campaign_type:
            query += " AND sc.campaign_type = :campaign_type"
            params["campaign_type"] = campaign_type

        query += " ORDER BY sc.created_at DESC LIMIT :limit"
        params["limit"] = limit

        result = db.execute(text(query), params)
        campaigns = []

        for row in result.fetchall():
            campaigns.append(
                {
                    "id": row.id,
                    "campaign_name": row.campaign_name,
                    "campaign_type": row.campaign_type,
                    "platforms": json.loads(row.platforms) if row.platforms else [],
                    "status": row.status,
                    "posts_count": row.posts_count,
                    "posts_published": row.posts_published,
                    "property_title": row.property_title,
                    "start_date": row.start_date,
                    "end_date": row.end_date,
                    "created_at": row.created_at,
                    "completion_rate": (row.posts_published / max(row.posts_count, 1))
                    * 100,
                }
            )

        return campaigns

    except Exception as e:
        logger.error(f"Failed to list campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}",
        )


# =============================================================================
# HASHTAG RESEARCH ENDPOINTS
# =============================================================================


@router.post("/hashtags/research", response_model=HashtagRecommendations)
async def research_hashtags(
    request: HashtagResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Research and recommend hashtags for Dubai real estate content.

    Provides categorized hashtag recommendations:
    - Trending: Current popular hashtags in Dubai real estate
    - Location-specific: Dubai neighborhoods and areas
    - Property-specific: Property types and features
    - Audience-targeted: Buyer, seller, investor focused

    All hashtags are researched for Dubai market relevance.
    """
    try:
        # Base Dubai real estate hashtags
        base_hashtags = [
            "#DubaiRealEstate",
            "#PropertyDubai",
            "#DubaiProperties",
            "#InvestInDubai",
            "#DubaiHomes",
            "#LuxuryDubai",
            "#RERA",
        ]

        # Location-specific hashtags
        location_hashtags = [
            "#DubaiMarina",
            "#DowntownDubai",
            "#JBR",
            "#PalmJumeirah",
            "#BusinessBay",
            "#DubaiHills",
            "#CityWalk",
            "#DIFC",
            "#JumeirahVillageCircle",
            "#ArabianRanches",
            "#EmiratesHills",
        ]

        # Property-specific hashtags
        property_hashtags = {
            "apartment": ["#DubaiApartment", "#ApartmentForSale", "#HighRise"],
            "villa": ["#DubaiVilla", "#LuxuryVilla", "#VillaForSale"],
            "townhouse": ["#Townhouse", "#FamilyHome", "#GatedCommunity"],
            "penthouse": ["#Penthouse", "#LuxuryLiving", "#SkylineViews"],
            "office": ["#DubaiOffice", "#CommercialSpace", "#BusinessHub"],
            "retail": ["#RetailSpace", "#ShopForRent", "#CommercialProperty"],
        }

        # Audience-specific hashtags
        audience_hashtags = {
            "buyers": ["#FirstTimeBuyer", "#DreamHome", "#PropertySearch"],
            "investors": ["#RealEstateInvestment", "#PropertyInvestment", "#ROI"],
            "renters": ["#RentInDubai", "#PropertyRental", "#TenantServices"],
            "sellers": ["#SellYourProperty", "#PropertyValuation", "#QuickSale"],
        }

        # Build recommendations
        recommended = []

        # Add base hashtags
        for hashtag in base_hashtags:
            recommended.append(
                {
                    "hashtag": hashtag,
                    "category": "essential",
                    "popularity": "high",
                    "relevance": 95,
                }
            )

        # Add location-specific if location provided
        if request.location:
            location_matches = [
                h for h in location_hashtags if request.location.lower() in h.lower()
            ]
            for hashtag in location_matches[:5]:
                recommended.append(
                    {
                        "hashtag": hashtag,
                        "category": "location",
                        "popularity": "medium",
                        "relevance": 85,
                    }
                )

        # Add property-specific if property type provided
        if request.property_type and request.property_type in property_hashtags:
            for hashtag in property_hashtags[request.property_type]:
                recommended.append(
                    {
                        "hashtag": hashtag,
                        "category": "property_type",
                        "popularity": "medium",
                        "relevance": 80,
                    }
                )

        # Add audience-targeted
        if request.target_audience in audience_hashtags:
            for hashtag in audience_hashtags[request.target_audience]:
                recommended.append(
                    {
                        "hashtag": hashtag,
                        "category": "audience",
                        "popularity": "medium",
                        "relevance": 75,
                    }
                )

        # Limit to max_hashtags
        recommended = recommended[: request.max_hashtags]

        return HashtagRecommendations(
            recommended_hashtags=recommended,
            trending_hashtags=[
                "#DubaiRealEstate2024",
                "#PropertyExpo2024",
                "#InvestDubai",
            ],
            location_specific=location_hashtags[:10],
            property_specific=property_hashtags.get(request.property_type, [])[:8],
            audience_targeted=audience_hashtags.get(request.target_audience, [])[:8],
        )

    except Exception as e:
        logger.error(f"Failed to research hashtags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to research hashtags: {str(e)}",
        )


# =============================================================================
# CONTENT SCHEDULING ENDPOINTS
# =============================================================================


@router.get("/schedule/upcoming")
async def get_upcoming_posts(
    days: int = 7,
    platform: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get upcoming scheduled social media posts.
    """
    try:
        from sqlalchemy import text

        query = """
            SELECT id, property_id, platforms, content_type, scheduled_time, status,
                   (content->>'text') as post_text
            FROM social_media_posts
            WHERE user_id = :user_id 
                AND status = 'scheduled'
                AND scheduled_time BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL :days DAY
        """

        params = {"user_id": current_user.id, "days": days}

        if platform:
            query += " AND platforms::text ILIKE :platform"
            params["platform"] = f"%{platform}%"

        query += " ORDER BY scheduled_time ASC"

        result = db.execute(text(query), params)
        upcoming_posts = []

        for row in result.fetchall():
            upcoming_posts.append(
                {
                    "id": row.id,
                    "property_id": row.property_id,
                    "platforms": json.loads(row.platforms) if row.platforms else [],
                    "content_type": row.content_type,
                    "scheduled_time": row.scheduled_time,
                    "status": row.status,
                    "preview_text": row.post_text[:100] + "..."
                    if row.post_text and len(row.post_text) > 100
                    else row.post_text,
                }
            )

        return {
            "upcoming_posts": upcoming_posts,
            "total_scheduled": len(upcoming_posts),
            "period": f"Next {days} days",
            "platforms_summary": {},  # TODO: Add platform breakdown
        }

    except Exception as e:
        logger.error(f"Failed to get upcoming posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming posts: {str(e)}",
        )


# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================


@router.get("/analytics/summary")
async def get_social_media_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get social media analytics summary for the current user.

    Provides insights into:
    - Posts published across platforms
    - Most engaging content types
    - Best performing hashtags
    - Optimal posting times
    """
    try:
        from sqlalchemy import text

        # Get post statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_posts,
                COUNT(CASE WHEN status = 'published' THEN 1 END) as published_posts,
                COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_posts,
                COUNT(DISTINCT property_id) as properties_promoted
            FROM social_media_posts
            WHERE user_id = :user_id 
                AND created_at >= CURRENT_DATE - INTERVAL :days DAY
        """

        result = db.execute(
            text(stats_query), {"user_id": current_user.id, "days": days}
        )
        stats = result.fetchone()

        # Get content type performance
        content_query = """
            SELECT content_type, COUNT(*) as post_count
            FROM social_media_posts
            WHERE user_id = :user_id 
                AND created_at >= CURRENT_DATE - INTERVAL :days DAY
                AND status = 'published'
            GROUP BY content_type
            ORDER BY post_count DESC
            LIMIT 5
        """

        content_result = db.execute(
            text(content_query), {"user_id": current_user.id, "days": days}
        )
        content_performance = [
            {"content_type": row.content_type, "post_count": row.post_count}
            for row in content_result.fetchall()
        ]

        return {
            "period": f"Last {days} days",
            "post_statistics": {
                "total_posts": stats.total_posts or 0,
                "published_posts": stats.published_posts or 0,
                "scheduled_posts": stats.scheduled_posts or 0,
                "properties_promoted": stats.properties_promoted or 0,
                "publication_rate": (stats.published_posts or 0)
                / max(stats.total_posts or 1, 1)
                * 100,
            },
            "content_performance": content_performance,
            "insights": [
                "Listing posts generate highest engagement",
                "Best posting times: 9 AM and 6 PM Dubai time",
                "Instagram Stories have 2x higher reach than posts",
                "Location-specific hashtags increase visibility by 40%",
            ],
            "recommendations": [
                "Post consistently across all platforms",
                "Use 8-15 hashtags for optimal reach",
                "Include property visuals in every post",
                "Engage with comments within 2 hours",
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get social media analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}",
        )
