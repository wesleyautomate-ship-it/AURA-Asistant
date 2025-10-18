from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import BrochureTemplate as BrochureTemplateModel
from app.schemas.brochure import BrochureTemplateOut


router = APIRouter(prefix="/api/v1/templates", tags=["Brochures"])


@router.get("", response_model=list[BrochureTemplateOut])
def list_templates(db: Session = Depends(get_db)) -> list[BrochureTemplateOut]:
    rows = db.query(BrochureTemplateModel).order_by(BrochureTemplateModel.created_at.desc()).all()
    out: list[BrochureTemplateOut] = []
    for row in rows:
        out.append(
            BrochureTemplateOut(
                id=row.id,
                name=row.name,
                description=row.description,
                file_path=row.file_path,
                created_at=row.created_at.isoformat() if row.created_at else "",
            )
        )
    return out

