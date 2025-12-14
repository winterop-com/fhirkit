"""CDS Hooks service request models."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class FHIRAuthorization(BaseModel):
    """OAuth2 authorization details for FHIR server access.

    See: https://cds-hooks.hl7.org/2.0/#fhir-resource-access
    """

    access_token: str = Field(..., alias="access_token")
    token_type: str = Field("Bearer", alias="token_type")
    expires_in: int = Field(..., alias="expires_in")
    scope: str
    subject: str
    patient: str | None = None

    model_config = {"populate_by_name": True}


class CDSRequest(BaseModel):
    """CDS Service request body.

    See: https://cds-hooks.hl7.org/2.0/#http-request_1
    """

    hook: str = Field(..., description="The hook that triggered this request")
    hookInstance: UUID = Field(..., description="UUID identifying this specific hook invocation")
    context: dict[str, Any] = Field(..., description="Hook-specific context data")
    fhirServer: str | None = None
    fhirAuthorization: FHIRAuthorization | None = None
    prefetch: dict[str, Any] | None = None

    model_config = {"populate_by_name": True}
