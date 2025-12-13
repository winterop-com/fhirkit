"""CDS Hooks discovery endpoint models."""

from pydantic import BaseModel, Field


class CDSServiceDescriptor(BaseModel):
    """CDS Service descriptor returned in discovery response.

    See: https://cds-hooks.hl7.org/2.0/#discovery
    """

    hook: str = Field(
        ...,
        description="The hook this service should be invoked on",
    )
    id: str = Field(
        ...,
        description="Unique identifier for this CDS Service",
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    title: str | None = Field(
        None,
        description="Human-readable title for the service",
    )
    description: str = Field(
        ...,
        description="Description of the service",
    )
    prefetch: dict[str, str] | None = Field(
        None,
        description="Prefetch templates for required data",
    )
    usageRequirements: str | None = Field(
        None,
        description="Human-readable description of any requirements",
    )

    model_config = {"populate_by_name": True}


class DiscoveryResponse(BaseModel):
    """Response to GET /cds-services.

    See: https://cds-hooks.hl7.org/2.0/#discovery-response
    """

    services: list[CDSServiceDescriptor] = Field(
        default_factory=list,
        description="Array of CDS Services",
    )
