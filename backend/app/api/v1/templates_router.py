from typing import Any, Dict, List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import BrochureTemplate

router = APIRouter(prefix="/api/v1/templates", tags=["Brochures"])


def _decode_fields_schema(raw: Any) -> Any:
    if raw is None:
        return None
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw


def _serialize_template(template: BrochureTemplate) -> Dict[str, Any]:
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "file_path": template.file_path,
        "preview_url": template.preview_url,
        "fields_schema": _decode_fields_schema(template.fields_schema),
        "created_at": template.created_at,
    }


@router.get("/")
def list_templates(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    templates = (
        db.query(BrochureTemplate)
        .order_by(BrochureTemplate.name.asc())
        .all()
    )
    return [_serialize_template(t) for t in templates]


@router.get("/{template_id}")
def get_template(
    template_id: str, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    template: Optional[BrochureTemplate] = (
        db.query(BrochureTemplate)
        .filter(BrochureTemplate.id == template_id)
        .one_or_none()
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return _serialize_template(template)

