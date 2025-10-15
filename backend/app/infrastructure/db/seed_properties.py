"""
Dev-only seed script to insert a few demo properties.
Run inside the API container after Alembic migrations:

  docker-compose exec api python -m app.infrastructure.db.seed_properties

"""
from sqlalchemy import create_engine, text
import os

# Prefer env var, fall back to Alembic .ini default
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://admin:password123@localhost:5432/real_estate_db"
)

SAMPLE_PROPERTIES = [
    {
        "title": "Downtown Dubai • 2BR with Burj View",
        "description": "Luxury apartment with iconic views, high floor, modern finish.",
        "price": 2500000,
        "location": "Downtown Dubai",
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 2.5,
        "area_sqft": 1200,
    },
    {
        "title": "Palm Jumeirah • Shoreline 3BR",
        "description": "Beachfront living with private beach access and balcony.",
        "price": 3500000,
        "location": "Palm Jumeirah",
        "property_type": "apartment",
        "bedrooms": 3,
        "bathrooms": 3.0,
        "area_sqft": 1800,
    },
    {
        "title": "Dubai Marina • Marina Gate 1BR",
        "description": "Modern 1BR with marina views, close to Metro.",
        "price": 1800000,
        "location": "Dubai Marina",
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 1.0,
        "area_sqft": 800,
    },
]


def seed_properties():
    engine = create_engine(DATABASE_URL)
    insert_sql = text(
        """
        INSERT INTO properties 
            (title, description, price, location, property_type, bedrooms, bathrooms, area_sqft)
        VALUES 
            (:title, :description, :price, :location, :property_type, :bedrooms, :bathrooms, :area_sqft)
        ON CONFLICT DO NOTHING
        RETURNING id
        """
    )

    with engine.begin() as conn:
        for p in SAMPLE_PROPERTIES:
            try:
                conn.execute(insert_sql, p)
            except Exception as e:
                # continue on individual failures
                print(f"⚠️  Failed to insert sample property '{p['title']}': {e}")

    print("✅ Seeded sample properties (if table existed and was empty).")


if __name__ == "__main__":
    seed_properties()
