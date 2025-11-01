from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import AuditLog
from app.domain.listings.enhanced_real_estate_models import (
    ContactActivity,
    ContactNote,
    EnhancedClient,
    FollowUp as FollowUpModel,
)
from app.seed_contacts import DEFAULT_SHEET_URL, import_contacts_from_google_sheet

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Contacts"])


class ContactBrief(BaseModel):
    id: str
    name: str
    temperature: str
    lastActivityAt: Optional[str] = None
    avatarUrl: Optional[str] = None


class ContactDetail(BaseModel):
    id: str
    name: str
    temperature: str
    email: Optional[str] = None
    phone: Optional[str] = None
    lastActivityAt: Optional[str] = None
    notes: str
    intentScore: Optional[int] = None
    signals: Optional[List[str]] = None
    area: Optional[str] = None
    budget: Optional[Dict[str, Optional[float]]] = None
    pipeline: Optional[str] = None
    risks: Optional[List[str]] = None


class ActivityItem(BaseModel):
    id: str
    type: str
    at: str  # ISO time
    text: str


class ContactNotesUpdate(BaseModel):
    notes: str


class ContactNotesResponse(BaseModel):
    id: str
    notes: str
    updatedAt: str


class GoogleSheetImportRequest(BaseModel):
    sheetUrl: Optional[str] = None


class GoogleSheetImportResponse(BaseModel):
    total: int
    created: int
    updated: int
    skipped: int
    errors: List[str]


def _ensure_db(db: Optional[Session]) -> Session:
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")
    return db


def _parse_contact_id(contact_id: str) -> int:
    try:
        return int(contact_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid contact id") from exc


def _to_iso(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    if dt.tzinfo:
        return dt.isoformat()
    return dt.isoformat() + "Z"


@router.post(
    "/contacts/import/google-sheet",
    response_model=GoogleSheetImportResponse,
    tags=["Contacts"],
)
async def import_contacts_from_google_sheet_endpoint(
    payload: GoogleSheetImportRequest = GoogleSheetImportRequest(),
    db: Optional[Session] = Depends(get_db),
) -> GoogleSheetImportResponse:
    session = _ensure_db(db)
    sheet_url = payload.sheetUrl or DEFAULT_SHEET_URL

    try:
        summary = import_contacts_from_google_sheet(session, sheet_url=sheet_url)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to import contacts from Google Sheet")
        raise HTTPException(
            status_code=500, detail="Failed to import contacts"
        ) from exc

    return GoogleSheetImportResponse(
        total=summary.total_rows,
        created=summary.created,
        updated=summary.updated,
        skipped=summary.skipped,
        errors=list(summary.errors),
    )


@router.get("/contacts", response_model=List[ContactBrief])
async def list_contacts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, min_length=1),
    db: Optional[Session] = Depends(get_db),
) -> List[ContactBrief]:
    session = _ensure_db(db)
    try:
        last_activity_subquery = (
            session.query(
                ContactActivity.contact_id.label("contact_id"),
                func.max(ContactActivity.occurred_at).label("last_activity_at"),
            )
            .group_by(ContactActivity.contact_id)
            .subquery()
        )

        query = (
            session.query(
                EnhancedClient,
                last_activity_subquery.c.last_activity_at,
            )
            .outerjoin(
                last_activity_subquery,
                EnhancedClient.id == last_activity_subquery.c.contact_id,
            )
        )

        if search:
            pattern = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(EnhancedClient.name).like(pattern),
                    func.lower(func.coalesce(EnhancedClient.email, "")).like(pattern),
                    func.lower(func.coalesce(EnhancedClient.phone, "")).like(pattern),
                )
            )

        order_expr = func.coalesce(
            last_activity_subquery.c.last_activity_at,
            EnhancedClient.last_activity_at,
            EnhancedClient.updated_at,
            EnhancedClient.created_at,
        )
        rows = (
            query.order_by(order_expr.desc().nullslast(), EnhancedClient.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as exc:
        logger.exception("Failed to list contacts")
        raise HTTPException(status_code=500, detail="Failed to list contacts") from exc

    output: List[ContactBrief] = []
    for client, last_activity_at in rows:
        status = getattr(client, "client_status", None) or ""
        temperature = {
            "active": "Active",
            "new": "New",
            "warm": "Warm",
            "cold": "Cold",
            "dormant": "Dormant",
        }.get(status.lower(), "Warm")
        output.append(
            ContactBrief(
                id=str(client.id),
                name=client.name,
                temperature=temperature,
                lastActivityAt=_to_iso(last_activity_at),
            )
        )
    return output


@router.get("/contacts/{contact_id}", response_model=ContactDetail)
async def get_contact(
    contact_id: str,
    db: Optional[Session] = Depends(get_db),
) -> ContactDetail:
    session = _ensure_db(db)
    cid = _parse_contact_id(contact_id)

    try:
        contact = (
            session.query(EnhancedClient)
            .filter(EnhancedClient.id == cid)
            .first()
        )
    except SQLAlchemyError as exc:
        logger.exception("Failed to load contact %s", contact_id)
        raise HTTPException(status_code=500, detail="Failed to load contact") from exc

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    try:
        latest_note = (
            session.query(ContactNote)
            .filter(ContactNote.contact_id == contact.id)
            .order_by(ContactNote.created_at.desc())
            .first()
        )
        last_activity = (
            session.query(ContactActivity.occurred_at)
            .filter(ContactActivity.contact_id == contact.id)
            .order_by(ContactActivity.occurred_at.desc())
            .first()
        )
    except SQLAlchemyError as exc:
        logger.exception("Failed to load contact detail %s", contact_id)
        raise HTTPException(status_code=500, detail="Failed to load contact") from exc

    status = getattr(contact, "client_status", "") or ""
    temperature = {
        "active": "Active",
        "new": "New",
        "warm": "Warm",
        "cold": "Cold",
        "dormant": "Dormant",
    }.get(status.lower(), "Warm")

    last_activity_at = _to_iso(last_activity[0]) if last_activity else None

    def _as_float(value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    budget_data: Optional[Dict[str, Optional[float]]] = None
    budget_min = getattr(contact, "budget_min", None)
    budget_max = getattr(contact, "budget_max", None)
    if budget_min is not None or budget_max is not None:
        budget_data = {
            "min": _as_float(budget_min),
            "max": _as_float(budget_max),
            "currency": "AED",
        }
        if budget_data["min"] is None and budget_data["max"] is None:
            budget_data = None

    area = getattr(contact, "preferred_location", None)
    pipeline = getattr(contact, "client_status", None)

    signals_list: List[str] = []
    raw_preferences = getattr(contact, "preferences", None)
    if raw_preferences:
        try:
            pref = json.loads(raw_preferences) if isinstance(raw_preferences, str) else raw_preferences
        except (TypeError, ValueError, json.JSONDecodeError):
            pref = None
        if isinstance(pref, list):
            signals_list.extend([str(item) for item in pref if item])
        elif isinstance(pref, dict):
            signals_list.extend([f"{k}: {v}" for k, v in pref.items() if v])
    if area:
        signals_list.insert(0, f"Prefers {area}")
    signals_value: Optional[List[str]] = signals_list or None

    risks_list: List[str] = []
    recent_activity = last_activity[0] if last_activity else getattr(contact, "last_activity_at", None)
    if isinstance(recent_activity, datetime):
        delta = datetime.utcnow() - recent_activity
        if delta.days >= 14:
            risks_list.append(f"Dormant {delta.days} days")
    risks_value: Optional[List[str]] = risks_list or None

    return ContactDetail(
        id=str(contact.id),
        name=contact.name,
        temperature=temperature,
        email=getattr(contact, "email", None),
        phone=getattr(contact, "phone", None),
        lastActivityAt=last_activity_at,
        notes=latest_note.body if latest_note else "",
        intentScore=None,
        signals=signals_value,
        area=area,
        budget=budget_data,
        pipeline=pipeline,
        risks=risks_value,
    )


@router.patch("/contacts/{contact_id}/notes", response_model=ContactNotesResponse)
async def update_contact_notes(
    contact_id: str,
    body: ContactNotesUpdate,
    request: Request,
    db: Optional[Session] = Depends(get_db),
) -> ContactNotesResponse:
    session = _ensure_db(db)
    cid = _parse_contact_id(contact_id)

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
        session.rollback()
        logger.exception("Failed to validate contact %s", contact_id)
        raise HTTPException(status_code=500, detail="Failed to update notes") from exc

    now = datetime.utcnow()
    note = ContactNote(contact_id=cid, body=body.notes, created_at=now)
    session.add(note)
    try:
        session.flush()
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Failed to persist note for contact %s", contact_id)
        raise HTTPException(status_code=500, detail="Failed to update notes") from exc

    # Bump denormalized last_activity
    timestamps = [ts for ts in (contact.last_activity_at, now) if ts]
    contact.last_activity_at = max(timestamps) if timestamps else now

    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    event_payload = json.dumps(
        {"contact_id": cid, "note_id": note.id, "request_id": request_id},
        separators=(",", ":"),
    )
    audit = AuditLog(
        user_id=None,
        event_type="contact.notes.update",
        event_data=event_payload,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        contact_id=cid,
        occurred_at=now,
        success=True,
    )
    session.add(audit)

    try:
        session.commit()
        session.refresh(note)
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Failed to finalize notes update for contact %s", contact_id)
        raise HTTPException(status_code=500, detail="Failed to update notes") from exc

    return ContactNotesResponse(
        id=str(cid),
        notes=note.body,
        updatedAt=_to_iso(note.created_at) or _to_iso(now) or now.isoformat() + "Z",
    )


def _collect_activity_items(
    cid: int,
    session: Session,
    window: int,
) -> List[Tuple[datetime, ActivityItem]]:
    events: List[Tuple[datetime, ActivityItem]] = []

    activities = (
        session.query(ContactActivity)
        .filter(ContactActivity.contact_id == cid)
        .order_by(ContactActivity.occurred_at.desc())
        .limit(window)
        .all()
    )
    for row in activities:
        when = row.occurred_at
        events.append(
            (
                when,
                ActivityItem(
                    id=f"activity-{row.id}",
                    type=row.kind,
                    at=_to_iso(when) or "",
                    text=row.summary,
                ),
            )
        )

    notes = (
        session.query(ContactNote)
        .filter(ContactNote.contact_id == cid)
        .order_by(ContactNote.created_at.desc())
        .limit(window)
        .all()
    )
    for row in notes:
        when = row.created_at
        events.append(
            (
                when,
                ActivityItem(
                    id=f"note-{row.id}",
                    type="note",
                    at=_to_iso(when) or "",
                    text=row.body,
                ),
            )
        )

    followups = (
        session.query(FollowUpModel)
        .filter(FollowUpModel.contact_id == cid)
        .order_by(FollowUpModel.created_at.desc().nullslast())
        .limit(window)
        .all()
    )
    for row in followups:
        when = row.created_at or row.due_at
        text = row.notes or f"{row.channel.title()} follow-up scheduled"
        events.append(
            (
                when,
                ActivityItem(
                    id=f"followup-{row.id}",
                    type="followup",
                    at=_to_iso(when) or _to_iso(row.due_at) or "",
                    text=text,
                ),
            )
        )

    audits = (
        session.query(AuditLog)
        .filter(
            AuditLog.contact_id == cid,
            AuditLog.event_type == "contact.notes.update",
        )
        .order_by(AuditLog.occurred_at.desc())
        .limit(window)
        .all()
    )
    for row in audits:
        when = row.occurred_at
        info = ""
        try:
            payload = json.loads(row.event_data or "{}")
            request_id = payload.get("request_id")
            if request_id:
                info = f" (request {request_id})"
        except (TypeError, ValueError):
            info = ""
        events.append(
            (
                when,
                ActivityItem(
                    id=f"audit-{row.id}",
                    type="audit",
                    at=_to_iso(when) or "",
                    text=f"Notes updated{info}",
                ),
            )
        )

    return events


@router.get("/contacts/{contact_id}/activity", response_model=List[ActivityItem])
async def get_contact_activity(
    contact_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Optional[Session] = Depends(get_db),
) -> List[ActivityItem]:
    session = _ensure_db(db)
    cid = _parse_contact_id(contact_id)

    try:
        exists = (
            session.query(EnhancedClient.id)
            .filter(EnhancedClient.id == cid)
            .first()
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Contact not found")
    except SQLAlchemyError as exc:
        logger.exception("Failed to validate contact %s", contact_id)
        raise HTTPException(status_code=500, detail="Failed to load activity") from exc

    window = limit + offset
    try:
        events = _collect_activity_items(cid, session, window * 2)
    except SQLAlchemyError as exc:
        logger.exception("Failed to gather activity for contact %s", contact_id)
        raise HTTPException(status_code=500, detail="Failed to load activity") from exc

    events.sort(key=lambda item: item[0] or datetime.utcnow(), reverse=True)
    sliced = events[offset : offset + limit]
    return [entry for _, entry in sliced]
