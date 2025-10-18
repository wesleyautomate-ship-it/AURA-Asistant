"""
Seed a deterministic set of CRM contacts with notes, activities, and follow-ups.
Idempotent: contacts are keyed by email/phone; child records are deduplicated.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.all_models import import_all_models
from app.core.database import SessionLocal
from app.domain.listings.enhanced_real_estate_models import (
    ContactActivity,
    ContactNote,
    EnhancedClient,
    FollowUp,
)

import_all_models()

CONTACT_DATA = [
    {
        "name": "Alex Johnson",
        "email": "alex.j@example.com",
        "phone": "+971501234567",
        "status": "active",
        "preferred_location": "Dubai Marina",
        "notes": [
            {"text": "Interested in waterfront 2BR around 6M AED", "hours_ago": 18},
        ],
        "activities": [
            {"kind": "email", "hours_ago": 6, "summary": "Sent brochure with Marina inventory"},
            {"kind": "call", "hours_ago": 2, "summary": "Discussed financing pre-approval"},
        ],
        "followups": [
            {"channel": "call", "hours_from_now": 24, "notes": "Confirm viewing availability"},
        ],
    },
    {
        "name": "Briana Chen",
        "email": "briana.c@example.com",
        "phone": "+971525550101",
        "status": "warm",
        "preferred_location": "Downtown",
        "notes": [
            {"text": "Prefers Burj-facing high floor units", "hours_ago": 26},
        ],
        "activities": [
            {"kind": "whatsapp", "hours_ago": 20, "summary": "Shared payment plan details"},
            {"kind": "email", "hours_ago": 8, "summary": "Followed up with brochure PDF"},
        ],
        "followups": [
            {"channel": "email", "hours_from_now": 12, "notes": "Send off-plan options"},
        ],
    },
    {
        "name": "Carlos Ramirez",
        "email": "carlos.r@example.com",
        "phone": "+971540002233",
        "status": "active",
        "preferred_location": "Palm Jumeirah",
        "notes": [
            {"text": "Focused on 3BR garden villas", "hours_ago": 40},
        ],
        "activities": [
            {"kind": "meeting", "hours_ago": 30, "summary": "On-site viewing of Frond B"},
            {"kind": "call", "hours_ago": 4, "summary": "Discussed seller counter-offer"},
        ],
        "followups": [
            {"channel": "meeting", "hours_from_now": 48, "notes": "Second viewing with family"},
        ],
    },
    {
        "name": "Danielle Brooks",
        "email": "danielle.b@example.com",
        "phone": "+971507770000",
        "status": "warm",
        "preferred_location": "Business Bay",
        "notes": [
            {"text": "Needs investment ROI above 7%", "hours_ago": 55},
        ],
        "activities": [
            {"kind": "email", "hours_ago": 24, "summary": "Sent cap rate analysis"},
            {"kind": "ai", "hours_ago": 3, "summary": "AI summary shared with investor"},
        ],
        "followups": [
            {"channel": "call", "hours_from_now": 18, "notes": "Review offer terms"},
        ],
    },
    {
        "name": "Ethan Patel",
        "email": "ethan.p@example.com",
        "phone": "+971502222222",
        "status": "cold",
        "preferred_location": "JVC",
        "notes": [
            {"text": "Paused search until Q1", "hours_ago": 120},
        ],
        "activities": [
            {"kind": "email", "hours_ago": 96, "summary": "Sent rental yield snapshot"},
        ],
        "followups": [
            {"channel": "email", "hours_from_now": 168, "notes": "Check-in for timeline"},
        ],
    },
    {
        "name": "Fatima Khan",
        "email": "fatima.k@example.com",
        "phone": "+971588887766",
        "status": "active",
        "preferred_location": "Arabian Ranches",
        "notes": [
            {"text": "Family relocating from UK in December", "hours_ago": 10},
        ],
        "activities": [
            {"kind": "call", "hours_ago": 7, "summary": "Discussed schools and commute"},
            {"kind": "email", "hours_ago": 5, "summary": "Shared gated community brochures"},
        ],
        "followups": [
            {"channel": "meeting", "hours_from_now": 36, "notes": "Preview ranch-style villas"},
        ],
    },
    {
        "name": "Grace Lee",
        "email": "grace.lee@example.com",
        "phone": "+971523456789",
        "status": "warm",
        "preferred_location": "City Walk",
        "notes": [
            {"text": "Investor seeking furnished 1BR units", "hours_ago": 15},
        ],
        "activities": [
            {"kind": "whatsapp", "hours_ago": 9, "summary": "Shared furnished unit inventory"},
        ],
        "followups": [
            {"channel": "email", "hours_from_now": 30, "notes": "Send rental performance comps"},
        ],
    },
    {
        "name": "Henry Nguyen",
        "email": "henry.n@example.com",
        "phone": "+971589999000",
        "status": "new",
        "preferred_location": "Expo City",
        "notes": [
            {"text": "Interested in Expo legacy developments", "hours_ago": 6},
        ],
        "activities": [
            {"kind": "call", "hours_ago": 4, "summary": "Introductory discovery call"},
        ],
        "followups": [
            {"channel": "email", "hours_from_now": 6, "notes": "Send masterplan overview"},
        ],
    },
    {
        "name": "Isabella Rossi",
        "email": "isabella.r@example.com",
        "phone": "+971544441212",
        "status": "active",
        "preferred_location": "Bluewaters",
        "notes": [
            {"text": "Comparing sea-view penthouses", "hours_ago": 12},
        ],
        "activities": [
            {"kind": "meeting", "hours_ago": 8, "summary": "Viewing at Bluewaters Residence"},
            {"kind": "email", "hours_ago": 2, "summary": "Shared pricing sheet"},
        ],
        "followups": [
            {"channel": "call", "hours_from_now": 20, "notes": "Gather feedback on penthouse"},
        ],
    },
    {
        "name": "Jamal Ali",
        "email": "jamal.ali@example.com",
        "phone": "+971503333210",
        "status": "warm",
        "preferred_location": "Meydan",
        "notes": [
            {"text": "Looking for golf course townhouses", "hours_ago": 36},
        ],
        "activities": [
            {"kind": "email", "hours_ago": 18, "summary": "Shared Meydan South brochure"},
        ],
        "followups": [
            {"channel": "call", "hours_from_now": 48, "notes": "Plan weekend viewing"},
        ],
    },
    {
        "name": "Leila Haddad",
        "email": "leila.h@example.com",
        "phone": "+971566601234",
        "status": "active",
        "preferred_location": "Jumeirah Beach Residence",
        "notes": [
            {"text": "Needs home office and maid room", "hours_ago": 20},
        ],
        "activities": [
            {"kind": "call", "hours_ago": 14, "summary": "Clarified layout requirements"},
            {"kind": "email", "hours_ago": 9, "summary": "Sent JBR inventory shortlist"},
        ],
        "followups": [
            {"channel": "meeting", "hours_from_now": 30, "notes": "Tour two shortlisted units"},
        ],
    },
]


def _ensure_client(db: Session, entry: dict, now: datetime) -> EnhancedClient:
    contact = db.query(EnhancedClient).filter(EnhancedClient.email == entry["email"]).first()
    if not contact:
        contact = EnhancedClient(
            name=entry["name"],
            email=entry["email"],
            phone=entry["phone"],
            client_status=entry["status"],
            preferred_location=entry.get("preferred_location"),
        )
        db.add(contact)
        db.flush()
    else:
        contact.name = entry["name"]
        contact.phone = entry["phone"]
        contact.client_status = entry["status"]
        contact.preferred_location = entry.get("preferred_location")
    return contact


def _ensure_note(db: Session, contact_id: int, text: str, created_at: datetime) -> None:
    exists = (
        db.query(ContactNote.id)
        .filter(ContactNote.contact_id == contact_id, ContactNote.body == text)
        .first()
    )
    if not exists:
        db.add(ContactNote(contact_id=contact_id, body=text, created_at=created_at))


def _ensure_activity(db: Session, contact_id: int, kind: str, occurred_at: datetime, summary: str) -> None:
    exists = (
        db.query(ContactActivity.id)
        .filter(
            ContactActivity.contact_id == contact_id,
            ContactActivity.kind == kind,
            ContactActivity.summary == summary,
        )
        .first()
    )
    if not exists:
        db.add(
            ContactActivity(
                contact_id=contact_id,
                kind=kind,
                occurred_at=occurred_at,
                summary=summary,
            )
        )


def _ensure_followup(db: Session, contact_id: int, channel: str, due_at: datetime, notes: str | None) -> None:
    exists = (
        db.query(FollowUp.id)
        .filter(
            FollowUp.contact_id == contact_id,
            FollowUp.due_at == due_at,
            FollowUp.channel == channel,
        )
        .first()
    )
    if not exists:
        db.add(
            FollowUp(
                contact_id=contact_id,
                channel=channel,
                due_at=due_at,
                notes=notes,
                status="scheduled",
            )
        )


def _update_last_activity(db: Session, contact_id: int) -> None:
    last = (
        db.query(func.max(ContactActivity.occurred_at))
        .filter(ContactActivity.contact_id == contact_id)
        .scalar()
    )
    note_last = (
        db.query(func.max(ContactNote.created_at))
        .filter(ContactNote.contact_id == contact_id)
        .scalar()
    )
    followup_last = (
        db.query(func.max(FollowUp.created_at))
        .filter(FollowUp.contact_id == contact_id)
        .scalar()
    )
    final_candidates = [last, note_last, followup_last]
    final_candidates = [ts for ts in final_candidates if ts is not None]
    final = max(final_candidates) if final_candidates else None
    if final is not None:
        db.query(EnhancedClient).filter(EnhancedClient.id == contact_id).update(
            {EnhancedClient.last_activity_at: final}, synchronize_session=False
        )


def run(data: Iterable[dict] | None = None) -> None:
    dataset = list(data) if data is not None else CONTACT_DATA
    now = datetime.utcnow()
    session = SessionLocal()
    try:
        for entry in dataset:
            contact = _ensure_client(session, entry, now)
            cid = contact.id

            for note in entry.get("notes", []):
                created_at = now - timedelta(hours=note.get("hours_ago", 0))
                _ensure_note(session, cid, note["text"], created_at)

            for activity in entry.get("activities", []):
                occurred_at = now - timedelta(hours=activity.get("hours_ago", 0))
                _ensure_activity(
                    session,
                    cid,
                    activity["kind"],
                    occurred_at,
                    activity["summary"],
                )

            for follow in entry.get("followups", []):
                due_at = now + timedelta(hours=follow.get("hours_from_now", 0))
                _ensure_followup(
                    session,
                    cid,
                    follow["channel"],
                    due_at,
                    follow.get("notes"),
                )

            _update_last_activity(session, cid)

        session.commit()
        print(f"Seeded {len(dataset)} contacts with notes, activities, and follow-ups.")
    finally:
        session.close()


if __name__ == "__main__":
    run()
