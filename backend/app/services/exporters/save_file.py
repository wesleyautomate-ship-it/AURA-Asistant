from __future__ import annotations

import uuid
from pathlib import Path
from app.core.settings import get_settings


def save_html(html: str, prefix: str = "brochure") -> str:
    """Save HTML content to the uploads directory and return a URL path.

    Returns a URL path like `/uploads/brochure-<id>.html`.
    """
    settings = get_settings()
    uploads_dir: Path = settings.upload_dir
    uploads_dir.mkdir(parents=True, exist_ok=True)

    file_id = uuid.uuid4().hex
    filename = f"{prefix}-{file_id}.html"
    file_path = uploads_dir / filename
    file_path.write_text(html, encoding="utf-8")

    return f"/uploads/{filename}"

