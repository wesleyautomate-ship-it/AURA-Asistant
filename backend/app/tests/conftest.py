import os
import asyncio
import pytest
import pytest_asyncio
import httpx


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client():
    # Use in-memory SQLite and create only required tables
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    import sys
    import types
    from datetime import datetime
    from fastapi import FastAPI
    from sqlalchemy import Column, String, DateTime, JSON, Text
    from sqlalchemy.orm import declarative_base
    from app.core.database import engine

    # Provide a minimal stub for app.core.models to avoid loading full model graph
    minimal_models = types.ModuleType("app.core.models")
    Base = declarative_base()

    import uuid
    class BrochureDraft(Base):
        __tablename__ = "brochure_drafts"
        id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
        data = Column(JSON)
        status = Column(String(20), index=True)
        download_url = Column(String(512))
        template_id = Column(String(36))
        contact_id = Column(String(36))
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    class BrochureTemplate(Base):
        __tablename__ = "brochure_templates"
        id = Column(String(36), primary_key=True, index=True)
        name = Column(String(255), index=True)
        description = Column(Text)
        file_path = Column(String(512))
        created_at = Column(DateTime, default=datetime.utcnow)

    minimal_models.Base = Base
    minimal_models.BrochureDraft = BrochureDraft
    minimal_models.BrochureTemplate = BrochureTemplate
    sys.modules['app.core.models'] = minimal_models

    from app.api.v1.brochures_router import router as brochures_router
    from app.api.v1.templates_router import router as templates_router

    # Minimal schema to avoid other models' types
    schema = (
        "CREATE TABLE IF NOT EXISTS brochure_templates ("
        "id VARCHAR(36) PRIMARY KEY NOT NULL,"
        "name VARCHAR(255) NOT NULL,"
        "description TEXT NULL,"
        "file_path VARCHAR(512) NOT NULL,"
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        ");"
    )
    drafts = (
        "CREATE TABLE IF NOT EXISTS brochure_drafts ("
        "id VARCHAR(36) PRIMARY KEY NOT NULL,"
        "data JSON,"
        "status VARCHAR(20) NOT NULL DEFAULT 'draft',"
        "download_url VARCHAR(512),"
        "template_id VARCHAR(36) NULL,"
        "contact_id INTEGER NULL,"
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP,"
        "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        ");"
    )
    idx = [
        "CREATE INDEX IF NOT EXISTS ix_brochure_drafts_status ON brochure_drafts(status);",
        "CREATE INDEX IF NOT EXISTS ix_brochure_drafts_id ON brochure_drafts(id);",
        "CREATE INDEX IF NOT EXISTS ix_brochure_drafts_created_at ON brochure_drafts(created_at);",
    ]
    with engine.begin() as conn:
        conn.exec_driver_sql(schema)
        conn.exec_driver_sql(drafts)
        for i in idx:
            conn.exec_driver_sql(i)

    app = FastAPI()
    app.include_router(brochures_router)
    app.include_router(templates_router)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
