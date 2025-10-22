import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import inspect

from app.core.database import engine


TEMPLATES: List[Dict[str, Any]] = [
    {
        "name": "Clean Minimal",
        "description": "Light, modern brochure with focus on hero imagery and essential facts.",
        "file_path": "templates/brochure/clean-minimal.html",
        "preview_url": "/static/brochures/clean-minimal.png",
        "fields_schema": [
            {"key": "property_title", "label": "Property Title", "type": "text", "required": True},
            {"key": "address", "label": "Address", "type": "text", "required": True},
            {"key": "highlights", "label": "Highlights", "type": "list", "required": False},
        ],
    },
    {
        "name": "Luxury Showcase",
        "description": "Premium layout tailored for high-end properties with flexible gallery sections.",
        "file_path": "templates/brochure/luxury-showcase.html",
        "preview_url": "/static/brochures/luxury-showcase.png",
        "fields_schema": [
            {"key": "property_title", "label": "Headline", "type": "text", "required": True},
            {"key": "price", "label": "Listing Price", "type": "currency", "required": True},
            {"key": "gallery", "label": "Gallery Images", "type": "list", "required": False},
            {"key": "agent_note", "label": "Agent Note", "type": "textarea", "required": False},
        ],
    },
    {
        "name": "Neighborhood Highlight",
        "description": "Balanced brochure that blends property facts with neighborhood callouts and amenities.",
        "file_path": "templates/brochure/neighborhood-highlight.html",
        "preview_url": "/static/brochures/neighborhood-highlight.png",
        "fields_schema": [
            {"key": "property_title", "label": "Property Title", "type": "text", "required": True},
            {"key": "neighborhood", "label": "Neighborhood", "type": "text", "required": True},
            {"key": "amenities", "label": "Amenities", "type": "list", "required": False},
            {"key": "market_stats", "label": "Market Stats", "type": "textarea", "required": False},
        ],
    },
]


def ensure_table_and_columns(connection) -> None:
    create_sql = (
        "CREATE TABLE IF NOT EXISTS brochure_templates ("
        "id TEXT PRIMARY KEY NOT NULL,"
        "name TEXT NOT NULL,"
        "description TEXT NULL,"
        "file_path TEXT NOT NULL,"
        "preview_url TEXT NULL,"
        "fields_schema TEXT NULL,"
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        ");"
    )
    connection.exec_driver_sql(create_sql)

    inspector = inspect(connection)
    columns = {col["name"] for col in inspector.get_columns("brochure_templates")}

    if "preview_url" not in columns:
        connection.exec_driver_sql("ALTER TABLE brochure_templates ADD COLUMN preview_url TEXT")

    if "fields_schema" not in columns:
        dialect = connection.dialect.name
        if dialect in {"postgresql"}:
            connection.exec_driver_sql(
                "ALTER TABLE brochure_templates ADD COLUMN fields_schema JSONB"
            )
        else:
            connection.exec_driver_sql(
                "ALTER TABLE brochure_templates ADD COLUMN fields_schema TEXT"
            )


def upsert_templates(connection) -> None:
    for template in TEMPLATES:
        payload = {
            "name": template["name"],
            "description": template.get("description"),
            "file_path": template["file_path"],
            "preview_url": template.get("preview_url"),
            "fields_schema": json.dumps(template.get("fields_schema") or []),
        }

        exists = connection.exec_driver_sql(
            "SELECT id FROM brochure_templates WHERE name = :name LIMIT 1",
            {"name": template["name"]},
        ).fetchone()

        if exists:
            connection.exec_driver_sql(
                "UPDATE brochure_templates "
                "SET description = :description, "
                "    file_path = :file_path, "
                "    preview_url = :preview_url, "
                "    fields_schema = :fields_schema "
                "WHERE name = :name",
                payload,
            )
        else:
            payload.update(
                {
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
            connection.exec_driver_sql(
                "INSERT INTO brochure_templates "
                "(id, name, description, file_path, preview_url, fields_schema, created_at) "
                "VALUES (:id, :name, :description, :file_path, :preview_url, :fields_schema, :created_at)",
                payload,
            )


def main() -> None:
    with engine.begin() as conn:
        ensure_table_and_columns(conn)
        upsert_templates(conn)

    print("Seeded brochure_templates (idempotent)")


if __name__ == "__main__":
    main()

