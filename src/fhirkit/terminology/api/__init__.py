"""Terminology API module.

Provides FastAPI-based REST API for terminology operations.
"""

from .app import create_app
from .routes import router

__all__ = ["create_app", "router"]
