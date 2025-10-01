import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = PROJECT_ROOT / "backend" / "openapi.json"


def _load_snapshot() -> dict:
    if not SNAPSHOT_PATH.exists():
        raise AssertionError(
            f"OpenAPI snapshot not found at {SNAPSHOT_PATH}. "
            "Generate it with `uvicorn backend.app.main:app` and save the schema to backend/openapi.json."
        )

    with SNAPSHOT_PATH.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def _normalize(schema: dict) -> dict:
    """Normalize schema for comparison by sorting keys recursively."""
    return json.loads(json.dumps(schema, sort_keys=True))


def test_openapi_contract_snapshot() -> None:
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200, "Failed to fetch OpenAPI schema from application."

    current_schema = _normalize(response.json())
    snapshot_schema = _normalize(_load_snapshot())

    assert (
        current_schema == snapshot_schema
    ), (
        "OpenAPI schema drift detected. If intentional, regenerate `backend/openapi.json` "
        "and commit the updated snapshot."
    )
