"""FastAPI application factory for FHIR server."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
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

    # Determine docs URLs based on settings
    api_base = settings.api_base_path.rstrip("/")
    docs_url = f"{api_base}/docs" if settings.enable_docs else None
    redoc_url = f"{api_base}/redoc" if settings.enable_docs else None
    openapi_url = f"{api_base}/openapi.json" if settings.enable_docs else None

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
