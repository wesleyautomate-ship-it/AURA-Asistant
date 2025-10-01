import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.middleware import get_current_user, require_agent_or_admin
from app.domain.listings.enhanced_real_estate_models import (
    EnhancedProperty,
    ListingHistory,
    PropertyConfidential,
)

router = APIRouter(
    prefix="/properties",
    tags=["Properties"],
    dependencies=[Depends(get_current_user)]
)

logger = logging.getLogger(__name__)


def _strip_nullable(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip()


def _validate_range(min_value: Optional[float], max_value: Optional[float], field_name: str) -> None:
    if min_value is not None and max_value is not None and min_value > max_value:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} minimum cannot be greater than maximum",
        )

class PropertySearchRequest(BaseModel):
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    bedrooms: Optional[int] = Field(default=None, ge=0)
    bathrooms: Optional[int] = Field(default=None, ge=0)
    property_type: Optional[str] = Field(default=None, min_length=1)
    location: Optional[str] = Field(default=None, min_length=1)
    min_area_sqft: Optional[float] = Field(default=None, ge=0)
    max_area_sqft: Optional[float] = Field(default=None, ge=0)


class PropertyCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)
    location: str = Field(..., min_length=2, max_length=255)
    property_type: str = Field(..., min_length=2, max_length=120)
    bedrooms: int = Field(..., ge=0)
    bathrooms: int = Field(..., ge=0)
    area_sqft: Optional[float] = Field(default=None, gt=0)


class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, min_length=10)
    price: Optional[float] = Field(default=None, gt=0)
    location: Optional[str] = Field(default=None, min_length=2, max_length=255)
    property_type: Optional[str] = Field(default=None, min_length=2, max_length=120)
    bedrooms: Optional[int] = Field(default=None, ge=0)
    bathrooms: Optional[int] = Field(default=None, ge=0)
    area_sqft: Optional[float] = Field(default=None, gt=0)

class PropertyResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    location: str
    property_type: str
    bedrooms: int
    bathrooms: int
    area_sqft: Optional[float] = None


class PropertyDetailsResponse(BaseModel):
    property: PropertyResponse
    similar_properties: List[PropertyResponse]
    market_analysis: Dict[str, Any]
    neighborhood_info: Dict[str, Any]


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class PropertySearchResponse(BaseModel):
    properties: List[PropertyResponse]
    pagination: PaginationMeta


def _property_to_response(prop: EnhancedProperty) -> PropertyResponse:
    price_value = prop.price_aed or prop.price or 0
    return PropertyResponse(
        id=prop.id,
        title=prop.title or "",
        description=prop.description or "",
        price=float(price_value),
        location=prop.location or "",
        property_type=prop.property_type or "Unknown",
        bedrooms=prop.bedrooms or 0,
        bathrooms=prop.bathrooms or 0,
        area_sqft=float(prop.area_sqft) if prop.area_sqft is not None else None,
    )

@router.get("/", response_model=List[PropertyResponse])
async def get_all_properties(db: Session = Depends(get_db)):
    """Get all properties from the database"""
    try:
        query = select(EnhancedProperty).where(EnhancedProperty.is_deleted.is_(False))
        rows = db.execute(query).scalars().all()
        return [_property_to_response(prop) for prop in rows]
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch properties")
        raise HTTPException(status_code=500, detail="Failed to fetch properties") from exc


@router.post("/", response_model=PropertyResponse, dependencies=[Depends(require_agent_or_admin)])
async def create_property(property_data: PropertyCreate, db: Session = Depends(get_db)):
    """Create a new property"""
    try:
        title = property_data.title.strip()
        description = property_data.description.strip()
        location = property_data.location.strip()
        property_type = property_data.property_type.strip()

        prop = EnhancedProperty(
            title=title,
            description=description,
            price_aed=property_data.price,
            price=property_data.price,
            location=location,
            property_type=property_type,
            bedrooms=property_data.bedrooms,
            bathrooms=property_data.bathrooms,
            area_sqft=property_data.area_sqft,
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)

        return _property_to_response(prop)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to create property")
        raise HTTPException(status_code=500, detail="Failed to create property") from exc

@router.get("/search", response_model=PropertySearchResponse)
async def search_properties(
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    bedrooms: Optional[int] = Query(None, description="Number of bedrooms"),
    bathrooms: Optional[int] = Query(None, description="Number of bathrooms"),
    property_type: Optional[str] = Query(None, description="Property type"),
    location: Optional[str] = Query(None, description="Location/area"),
    min_area_sqft: Optional[float] = Query(None, description="Minimum area in sqft"),
    max_area_sqft: Optional[float] = Query(None, description="Maximum area in sqft"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return")
):
    """Advanced property search with multiple filters and pagination"""

    _validate_range(min_price, max_price, "Price")
    _validate_range(min_area_sqft, max_area_sqft, "Area (sqft)")

    try:
        query = select(EnhancedProperty).where(EnhancedProperty.is_deleted.is_(False))

        if min_price is not None:
            query = query.where((EnhancedProperty.price_aed >= min_price) | (EnhancedProperty.price >= min_price))
        if max_price is not None:
            query = query.where((EnhancedProperty.price_aed <= max_price) | (EnhancedProperty.price <= max_price))
        if bedrooms is not None:
            query = query.where(EnhancedProperty.bedrooms == bedrooms)
        if bathrooms is not None:
            query = query.where(EnhancedProperty.bathrooms == bathrooms)
        if property_type:
            query = query.where(func.lower(EnhancedProperty.property_type).like(f"%{property_type.lower()}%"))
        if location:
            query = query.where(func.lower(EnhancedProperty.location).like(f"%{location.lower()}%"))
        if min_area_sqft is not None:
            query = query.where(EnhancedProperty.area_sqft >= min_area_sqft)
        if max_area_sqft is not None:
            query = query.where(EnhancedProperty.area_sqft <= max_area_sqft)

        total_count = db.execute(query.with_only_columns(func.count()).order_by(None)).scalar_one()

        offset = (page - 1) * limit
        rows = db.execute(query.order_by(EnhancedProperty.id.desc()).offset(offset).limit(limit)).scalars().all()

        return PropertySearchResponse(
            properties=[_property_to_response(prop) for prop in rows],
            pagination=PaginationMeta(
                page=page,
                limit=limit,
                total=total_count,
                pages=(total_count + limit - 1) // limit,
            ),
        )
    except SQLAlchemyError as exc:
        logger.exception("Failed to search properties")
        raise HTTPException(status_code=500, detail="Failed to search properties") from exc

@router.get("/{property_id}", response_model=PropertyDetailsResponse)
async def get_property_details(property_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific property"""
    try:
        property_obj = db.execute(
            select(EnhancedProperty).options(joinedload(EnhancedProperty.confidential_details)).where(EnhancedProperty.id == property_id)
        ).scalar_one_or_none()

        if not property_obj or property_obj.is_deleted:
            raise HTTPException(status_code=404, detail="Property not found")

        property_data = _property_to_response(property_obj)
        price_value = property_data.price
        price_range = price_value * 0.2 if price_value else 0
        min_price = max(price_value - price_range, 0)
        max_price = price_value + price_range

        similar_properties: List[PropertyResponse] = []
        if property_obj.property_type:
            price_column = func.coalesce(EnhancedProperty.price_aed, EnhancedProperty.price)
            similar_query = (
                select(EnhancedProperty)
                .where(
                    EnhancedProperty.property_type == property_obj.property_type,
                    EnhancedProperty.id != property_id,
                    EnhancedProperty.is_deleted.is_(False),
                    price_column.between(min_price, max_price),
                )
                .limit(5)
            )
            similar_rows = db.execute(similar_query).scalars().all()
            similar_properties = [_property_to_response(row) for row in similar_rows]

        market_analysis = {
            "average_price": price_value * 1.1 if price_value else 0,
            "price_trend": "increasing",
            "days_on_market": 15,
            "price_per_sqft": price_value / (float(property_obj.area_sqft) or 1000) if price_value else 0,
        }

        neighborhood_info = {
            "schools": ["Dubai International School", "American School of Dubai"],
            "amenities": ["Shopping Mall", "Park", "Hospital"],
            "transportation": ["Metro Station", "Bus Stop"],
            "crime_rate": "Low",
        }

        return PropertyDetailsResponse(
            property=property_data,
            similar_properties=similar_properties,
            market_analysis=market_analysis,
            neighborhood_info=neighborhood_info,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch property details", extra={"property_id": property_id})
        raise HTTPException(status_code=500, detail="Failed to fetch property details") from exc

@router.put(
    "/{property_id}",
    response_model=PropertyResponse,
    dependencies=[Depends(require_agent_or_admin)]
)
async def update_property(property_id: int, property_data: PropertyUpdate, db: Session = Depends(get_db)):
    """Update an existing property"""
    try:
        property_obj = db.get(EnhancedProperty, property_id)
        if not property_obj or property_obj.is_deleted:
            raise HTTPException(status_code=404, detail="Property not found")

        updated = False

        if property_data.title is not None:
            property_obj.title = property_data.title.strip()
            updated = True

        if property_data.description is not None:
            property_obj.description = property_data.description.strip()
            updated = True

        if property_data.price is not None:
            property_obj.price_aed = property_data.price
            property_obj.price = property_data.price
            updated = True

        if property_data.location is not None:
            property_obj.location = _strip_nullable(property_data.location) or ""
            updated = True

        if property_data.property_type is not None:
            property_obj.property_type = _strip_nullable(property_data.property_type) or property_obj.property_type
            updated = True

        if property_data.bedrooms is not None:
            property_obj.bedrooms = property_data.bedrooms
            updated = True

        if property_data.bathrooms is not None:
            property_obj.bathrooms = property_data.bathrooms
            updated = True

        if property_data.area_sqft is not None:
            property_obj.area_sqft = property_data.area_sqft
            updated = True

        if not updated:
            raise HTTPException(status_code=400, detail="No fields to update")

        db.add(property_obj)
        db.commit()
        db.refresh(property_obj)

        return _property_to_response(property_obj)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to update property", extra={"property_id": property_id})
        raise HTTPException(status_code=500, detail="Failed to update property") from exc

@router.delete(
    "/{property_id}",
    dependencies=[Depends(require_agent_or_admin)]
)
async def delete_property(property_id: int, db: Session = Depends(get_db)):
    """Delete a property"""
    try:
        property_obj = db.get(EnhancedProperty, property_id)
        if not property_obj or property_obj.is_deleted:
            raise HTTPException(status_code=404, detail="Property not found")

        property_obj.is_deleted = True
        db.add(property_obj)
        db.commit()

        return {"message": "Property deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to delete property", extra={"property_id": property_id})
        raise HTTPException(status_code=500, detail="Failed to delete property") from exc

@router.get("/types/list")
async def get_property_types(db: Session = Depends(get_db)):
    """Get list of available property types"""
    try:
        query = (
            select(func.distinct(EnhancedProperty.property_type))
            .where(EnhancedProperty.property_type.isnot(None))
            .where(EnhancedProperty.property_type != "")
        )
        rows = db.execute(query).scalars().all()
        return {"property_types": rows}
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch property types")
        raise HTTPException(status_code=500, detail="Failed to fetch property types") from exc

@router.get("/locations/list")
async def get_property_locations(db: Session = Depends(get_db)):
    """Get list of available property locations"""
    try:
        query = (
            select(func.distinct(EnhancedProperty.location))
            .where(EnhancedProperty.location.isnot(None))
            .where(EnhancedProperty.location != "")
        )
        rows = db.execute(query).scalars().all()
        return {"locations": rows}
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch property locations")
        raise HTTPException(status_code=500, detail="Failed to fetch property locations") from exc

# --- Phase 1: Granular Data & Security Foundation ---

@router.put("/{property_id}/status", tags=["Properties"])
async def update_property_status(
    property_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update property listing status with access control"""
    # Check for valid status
    valid_statuses = ['draft', 'live', 'pocket', 'sold', 'archived']
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status provided.")

    try:
        property_obj = db.get(EnhancedProperty, property_id)
        if not property_obj or property_obj.is_deleted:
            raise HTTPException(status_code=404, detail="Property not found.")

        if property_obj.agent_id != current_user.id and getattr(current_user, "role", None) != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this property.")

        old_status = property_obj.listing_status
        property_obj.listing_status = new_status

        history_entry = ListingHistory(
            property_id=property_obj.id,
            event_type="status_change",
            old_value=old_status,
            new_value=new_status,
            changed_by_agent_id=current_user.id,
        )
        db.add(history_entry)
        db.add(property_obj)
        db.commit()

        return {"message": f"Property {property_id} status updated to {new_status}."}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to update property status", extra={"property_id": property_id})
        raise HTTPException(status_code=500, detail="Failed to update property status") from exc

@router.get("/{property_id}/confidential", tags=["Properties"])
async def get_confidential_property_data(
    property_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get confidential property data with access control"""
    try:
        property_obj = db.get(EnhancedProperty, property_id)
        if not property_obj or property_obj.is_deleted:
            raise HTTPException(status_code=404, detail="Property not found.")

        user_role = getattr(current_user, "role", None)
        is_authorized = user_role in ["admin", "manager"] or property_obj.agent_id == current_user.id

        if not is_authorized:
            raise HTTPException(status_code=403, detail="You do not have permission to view these details.")

        confidential_data = property_obj.confidential_details
        if not confidential_data:
            raise HTTPException(status_code=404, detail="Confidential data not found for this property.")

        return {
            "unit_number": confidential_data.unit_number,
            "plot_number": confidential_data.plot_number,
            "floor": confidential_data.floor,
            "owner_details": confidential_data.owner_details,
            "created_at": confidential_data.created_at,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch confidential property data", extra={"property_id": property_id})
        raise HTTPException(status_code=500, detail="Failed to fetch confidential property data") from exc
