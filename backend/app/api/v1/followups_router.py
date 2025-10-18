from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.listings.enhanced_real_estate_models import (
    EnhancedClient,
    FollowUp as FollowUpModel,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Followups"])


class FollowUpItem(BaseModel):
    id: str
    contactId: str
    channel: str
    dueAt: str
    status: str
    notes: Optional[str] = None
    createdAt: str


class FollowUpCreate(BaseModel):
    contactId: str
    channel: str = Field(..., pattern="^(call|email|whatsapp|meeting)$")
    dueAt: str
    notes: Optional[str] = None
    status: Optional[str] = "scheduled"


def _ensure_db(db: Optional[Session]) -> Session:
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")
    return db


def _parse_contact_id(contact_id: str) -> int:
    try:
        return int(contact_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid contact id") from exc


def _parse_iso(dt: str) -> datetime:
    value = dt.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid dueAt format") from exc


def _to_iso(dt: datetime) -> str:
    if dt.tzinfo:
        return dt.isoformat()
    return dt.isoformat() + "Z"


@router.get("/followups", response_model=List[FollowUpItem])
async def list_followups(
    contactId: str = Query(...),
    db: Optional[Session] = Depends(get_db),
) -> List[FollowUpItem]:
    session = _ensure_db(db)
    cid = _parse_contact_id(contactId)

    try:
        exists = (
            session.query(EnhancedClient.id)
            .filter(EnhancedClient.id == cid)
            .first()
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Contact not found")

        rows = (
            session.query(FollowUpModel)
            .filter(FollowUpModel.contact_id == cid)
            .order_by(FollowUpModel.due_at.asc())
            .all()
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Failed to list followups for contact %s", contactId)
        raise HTTPException(status_code=500, detail="Failed to list followups") from exc

    items: List[FollowUpItem] = []
    for row in rows:
        status = getattr(row, "status", None) or "scheduled"
        items.append(
            FollowUpItem(
                id=str(row.id),
                contactId=str(row.contact_id),
                channel=row.channel,
                dueAt=_to_iso(row.due_at),
                status=status,
                notes=row.notes,
                createdAt=_to_iso(row.created_at),
            )
        )
    return items


@router.post("/followups", response_model=FollowUpItem, status_code=201)
async def create_followup(
    body: FollowUpCreate,
    db: Optional[Session] = Depends(get_db),
) -> FollowUpItem:
    session = _ensure_db(db)
    cid = _parse_contact_id(body.contactId)

    try:
        contact = (
            session.query(EnhancedClient)
            .filter(EnhancedClient.id == cid)
            .with_for_update()
            .first()
        )
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
    except SQLAlchemyError as exc:
        logger.exception("Failed to validate contact %s", body.contactId)
        raise HTTPException(status_code=500, detail="Failed to create followup") from exc

    due_at = _parse_iso(body.dueAt)
    status = body.status or "scheduled"
    followup = FollowUpModel(
        contact_id=cid,
        channel=body.channel,
        due_at=due_at,
        notes=body.notes,
        status=status,
    )
    try:
        session.add(followup)
        session.flush()
        event_time = followup.created_at or due_at
        timestamps = [ts for ts in (contact.last_activity_at, event_time) if ts]
        contact.last_activity_at = max(timestamps) if timestamps else event_time
        session.commit()
        session.refresh(followup)
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Failed to create followup for contact %s", body.contactId)
        raise HTTPException(status_code=500, detail="Failed to create followup") from exc

    return FollowUpItem(
        id=str(followup.id),
        contactId=str(followup.contact_id),
        channel=followup.channel,
        dueAt=_to_iso(followup.due_at),
        status=getattr(followup, "status", None) or "scheduled",
        notes=followup.notes,
        createdAt=_to_iso(followup.created_at),
    )
