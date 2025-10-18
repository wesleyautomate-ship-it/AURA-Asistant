from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime, timedelta

router = APIRouter(tags=["Contacts"])


class ContactBrief(BaseModel):
    id: str
    name: str
    temperature: Literal["New", "Active", "Warm", "Cold", "Dormant"]
    lastActivityAt: Optional[str] = None
    avatarUrl: Optional[str] = None


class ContactDetail(BaseModel):
    id: str
    name: str
    temperature: Literal["New", "Active", "Warm", "Cold", "Dormant"]
    email: Optional[str] = None
    phone: Optional[str] = None
    lastActivityAt: Optional[str] = None
    notes: str
    intentScore: Optional[int] = None
    signals: Optional[List[str]] = None


class ActivityItem(BaseModel):
    id: str
    type: Literal["call", "email", "ai", "whatsapp", "meeting"]
    at: str  # ISO time
    text: str


# In-memory store (TODO: replace with persistent DB models)
_now = datetime.utcnow()
_CONTACTS: dict[str, ContactDetail] = {
    "1": ContactDetail(
        id="1",
        name="Alex Johnson",
        temperature="Active",
        email="alex.j@example.com",
        phone="+971 50 123 4567",
        lastActivityAt=(_now - timedelta(hours=2)).isoformat() + "Z",
        notes="Initial notes...\n- Preferences: Sea view, 2-3BR\n- Budget: ~6M AED",
        intentScore=62,
        signals=["Opened brochure", "Visited listing page"],
    ),
    "2": ContactDetail(
        id="2",
        name="Briana Chen",
        temperature="New",
        email="briana.c@example.com",
        phone="+971 52 555 0101",
        lastActivityAt=_now.isoformat() + "Z",
        notes="Call back after 6pm.",
        intentScore=48,
        signals=["Clicked email"],
    ),
    "3": ContactDetail(
        id="3",
        name="Carlos Ramirez",
        temperature="Warm",
        email="carlos.r@example.com",
        phone="+971 54 000 2233",
        lastActivityAt=(_now - timedelta(days=1)).isoformat() + "Z",
        notes="Interested in Marina 2BR.",
        intentScore=57,
        signals=["Saved property"],
    ),
}

_ACTIVITY: dict[str, List[ActivityItem]] = {
    "1": [
        ActivityItem(
            id="1-t1",
            type="call",
            at=(_now - timedelta(minutes=30)).isoformat() + "Z",
            text="Discussed waterfront options"
        ),
        ActivityItem(
            id="1-t2",
            type="email",
            at=(_now - timedelta(hours=2)).isoformat() + "Z",
            text="Sent brochure PDF"
        ),
        ActivityItem(
            id="1-t3",
            type="ai",
            at=(_now - timedelta(hours=20)).isoformat() + "Z",
            text="AI summarized last meeting"
        ),
    ],
    "2": [
        ActivityItem(
            id="2-t1",
            type="email",
            at=(_now - timedelta(minutes=10)).isoformat() + "Z",
            text="Sent intro email"
        ),
    ],
    "3": [
        ActivityItem(
            id="3-t1",
            type="meeting",
            at=(_now - timedelta(days=3)).isoformat() + "Z",
            text="On-site viewing booked"
        ),
    ],
}


@router.get("/contacts", response_model=List[ContactBrief])
async def list_contacts() -> List[ContactBrief]:
    return [
        ContactBrief(
            id=c.id,
            name=c.name,
            temperature=c.temperature,
            lastActivityAt=c.lastActivityAt,
        )
        for c in _CONTACTS.values()
    ]


@router.get("/contacts/{contact_id}", response_model=ContactDetail)
async def get_contact(contact_id: str) -> ContactDetail:
    if contact_id not in _CONTACTS:
        raise HTTPException(status_code=404, detail="Contact not found")
    return _CONTACTS[contact_id]


@router.get("/contacts/{contact_id}/activity", response_model=List[ActivityItem])
async def get_contact_activity(contact_id: str) -> List[ActivityItem]:
    if contact_id not in _CONTACTS:
        raise HTTPException(status_code=404, detail="Contact not found")
    return _ACTIVITY.get(contact_id, [])

