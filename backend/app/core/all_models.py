# backend/app/core/all_models.py
"""
Utility to import every module that defines ORM models so SQLAlchemy's registry
knows them (needed for string-based relationship() resolution).
Call import_all_models() at startup, in seed scripts, and in alembic/env.py.
"""

import importlib

_MODULES = [
    "app.domain.listings.enhanced_real_estate_models",
    "app.domain.listings.brokerage_models",
    "app.domain.listings.phase3_advanced_models",
    "app.domain.listings.ai_assistant_models",
    "app.domain.ai.rag_service",
    "app.domain.ai.hybrid_search_engine",
    "app.core.ai_content_generator",
]


def import_all_models() -> bool:
    """Import all ORM model modules so SQLAlchemy can resolve string relationships."""

    for module_name in _MODULES:
        try:
            importlib.import_module(module_name)
        except ImportError:
            # Optional/feature modules may not be present in all environments.
            pass

    # Import the core models after dependencies so any relationship targets exist.
    from app.core import models as _models  # noqa: F401

    return True
