"""
Command Center Router
====================

Provides aggregated metrics and dashboard data for the PropertyPro AI command center.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.middleware import get_current_user
from app.core.models import User
from app.domain.listings.enhanced_real_estate_models import (
    EnhancedProperty,
    EnhancedClient,
    Transaction,
)

router = APIRouter(prefix="/command-center", tags=["Command Center"])
logger = logging.getLogger(__name__)


@router.get("", summary="Get command center dashboard data")
async def get_command_center_data(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard data for the command center.

    Returns:
        Dictionary containing metrics, recent activities, and summary data
    """
    try:
        # Basic counts
        total_properties = (
            db.query(EnhancedProperty)
            .filter(EnhancedProperty.is_deleted.is_(False))
            .count()
        )

        available_properties = (
            db.query(EnhancedProperty)
            .filter(
                EnhancedProperty.is_deleted.is_(False),
                EnhancedProperty.listing_status == "available",
            )
            .count()
        )

        pending_properties = (
            db.query(EnhancedProperty)
            .filter(
                EnhancedProperty.is_deleted.is_(False),
                EnhancedProperty.listing_status == "pending",
            )
            .count()
        )

        total_clients = db.query(EnhancedClient).count()
        active_clients = (
            db.query(EnhancedClient)
            .filter(EnhancedClient.client_status == "active")
            .count()
        )

        # Recent properties (last 5)
        recent_properties = (
            db.query(EnhancedProperty)
            .filter(EnhancedProperty.is_deleted.is_(False))
            .order_by(desc(EnhancedProperty.id))
            .limit(5)
            .all()
        )

        # Recent clients (last 5)
        recent_clients = (
            db.query(EnhancedClient).order_by(desc(EnhancedClient.id)).limit(5).all()
        )

        # Property type distribution
        property_types = (
            db.query(
                EnhancedProperty.property_type,
                func.count(EnhancedProperty.id).label("count"),
            )
            .filter(EnhancedProperty.is_deleted.is_(False))
            .group_by(EnhancedProperty.property_type)
            .all()
        )

        # Client type distribution
        client_types = (
            db.query(
                EnhancedClient.client_type, func.count(EnhancedClient.id).label("count")
            )
            .group_by(EnhancedClient.client_type)
            .all()
        )

        # Average property prices by type
        avg_prices = (
            db.query(
                EnhancedProperty.property_type,
                func.avg(EnhancedProperty.price_aed).label("avg_price"),
            )
            .filter(
                EnhancedProperty.is_deleted.is_(False),
                EnhancedProperty.price_aed.isnot(None),
            )
            .group_by(EnhancedProperty.property_type)
            .all()
        )

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "user": {
                "id": current_user.id,
                "name": f"{current_user.first_name} {current_user.last_name}",
                "role": current_user.role,
            },
            "metrics": {
                "properties": {
                    "total": total_properties,
                    "available": available_properties,
                    "pending": pending_properties,
                    "sold": total_properties
                    - available_properties
                    - pending_properties,
                },
                "clients": {
                    "total": total_clients,
                    "active": active_clients,
                    "inactive": total_clients - active_clients,
                },
            },
            "distributions": {
                "property_types": [
                    {"type": pt.property_type or "Unknown", "count": pt.count}
                    for pt in property_types
                ],
                "client_types": [
                    {"type": ct.client_type or "Unknown", "count": ct.count}
                    for ct in client_types
                ],
            },
            "market_data": {
                "average_prices": [
                    {
                        "property_type": ap.property_type or "Unknown",
                        "average_price": float(ap.avg_price) if ap.avg_price else 0,
                    }
                    for ap in avg_prices
                ]
            },
            "recent": {
                "properties": [
                    {
                        "id": prop.id,
                        "title": prop.title,
                        "location": prop.location,
                        "price_aed": float(prop.price_aed) if prop.price_aed else 0,
                        "property_type": prop.property_type,
                        "bedrooms": prop.bedrooms,
                        "bathrooms": prop.bathrooms,
                        "status": prop.listing_status,
                        "created_at": prop.created_at.isoformat()
                        if prop.created_at
                        else None,
                    }
                    for prop in recent_properties
                ],
                "clients": [
                    {
                        "id": client.id,
                        "name": client.name,
                        "email": client.email,
                        "phone": client.phone,
                        "client_type": client.client_type,
                        "status": client.client_status,
                        "budget_range": {
                            "min": float(client.budget_min) if client.budget_min else 0,
                            "max": float(client.budget_max) if client.budget_max else 0,
                        },
                        "created_at": client.created_at.isoformat()
                        if client.created_at
                        else None,
                    }
                    for client in recent_clients
                ],
            },
        }

    except Exception as e:
        logger.error(f"Error fetching command center data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch command center data: {str(e)}"
        )


@router.get("/quick-stats", summary="Get quick statistics")
async def get_quick_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get quick statistics for the dashboard.

    Returns:
        Dictionary with key metrics
    """
    try:
        stats = {
            "properties_count": db.query(EnhancedProperty)
            .filter(EnhancedProperty.is_deleted.is_(False))
            .count(),
            "clients_count": db.query(EnhancedClient).count(),
            "available_properties": db.query(EnhancedProperty)
            .filter(
                EnhancedProperty.is_deleted.is_(False),
                EnhancedProperty.listing_status == "available",
            )
            .count(),
            "active_clients": db.query(EnhancedClient)
            .filter(EnhancedClient.client_status == "active")
            .count(),
        }

        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching quick stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch quick stats: {str(e)}"
        )
