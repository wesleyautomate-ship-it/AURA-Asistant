"""
Shared database base for all models
"""

from sqlalchemy.ext.declarative import declarative_base

# Shared base for all models
Base = declarative_base()

__all__ = ['Base']

