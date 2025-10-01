"""
Transactions Router
===================

FastAPI router providing CRUD for transactions and simple status updates.
Aligns to `Transaction` model in enhanced models and frontend needs.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.middleware import get_current_user, require_agent_or_admin
from app.core.models import User
from app.domain.listings.enhanced_real_estate_models import Transaction, TransactionHistory


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])


# ======================
# Pydantic Schemas
# ======================

class TransactionBase(BaseModel):
    property_id: int
    buyer_id: Optional[int] = None
    seller_id: Optional[int] = None
    agent_id: Optional[int] = None
    transaction_type: str = Field(..., description="sale | rental | lease | investment")
    transaction_status: str = Field(default="pending")
    offer_price: Optional[float] = None
    final_price: Optional[float] = None
    commission_rate: Optional[float] = None
    commission_amount: Optional[float] = None
    transaction_date: Optional[date] = None
    closing_date: Optional[date] = None
    contract_signed_date: Optional[date] = None
    payment_terms: Optional[Dict[str, Any]] = None
    documents: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    property_id: int
    transaction_type: str


class TransactionUpdate(BaseModel):
    buyer_id: Optional[int] = None
    seller_id: Optional[int] = None
    agent_id: Optional[int] = None
    transaction_status: Optional[str] = None
    offer_price: Optional[float] = None
    final_price: Optional[float] = None
    commission_rate: Optional[float] = None
    commission_amount: Optional[float] = None
    transaction_date: Optional[date] = None
    closing_date: Optional[date] = None
    contract_signed_date: Optional[date] = None
    payment_terms: Optional[Dict[str, Any]] = None
    documents: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int

    class Config:
        from_attributes = True


class StatusChange(BaseModel):
    new_status: str
    reason: Optional[str] = None


# ======================
# Routes
# ======================

@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Transaction).order_by(Transaction.id.desc()).offset(offset).limit(limit)
        return [TransactionResponse.model_validate(obj) for obj in query.all()]
    except SQLAlchemyError as exc:
        logger.exception("Failed to list transactions")
        raise HTTPException(status_code=500, detail="Failed to list transactions") from exc


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obj = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse.model_validate(obj)


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_agent_or_admin)])
async def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        obj = Transaction(
            property_id=payload.property_id,
            buyer_id=payload.buyer_id,
            seller_id=payload.seller_id,
            agent_id=payload.agent_id or current_user.id,
            transaction_type=payload.transaction_type,
            transaction_status=payload.transaction_status or "pending",
            offer_price=payload.offer_price,
            final_price=payload.final_price,
            commission_rate=payload.commission_rate,
            commission_amount=payload.commission_amount,
            transaction_date=payload.transaction_date,
            closing_date=payload.closing_date,
            contract_signed_date=payload.contract_signed_date,
            payment_terms=payload.payment_terms or {},
            documents=payload.documents or [],
            notes=payload.notes,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return TransactionResponse.model_validate(obj)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to create transaction")
        raise HTTPException(status_code=500, detail="Failed to create transaction") from exc


@router.put("/{transaction_id}", response_model=TransactionResponse, dependencies=[Depends(require_agent_or_admin)])
async def update_transaction(
    transaction_id: int,
    updates: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obj = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        prev_status = obj.transaction_status
        data = updates.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(obj, key, value)
        db.add(obj)
        db.commit()
        db.refresh(obj)

        if "transaction_status" in data and data["transaction_status"] != prev_status:
            hist = TransactionHistory(
                transaction_id=obj.id,
                status_change="status_update",
                previous_status=prev_status,
                new_status=data["transaction_status"],
                changed_by=current_user.id,
            )
            db.add(hist)
            db.commit()

        return TransactionResponse.model_validate(obj)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to update transaction", extra={"transaction_id": transaction_id})
        raise HTTPException(status_code=500, detail="Failed to update transaction") from exc


@router.post("/{transaction_id}/status", response_model=TransactionResponse, dependencies=[Depends(require_agent_or_admin)])
async def change_status(
    transaction_id: int,
    payload: StatusChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obj = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        prev_status = obj.transaction_status
        obj.transaction_status = payload.new_status
        db.add(obj)
        db.commit()
        db.refresh(obj)

        hist = TransactionHistory(
            transaction_id=obj.id,
            status_change="status_update",
            previous_status=prev_status,
            new_status=payload.new_status,
            changed_by=current_user.id,
            change_reason=payload.reason,
        )
        db.add(hist)
        db.commit()

        return TransactionResponse.model_validate(obj)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to change transaction status", extra={"transaction_id": transaction_id})
        raise HTTPException(status_code=500, detail="Failed to change transaction status") from exc


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_agent_or_admin)])
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obj = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        db.delete(obj)
        db.commit()
        return None
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to delete transaction", extra={"transaction_id": transaction_id})
        raise HTTPException(status_code=500, detail="Failed to delete transaction") from exc


