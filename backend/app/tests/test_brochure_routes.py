import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_templates(client: AsyncClient):
    # Seed one template via SQL (idempotent)
    from app.core.database import engine
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT OR IGNORE INTO brochure_templates (id, name, description, file_path) VALUES (:id,:n,:d,:p)",
            {"id": "11111111-1111-1111-1111-111111111111", "n": "Clean Minimal", "d": "A clean template", "p": "templates/brochure/clean-minimal.html"},
        )
    res = await client.get("/api/v1/templates")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list) and any(t["name"] == "Clean Minimal" for t in items)


@pytest.mark.asyncio
async def test_create_and_get_brochure(client: AsyncClient):
    # Ensure tables exist
    from app.core.database import engine
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS brochure_drafts (id VARCHAR(36) PRIMARY KEY NOT NULL, data JSON, status VARCHAR(20) NOT NULL DEFAULT 'draft', download_url VARCHAR(512), template_id VARCHAR(36) NULL, contact_id INTEGER NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    r = await client.post("/api/v1/brochures", json={"templateKey": "clean-minimal"})
    assert r.status_code == 200, r.text
    data = r.json()
    draft_id = data["id"]
    assert data["status"] == "draft"
    assert isinstance(draft_id, str) and len(draft_id) > 0

    r2 = await client.get(f"/api/v1/brochures/{draft_id}")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["id"] == draft_id
    assert data2["status"] == "draft"


@pytest.mark.asyncio
async def test_list_brochures(client: AsyncClient):
    r = await client.get("/api/v1/brochures?limit=10&offset=0")
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list)


@pytest.mark.asyncio
async def test_render_and_download_brochure(client: AsyncClient):
    # Create
    r = await client.post("/api/v1/brochures", json={"templateKey": "clean-minimal", "data": {"about": {"body": "Nice place"}}})
    assert r.status_code == 200
    draft_id = r.json()["id"]

    # Render
    rr = await client.post(f"/api/v1/brochures/{draft_id}/render")
    assert rr.status_code == 200, rr.text
    dl = rr.json().get("download_url")
    assert dl and dl.startswith("/uploads/")

    # Download URL getter
    gd = await client.get(f"/api/v1/brochures/{draft_id}/download")
    assert gd.status_code == 200
    assert gd.json().get("download_url") == dl


@pytest.mark.asyncio
async def test_not_found_errors(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    r = await client.get(f"/api/v1/brochures/{fake_id}")
    assert r.status_code == 404

    r2 = await client.get(f"/api/v1/brochures/{fake_id}/download")
    assert r2.status_code == 404
