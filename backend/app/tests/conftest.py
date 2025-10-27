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
    import uuid
    from datetime import datetime
    from fastapi import FastAPI
    from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Float
    from sqlalchemy.orm import declarative_base

    from app.core.database import engine

    # Provide a minimal stub for app.core.models to avoid loading full model graph
    minimal_models = types.ModuleType("app.core.models")
    Base = declarative_base()

    class BrochureDraft(Base):
        __tablename__ = "brochure_drafts"
        id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
        data = Column(JSON)
        status = Column(String(20), index=True, default="draft")
        download_url = Column(String(512))
        template_id = Column(String(36))
        contact_id = Column(String(36))
        property_id = Column(String(36))
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    class BrochureTemplate(Base):
        __tablename__ = "brochure_templates"
        id = Column(String(36), primary_key=True, index=True)
        name = Column(String(255), index=True)
        description = Column(Text)
        file_path = Column(String(512))
        preview_url = Column(String(512))
        fields_schema = Column(JSON)
        created_at = Column(DateTime, default=datetime.utcnow)

    class Property(Base):
        __tablename__ = "properties"
        id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
        title = Column(String(255), nullable=False)
        building = Column(String(255))
        community = Column(String(255))
        unit = Column(String(100))
        property_type = Column(String(50))
        beds = Column(Integer)
        baths = Column(Float)
        area_sqft = Column(Float)
        price_aed = Column(Integer)
        description = Column(Text)
        location_lat = Column(Float)
        location_lng = Column(Float)
        status = Column(String(20))
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    class PropertyPhoto(Base):
        __tablename__ = "property_photos"
        id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
        property_id = Column(String(36))
        url = Column(String(512), nullable=False)
        alt_text = Column(String(255))
        sort_order = Column(Integer)
        created_at = Column(DateTime, default=datetime.utcnow)

    minimal_models.Base = Base
    minimal_models.BrochureDraft = BrochureDraft
    minimal_models.BrochureTemplate = BrochureTemplate
    minimal_models.Property = Property
    minimal_models.PropertyPhoto = PropertyPhoto
    sys.modules["app.core.models"] = minimal_models

    from app.api.v1.brochures_router import router as brochures_router
    from app.api.v1.templates_router import router as templates_router

    schema_statements = [
        """
        CREATE TABLE IF NOT EXISTS brochure_templates (
            id VARCHAR(36) PRIMARY KEY NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT NULL,
            file_path VARCHAR(512) NOT NULL,
            preview_url VARCHAR(512) NULL,
            fields_schema JSON NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS brochure_drafts (
            id VARCHAR(36) PRIMARY KEY NOT NULL,
            data JSON,
            status VARCHAR(20) NOT NULL DEFAULT 'draft',
            download_url VARCHAR(512),
            template_id VARCHAR(36) NULL,
            contact_id INTEGER NULL,
            property_id VARCHAR(36) NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS properties (
            id VARCHAR(36) PRIMARY KEY NOT NULL,
            title VARCHAR(255) NOT NULL,
            building VARCHAR(255),
            community VARCHAR(255),
            unit VARCHAR(100),
            property_type VARCHAR(50),
            beds INTEGER,
            baths FLOAT,
            area_sqft FLOAT,
            price_aed INTEGER,
            description TEXT,
            location_lat FLOAT,
            location_lng FLOAT,
            status VARCHAR(20),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS property_photos (
            id VARCHAR(36) PRIMARY KEY NOT NULL,
            property_id VARCHAR(36),
            url VARCHAR(512) NOT NULL,
            alt_text VARCHAR(255),
            sort_order INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        "CREATE INDEX IF NOT EXISTS ix_brochure_drafts_status ON brochure_drafts(status);",
        "CREATE INDEX IF NOT EXISTS ix_brochure_drafts_id ON brochure_drafts(id);",
        "CREATE INDEX IF NOT EXISTS ix_brochure_drafts_created_at ON brochure_drafts(created_at);",
    ]

    with engine.begin() as conn:
        for statement in schema_statements:
            conn.exec_driver_sql(statement)
        conn.exec_driver_sql(
            "INSERT INTO brochure_templates (id, name, description, file_path, preview_url, fields_schema) "
            "VALUES ('template-1', 'Classic Brochure', 'A brochure template.', '/tmp/classic_brochure.html', 'https://example.com/preview.jpg', NULL) "
            "ON CONFLICT(id) DO NOTHING;"
        )
        conn.exec_driver_sql(
            "INSERT INTO properties (id, title, building, community, unit, property_type, beds, baths, area_sqft, price_aed, description, location_lat, location_lng, status) "
            "VALUES ('property-1', 'Marina Heights Penthouse', 'Marina Heights', 'Dubai Marina', 'PH-01', 'penthouse', 3, 4.0, 2500, 4200000, "
            "'A luxury penthouse with marina views and premium finishes.', 25.0803, 55.1440, 'live') ON CONFLICT(id) DO NOTHING;"
        )
        conn.exec_driver_sql(
            "INSERT INTO property_photos (id, property_id, url, alt_text, sort_order) "
            "VALUES ('photo-1', 'property-1', 'https://example.com/marina-heights.jpg', 'Living room with marina skyline', 1) "
            "ON CONFLICT(id) DO NOTHING;"
        )

    app = FastAPI()
    app.include_router(brochures_router)
    app.include_router(templates_router)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
