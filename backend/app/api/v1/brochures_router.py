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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import BrochureDraft as BrochureDraftModel
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
    row = BrochureDraftModel(data=data, status="draft")
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

    if patch.data is not None:
        row.data = _deep_merge(row.data or {}, patch.data)
    if patch.status is not None:
        row.status = patch.status
    if patch.download_url is not None:
        row.download_url = patch.download_url
    if patch.error is not None:
        meta = (row.data or {}).get("meta", {})
        meta["error"] = patch.error
        row.data["meta"] = meta

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

