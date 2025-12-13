"""CDS Hooks FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config.settings import CDSHooksSettings
from ..service.card_builder import CardBuilder
from ..service.executor import CDSExecutor
from ..service.registry import ServiceRegistry
from .routes import create_router


def create_app(settings: CDSHooksSettings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Optional settings override

    Returns:
        Configured FastAPI application
    """
    if settings is None:
        settings = CDSHooksSettings()

    app = FastAPI(
        title="CDS Hooks Service",
        description="CQL-based Clinical Decision Support Hooks",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )

    # Initialize services
    registry = ServiceRegistry(settings)
    executor = CDSExecutor(settings)
    card_builder = CardBuilder()

    # Store in app state for dependency injection
    app.state.settings = settings
    app.state.registry = registry
    app.state.executor = executor
    app.state.card_builder = card_builder

    # Include routes
    router = create_router()
    app.include_router(router, prefix=settings.base_path)

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app
