"""Terminology API routes.

Provides FastAPI routes for FHIR terminology operations:
- POST /ValueSet/$validate-code
- POST /CodeSystem/$subsumes
- GET /memberOf
- GET /ValueSet/{id}
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from ..models import (
    MemberOfRequest,
    MemberOfResponse,
    SubsumesRequest,
    SubsumesResponse,
    ValidateCodeRequest,
    ValidateCodeResponse,
    ValueSet,
)
from ..service import InMemoryTerminologyService, TerminologyService

router = APIRouter(tags=["terminology"])

# Global service instance (set by app factory)
_service: TerminologyService | None = None


def get_service() -> TerminologyService:
    """Dependency to get the terminology service."""
    if _service is None:
        raise HTTPException(status_code=500, detail="Terminology service not initialized")
    return _service


def set_service(service: TerminologyService) -> None:
    """Set the global terminology service instance."""
    global _service
    _service = service


@router.post(
    "/ValueSet/$validate-code",
    response_model=ValidateCodeResponse,
    summary="Validate a code against a value set",
    description="Validate that a coded value is in the set of codes allowed by a value set.",
)
async def validate_code(
    request: ValidateCodeRequest,
    service: TerminologyService = Depends(get_service),
) -> ValidateCodeResponse:
    """Validate a code against a value set.

    This operation validates a code against a value set. The operation
    can be used to:
    - Test if a given code/display is valid against a value set
    - Validate a coding element
    - Validate a CodeableConcept
    """
    try:
        return service.validate_code(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/ValueSet/$validate-code",
    response_model=ValidateCodeResponse,
    summary="Validate a code (GET)",
    description="Validate that a coded value is in the set of codes allowed by a value set.",
)
async def validate_code_get(
    url: str = Query(..., description="The value set URL"),
    code: str = Query(..., description="The code to validate"),
    system: str | None = Query(None, description="The code system"),
    display: str | None = Query(None, description="The display value"),
    service: TerminologyService = Depends(get_service),
) -> ValidateCodeResponse:
    """Validate a code against a value set using GET parameters."""
    request = ValidateCodeRequest(url=url, code=code, system=system, display=display)
    try:
        return service.validate_code(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/CodeSystem/$subsumes",
    response_model=SubsumesResponse,
    summary="Test subsumption between codes",
    description="Test whether code A subsumes code B in a given code system.",
)
async def subsumes(
    request: SubsumesRequest,
    service: TerminologyService = Depends(get_service),
) -> SubsumesResponse:
    """Test the subsumption relationship between two codes.

    Returns one of:
    - equivalent: A and B are equivalent
    - subsumes: A subsumes B (A is broader than B)
    - subsumed-by: A is subsumed by B (A is narrower than B)
    - not-subsumed: A and B are not related
    """
    try:
        return service.subsumes(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/CodeSystem/$subsumes",
    response_model=SubsumesResponse,
    summary="Test subsumption (GET)",
    description="Test whether code A subsumes code B using GET parameters.",
)
async def subsumes_get(
    codeA: str = Query(..., description="Code A"),
    codeB: str = Query(..., description="Code B"),
    system: str = Query(..., description="Code system URL"),
    version: str | None = Query(None, description="Code system version"),
    service: TerminologyService = Depends(get_service),
) -> SubsumesResponse:
    """Test subsumption using GET parameters."""
    request = SubsumesRequest(codeA=codeA, codeB=codeB, system=system, version=version)
    try:
        return service.subsumes(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/memberOf",
    response_model=MemberOfResponse,
    summary="Check value set membership",
    description="Check if a code is a member of a value set.",
)
async def member_of(
    code: str = Query(..., description="The code to check"),
    system: str = Query(..., description="The code system"),
    valueSetUrl: str = Query(..., alias="valueset", description="The value set URL"),
    version: str | None = Query(None, description="Code version"),
    service: TerminologyService = Depends(get_service),
) -> MemberOfResponse:
    """Check if a code is a member of a value set.

    This is a convenience operation that wraps $validate-code
    to provide a simple membership check.
    """
    request = MemberOfRequest(
        code=code,
        system=system,
        valueSetUrl=valueSetUrl,
        version=version,
    )
    try:
        return service.member_of(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/ValueSet",
    response_model=ValueSet | None,
    summary="Get a value set",
    description="Retrieve a value set by URL.",
)
async def get_value_set(
    url: str = Query(..., description="The value set URL"),
    version: str | None = Query(None, description="Value set version"),
    service: TerminologyService = Depends(get_service),
) -> ValueSet | None:
    """Get a value set by its canonical URL."""
    result = service.get_value_set(url, version)
    if result is None:
        raise HTTPException(status_code=404, detail=f"ValueSet not found: {url}")
    return result


@router.get(
    "/ValueSet/{value_set_id}",
    response_model=ValueSet | None,
    summary="Get a value set by ID",
    description="Retrieve a value set by its resource ID.",
)
async def get_value_set_by_id(
    value_set_id: str,
    service: TerminologyService = Depends(get_service),
) -> ValueSet | None:
    """Get a value set by its resource ID.

    Note: This searches through loaded value sets for a matching ID.
    """
    # For in-memory service, we search by ID
    if isinstance(service, InMemoryTerminologyService):
        for vs in service._value_sets.values():
            if vs.id == value_set_id:
                return vs
    raise HTTPException(status_code=404, detail=f"ValueSet not found: {value_set_id}")
