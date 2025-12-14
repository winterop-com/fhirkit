"""Terminology API application factory.

Creates and configures the FastAPI application for the terminology service.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..service import InMemoryTerminologyService, TerminologyService
from .routes import router, set_service


def create_app(
    service: TerminologyService | None = None,
    value_set_directory: Path | str | None = None,
    title: str = "FHIR Terminology Service",
    version: str = "1.0.0",
    cors_origins: list[str] | None = None,
) -> FastAPI:
    """Create and configure the terminology service FastAPI application.

    Args:
        service: Optional pre-configured terminology service.
                If not provided, creates an InMemoryTerminologyService.
        value_set_directory: Optional directory to load value sets from.
        title: API title for OpenAPI docs.
        version: API version for OpenAPI docs.
        cors_origins: Optional list of CORS allowed origins.

    Returns:
        Configured FastAPI application.

    Example:
        # Create app with default in-memory service
        app = create_app()

        # Create app with value sets from directory
        app = create_app(value_set_directory="/path/to/valuesets")

        # Create app with custom service
        service = FHIRTerminologyService("https://tx.fhir.org/r4")
        app = create_app(service=service)
    """
    app = FastAPI(
        title=title,
        description="""
FHIR Terminology Service providing CQL/FHIRPath terminology operations.

## Operations

### ValueSet Operations
- **$validate-code**: Validate a code against a value set
- **memberOf**: Check if a code is in a value set

### CodeSystem Operations
- **$subsumes**: Test subsumption relationship between codes

## Usage

This service can be used standalone or integrated with CQL evaluation
to provide terminology validation for clinical decision support.
        """,
        version=version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware if origins specified
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Initialize service
    if service is None:
        service = InMemoryTerminologyService()
        # Load value sets if directory provided
        if value_set_directory:
            count = service.load_value_sets_from_directory(Path(value_set_directory))
            app.state.value_sets_loaded = count

    # Set the global service instance
    set_service(service)
    app.state.terminology_service = service

    # Include routes
    app.include_router(router, prefix="/terminology")

    # Health check endpoint
    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        """Check service health."""
        return {"status": "healthy"}

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        """Root endpoint with service info."""
        return {
            "service": title,
            "version": version,
            "docs": "/docs",
            "terminology": "/terminology",
        }

    return app


def run_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    value_set_directory: Path | str | None = None,
    reload: bool = False,
) -> None:
    """Run the terminology server.

    Args:
        host: Host to bind to.
        port: Port to listen on.
        value_set_directory: Optional directory to load value sets from.
        reload: Enable auto-reload for development.
    """
    import uvicorn

    app = create_app(value_set_directory=value_set_directory)
    uvicorn.run(app, host=host, port=port, reload=reload)
