"""Seed development data for local runs.

Usage::
    python dev_data/load.py

Requires DATABASE_URL to be set (defaults to sqlite:///./dev.db).
"""

import os
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import SessionLocal, engine
from app.core import models as models
from app.core.utils import hash_password


def ensure_tables() -> None:
    models.Base.metadata.create_all(bind=engine)


def seed_user(session):
    email = "agent@example.com"
    stmt = select(models.User).where(models.User.email == email)
    user = session.execute(stmt).scalar_one_or_none()
    if user:
        return user

    now = datetime.now(timezone.utc)
    user = models.User(
        email=email,
        password_hash=hash_password("pass1234"),
        first_name="Dev",
        last_name="Agent",
        role="agent",
        is_active=True,
        email_verified=True,
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    session.flush()
    return user


def seed_property(session):
    prop_stmt = select(models.Property).where(models.Property.title == "Marina Heights Penthouse")
    property_obj = session.execute(prop_stmt).scalar_one_or_none()
    if property_obj:
        return property_obj

    now = datetime.now(timezone.utc)
    property_obj = models.Property(
        title="Marina Heights Penthouse",
        building="Marina Heights",
        community="Dubai Marina",
        unit="PH-01",
        property_type=models.PropertyType.apartment,
        beds=3,
        baths=4.0,
        area_sqft=2500.0,
        price_aed=4200000,
        description="A luxury penthouse with marina views and premium finishes.",
        location_lat=25.0803,
        location_lng=55.1440,
        status=models.PropertyStatus.active,
        created_at=now,
        updated_at=now,
    )
    session.add(property_obj)
    session.flush()

    photo = models.PropertyPhoto(
        property_id=property_obj.id,
        url="https://example.com/marina-heights.jpg",
        sort_order=1,
    )
    session.add(photo)
    return property_obj


def seed_brochure_template(session):
    template_stmt = select(models.BrochureTemplate).where(models.BrochureTemplate.id == "template-classic")
    template = session.execute(template_stmt).scalar_one_or_none()
    if template:
        return template

    template = models.BrochureTemplate(
        id="template-classic",
        name="Classic Brochure",
        description="Multi-section brochure layout for premium listings.",
        file_path="/tmp/classic_brochure.html",
        created_at=datetime.now(timezone.utc),
    )
    session.add(template)
    return template


def main() -> None:
    ensure_tables()
    with SessionLocal() as session:
        seed_user(session)
        seed_property(session)
        seed_brochure_template(session)
        session.commit()
        print("Seed data loaded.")


if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:///./dev.db"
    main()
