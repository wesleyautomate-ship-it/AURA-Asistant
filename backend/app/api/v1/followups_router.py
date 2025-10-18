from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid

router = APIRouter(tags=["Followups"])


Channel = Literal["call", "email", "whatsapp", "meeting"]


class FollowUpItem(BaseModel):
    id: str
    contactId: str
    channel: Channel
    dueAt: str  # ISO string
    notes: Optional[str] = None
    createdAt: str


# In-memory store (TODO: replace with DB later)
_FOLLOWUPS: List[FollowUpItem] = []


@router.get("/followups", response_model=List[FollowUpItem])
async def list_followups(contactId: str = Query(...)) -> List[FollowUpItem]:
    return [f for f in _FOLLOWUPS if f.contactId == contactId]


class FollowUpCreate(BaseModel):
    id: Optional[str] = Field(default=None)
    contactId: str
    channel: Channel
    dueAt: str
    notes: Optional[str] = None
    createdAt: Optional[str] = Field(default=None)


@router.post("/followups", response_model=FollowUpItem)
async def create_followup(body: FollowUpCreate) -> FollowUpItem:
    fid = body.id or str(uuid.uuid4())
    created = body.createdAt or datetime.utcnow().isoformat() + "Z"
    item = FollowUpItem(
        id=fid,
        contactId=body.contactId,
        channel=body.channel,
        dueAt=body.dueAt,
        notes=body.notes,
        createdAt=created,
    )
    _FOLLOWUPS.append(item)
    return item

