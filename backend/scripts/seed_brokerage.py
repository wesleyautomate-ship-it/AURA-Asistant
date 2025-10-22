from app.core.all_models import import_all_models
from app.core.database import SessionLocal
from app.core.models import Brokerage


def upsert_default() -> None:
    """Ensure a default brokerage exists for local development."""
    import_all_models()

    name = "Dubai Prime Realty"
    db = SessionLocal()
    try:
        row = db.query(Brokerage).filter(Brokerage.name == name).first()
        if not row:
            row = Brokerage(name=name)
            db.add(row)
            db.commit()
            db.refresh(row)
        print(f"Default brokerage id: {row.id}")
    finally:
        db.close()


if __name__ == "__main__":
    upsert_default()
