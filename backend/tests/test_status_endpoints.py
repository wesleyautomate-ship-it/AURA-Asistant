import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.main as main_module


client = TestClient(app)


def test_healthz_ok():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_readyz_ok():
    response = client.get("/readyz")
    payload = response.json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["checks"]["db"] == "ok"


def test_version_shape(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GIT_SHA", raising=False)
    response = client.get("/version")
    payload = response.json()

    assert response.status_code == 200
    assert "git_sha" in payload
    assert "built_at" in payload


def test_readyz_db_failure(monkeypatch: pytest.MonkeyPatch):
    def broken_session_factory(*_args, **_kwargs):
        raise RuntimeError("db offline")

    monkeypatch.setattr(main_module, "SessionLocal", broken_session_factory)

    response = client.get("/readyz")
    payload = response.json()

    assert response.status_code == 503
    assert payload["ok"] is False
    assert payload["checks"]["db"] == "error"
