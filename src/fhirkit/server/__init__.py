"""FHIR Server with synthetic data generation.

This module provides a simple FHIR R4 REST server with:
- Full CRUD operations (GET/POST/PUT/DELETE)
- FHIR search parameters
- Faker-based synthetic data generation
- Preload capabilities for CQL libraries and ValueSets
"""

from .api.app import create_app, run_server
from .config.settings import FHIRServerSettings
from .generator import PatientRecordGenerator
from .storage.fhir_store import FHIRStore

__all__ = [
    "create_app",
    "run_server",
    "FHIRServerSettings",
    "FHIRStore",
    "PatientRecordGenerator",
]
