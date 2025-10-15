"""
Data Router - FastAPI Router for Core Real Estate Data Endpoints

This router handles all core real estate data endpoints migrated from main.py
to maintain frontend compatibility while following the secure architecture
patterns of main_secure.py.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from datetime import datetime

# Import dependencies
from database_manager import get_db_connection

# Initialize router
router = APIRouter(prefix="/market", tags=["Market Data"])

# Root level data endpoints
root_router = APIRouter(tags=["Data"])

# Pydantic Models
class MarketOverview(BaseModel):
    """Market overview data model"""

    total_properties: int
    average_price: float
    price_change_24h: float
    volume_change_24h: float
    hot_areas: List[Dict[str, Any]]
    property_types: Dict[str, Dict[str, Any]]
    market_trends: Dict[str, Any]


class MarketTrends(BaseModel):
    """Market trends data model"""

    overall_trend: str
    price_change_percentage: float
    volume_change_percentage: float
    average_days_on_market: int
    top_performing_areas: List[Dict[str, Any]]
    property_type_performance: Dict[str, Dict[str, Any]]
    price_ranges: Dict[str, Dict[str, Any]]
    forecast: Dict[str, Any]


class Property(BaseModel):
    """Property data model"""

    address: Optional[str] = None
    price: Optional[float] = None
    bedrooms: Optional[str] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[str] = None
    property_type: Optional[str] = None
    description: Optional[str] = None


class Client(BaseModel):
    """Client data model"""

    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    requirements: Optional[str] = None


# Router Endpoints


@router.get("/overview")
async def get_market_overview():
    """Get market overview data"""
    try:
        # Mock market overview data
        market_data = {
            "total_properties": 1250,
            "average_price": 2850000,
            "price_change_24h": 2.5,
            "volume_change_24h": 8.3,
            "hot_areas": [
                {"name": "Dubai Marina", "price_change": 5.2, "volume": 45},
                {"name": "Palm Jumeirah", "price_change": 3.8, "volume": 32},
                {"name": "Downtown Dubai", "price_change": 4.1, "volume": 38},
                {"name": "Business Bay", "price_change": 2.9, "volume": 28},
            ],
            "property_types": {
                "apartments": {"count": 850, "avg_price": 2200000},
                "villas": {"count": 320, "avg_price": 5800000},
                "townhouses": {"count": 80, "avg_price": 3200000},
            },
            "market_trends": {
                "trend": "bullish",
                "confidence": 85,
                "prediction": "Continued growth expected",
            },
        }

        return market_data
    except Exception as e:
        print(f"Error in get_market_overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_market_trends():
    """
    Get real estate market trends and analysis
    """
    try:
        # Mock market trends data - in production this would come from real market data
        market_trends = {
            "overall_trend": "increasing",
            "price_change_percentage": 5.2,
            "volume_change_percentage": 12.8,
            "average_days_on_market": 45,
            "top_performing_areas": [
                {"area": "Downtown Dubai", "growth": 8.5, "volume": 156},
                {"area": "Palm Jumeirah", "growth": 7.2, "volume": 89},
                {"area": "Dubai Marina", "growth": 6.8, "volume": 234},
            ],
            "property_type_performance": {
                "apartments": {"growth": 6.1, "volume": 456},
                "villas": {"growth": 4.8, "volume": 123},
                "townhouses": {"growth": 5.5, "volume": 67},
            },
            "price_ranges": {
                "under_500k": {"growth": 3.2, "volume": 234},
                "500k_to_1m": {"growth": 5.8, "volume": 345},
                "1m_to_2m": {"growth": 7.1, "volume": 189},
                "over_2m": {"growth": 4.3, "volume": 78},
            },
            "forecast": {
                "next_quarter": "stable_growth",
                "next_year": "moderate_increase",
                "confidence_level": 0.85,
            },
        }

        return market_trends

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch market trends: {str(e)}"
        )


@root_router.get("/properties")
async def get_properties():
    """Get all properties from the database"""
    try:
        with get_db_connection() as conn:
            # First, let's see the actual table structure
            result = conn.execute(text("SELECT * FROM properties LIMIT 1"))
            first_row = result.fetchone()
            if first_row:
                row_data = list(first_row)
                print(f"DEBUG: First row has {len(row_data)} columns: {row_data}")

            # Now get all properties
            result = conn.execute(text("SELECT * FROM properties"))
            properties = []
            for row in result:
                row_data = list(row)

                # Handle different table schemas based on column count
                property_obj = {}

                if len(row_data) == 7:
                    # Original schema: address,price,bedrooms,bathrooms,square_feet,property_type,description
                    property_obj = {
                        "id": row_data[0] if len(row_data) > 0 else None,
                        "title": row_data[0]
                        if len(row_data) > 0
                        else "Untitled Property",
                        "address": row_data[0]
                        if len(row_data) > 0
                        else "Location not specified",
                        "price": float(row_data[1])
                        if len(row_data) > 1 and row_data[1]
                        else 0,
                        "bedrooms": int(row_data[2])
                        if len(row_data) > 2 and row_data[2]
                        else 0,
                        "bathrooms": float(row_data[3])
                        if len(row_data) > 3 and row_data[3]
                        else 0,
                        "square_feet": int(row_data[4])
                        if len(row_data) > 4 and row_data[4]
                        else 0,
                        "property_type": row_data[5]
                        if len(row_data) > 5
                        else "Unknown",
                        "description": row_data[6]
                        if len(row_data) > 6
                        else "No description available",
                    }
                elif len(row_data) >= 23:
                    # New schema from property_listings.csv with 23+ columns
                    # Based on debug output: [id, listing_id, title, property_type, bedrooms, bathrooms, area_sqft, price_aed, price_per_sqft, location, building, developer, agent_id, listing_status, listing_date, last_updated, views_count, furnished, parking_spaces, balcony, gym_access, pool_access, security, description, created_at]
                    property_obj = {
                        "id": row_data[0] if len(row_data) > 0 else None,
                        "listing_id": row_data[1] if len(row_data) > 1 else "",
                        "title": row_data[2]
                        if len(row_data) > 2
                        else "Untitled Property",
                        "property_type": row_data[3]
                        if len(row_data) > 3
                        else "Unknown",
                        "bedrooms": int(row_data[4])
                        if len(row_data) > 4 and row_data[4] is not None
                        else 0,
                        "bathrooms": int(row_data[5])
                        if len(row_data) > 5 and row_data[5] is not None
                        else 0,
                        "area_sqft": int(row_data[6])
                        if len(row_data) > 6 and row_data[6] is not None
                        else 0,
                        "price": float(row_data[7])
                        if len(row_data) > 7 and row_data[7] is not None
                        else 0,
                        "price_per_sqft": float(row_data[8])
                        if len(row_data) > 8 and row_data[8] is not None
                        else 0,
                        "location": row_data[9]
                        if len(row_data) > 9
                        else "Location not specified",
                        "building": row_data[10] if len(row_data) > 10 else "",
                        "developer": row_data[11] if len(row_data) > 11 else "",
                        "agent_id": row_data[12] if len(row_data) > 12 else "",
                        "listing_status": row_data[13]
                        if len(row_data) > 13
                        else "active",
                        "description": row_data[23]
                        if len(row_data) > 23
                        else "No description available",
                    }
                else:
                    # Fallback for any other structure
                    property_obj = {
                        "id": row_data[0] if len(row_data) > 0 else None,
                        "title": row_data[1]
                        if len(row_data) > 1
                        else "Untitled Property",
                        "address": row_data[2]
                        if len(row_data) > 2
                        else "Location not specified",
                        "price": float(row_data[3])
                        if len(row_data) > 3 and row_data[3]
                        else 0,
                        "bedrooms": int(row_data[4])
                        if len(row_data) > 4 and row_data[4]
                        else 0,
                        "bathrooms": float(row_data[5])
                        if len(row_data) > 5 and row_data[5]
                        else 0,
                        "property_type": row_data[6]
                        if len(row_data) > 6
                        else "Unknown",
                        "description": row_data[7]
                        if len(row_data) > 7
                        else "No description available",
                    }

                properties.append(property_obj)
            return {"properties": properties}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@root_router.get("/clients")
async def get_clients():
    """Get all clients from the database"""
    try:
        with get_db_connection() as conn:
            result = conn.execute(text("SELECT * FROM clients"))
            clients = []
            for row in result:
                # Convert row to list and handle any number of columns safely
                row_data = list(row)

                # Create client object with safe column access
                client = {}
                if len(row_data) > 0:
                    client["id"] = row_data[0]
                if len(row_data) > 1:
                    client["name"] = row_data[1]
                if len(row_data) > 2:
                    client["email"] = row_data[2]
                if len(row_data) > 3:
                    client["phone"] = row_data[3]
                if len(row_data) > 4:
                    try:
                        client["budget_min"] = (
                            float(row_data[4]) if row_data[4] else None
                        )
                    except (ValueError, TypeError):
                        client["budget_min"] = None
                if len(row_data) > 5:
                    try:
                        client["budget_max"] = (
                            float(row_data[5]) if row_data[5] else None
                        )
                    except (ValueError, TypeError):
                        client["budget_max"] = None
                if len(row_data) > 6:
                    client["preferred_location"] = row_data[6]
                if len(row_data) > 7:
                    client["requirements"] = row_data[7]

                clients.append(client)
            return {"clients": clients}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
