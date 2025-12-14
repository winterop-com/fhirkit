"""FHIR Terminology Service.

This module provides terminology operations for CQL and FHIRPath:
- Code validation against value sets
- Value set membership checks
- Subsumption testing

Usage:
    # Create in-memory service
    from fhirkit.terminology import InMemoryTerminologyService

    service = InMemoryTerminologyService()
    service.load_value_sets_from_directory("path/to/valuesets")

    # Validate a code
    from fhirkit.terminology import ValidateCodeRequest

    request = ValidateCodeRequest(
        url="http://hl7.org/fhir/ValueSet/observation-status",
        code="final",
        system="http://hl7.org/fhir/observation-status"
    )
    result = service.validate_code(request)
    print(f"Valid: {result.result}")

    # Run FastAPI server
    from fhirkit.terminology.api import create_app

    app = create_app(value_set_directory="path/to/valuesets")
"""

from .models import (
    CodeableConcept,
    Coding,
    MemberOfRequest,
    MemberOfResponse,
    SubsumesRequest,
    SubsumesResponse,
    ValidateCodeRequest,
    ValidateCodeResponse,
    ValueSet,
    ValueSetCompose,
    ValueSetComposeInclude,
    ValueSetComposeIncludeConcept,
    ValueSetExpansion,
    ValueSetExpansionContains,
)
from .service import (
    FHIRTerminologyService,
    InMemoryTerminologyService,
    TerminologyService,
)

__all__ = [
    # Models
    "Coding",
    "CodeableConcept",
    "ValueSet",
    "ValueSetCompose",
    "ValueSetComposeInclude",
    "ValueSetComposeIncludeConcept",
    "ValueSetExpansion",
    "ValueSetExpansionContains",
    "ValidateCodeRequest",
    "ValidateCodeResponse",
    "SubsumesRequest",
    "SubsumesResponse",
    "MemberOfRequest",
    "MemberOfResponse",
    # Services
    "TerminologyService",
    "InMemoryTerminologyService",
    "FHIRTerminologyService",
]
