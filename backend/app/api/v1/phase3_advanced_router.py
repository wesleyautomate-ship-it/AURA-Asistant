"""
Phase 3 Advanced Router
=======================

FastAPI router for Phase 3 advanced features including:
- Dubai data integration
- Developer panel
- Advanced analytics
- System monitoring
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from auth.database import get_db
from auth.middleware import get_current_user, require_roles
from auth.models import User
from services.dubai_data_integration_service import DubaiDataIntegrationService
from services.developer_panel_service import DeveloperPanelService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/phase3", tags=["Phase 3 Advanced Features"])

# =====================================================
# PYDANTIC MODELS
# =====================================================


class MarketDataRequest(BaseModel):
    area_name: str = Field(..., description="Dubai area name (e.g., 'Dubai Marina')")
    property_type: str = Field(
        ..., description="Property type (e.g., 'apartment', 'villa')"
    )
    data_types: Optional[List[str]] = Field(None, description="Types of data to fetch")
    period_start: Optional[date] = Field(None, description="Start date for data period")
    period_end: Optional[date] = Field(None, description="End date for data period")


class RERAComplianceRequest(BaseModel):
    property_id: int = Field(..., description="Property ID to check compliance for")
    compliance_type: str = Field("listing", description="Type of compliance check")


class SystemAlertCreate(BaseModel):
    alert_type: str = Field(
        ..., description="Alert type (error, warning, info, performance)"
    )
    alert_category: str = Field(
        ...,
        description="Alert category (system, database, ai_processing, user_activity)",
    )
    alert_title: str = Field(..., description="Alert title")
    alert_message: str = Field(..., description="Alert message")
    severity: str = Field(
        "medium", description="Alert severity (low, medium, high, critical)"
    )
    affected_components: Optional[List[str]] = Field(
        None, description="List of affected components"
    )
    alert_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional alert data"
    )


class SystemAlertResolve(BaseModel):
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")


class DeveloperSettingsUpdate(BaseModel):
    settings: Dict[str, Dict[str, Any]] = Field(..., description="Settings to update")


# =====================================================
# DUBAI DATA INTEGRATION ENDPOINTS
# =====================================================


@router.get("/dubai/market-data", response_model=Dict[str, Any])
async def get_market_data(
    area_name: str = Query(..., description="Dubai area name"),
    property_type: str = Query(..., description="Property type"),
    data_types: Optional[str] = Query(None, description="Comma-separated data types"),
    period_start: Optional[date] = Query(None, description="Start date"),
    period_end: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get Dubai market data for a specific area and property type"""
    try:
        service = DubaiDataIntegrationService(db)

        data_types_list = data_types.split(",") if data_types else None

        result = await service.fetch_market_data(
            area_name=area_name,
            property_type=property_type,
            data_types=data_types_list,
            period_start=period_start,
            period_end=period_end,
        )

        return result

    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market data: {str(e)}",
        )


@router.get("/dubai/rera-data/{rera_number}", response_model=Dict[str, Any])
async def get_rera_data(
    rera_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get RERA property data by RERA number"""
    try:
        service = DubaiDataIntegrationService(db)

        result = await service.fetch_rera_property_data(rera_number)

        return result

    except Exception as e:
        logger.error(f"Error getting RERA data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get RERA data: {str(e)}",
        )


@router.post("/dubai/compliance-check", response_model=Dict[str, Any])
async def check_rera_compliance(
    compliance_request: RERAComplianceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check RERA compliance for a property"""
    try:
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage",
            )

        service = DubaiDataIntegrationService(db)

        result = await service.check_rera_compliance(
            property_id=compliance_request.property_id,
            brokerage_id=current_user.brokerage_id,
            compliance_type=compliance_request.compliance_type,
        )

        return result

    except Exception as e:
        logger.error(f"Error checking RERA compliance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check compliance: {str(e)}",
        )


@router.get("/dubai/market-analytics", response_model=Dict[str, Any])
async def get_market_analytics(
    area_name: Optional[str] = Query(None, description="Filter by area name"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    period_days: int = Query(30, description="Period in days"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive market analytics"""
    try:
        service = DubaiDataIntegrationService(db)

        result = await service.get_market_analytics(
            area_name=area_name, property_type=property_type, period_days=period_days
        )

        return result

    except Exception as e:
        logger.error(f"Error getting market analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market analytics: {str(e)}",
        )


@router.get("/dubai/compliance-analytics", response_model=Dict[str, Any])
async def get_compliance_analytics(
    current_user: User = Depends(require_roles(["admin", "brokerage_owner"])),
    db: Session = Depends(get_db),
):
    """Get compliance analytics for a brokerage"""
    try:
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage",
            )

        service = DubaiDataIntegrationService(db)

        result = await service.get_compliance_analytics(current_user.brokerage_id)

        return result

    except Exception as e:
        logger.error(f"Error getting compliance analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance analytics: {str(e)}",
        )


# =====================================================
# DEVELOPER PANEL ENDPOINTS
# =====================================================


@router.get("/developer/system-health", response_model=Dict[str, Any])
async def get_system_health(
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Get comprehensive system health status"""
    try:
        service = DeveloperPanelService(db)

        result = await service.get_system_health()

        return result

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}",
        )


@router.get("/developer/performance-analytics", response_model=Dict[str, Any])
async def get_performance_analytics(
    period_hours: int = Query(24, description="Period in hours"),
    metric_categories: Optional[str] = Query(
        None, description="Comma-separated metric categories"
    ),
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Get comprehensive performance analytics"""
    try:
        service = DeveloperPanelService(db)

        categories_list = metric_categories.split(",") if metric_categories else None

        result = await service.get_performance_analytics(
            period_hours=period_hours, metric_categories=categories_list
        )

        return result

    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance analytics: {str(e)}",
        )


@router.get("/developer/user-activity-analytics", response_model=Dict[str, Any])
async def get_user_activity_analytics(
    period_days: int = Query(7, description="Period in days"),
    brokerage_id: Optional[int] = Query(None, description="Filter by brokerage ID"),
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Get user activity analytics"""
    try:
        service = DeveloperPanelService(db)

        result = await service.get_user_activity_analytics(
            period_days=period_days, brokerage_id=brokerage_id
        )

        return result

    except Exception as e:
        logger.error(f"Error getting user activity analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user activity analytics: {str(e)}",
        )


@router.get("/developer/multi-brokerage-analytics", response_model=Dict[str, Any])
async def get_multi_brokerage_analytics(
    period_days: int = Query(30, description="Period in days"),
    analytics_types: Optional[str] = Query(
        None, description="Comma-separated analytics types"
    ),
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Get system-wide analytics across all brokerages"""
    try:
        service = DeveloperPanelService(db)

        types_list = analytics_types.split(",") if analytics_types else None

        result = await service.get_multi_brokerage_analytics(
            period_days=period_days, analytics_types=types_list
        )

        return result

    except Exception as e:
        logger.error(f"Error getting multi-brokerage analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get multi-brokerage analytics: {str(e)}",
        )


# =====================================================
# SYSTEM ALERTS MANAGEMENT
# =====================================================


@router.get("/developer/system-alerts", response_model=Dict[str, Any])
async def get_system_alerts(
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    is_resolved: Optional[bool] = Query(
        None, description="Filter by resolution status"
    ),
    limit: int = Query(50, description="Number of alerts to return"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Get system alerts with filtering"""
    try:
        service = DeveloperPanelService(db)

        result = await service.get_system_alerts(
            alert_type=alert_type,
            severity=severity,
            is_resolved=is_resolved,
            limit=limit,
            offset=offset,
        )

        return result

    except Exception as e:
        logger.error(f"Error getting system alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system alerts: {str(e)}",
        )


@router.post("/developer/system-alerts", response_model=Dict[str, Any])
async def create_system_alert(
    alert_data: SystemAlertCreate,
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Create a new system alert"""
    try:
        service = DeveloperPanelService(db)

        result = await service.create_system_alert(
            alert_type=alert_data.alert_type,
            alert_category=alert_data.alert_category,
            alert_title=alert_data.alert_title,
            alert_message=alert_data.alert_message,
            severity=alert_data.severity,
            affected_components=alert_data.affected_components,
            alert_data=alert_data.alert_data,
        )

        return result

    except Exception as e:
        logger.error(f"Error creating system alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create system alert: {str(e)}",
        )


@router.post(
    "/developer/system-alerts/{alert_id}/resolve", response_model=Dict[str, Any]
)
async def resolve_system_alert(
    alert_id: int,
    resolution_data: SystemAlertResolve,
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Resolve a system alert"""
    try:
        service = DeveloperPanelService(db)

        result = await service.resolve_system_alert(
            alert_id=alert_id,
            resolved_by=current_user.id,
            resolution_notes=resolution_data.resolution_notes,
        )

        return result

    except Exception as e:
        logger.error(f"Error resolving system alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve system alert: {str(e)}",
        )


# =====================================================
# DEVELOPER SETTINGS MANAGEMENT
# =====================================================


@router.get("/developer/settings", response_model=Dict[str, Any])
async def get_developer_settings(
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Get developer panel settings"""
    try:
        service = DeveloperPanelService(db)

        result = await service.get_developer_settings(current_user.id)

        return result

    except Exception as e:
        logger.error(f"Error getting developer settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get developer settings: {str(e)}",
        )


@router.put("/developer/settings", response_model=Dict[str, Any])
async def update_developer_settings(
    settings_data: DeveloperSettingsUpdate,
    current_user: User = Depends(require_roles(["admin", "developer"])),
    db: Session = Depends(get_db),
):
    """Update developer panel settings"""
    try:
        service = DeveloperPanelService(db)

        result = await service.update_developer_settings(
            user_id=current_user.id, settings=settings_data.settings
        )

        return result

    except Exception as e:
        logger.error(f"Error updating developer settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update developer settings: {str(e)}",
        )


# =====================================================
# UTILITY ENDPOINTS
# =====================================================


@router.get("/dubai/areas", response_model=List[str])
async def get_dubai_areas():
    """Get list of Dubai areas"""
    return [
        "Dubai Marina",
        "Palm Jumeirah",
        "Downtown Dubai",
        "Business Bay",
        "Jumeirah Beach Residence",
        "Dubai Hills",
        "Arabian Ranches",
        "Dubai Sports City",
        "International City",
        "Dubai Silicon Oasis",
        "Dubai Investment Park",
        "Dubai Production City",
        "Dubai Studio City",
        "Dubai Media City",
        "Dubai Internet City",
        "Dubai Knowledge Park",
        "Dubai Healthcare City",
        "Dubai International Financial Centre",
        "Dubai World Trade Centre",
        "Burj Khalifa Area",
    ]


@router.get("/dubai/property-types", response_model=List[str])
async def get_property_types():
    """Get list of property types"""
    return [
        "apartment",
        "villa",
        "townhouse",
        "penthouse",
        "office",
        "retail",
        "warehouse",
        "land",
        "hotel",
        "serviced_apartment",
    ]


@router.get("/developer/health")
async def health_check():
    """Health check endpoint for Phase 3 services"""
    return {
        "status": "healthy",
        "service": "Phase 3 Advanced Features",
        "timestamp": datetime.utcnow(),
    }
