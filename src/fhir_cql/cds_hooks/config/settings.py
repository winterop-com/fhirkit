"""CDS Hooks configuration settings."""

from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class CardTemplate(BaseModel):
    """Template for generating cards from CQL results."""

    condition: str | None = Field(
        None,
        description="CQL definition that triggers this card (must be truthy)",
    )
    indicator: str = Field(
        "info",
        description="Card indicator: info, warning, critical",
    )
    summary: str = Field(
        ...,
        description="Template for card summary (supports {{variable}} substitution)",
    )
    detail: str | None = Field(
        None,
        description="Template for card detail (markdown, supports {{variable}})",
    )
    source: str = Field(
        ...,
        description="Source label for the card",
    )
    sourceUrl: str | None = Field(None, description="Optional source URL")
    suggestions: list[dict[str, Any]] = Field(default_factory=list)
    links: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class CDSServiceConfig(BaseModel):
    """Configuration for a single CDS service."""

    id: str = Field(..., description="Unique service identifier")
    hook: str = Field(..., description="Hook type (patient-view, order-select, etc.)")
    title: str = Field(..., description="Service title")
    description: str = Field(..., description="Service description")

    # CQL configuration
    cqlLibrary: str = Field(
        ...,
        description="Path to CQL library file",
    )
    evaluateDefinitions: list[str] = Field(
        ...,
        description="CQL definitions to evaluate",
    )

    # Prefetch templates
    prefetch: dict[str, str] = Field(
        default_factory=dict,
        description="Prefetch templates keyed by name",
    )

    # Card generation
    cards: list[CardTemplate] = Field(
        default_factory=list,
        description="Card templates for result conversion",
    )

    # Optional settings
    enabled: bool = True
    usageRequirements: str | None = Field(None)

    model_config = {"populate_by_name": True}


class CDSHooksSettings(BaseSettings):
    """Application settings for CDS Hooks server."""

    host: str = "0.0.0.0"
    port: int = 8080
    base_path: str = "/cds-services"

    # Service configuration
    services_config_path: str = Field(
        "cds_services.yaml",
        description="Path to services configuration file",
    )
    cql_library_path: str = Field(
        "",
        description="Base path for CQL library files (defaults to current dir)",
    )

    # Security
    enable_cors: bool = True
    allowed_origins: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"
    log_requests: bool = True

    # Performance
    max_cards_per_response: int = 10
    evaluation_timeout_seconds: int = 30

    model_config = {
        "env_prefix": "CDS_HOOKS_",
        "env_file": ".env",
    }
