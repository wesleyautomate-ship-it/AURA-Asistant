"""
Clients Router
==============

FastAPI router providing basic CRUD for clients (CRM) aligned with
frontend types and enhanced SQLAlchemy models.
"""

from typing import List, Optional, Dict, Any
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.middleware import get_current_user, require_agent_or_admin
from app.core.models import User
from app.domain.listings.enhanced_real_estate_models import EnhancedClient


router = APIRouter(prefix="/api/v1/clients", tags=["Clients"])


# ======================
# Pydantic Schemas
# ======================


class ClientBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    requirements: Optional[str] = None
    client_type: Optional[str] = Field(default="buyer")
    client_status: Optional[str] = Field(default="active")
    assigned_agent_id: Optional[int] = None
    relationship_start_date: Optional[date] = None
    notes: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class ClientCreate(ClientBase):
    name: str


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    requirements: Optional[str] = None
    client_type: Optional[str] = None
    client_status: Optional[str] = None
    assigned_agent_id: Optional[int] = None
    relationship_start_date: Optional[date] = None
    notes: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class ClientResponse(ClientBase):
    id: int

    class Config:
        from_attributes = True


# ======================
# Routes
# ======================


@router.get("/dev", response_model=List[ClientResponse])
async def list_clients_dev():
    """Development endpoint to list clients without authentication."""
    import os

    if os.getenv("DISABLE_AUTH", "false").lower() != "true":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development endpoint not available",
        )

    # Return sample clients for development
    sample_clients = [
        {
            "id": 1,
            "name": "Ahmed Al-Mahmoud",
            "email": "ahmed.mahmoud@gmail.com",
            "phone": "+971 50 123 4567",
            "budget_min": 2000000.0,
            "budget_max": 5000000.0,
            "preferred_location": "Downtown Dubai",
            "requirements": "3+ bedroom apartment with marina view",
            "client_type": "buyer",
            "client_status": "active",
            "assigned_agent_id": 1,
            "relationship_start_date": "2024-12-01",
            "notes": "High-value client interested in luxury properties",
            "preferences": {
                "view": "marina",
                "parking": "2_spaces",
                "amenities": ["pool", "gym"],
            },
        },
        {
            "id": 2,
            "name": "Sarah Johnson",
            "email": "sarah.j@outlook.com",
            "phone": "+971 55 987 6543",
            "budget_min": 1500000.0,
            "budget_max": 3000000.0,
            "preferred_location": "Dubai Marina",
            "requirements": "2 bedroom apartment, modern furnished",
            "client_type": "buyer",
            "client_status": "active",
            "assigned_agent_id": 1,
            "relationship_start_date": "2024-11-15",
            "notes": "First-time buyer, needs guidance",
            "preferences": {
                "furnished": True,
                "floor": "high",
                "amenities": ["concierge"],
            },
        },
        {
            "id": 3,
            "name": "Mohammed Al-Rashid",
            "email": "m.alrashid@emirates.com",
            "phone": "+971 50 456 7890",
            "budget_min": 8000000.0,
            "budget_max": 15000000.0,
            "preferred_location": "Palm Jumeirah",
            "requirements": "Villa with private beach access",
            "client_type": "buyer",
            "client_status": "active",
            "assigned_agent_id": 1,
            "relationship_start_date": "2024-10-20",
            "notes": "VIP client looking for ultra-luxury property",
            "preferences": {"beach_access": True, "pool": "private", "size": "large"},
        },
    ]

    return [ClientResponse(**client) for client in sample_clients]


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        query = (
            db.query(EnhancedClient)
            .order_by(EnhancedClient.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return [ClientResponse.model_validate(obj) for obj in query.all()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list clients: {str(e)}")


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj = db.query(EnhancedClient).filter(EnhancedClient.id == client_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientResponse.model_validate(obj)


@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_agent_or_admin)],
)
async def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        obj = EnhancedClient(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            budget_min=payload.budget_min,
            budget_max=payload.budget_max,
            preferred_location=payload.preferred_location,
            requirements=payload.requirements,
            client_type=payload.client_type or "buyer",
            client_status=payload.client_status or "active",
            assigned_agent_id=payload.assigned_agent_id or current_user.id,
            relationship_start_date=payload.relationship_start_date,
            preferences=payload.preferences or {},
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return ClientResponse.model_validate(obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create client: {str(e)}"
        )


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    dependencies=[Depends(require_agent_or_admin)],
)
async def update_client(
    client_id: int,
    updates: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = db.query(EnhancedClient).filter(EnhancedClient.id == client_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Client not found")
    try:
        data = updates.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(obj, key, value)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return ClientResponse.model_validate(obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update client: {str(e)}"
        )


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_agent_or_admin)],
)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = db.query(EnhancedClient).filter(EnhancedClient.id == client_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Client not found")
    try:
        db.delete(obj)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete client: {str(e)}"
        )
