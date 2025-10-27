import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

from .settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class DevBypassUser:
    """Simple stand-in user object for dev bypass."""

    id: int = 0
    email: str = "dev@local"
    first_name: str = "Dev"
    last_name: str = "Bypass"
    role: str = "admin"
    is_active: bool = True
    email_verified: bool = True
    is_superuser: bool = True
    roles: List[str] = field(default_factory=lambda: ["admin"])
    scopes: List[str] = field(default_factory=lambda: ["*"])
    permissions: List[str] = field(default_factory=lambda: ["*"])
    brokerage_id: Optional[int] = None
    is_dev_user: bool = True
    full_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.full_name = f"{self.first_name} {self.last_name}".strip()

    @property
    def is_locked(self) -> bool:  # pragma: no cover - simple getter
        return False


def _environment_name(settings) -> str:
    env = getattr(settings, "ENV", None) or os.getenv("ENV")
    env = env or getattr(settings, "ENVIRONMENT", None) or os.getenv(
        "ENVIRONMENT", "development"
    )
    return str(env).lower()


def _bypass_enabled(settings) -> bool:
    if not getattr(settings, "DEV_AUTH_BYPASS", False):
        return False

    env = _environment_name(settings)
    if env in {"development", "dev", "local"}:
        return True

    # Allow explicit debug flag for app.debug style configs
    return bool(getattr(settings, "debug", False))


def maybe_get_dev_user(request_path: Optional[str] = None) -> Optional[DevBypassUser]:
    """
    Return a fake user when the dev bypass is explicitly enabled.

    Args:
        request_path: Used for logging so we can audit bypass usage.
    """
    settings = get_settings()
    if not _bypass_enabled(settings):
        return None

    dev_user = DevBypassUser(id=1, email="dev@local", first_name="Dev", last_name="Bypass")
    logger.warning(
        "DEV AUTH BYPASS ENABLED \u2014 returning fake user (id=%s, email=%s) for route %s",
        dev_user.id,
        dev_user.email,
        request_path or "<unknown>",
    )
    return dev_user
