"""FastAPI application factory for FHIR server."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..config.settings import FHIRServerSettings
from ..generator import PatientRecordGenerator
from ..storage.fhir_store import FHIRStore
from .routes import create_router
from .ui_routes import create_ui_router

logger = logging.getLogger(__name__)

# Template and static directories
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
STATIC_DIR = Path(__file__).parent.parent / "static"


def create_app(
    settings: FHIRServerSettings | None = None,
    store: FHIRStore | None = None,
) -> FastAPI:
    """Create and configure the FHIR server FastAPI application.

    Args:
        settings: Server settings (uses defaults if None)
        store: FHIR data store (creates new if None)

    Returns:
        Configured FastAPI application
    """
    if settings is None:
        settings = FHIRServerSettings()

    if store is None:
        store = FHIRStore()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan handler."""
        # Startup
        logger.info("Starting FHIR server...")

        # Generate synthetic data if requested
        if settings.patients > 0:
            logger.info(f"Generating {settings.patients} synthetic patients...")
            generator = PatientRecordGenerator(seed=settings.seed)
            resources = generator.generate_population(settings.patients)

            for resource in resources:
                store.create(resource)

            logger.info(f"Generated {len(resources)} resources for {settings.patients} patients")

        # Store references in app state
        app.state.store = store
        app.state.settings = settings

        yield

        # Shutdown
        logger.info("Shutting down FHIR server...")

    # Determine docs URLs based on settings (docs at root, not under FHIR base path)
    api_base = settings.api_base_path.rstrip("/")
    docs_url = "/docs" if settings.enable_docs else None
    redoc_url = "/redoc" if settings.enable_docs else None
    openapi_url = "/openapi.json" if settings.enable_docs else None

    app = FastAPI(
        title=settings.server_name,
        description="FHIR R4 REST Server with synthetic data generation and Web UI",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    # Add CORS middleware
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Create and include FHIR API router at /baseR4
    base_url = f"http://{settings.host}:{settings.port}{api_base}"
    fhir_router = create_router(store=store, base_url=base_url)
    app.include_router(fhir_router, prefix=api_base)

    # CDS Hooks endpoints (per HL7 CDS Hooks specification)
    # NOTE: Must be defined BEFORE UI router to avoid being caught by /{resource_type}
    @app.get("/cds-services", tags=["CDS Hooks"])
    async def cds_services_discovery() -> dict[str, Any]:
        """CDS Hooks discovery endpoint.

        Returns the list of CDS services available on this server.
        """
        return {
            "services": [
                {
                    "hook": "patient-view",
                    "title": "Patient Summary",
                    "description": "Provides a summary of patient data when viewing a patient record",
                    "id": "patient-summary",
                    "prefetch": {
                        "patient": "Patient/{{context.patientId}}",
                        "conditions": "Condition?patient={{context.patientId}}&clinical-status=active",
                        "medications": "MedicationRequest?patient={{context.patientId}}&status=active",
                    },
                },
                {
                    "hook": "order-select",
                    "title": "Drug Interaction Check",
                    "description": "Checks for potential drug interactions when selecting medications",
                    "id": "drug-interaction-check",
                    "prefetch": {
                        "patient": "Patient/{{context.patientId}}",
                        "medications": "MedicationRequest?patient={{context.patientId}}&status=active",
                    },
                },
            ]
        }

    @app.post("/cds-services/{service_id}", tags=["CDS Hooks"])
    async def cds_services_invoke(service_id: str, request: Request) -> dict[str, Any]:
        """Invoke a CDS Hook service.

        Args:
            service_id: The ID of the CDS service to invoke
            request: The CDS Hooks request containing hook context and prefetch data
        """
        body = await request.json()

        # Simple mock implementation for demo purposes
        cards = []

        if service_id == "patient-summary":
            # Generate a summary card based on prefetch data
            patient = body.get("prefetch", {}).get("patient", {})
            patient_name = "Unknown"
            if patient.get("name"):
                name = patient["name"][0] if patient["name"] else {}
                given = " ".join(name.get("given", []))
                family = name.get("family", "")
                patient_name = f"{given} {family}".strip()

            cards.append(
                {
                    "uuid": "patient-summary-card",
                    "summary": f"Patient Summary: {patient_name}",
                    "indicator": "info",
                    "detail": (
                        "This is a demo CDS Hooks response. In production, "
                        "this would provide clinical decision support based on patient data."
                    ),
                    "source": {
                        "label": "FHIR CQL Server",
                        "url": f"http://{settings.host}:{settings.port}",
                    },
                }
            )

        elif service_id == "drug-interaction-check":
            cards.append(
                {
                    "uuid": "drug-check-card",
                    "summary": "No drug interactions detected",
                    "indicator": "info",
                    "detail": ("This is a demo response. In production, actual drug interaction checking would occur."),
                    "source": {
                        "label": "FHIR CQL Server",
                    },
                }
            )

        else:
            return {"cards": [], "systemActions": []}

        return {"cards": cards, "systemActions": []}

    # Setup Web UI if enabled
    if settings.enable_ui:
        # Setup Jinja2 templates
        templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

        # Mount static files if directory exists
        if STATIC_DIR.exists():
            app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

        # Create and include UI router
        ui_router = create_ui_router(
            templates=templates,
            store=store,
            settings=settings,
        )

        # Mount UI at root or specified path
        ui_prefix = settings.ui_mount_path if settings.ui_mount_path else ""
        app.include_router(ui_router, prefix=ui_prefix)

        logger.info(f"Web UI enabled at {ui_prefix or '/'}")

    # API info endpoint (always at /api-info for discoverability)
    @app.get("/api-info", tags=["Info"])
    async def api_info() -> dict[str, Any]:
        """API information endpoint."""
        return {
            "name": settings.server_name,
            "fhirVersion": "4.0.1",
            "status": "running",
            "endpoints": {
                "fhir_api": api_base,
                "metadata": f"{api_base}/metadata",
                "docs": docs_url,
                "ui": settings.ui_mount_path or "/" if settings.enable_ui else None,
                "cds_hooks": "/cds-services",
            },
        }

    return app


def run_server(
    settings: FHIRServerSettings | None = None,
    store: FHIRStore | None = None,
) -> None:
    """Run the FHIR server with uvicorn.

    Args:
        settings: Server settings
        store: Optional pre-configured store
    """
    import uvicorn

    if settings is None:
        settings = FHIRServerSettings()

    app = create_app(settings=settings, store=store)

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
