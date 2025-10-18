import os
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.core import models as core_models
from backend.app.domain.listings.enhanced_real_estate_models import (
    EnhancedClient,
    ContactActivity,
)


def setup_test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Create tables for all models using shared Base
    core_models.Base.metadata.create_all(bind=engine)

    def _get_db():
        db = TestingSessionLocal()
        try:
            yield db
            db.commit()
        finally:
            db.close()

    return _get_db, TestingSessionLocal


def test_contacts_list_and_activity_db_backed():
    get_db_override, SessionLocal = setup_test_db()
    app.dependency_overrides[__import__("backend.app.core.database", fromlist=["get_db"]).get_db] = get_db_override  # type: ignore

    # Seed minimal data
    db = SessionLocal()
    try:
        c = EnhancedClient(name="Test Contact", email="test@example.com", phone="+971500000000")
        db.add(c)
        db.commit()
        db.refresh(c)
        db.add(
            ContactActivity(
                contact_id=c.id,
                kind="email",
                occurred_at=datetime.utcnow() - timedelta(minutes=5),
                summary="Sent intro email",
            )
        )
        db.commit()
    finally:
        db.close()

    client = TestClient(app)
    r = client.get("/contacts?limit=10&offset=0")
    assert r.status_code == 200
    items = r.json()
    assert any(str(i["id"]) == str(c.id) for i in items)

    r2 = client.get(f"/contacts/{c.id}/activity")
    assert r2.status_code == 200
    acts = r2.json()
    assert len(acts) >= 1
    assert acts[0]["type"] in {"email", "call", "ai", "whatsapp", "meeting"}


def test_followups_create_and_list_db_backed():
    get_db_override, SessionLocal = setup_test_db()
    app.dependency_overrides[__import__("backend.app.core.database", fromlist=["get_db"]).get_db] = get_db_override  # type: ignore

    # Seed one contact
    db = SessionLocal()
    try:
        c = EnhancedClient(name="Follow Up", email="fu@example.com", phone="+971511111111")
        db.add(c)
        db.commit()
        db.refresh(c)
        cid = c.id
    finally:
        db.close()

    client = TestClient(app)
    due_at = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
    payload = {
        "contactId": str(cid),
        "channel": "call",
        "dueAt": due_at,
        "notes": "Schedule a quick call",
    }
    r = client.post("/followups", json=payload)
    assert r.status_code == 200
    created = r.json()
    assert created["contactId"] == str(cid)
    assert created["channel"] == "call"

    r2 = client.get(f"/followups?contactId={cid}")
    assert r2.status_code == 200
    items = r2.json()
    assert any(i["id"] == created["id"] for i in items)

