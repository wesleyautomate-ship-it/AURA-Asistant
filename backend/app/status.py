from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

class _SessionFactory(Protocol):
    """Typing protocol for SQLAlchemy session factories."""

    def __call__(self):
        ...


def liveness() -> Dict[str, bool]:
    """Always-on liveness responder."""
    return {"ok": True}


def readiness(
    db_session_factory: _SessionFactory, object_store_path: Optional[Path]
) -> Dict[str, Any]:
    """
    Validate core dependencies required for serving traffic.

    * Database: open a session and run a lightweight SELECT 1.
    * Object store (optional): ensure directory exists and is writable.
    """
    checks: Dict[str, str] = {"object_store": "skipped"}
    session: Optional[Any] = None

    try:
        from sqlalchemy import text  # Local import keeps optional deps lazy

        session = db_session_factory()
        session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as exc:
        checks["db"] = "error"
        summary = f"database check failed: {exc}"
        return {"ok": False, "checks": checks, "error": summary}
    finally:
        if session is not None:
            try:
                session.close()
            except Exception:
                pass

    if object_store_path:
        try:
            object_store_path.mkdir(parents=True, exist_ok=True)
            probe_path = object_store_path / f".status-probe-{uuid.uuid4().hex}"
            probe_path.touch()
            probe_path.unlink(missing_ok=True)
            checks["object_store"] = "ok"
        except Exception as exc:
            checks["object_store"] = "error"
            summary = f"object store check failed: {exc}"
            return {"ok": False, "checks": checks, "error": summary}

    return {"ok": True, "checks": checks}


def version_info() -> Dict[str, Optional[str]]:
    """
    Report build metadata for diagnostics.

    Priority:
    1. GIT_SHA environment variable (e.g., set during CI/CD).
    2. VERSION file in repository root.
    3. Fallback to 'dev'.
    """
    git_sha = os.getenv("GIT_SHA")
    if not git_sha:
        version_file = Path(__file__).resolve().parents[2] / "VERSION"
        if version_file.is_file():
            git_sha = version_file.read_text(encoding="utf-8").strip()
    if not git_sha:
        git_sha = "dev"

    built_at = os.getenv("BUILD_TIME")

    return {"git_sha": git_sha, "built_at": built_at if built_at else None}


__all__ = ["liveness", "readiness", "version_info"]
