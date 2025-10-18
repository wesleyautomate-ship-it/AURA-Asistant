import json
import sys
from pathlib import Path

from fastapi import FastAPI


def main(out_path: str) -> None:
    root = Path(__file__).resolve().parents[1]
    backend_dir = root / "backend"
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(backend_dir))

    from app.api.v1.contacts_router import router as contacts_router  # type: ignore
    from app.api.v1.followups_router import router as followups_router  # type: ignore
    from app.api.v1.ai_contacts_router import router as ai_contacts_router  # type: ignore

    app = FastAPI(title="Contacts API", version="1.0.0")
    app.include_router(contacts_router)
    app.include_router(followups_router)
    app.include_router(ai_contacts_router)

    schema = app.openapi()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"Wrote OpenAPI schema to {out}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent / "openapi.contacts.json")
    main(out)

