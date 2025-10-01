"""Shared declarative base for listings domain models."""

from app.core import models as core_models

# Reuse the application's core declarative base to ensure unified metadata
Base = core_models.Base

__all__ = ["Base"]
