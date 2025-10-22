"""
🏠 [Property] Property Management API

Provides CRUD operations and search for real estate properties.
Designed for property-brochure integration with idempotent operations.
"""

import logging
from typing import List, Optional, Dict, Any
from urllib.parse import unquote
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.database import get_db
from app.core.models import Property, PropertyPhoto, PropertyType, PropertyStatus
from app.services.storage_service import get_storage_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/properties", tags=["Properties"])


# ========================================
# Pydantic Models
# ========================================

class PropertyPhotoIn(BaseModel):
    """Property photo input"""
    url: str
    sort_order: Optional[int] = 0


class PropertyCreate(BaseModel):
    """Property creation model"""
    title: str
    building: str
    community: Optional[str] = None
    unit: Optional[str] = None
    property_type: Optional[str] = "apartment"
    beds: Optional[int] = None
    baths: Optional[float] = None
    area_sqft: Optional[float] = None
    price_aed: Optional[int] = None
    description: Optional[str] = None
    photos: List[PropertyPhotoIn] = []


class PropertyUpdate(PropertyCreate):
    """Property update model (same as create for simplicity)"""
    pass


class PropertyPhotoOut(BaseModel):
    """Property photo output"""
    id: str
    url: str
    sort_order: int


class PropertyOut(BaseModel):
    """Property output model"""
    id: str
    created_at: str
    updated_at: str
    title: str
    building: str
    community: Optional[str]
    unit: Optional[str]
    property_type: str
    beds: Optional[int]
    baths: Optional[float]
    area_sqft: Optional[float]
    price_aed: Optional[int]
    description: Optional[str]
    status: str
    photos: List[PropertyPhotoOut] = []

    class Config:
        from_attributes = True


# ========================================
# API Endpoints
# ========================================

@router.post("", response_model=PropertyOut)
async def create_property(
    payload: PropertyCreate,
    db: Session = Depends(get_db)
) -> PropertyOut:
    """
    Create new property (idempotent by building, unit, beds, baths, area_sqft, price_aed)
    
    If a property with the same key fields exists, update it instead of creating a duplicate.
    """
    logger.info(f"🏠 [Property] Creating property: {payload.title}")
    
    # Check for existing property (idempotent logic)
    existing = db.query(Property).filter(
        and_(
            Property.building == payload.building,
            Property.unit == payload.unit if payload.unit else Property.unit.is_(None),
            Property.beds == payload.beds if payload.beds else Property.beds.is_(None),
            Property.baths == payload.baths if payload.baths else Property.baths.is_(None),
            Property.area_sqft == payload.area_sqft if payload.area_sqft else Property.area_sqft.is_(None),
            Property.price_aed == payload.price_aed if payload.price_aed else Property.price_aed.is_(None)
        )
    ).first()
    
    if existing:
        logger.info(f"🔄 [Property] Updating existing property {existing.id}")
        # Update existing property
        for field, value in payload.dict(exclude={'photos'}).items():
            if value is not None:
                setattr(existing, field, value)
        
        # Handle property type enum
        if payload.property_type:
            existing.property_type = PropertyType(payload.property_type)
        
        property_obj = existing
    else:
        # Create new property
        property_data = payload.dict(exclude={'photos'})
        property_data['property_type'] = PropertyType(payload.property_type or 'apartment')
        property_obj = Property(**property_data)
        db.add(property_obj)
    
    # Handle photos
    if payload.photos:
        # Remove existing photos if updating
        if existing:
            db.query(PropertyPhoto).filter(PropertyPhoto.property_id == property_obj.id).delete()
        
        for photo_data in payload.photos:
            photo = PropertyPhoto(
                property_id=property_obj.id,
                url=photo_data.url,
                sort_order=photo_data.sort_order
            )
            db.add(photo)
    
    db.commit()
    db.refresh(property_obj)
    
    return _property_to_out(property_obj)


@router.get("", response_model=List[PropertyOut])
async def search_properties(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search query"),
    building: Optional[str] = Query(None, description="Filter by building"),
    unit: Optional[str] = Query(None, description="Filter by unit"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> List[PropertyOut]:
    """Search properties with filters"""
    logger.info(f"🔍 [Property] Searching properties: q={q}, building={building}, unit={unit}")
    
    query = db.query(Property)
    
    # Apply filters
    if q:
        # Search in title, building, community, description
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Property.title.ilike(search_term),
                Property.building.ilike(search_term),
                Property.community.ilike(search_term),
                Property.description.ilike(search_term)
            )
        )
    
    if building:
        query = query.filter(Property.building.ilike(f"%{building}%"))
    
    if unit:
        query = query.filter(Property.unit.ilike(f"%{unit}%"))
    
    if status:
        query = query.filter(Property.status == PropertyStatus(status))
    
    # Order by created_at desc and apply pagination
    properties = (
        query.order_by(Property.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return [_property_to_out(prop) for prop in properties]


@router.get("/{property_id}", response_model=PropertyOut)
async def get_property(
    property_id: str,
    db: Session = Depends(get_db)
) -> PropertyOut:
    """Get property by ID"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return _property_to_out(property_obj)


@router.patch("/{property_id}", response_model=PropertyOut)
async def update_property(
    property_id: str,
    payload: PropertyUpdate,
    db: Session = Depends(get_db)
) -> PropertyOut:
    """Update property by ID"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    logger.info(f"🔄 [Property] Updating property {property_id}")
    
    # Update fields
    for field, value in payload.dict(exclude={'photos'}).items():
        if value is not None:
            if field == 'property_type':
                setattr(property_obj, field, PropertyType(value))
            else:
                setattr(property_obj, field, value)
    
    # Handle photos
    if payload.photos:
        # Remove existing photos
        db.query(PropertyPhoto).filter(PropertyPhoto.property_id == property_id).delete()
        
        # Add new photos
        for photo_data in payload.photos:
            photo = PropertyPhoto(
                property_id=property_id,
                url=photo_data.url,
                sort_order=photo_data.sort_order
            )
            db.add(photo)
    
    db.commit()
    db.refresh(property_obj)
    
    return _property_to_out(property_obj)


@router.post("/{property_id}/photos")
async def append_photos(
    property_id: str,
    photos: List[PropertyPhotoIn],
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Append photos to property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    logger.info(f"📸 [Property] Adding {len(photos)} photos to property {property_id}")
    
    # Get current max sort_order
    max_sort = db.query(func.max(PropertyPhoto.sort_order)).filter(
        PropertyPhoto.property_id == property_id
    ).scalar() or 0
    
    # Add new photos
    for i, photo_data in enumerate(photos):
        photo = PropertyPhoto(
            property_id=property_id,
            url=photo_data.url,
            sort_order=max_sort + i + 1
        )
        db.add(photo)
    
    db.commit()
    
    return {"message": f"Added {len(photos)} photos"}


@router.get("/_sample")
async def get_sample_properties(db: Session = Depends(get_db)) -> List[PropertyOut]:
    """
    Get sample properties for development (DEV only)
    """
    # Only allow in development
    import os
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=404, detail="Not available in production")
    
    logger.info("🧪 [Property] Creating sample properties for development")
    
    # Check if sample properties already exist
    existing = db.query(Property).filter(Property.building.in_(["Orla Residences", "Six Senses"])).all()
    if existing:
        return [_property_to_out(prop) for prop in existing]
    
    # Create sample properties
    samples = [
        {
            "title": "2BR at Orla Residences",
            "building": "Orla Residences", 
            "community": "Palm Jumeirah",
            "beds": 2,
            "baths": 2.0,
            "area_sqft": 1650.0,
            "price_aed": 7200000,
            "description": "Stunning 2-bedroom apartment with panoramic sea views",
            "property_type": PropertyType.apartment,
            "photos": []
        },
        {
            "title": "3BR Penthouse at Six Senses",
            "building": "Six Senses",
            "community": "The Palm",
            "beds": 3,
            "baths": 3.5,
            "area_sqft": 2400.0, 
            "price_aed": 15000000,
            "description": "Luxury penthouse with private terrace and beach access",
            "property_type": PropertyType.apartment,
            "photos": []
        }
    ]
    
    created_properties = []
    for sample_data in samples:
        property_obj = Property(**sample_data)
        db.add(property_obj)
        created_properties.append(property_obj)
    
    db.commit()
    
    for prop in created_properties:
        db.refresh(prop)
    
    return [_property_to_out(prop) for prop in created_properties]


# ========================================
# Helper Functions
# ========================================

def _property_to_out(property_obj: Property) -> PropertyOut:
    """Convert Property model to PropertyOut"""
    photos_out = [
        PropertyPhotoOut(
            id=photo.id,
            url=photo.url,
            sort_order=photo.sort_order
        )
        for photo in sorted(property_obj.photos, key=lambda p: p.sort_order)
    ]
    
    return PropertyOut(
        id=property_obj.id,
        created_at=property_obj.created_at.isoformat() if property_obj.created_at else "",
        updated_at=property_obj.updated_at.isoformat() if property_obj.updated_at else "",
        title=property_obj.title,
        building=property_obj.building,
        community=property_obj.community,
        unit=property_obj.unit,
        property_type=property_obj.property_type.value,
        beds=property_obj.beds,
        baths=property_obj.baths,
        area_sqft=property_obj.area_sqft,
        price_aed=property_obj.price_aed,
        description=property_obj.description,
        status=property_obj.status.value,
        photos=photos_out
    )