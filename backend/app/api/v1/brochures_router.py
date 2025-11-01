"""
Brochures API - DB-backed implementation

Endpoints:
- POST   /api/v1/brochures             -> create new draft
- GET    /api/v1/brochures/{id}        -> fetch one draft
- PATCH  /api/v1/brochures/{id}        -> deep-merge partial update into data/status
- POST   /api/v1/brochures/{id}/render -> generate PDF, update status+download_url
- GET    /api/v1/brochures/{id}/download -> return download_url
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import BrochureDraft as BrochureDraftModel, Property, PropertyPhoto
from app.schemas.brochure import (
    BrochureDraftCreate,
    BrochureDraftUpdate,
    BrochureDraftOut,
)
from app.services.render_service import render_brochure_to_pdf
from app.domain.ai.file_storage_service import file_storage


router = APIRouter(prefix="/api/v1/brochures", tags=["Brochures"])


def _deep_merge(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in patch.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _enrich_with_property_data(db: Session, property_id: str) -> Dict[str, Any] | None:
    """
    [Brochure] Enrich brochure data with property information.

    Fetches property data and converts it into the listingData payload expected by
    the brochure renderer so we stay aligned with the primary property record.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Fetch property with photos
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            logger.warning("[Brochure] Property %s not found for enrichment", property_id)
            return None
        
        # Build listingData from property
        listing_data = {
            "title": property_obj.title,
            "building": property_obj.building, 
            "community": property_obj.community,
            "beds": property_obj.beds,
            "baths": property_obj.baths,
            "area_sqft": property_obj.area_sqft,
            "price_aed": property_obj.price_aed,
            "description": property_obj.description,
            "photos": [
                {"url": photo.url, "sort": photo.sort_order} 
                for photo in sorted(property_obj.photos, key=lambda p: p.sort_order)
            ]
        }
        
        # Remove None values
        listing_data = {k: v for k, v in listing_data.items() if v is not None}
        
        logger.info("[Brochure] Enriched brochure with property %s (%s)", property_id, listing_data.get("title"))
        return listing_data
        
    except Exception as exc:
        logger.error("[Brochure] Failed to enrich brochure with property %s: %s", property_id, exc)
        return None


def _default_data(template_key: str) -> Dict[str, Any]:
    return {
        "templateKey": template_key,
        "propertyId": None,
        "hero": {"title": "", "subtitle": "", "image": None},
        "about": {"heading": "", "body": "", "gallery": []},
        "whyInvest": {"bullets": [], "sideQuote": "", "interiorImage": None},
        "paymentPlan": {"items": [], "blurb": ""},
        "amenities": {"sections": [], "features": [], "bgImage": None},
        "collections": {"groups": []},
        "agent": {"name": "", "about": "", "phone": "", "website": "", "company": "", "photo": None},
        "branding": {"primary": "", "secondary": "", "fontHead": "", "fontBody": "", "logo": None},
        "meta": {"lastEdited": "", "status": "draft"},
    }


@router.post("", response_model=BrochureDraftOut)
def create_brochure(payload: BrochureDraftCreate, db: Session = Depends(get_db)) -> BrochureDraftOut:
    template_key = payload.templateKey or "clean-minimal"
    data = _deep_merge(_default_data(template_key), payload.data or {})

    if payload.property_id:
        data["propertyId"] = payload.property_id

    # [Brochure] Property enrichment - inject property data if property_id provided
    if payload.property_id:
        property_data = _enrich_with_property_data(db, payload.property_id)
        if property_data:
            data = _deep_merge(data, {"listingData": property_data})

    row = BrochureDraftModel(
        data=data,
        status="draft",
        property_id=payload.property_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return BrochureDraftOut(
        id=row.id,
        data=row.data,
        status=row.status,
        download_url=row.download_url,
        created_at=row.created_at.isoformat() if row.created_at else "",
        updated_at=row.updated_at.isoformat() if row.updated_at else "",
    )

@router.get("/{draft_id}", response_model=BrochureDraftOut)
def get_brochure(draft_id: str, db: Session = Depends(get_db)) -> BrochureDraftOut:
    row = db.get(BrochureDraftModel, draft_id)
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")
    return BrochureDraftOut(
        id=row.id,
        data=row.data,
        status=row.status,
        download_url=row.download_url,
        created_at=row.created_at.isoformat() if row.created_at else "",
        updated_at=row.updated_at.isoformat() if row.updated_at else "",
    )


@router.patch("/{draft_id}", response_model=BrochureDraftOut)
def update_brochure(draft_id: str, patch: BrochureDraftUpdate, db: Session = Depends(get_db)) -> BrochureDraftOut:
    row = db.get(BrochureDraftModel, draft_id)
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")

    payload_data = patch.data or {}

    if patch.data is not None:
        existing_data = row.data or {}
        row.data = _deep_merge(existing_data, patch.data)

    if patch.status is not None:
        row.status = patch.status
    if patch.download_url is not None:
        row.download_url = patch.download_url
    if patch.error is not None:
        meta = (row.data or {}).get("meta", {})
        meta["error"] = patch.error
        if row.data is None:
            row.data = {}
        row.data["meta"] = meta

    property_id_from_data = None
    if patch.data is not None and isinstance(patch.data, dict) and "propertyId" in patch.data:
        property_id_from_data = patch.data.get("propertyId")

    if patch.property_id is not None:
        row.property_id = patch.property_id or None
    elif property_id_from_data is not None:
        row.property_id = property_id_from_data or None

    if row.property_id:
        if row.data is None:
            row.data = {}
        row.data["propertyId"] = row.property_id
        incoming_listing = payload_data.get("listingData") if isinstance(payload_data, dict) else None
        if not incoming_listing:
            enriched_listing = _enrich_with_property_data(db, row.property_id)
            if enriched_listing:
                row.data = _deep_merge(row.data, {"listingData": enriched_listing})
    elif row.data and "propertyId" in row.data:
        row.data["propertyId"] = None

    db.add(row)
    db.commit()
    db.refresh(row)
    return BrochureDraftOut(
        id=row.id,
        data=row.data,
        status=row.status,
        download_url=row.download_url,
        created_at=row.created_at.isoformat() if row.created_at else "",
        updated_at=row.updated_at.isoformat() if row.updated_at else "",
    )
@router.post("/{draft_id}/render")
async def render_brochure(draft_id: str, db: Session = Depends(get_db)) -> Dict[str, str]:
    row = db.get(BrochureDraftModel, draft_id)
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")

    row.status = "rendering"
    db.add(row)
    db.commit()

    try:
        pdf_bytes = await render_brochure_to_pdf(row.data or {})
        filename = f"brochure-{draft_id}.pdf"
        saved = await file_storage.save_deliverable(
            pdf_bytes, draft_id, file_type="pdf", filename=filename, mime_type="application/pdf"
        )
        row.download_url = saved.get("url")
        row.status = "ready"
        meta = (row.data or {}).get("meta", {})
        meta.pop("error", None)
        row.data["meta"] = meta
        db.add(row)
        db.commit()
        return {"download_url": row.download_url or ""}
    except Exception as e:
        meta = (row.data or {}).get("meta", {})
        meta["error"] = str(e)
        row.data["meta"] = meta
        row.status = "error"
        db.add(row)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Render failed: {e}")


@router.get("/{draft_id}/download")
def get_download(draft_id: str, db: Session = Depends(get_db)) -> Dict[str, str]:
    row = db.get(BrochureDraftModel, draft_id)
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")
    if not row.download_url:
        raise HTTPException(status_code=404, detail="Download not available")
    return {"download_url": row.download_url}
@router.get("", response_model=list[BrochureDraftOut])
def list_brochures(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[BrochureDraftOut]:
    rows = (
        db.query(BrochureDraftModel)
        .order_by(BrochureDraftModel.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    out: list[BrochureDraftOut] = []
    for row in rows:
        out.append(
            BrochureDraftOut(
                id=row.id,
                data=row.data,
                status=row.status,
                download_url=row.download_url,
                created_at=row.created_at.isoformat() if row.created_at else "",
                updated_at=row.updated_at.isoformat() if row.updated_at else "",
            )
        )
    return out
