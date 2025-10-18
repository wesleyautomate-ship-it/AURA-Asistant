import uuid
from datetime import datetime
from sqlalchemy import text

from app.core.database import engine


TEMPLATES = [
    {"name": "Clean Minimal", "description": "Light, modern brochure with focus on imagery.", "file_path": "templates/brochure/clean-minimal.html"},
    {"name": "Luxury Showcase", "description": "Premium layout for high-end properties.", "file_path": "templates/brochure/luxury-showcase.html"},
    {"name": "Neighborhood Highlight", "description": "Area highlights with local amenities.", "file_path": "templates/brochure/neighborhood-highlight.html"},
]


def main():
    create_sql = (
        "CREATE TABLE IF NOT EXISTS brochure_templates ("
        "id TEXT PRIMARY KEY NOT NULL,"
        "name TEXT NOT NULL,"
        "description TEXT NULL,"
        "file_path TEXT NOT NULL,"
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        ");"
    )

    with engine.begin() as conn:
        conn.exec_driver_sql(create_sql)
        # Upsert by name
        for t in TEMPLATES:
            exists = conn.exec_driver_sql(
                "SELECT 1 FROM brochure_templates WHERE name = :name LIMIT 1",
                {"name": t["name"]},
            ).fetchone()
            if exists:
                continue
            conn.exec_driver_sql(
                "INSERT INTO brochure_templates (id, name, description, file_path, created_at) "
                "VALUES (:id, :name, :description, :file_path, :created_at)",
                {
                    "id": str(uuid.uuid4()),
                    "name": t["name"],
                    "description": t.get("description"),
                    "file_path": t["file_path"],
                    "created_at": datetime.utcnow().isoformat(),
                },
            )

    print("Seeded brochure_templates (idempotent)")


if __name__ == "__main__":
    main()

