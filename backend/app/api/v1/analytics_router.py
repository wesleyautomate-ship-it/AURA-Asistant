"""
Analytics and Reporting Router
===============================

FastAPI router that provides comprehensive analytics and reporting functionality.

Features:
- Business intelligence dashboards
- Property performance analytics
- Market trend analysis and forecasting
- Lead generation and conversion tracking
- Agent performance metrics
- Revenue and commission reporting
- Custom report generation
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.middleware import get_current_user, require_roles
from app.core.models import User
from app.domain.ai.task_orchestrator import AITaskOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Reporting"])

# Dependency injection for AI orchestrator
def get_orchestrator(db: Session = Depends(get_db)) -> AITaskOrchestrator:
    """Get AI task orchestrator instance"""
    return AITaskOrchestrator(lambda: db)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class AnalyticsRequest(BaseModel):
    """Request model for analytics queries"""

    metric_type: str = Field(
        ..., pattern="^(performance|market|leads|revenue|properties)$"
    )
    time_period: str = Field(
        "30days", pattern="^(7days|30days|90days|12months|ytd|all)$"
    )
    granularity: str = Field("daily", pattern="^(hourly|daily|weekly|monthly)$")
    filters: Optional[Dict[str, Any]] = None


class ReportGenerationRequest(BaseModel):
    """Request model for custom report generation"""

    report_type: str = Field(
        ...,
        pattern="^(performance|market_analysis|lead_funnel|commission|property_portfolio)$",
    )
    report_name: str
    time_period: str = Field(
        "30days", pattern="^(7days|30days|90days|12months|ytd|custom)$"
    )
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_charts: bool = True
    include_forecasting: bool = False
    recipients: Optional[List[str]] = []


class DashboardRequest(BaseModel):
    """Request model for dashboard configuration"""

    dashboard_type: str = Field("agent", pattern="^(agent|team|brokerage|market)$")
    widgets: List[str] = Field(default_factory=list)
    refresh_interval: int = Field(300, ge=60, le=3600)  # seconds


class PerformanceMetrics(BaseModel):
    """Response model for performance metrics"""

    total_listings: int
    active_listings: int
    sold_listings: int
    total_revenue: float
    avg_days_on_market: float
    conversion_rate: float
    lead_count: int
    qualified_leads: int
    period: str


class MarketInsights(BaseModel):
    """Response model for market insights"""

    avg_price_psf: float
    median_price: float
    total_transactions: int
    price_trend: float
    inventory_levels: str
    hottest_areas: List[Dict[str, Any]]
    market_forecast: Optional[Dict[str, Any]] = None


class LeadAnalytics(BaseModel):
    """Response model for lead analytics"""

    total_leads: int
    qualified_leads: int
    conversion_rate: float
    lead_sources: List[Dict[str, Any]]
    lead_funnel: Dict[str, int]
    avg_response_time: float  # hours


# =============================================================================
# DASHBOARD ENDPOINTS
# =============================================================================


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    time_period: str = Query("30days", pattern="^(7days|30days|90days|12months)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive dashboard overview for the current user.

    Provides high-level metrics across all key areas:
    - Property performance and listings
    - Revenue and commission tracking
    - Lead generation and conversion
    - Market position and trends
    - Recent activity summary

    This is the main dashboard that agents see when they login.
    """
    try:
        from sqlalchemy import text

        # Calculate date range
        if time_period == "7days":
            days = 7
        elif time_period == "30days":
            days = 30
        elif time_period == "90days":
            days = 90
        else:  # 12months
            days = 365

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get property statistics
        property_stats_query = """
            SELECT 
                COUNT(*) as total_listings,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_listings,
                COUNT(CASE WHEN status = 'sold' THEN 1 END) as sold_listings,
                COUNT(CASE WHEN status = 'rented' THEN 1 END) as rented_listings,
                AVG(price) as avg_price,
                SUM(CASE WHEN status IN ('sold', 'rented') THEN price ELSE 0 END) as total_revenue
            FROM properties
            WHERE agent_id = :agent_id 
                AND created_at >= :cutoff_date
        """

        result = db.execute(
            text(property_stats_query),
            {"agent_id": current_user.id, "cutoff_date": cutoff_date},
        )
        property_stats = result.fetchone()

        # Get lead statistics
        lead_stats_query = """
            SELECT 
                COUNT(*) as total_leads,
                COUNT(CASE WHEN status = 'qualified' THEN 1 END) as qualified_leads,
                COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_leads
            FROM leads
            WHERE agent_id = :agent_id 
                AND created_at >= :cutoff_date
        """

        lead_result = db.execute(
            text(lead_stats_query),
            {"agent_id": current_user.id, "cutoff_date": cutoff_date},
        )
        lead_stats = lead_result.fetchone()

        # Get recent activities
        activity_query = """
            SELECT activity_type, description, created_at, property_id
            FROM agent_activities
            WHERE agent_id = :agent_id
            ORDER BY created_at DESC
            LIMIT 10
        """

        activity_result = db.execute(
            text(activity_query), {"agent_id": current_user.id}
        )
        recent_activities = [
            {
                "activity_type": row.activity_type,
                "description": row.description,
                "created_at": row.created_at,
                "property_id": row.property_id,
            }
            for row in activity_result.fetchall()
        ]

        # Calculate key metrics
        conversion_rate = (
            (lead_stats.converted_leads or 0)
            / max(lead_stats.total_leads or 1, 1)
            * 100
            if lead_stats
            else 0
        )

        return {
            "period": time_period,
            "date_range": {
                "start": cutoff_date.isoformat(),
                "end": datetime.utcnow().isoformat(),
            },
            "property_performance": {
                "total_listings": property_stats.total_listings or 0,
                "active_listings": property_stats.active_listings or 0,
                "sold_listings": property_stats.sold_listings or 0,
                "rented_listings": property_stats.rented_listings or 0,
                "avg_price": property_stats.avg_price or 0,
                "total_revenue": property_stats.total_revenue or 0,
            },
            "lead_performance": {
                "total_leads": lead_stats.total_leads or 0,
                "qualified_leads": lead_stats.qualified_leads or 0,
                "converted_leads": lead_stats.converted_leads or 0,
                "conversion_rate": round(conversion_rate, 2),
            },
            "recent_activities": recent_activities,
            "quick_actions": [
                {
                    "action": "create_listing",
                    "label": "Add New Listing",
                    "url": "/api/properties",
                },
                {
                    "action": "generate_cma",
                    "label": "Create CMA Report",
                    "url": "/api/v1/cma/reports",
                },
                {
                    "action": "social_post",
                    "label": "Create Social Post",
                    "url": "/api/v1/social/posts",
                },
                {
                    "action": "lead_follow_up",
                    "label": "Follow Up Leads",
                    "url": "/api/leads",
                },
            ],
            "alerts": [],  # TODO: Add intelligent alerts based on performance
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard overview: {str(e)}",
        )


@router.get("/dashboard/widgets/{widget_type}")
async def get_dashboard_widget(
    widget_type: str,
    time_period: str = Query("30days"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get specific dashboard widget data.

    Supports various widget types:
    - listings_chart: Property listings over time
    - revenue_chart: Revenue trends and forecasting
    - lead_funnel: Lead conversion funnel
    - market_pulse: Current market conditions
    - top_properties: Best performing listings
    """
    try:
        from sqlalchemy import text

        if widget_type == "listings_chart":
            # Get listings data over time
            query = """
                SELECT DATE(created_at) as date, COUNT(*) as count, status
                FROM properties
                WHERE agent_id = :agent_id 
                    AND created_at >= CURRENT_DATE - INTERVAL 30 DAY
                GROUP BY DATE(created_at), status
                ORDER BY date
            """

            result = db.execute(text(query), {"agent_id": current_user.id})
            data = [
                {"date": row.date.isoformat(), "count": row.count, "status": row.status}
                for row in result.fetchall()
            ]

            return {"widget_type": "listings_chart", "data": data}

        elif widget_type == "revenue_chart":
            # Get revenue data over time
            query = """
                SELECT DATE(updated_at) as date, SUM(price) as revenue
                FROM properties
                WHERE agent_id = :agent_id 
                    AND status IN ('sold', 'rented')
                    AND updated_at >= CURRENT_DATE - INTERVAL 30 DAY
                GROUP BY DATE(updated_at)
                ORDER BY date
            """

            result = db.execute(text(query), {"agent_id": current_user.id})
            data = [
                {"date": row.date.isoformat(), "revenue": float(row.revenue)}
                for row in result.fetchall()
            ]

            return {"widget_type": "revenue_chart", "data": data}

        elif widget_type == "lead_funnel":
            # Get lead funnel data
            query = """
                SELECT status, COUNT(*) as count
                FROM leads
                WHERE agent_id = :agent_id
                GROUP BY status
                ORDER BY 
                    CASE status 
                        WHEN 'new' THEN 1
                        WHEN 'contacted' THEN 2
                        WHEN 'qualified' THEN 3
                        WHEN 'viewing' THEN 4
                        WHEN 'offer' THEN 5
                        WHEN 'converted' THEN 6
                        ELSE 7
                    END
            """

            result = db.execute(text(query), {"agent_id": current_user.id})
            data = [
                {"status": row.status, "count": row.count} for row in result.fetchall()
            ]

            return {"widget_type": "lead_funnel", "data": data}

        elif widget_type == "market_pulse":
            # Get current market conditions
            query = """
                SELECT 
                    AVG(price/area_sqft) as avg_price_psf,
                    COUNT(*) as total_listings,
                    AVG(CASE WHEN status = 'sold' 
                        THEN EXTRACT(DAY FROM updated_at - created_at) 
                        ELSE NULL 
                    END) as avg_days_on_market
                FROM properties
                WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAY
            """

            result = db.execute(text(query))
            row = result.fetchone()

            data = {
                "avg_price_psf": round(row.avg_price_psf or 0, 2),
                "total_listings": row.total_listings or 0,
                "avg_days_on_market": round(row.avg_days_on_market or 0, 1),
                "market_trend": "stable",  # TODO: Calculate actual trend
            }

            return {"widget_type": "market_pulse", "data": data}

        elif widget_type == "top_properties":
            # Get top performing properties
            query = """
                SELECT id, title, location, price, status, created_at,
                       (price/area_sqft) as price_per_sqft
                FROM properties
                WHERE agent_id = :agent_id
                ORDER BY price DESC
                LIMIT 5
            """

            result = db.execute(text(query), {"agent_id": current_user.id})
            data = [
                {
                    "id": row.id,
                    "title": row.title,
                    "location": row.location,
                    "price": float(row.price),
                    "status": row.status,
                    "price_per_sqft": round(row.price_per_sqft or 0, 2),
                }
                for row in result.fetchall()
            ]

            return {"widget_type": "top_properties", "data": data}

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown widget type: {widget_type}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard widget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget data: {str(e)}",
        )


# =============================================================================
# PERFORMANCE ANALYTICS ENDPOINTS
# =============================================================================


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    time_period: str = Query("30days"),
    include_forecast: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive performance metrics for the current user.

    Includes:
    - Listing performance (total, active, sold)
    - Revenue and commission tracking
    - Market positioning metrics
    - Lead conversion statistics
    - Productivity indicators
    """
    try:
        from sqlalchemy import text

        # Calculate date range
        days_map = {"7days": 7, "30days": 30, "90days": 90, "12months": 365}
        days = days_map.get(time_period, 30)
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get comprehensive property stats
        property_query = """
            SELECT 
                COUNT(*) as total_listings,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_listings,
                COUNT(CASE WHEN status = 'sold' THEN 1 END) as sold_listings,
                SUM(CASE WHEN status IN ('sold', 'rented') THEN price ELSE 0 END) as total_revenue,
                AVG(CASE WHEN status = 'sold' 
                    THEN EXTRACT(DAY FROM updated_at - created_at)
                    ELSE NULL 
                END) as avg_days_on_market
            FROM properties
            WHERE agent_id = :agent_id 
                AND created_at >= :cutoff_date
        """

        prop_result = db.execute(
            text(property_query),
            {"agent_id": current_user.id, "cutoff_date": cutoff_date},
        )
        prop_stats = prop_result.fetchone()

        # Get lead stats
        lead_query = """
            SELECT 
                COUNT(*) as lead_count,
                COUNT(CASE WHEN status IN ('qualified', 'viewing', 'offer') THEN 1 END) as qualified_leads,
                COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_leads
            FROM leads
            WHERE agent_id = :agent_id 
                AND created_at >= :cutoff_date
        """

        lead_result = db.execute(
            text(lead_query), {"agent_id": current_user.id, "cutoff_date": cutoff_date}
        )
        lead_stats = lead_result.fetchone()

        # Calculate conversion rate
        conversion_rate = (
            (lead_stats.converted_leads or 0) / max(lead_stats.lead_count or 1, 1) * 100
        )

        return PerformanceMetrics(
            total_listings=prop_stats.total_listings or 0,
            active_listings=prop_stats.active_listings or 0,
            sold_listings=prop_stats.sold_listings or 0,
            total_revenue=float(prop_stats.total_revenue or 0),
            avg_days_on_market=round(prop_stats.avg_days_on_market or 0, 1),
            conversion_rate=round(conversion_rate, 2),
            lead_count=lead_stats.lead_count or 0,
            qualified_leads=lead_stats.qualified_leads or 0,
            period=time_period,
        )

    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}",
        )


@router.get("/performance/trends")
async def get_performance_trends(
    metric: str = Query("revenue", pattern="^(revenue|listings|leads|conversion)$"),
    time_period: str = Query("90days"),
    granularity: str = Query("weekly", pattern="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get performance trends over time for specific metrics.

    Supports trend analysis for:
    - Revenue patterns and seasonality
    - Listing activity cycles
    - Lead generation trends
    - Conversion rate evolution
    """
    try:
        from sqlalchemy import text

        # Define date grouping based on granularity
        date_group = {
            "daily": "DATE(created_at)",
            "weekly": "DATE_SUB(DATE(created_at), INTERVAL WEEKDAY(created_at) DAY)",
            "monthly": "DATE_FORMAT(created_at, '%Y-%m-01')",
        }[granularity]

        if metric == "revenue":
            query = f"""
                SELECT {date_group} as period, 
                       SUM(CASE WHEN status IN ('sold', 'rented') THEN price ELSE 0 END) as value
                FROM properties
                WHERE agent_id = :agent_id
                    AND created_at >= CURRENT_DATE - INTERVAL 90 DAY
                GROUP BY {date_group}
                ORDER BY period
            """

        elif metric == "listings":
            query = f"""
                SELECT {date_group} as period, COUNT(*) as value
                FROM properties
                WHERE agent_id = :agent_id
                    AND created_at >= CURRENT_DATE - INTERVAL 90 DAY
                GROUP BY {date_group}
                ORDER BY period
            """

        elif metric == "leads":
            query = f"""
                SELECT {date_group} as period, COUNT(*) as value
                FROM leads
                WHERE agent_id = :agent_id
                    AND created_at >= CURRENT_DATE - INTERVAL 90 DAY
                GROUP BY {date_group}
                ORDER BY period
            """

        else:  # conversion
            query = f"""
                SELECT {date_group} as period,
                       (COUNT(CASE WHEN status = 'converted' THEN 1 END) / 
                        GREATEST(COUNT(*), 1) * 100) as value
                FROM leads
                WHERE agent_id = :agent_id
                    AND created_at >= CURRENT_DATE - INTERVAL 90 DAY
                GROUP BY {date_group}
                ORDER BY period
            """

        result = db.execute(text(query), {"agent_id": current_user.id})
        trend_data = [
            {
                "period": row.period.isoformat()
                if hasattr(row.period, "isoformat")
                else str(row.period),
                "value": float(row.value or 0),
            }
            for row in result.fetchall()
        ]

        return {
            "metric": metric,
            "granularity": granularity,
            "time_period": time_period,
            "trend_data": trend_data,
            "summary": {
                "total_points": len(trend_data),
                "avg_value": sum(p["value"] for p in trend_data)
                / max(len(trend_data), 1),
                "trend_direction": "stable",  # TODO: Calculate actual trend direction
            },
        }

    except Exception as e:
        logger.error(f"Failed to get performance trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trends: {str(e)}",
        )


# =============================================================================
# MARKET ANALYTICS ENDPOINTS
# =============================================================================


@router.get("/market/insights", response_model=MarketInsights)
async def get_market_insights(
    area: Optional[str] = None,
    property_type: Optional[str] = None,
    include_forecast: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive market insights for Dubai real estate.

    Provides market intelligence including:
    - Average pricing and trends
    - Transaction volume analysis
    - Inventory levels and activity
    - Hottest areas and property types
    - Market forecasting (optional)
    """
    try:
        from sqlalchemy import text

        # Build market analysis query with optional filters
        base_query = """
            SELECT 
                AVG(price/area_sqft) as avg_price_psf,
                AVG(price) as median_price,
                COUNT(*) as total_transactions,
                AVG(CASE WHEN status = 'sold' 
                    THEN EXTRACT(DAY FROM updated_at - created_at)
                    ELSE NULL 
                END) as avg_days_on_market
            FROM properties
            WHERE created_at >= CURRENT_DATE - INTERVAL 90 DAY
        """

        params = {}

        if area:
            base_query += " AND location ILIKE :area"
            params["area"] = f"%{area}%"

        if property_type:
            base_query += " AND property_type = :property_type"
            params["property_type"] = property_type

        result = db.execute(text(base_query), params)
        market_data = result.fetchone()

        # Get hottest areas
        area_query = """
            SELECT location, COUNT(*) as transaction_count,
                   AVG(price) as avg_price
            FROM properties
            WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAY
                AND status = 'sold'
            GROUP BY location
            ORDER BY transaction_count DESC
            LIMIT 5
        """

        area_result = db.execute(text(area_query))
        hottest_areas = [
            {
                "area": row.location,
                "transactions": row.transaction_count,
                "avg_price": float(row.avg_price),
                "activity_level": "high" if row.transaction_count > 5 else "medium",
            }
            for row in area_result.fetchall()
        ]

        # Calculate price trend (simplified)
        trend_query = """
            SELECT 
                AVG(CASE WHEN created_at >= CURRENT_DATE - INTERVAL 30 DAY 
                    THEN price/area_sqft ELSE NULL END) as recent_price_psf,
                AVG(CASE WHEN created_at >= CURRENT_DATE - INTERVAL 60 DAY 
                         AND created_at < CURRENT_DATE - INTERVAL 30 DAY
                    THEN price/area_sqft ELSE NULL END) as prev_price_psf
            FROM properties
        """

        trend_result = db.execute(text(trend_query))
        trend_data = trend_result.fetchone()

        price_trend = 0.0
        if trend_data.recent_price_psf and trend_data.prev_price_psf:
            price_trend = (
                (trend_data.recent_price_psf - trend_data.prev_price_psf)
                / trend_data.prev_price_psf
                * 100
            )

        # Determine inventory levels
        inventory_levels = "balanced"
        if market_data.avg_days_on_market:
            if market_data.avg_days_on_market < 30:
                inventory_levels = "low"
            elif market_data.avg_days_on_market > 90:
                inventory_levels = "high"

        return MarketInsights(
            avg_price_psf=round(market_data.avg_price_psf or 0, 2),
            median_price=round(market_data.median_price or 0, 2),
            total_transactions=market_data.total_transactions or 0,
            price_trend=round(price_trend, 2),
            inventory_levels=inventory_levels,
            hottest_areas=hottest_areas,
            market_forecast={"status": "coming_soon"} if include_forecast else None,
        )

    except Exception as e:
        logger.error(f"Failed to get market insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market insights: {str(e)}",
        )


# =============================================================================
# LEAD ANALYTICS ENDPOINTS
# =============================================================================


@router.get("/leads", response_model=LeadAnalytics)
async def get_lead_analytics(
    time_period: str = Query("30days"),
    source_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive lead analytics and conversion tracking.

    Provides insights into:
    - Lead generation performance
    - Source attribution and ROI
    - Conversion funnel analysis
    - Response time optimization
    - Lead quality scoring
    """
    try:
        from sqlalchemy import text

        days_map = {"7days": 7, "30days": 30, "90days": 90, "12months": 365}
        days = days_map.get(time_period, 30)
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get lead statistics
        lead_query = """
            SELECT 
                COUNT(*) as total_leads,
                COUNT(CASE WHEN status IN ('qualified', 'viewing', 'offer') THEN 1 END) as qualified_leads,
                COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_leads,
                AVG(CASE WHEN first_contact_time IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM first_contact_time - created_at) / 3600.0
                    ELSE NULL 
                END) as avg_response_hours
            FROM leads
            WHERE agent_id = :agent_id 
                AND created_at >= :cutoff_date
        """

        if source_filter:
            lead_query += " AND source = :source_filter"

        params = {"agent_id": current_user.id, "cutoff_date": cutoff_date}
        if source_filter:
            params["source_filter"] = source_filter

        lead_result = db.execute(text(lead_query), params)
        lead_stats = lead_result.fetchone()

        # Get lead sources
        source_query = """
            SELECT source, COUNT(*) as count,
                   COUNT(CASE WHEN status = 'converted' THEN 1 END) as conversions
            FROM leads
            WHERE agent_id = :agent_id 
                AND created_at >= :cutoff_date
            GROUP BY source
            ORDER BY count DESC
            LIMIT 10
        """

        source_result = db.execute(text(source_query), params)
        lead_sources = [
            {
                "source": row.source,
                "count": row.count,
                "conversions": row.conversions,
                "conversion_rate": round(
                    (row.conversions / max(row.count, 1)) * 100, 2
                ),
            }
            for row in source_result.fetchall()
        ]

        # Get lead funnel
        funnel_query = """
            SELECT status, COUNT(*) as count
            FROM leads
            WHERE agent_id = :agent_id 
                AND created_at >= :cutoff_date
            GROUP BY status
        """

        funnel_result = db.execute(text(funnel_query), params)
        lead_funnel = {row.status: row.count for row in funnel_result.fetchall()}

        # Calculate conversion rate
        conversion_rate = (
            (lead_stats.converted_leads or 0)
            / max(lead_stats.total_leads or 1, 1)
            * 100
        )

        return LeadAnalytics(
            total_leads=lead_stats.total_leads or 0,
            qualified_leads=lead_stats.qualified_leads or 0,
            conversion_rate=round(conversion_rate, 2),
            lead_sources=lead_sources,
            lead_funnel=lead_funnel,
            avg_response_time=round(lead_stats.avg_response_hours or 0, 2),
        )

    except Exception as e:
        logger.error(f"Failed to get lead analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lead analytics: {str(e)}",
        )


# =============================================================================
# CUSTOM REPORT GENERATION ENDPOINTS
# =============================================================================


@router.post("/reports/generate")
async def generate_custom_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Generate custom analytical reports.

    Supports various report types:
    - Performance: Agent productivity and achievements
    - Market Analysis: Area and property type insights
    - Lead Funnel: Conversion tracking and optimization
    - Commission: Revenue and earnings breakdown
    - Property Portfolio: Listing performance analysis

    Reports can be scheduled, shared, and exported in multiple formats.
    """
    try:
        # Set date range
        if request.start_date and request.end_date:
            start_date = request.start_date
            end_date = request.end_date
        else:
            days_map = {
                "7days": 7,
                "30days": 30,
                "90days": 90,
                "12months": 365,
                "ytd": None,
            }
            if request.time_period == "ytd":
                start_date = datetime(datetime.utcnow().year, 1, 1)
                end_date = datetime.utcnow()
            else:
                days = days_map.get(request.time_period, 30)
                start_date = datetime.utcnow() - timedelta(days=days)
                end_date = datetime.utcnow()

        # Submit report generation task
        task_data = {
            "report_type": request.report_type,
            "report_name": request.report_name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "include_charts": request.include_charts,
            "include_forecasting": request.include_forecasting,
            "recipients": request.recipients,
            "user_id": current_user.id,
            "agent_data": {
                "name": current_user.full_name
                or f"{current_user.first_name} {current_user.last_name}",
                "email": current_user.email,
            },
        }

        task_id = await orchestrator.submit_task(
            task_type="report_generation",
            task_data=task_data,
            user_id=current_user.id,
            priority="low",
        )

        logger.info(
            f"Report generation task {task_id} submitted: {request.report_name} by user {current_user.id}"
        )

        return {
            "task_id": task_id,
            "report_name": request.report_name,
            "report_type": request.report_type,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "status": "processing",
            "message": f"Report '{request.report_name}' generation started.",
            "estimated_completion": "3-8 minutes",
            "check_status_url": f"/api/v1/analytics/reports/{task_id}/status",
        }

    except Exception as e:
        logger.error(f"Failed to generate custom report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("/reports/{task_id}/status")
async def get_report_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Check the status of a report generation task.
    """
    try:
        task_status = await orchestrator.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report generation task not found",
            )

        # Check user access
        if task_status.get("user_id") != current_user.id and current_user.role not in [
            "admin"
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report",
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
                    "report_data": task_status["result"],
                    "download_url": f"/api/v1/analytics/reports/{task_id}/download",
                }
            )
        elif task_status.get("status") == "failed":
            response_data["error"] = task_status.get("error", "Unknown error occurred")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report status: {str(e)}",
        )


@router.get("/reports")
async def list_generated_reports(
    report_type: Optional[str] = None,
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List previously generated reports for the current user.
    """
    try:
        from sqlalchemy import text

        query = """
            SELECT id, report_name, report_type, generated_at, file_path, 
                   status, parameters
            FROM generated_reports
            WHERE user_id = :user_id
        """

        params = {"user_id": current_user.id}

        if report_type:
            query += " AND report_type = :report_type"
            params["report_type"] = report_type

        query += " ORDER BY generated_at DESC LIMIT :limit"
        params["limit"] = limit

        result = db.execute(text(query), params)
        reports = []

        for row in result.fetchall():
            reports.append(
                {
                    "id": row.id,
                    "report_name": row.report_name,
                    "report_type": row.report_type,
                    "generated_at": row.generated_at,
                    "status": row.status,
                    "file_path": row.file_path,
                    "parameters": json.loads(row.parameters) if row.parameters else {},
                    "download_url": f"/api/v1/analytics/reports/{row.id}/download"
                    if row.status == "completed"
                    else None,
                }
            )

        return {
            "reports": reports,
            "total_reports": len(reports),
            "available_types": [
                "performance",
                "market_analysis",
                "lead_funnel",
                "commission",
                "property_portfolio",
            ],
        }

    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reports: {str(e)}",
        )


# =============================================================================
# COMPARATIVE ANALYTICS ENDPOINTS
# =============================================================================


@router.get("/benchmarks")
async def get_performance_benchmarks(
    benchmark_type: str = Query("market", pattern="^(market|peer|historical)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get performance benchmarks for comparative analysis.

    Compares current user performance against:
    - Market averages in their area
    - Peer agents in similar markets
    - Historical performance trends
    """
    try:
        from sqlalchemy import text

        if benchmark_type == "market":
            # Compare against market averages
            query = """
                SELECT 
                    AVG(CASE WHEN agent_id = :agent_id THEN price ELSE NULL END) as user_avg_price,
                    AVG(CASE WHEN agent_id != :agent_id THEN price ELSE NULL END) as market_avg_price,
                    COUNT(CASE WHEN agent_id = :agent_id THEN 1 END) as user_listings,
                    COUNT(CASE WHEN agent_id != :agent_id THEN 1 END) as market_listings
                FROM properties
                WHERE created_at >= CURRENT_DATE - INTERVAL 90 DAY
                    AND status = 'sold'
            """

            result = db.execute(text(query), {"agent_id": current_user.id})
            benchmark = result.fetchone()

            return {
                "benchmark_type": "market",
                "user_performance": {
                    "avg_price": float(benchmark.user_avg_price or 0),
                    "total_listings": benchmark.user_listings or 0,
                },
                "market_performance": {
                    "avg_price": float(benchmark.market_avg_price or 0),
                    "total_listings": benchmark.market_listings or 0,
                },
                "comparison": {
                    "price_vs_market": (
                        (
                            (benchmark.user_avg_price or 0)
                            - (benchmark.market_avg_price or 0)
                        )
                        / max(benchmark.market_avg_price or 1, 1)
                        * 100
                    ),
                    "performance_rating": "above_average",  # TODO: Calculate actual rating
                },
            }

        else:
            return {
                "benchmark_type": benchmark_type,
                "status": "coming_soon",
                "message": f"{benchmark_type.title()} benchmarks will be available in the next release",
            }

    except Exception as e:
        logger.error(f"Failed to get benchmarks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get benchmarks: {str(e)}",
        )
