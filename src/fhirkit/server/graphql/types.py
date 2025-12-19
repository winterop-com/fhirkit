"""GraphQL types for FHIR resources.

This module defines the GraphQL types used in the FHIR GraphQL API.
Types are designed to be flexible using JSON scalars while still providing
type safety for common fields.
"""

import base64
from typing import TYPE_CHECKING, Any, Optional

import strawberry
from strawberry.scalars import JSON

if TYPE_CHECKING:
    from ..storage.fhir_store import FHIRStore


# =============================================================================
# Custom Scalars
# =============================================================================


@strawberry.scalar(
    description="FHIR instant type (timestamp with timezone)",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
class FHIRInstant(str):
    """FHIR instant scalar for precise timestamps."""

    pass


@strawberry.scalar(
    description="FHIR date type (YYYY, YYYY-MM, or YYYY-MM-DD)",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
class FHIRDate(str):
    """FHIR date scalar."""

    pass


@strawberry.scalar(
    description="FHIR dateTime type",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
class FHIRDateTime(str):
    """FHIR dateTime scalar."""

    pass


@strawberry.scalar(
    description="FHIR URI type",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
class FHIRURI(str):
    """FHIR URI scalar."""

    pass


# =============================================================================
# FHIR Data Types (Partial typing for common fields)
# =============================================================================


@strawberry.type(description="A reference to another FHIR resource")
class Reference:
    """FHIR Reference type with optional inline resolution."""

    reference: Optional[str] = strawberry.field(default=None, description="Literal reference (e.g., 'Patient/123')")
    type: Optional[str] = strawberry.field(default=None, description="Type of the referenced resource")
    display: Optional[str] = strawberry.field(default=None, description="Display text for the reference")

    # Private field for store access
    _store: strawberry.Private[Optional["FHIRStore"]] = None

    @strawberry.field(description="Resolve this reference to its target resource")
    def resource(
        self,
        info: strawberry.Info,
        optional: bool = False,
    ) -> Optional[JSON]:
        """Resolve reference to the actual resource.

        This implements the FHIR GraphQL reference resolution pattern where
        clients can request inline resolution of references.

        Args:
            info: Strawberry info context
            optional: If true, return None for unresolvable refs instead of error

        Returns:
            The resolved resource as JSON, or None if not found and optional=True
        """
        if not self.reference:
            return None

        store = info.context.get("store")
        if not store:
            if optional:
                return None
            raise ValueError("Store not available in context")

        # Parse reference string (e.g., "Patient/123" or just "123")
        if "/" in self.reference:
            ref_type, ref_id = self.reference.split("/", 1)
        else:
            # If no type in reference, use the type field
            ref_type = self.type
            ref_id = self.reference

        if not ref_type:
            if optional:
                return None
            raise ValueError(f"Cannot determine resource type for reference: {self.reference}")

        resource = store.read(ref_type, ref_id)

        if resource is None and not optional:
            raise ValueError(f"Reference not found: {self.reference}")

        return resource


@strawberry.type(description="A human name")
class HumanName:
    """FHIR HumanName type."""

    use: Optional[str] = None
    text: Optional[str] = None
    family: Optional[str] = None
    given: Optional[list[str]] = None
    prefix: Optional[list[str]] = None
    suffix: Optional[list[str]] = None


@strawberry.type(description="Contact point (phone, email, etc.)")
class ContactPoint:
    """FHIR ContactPoint type."""

    system: Optional[str] = None
    value: Optional[str] = None
    use: Optional[str] = None
    rank: Optional[int] = None


@strawberry.type(description="Physical address")
class Address:
    """FHIR Address type."""

    use: Optional[str] = None
    type: Optional[str] = None
    text: Optional[str] = None
    line: Optional[list[str]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None


@strawberry.type(description="Coding from a terminology system")
class Coding:
    """FHIR Coding type."""

    system: Optional[str] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    userSelected: Optional[bool] = None


@strawberry.type(description="Concept with coding and text")
class CodeableConcept:
    """FHIR CodeableConcept type."""

    coding: Optional[list[Coding]] = None
    text: Optional[str] = None


@strawberry.type(description="An identifier for a resource")
class Identifier:
    """FHIR Identifier type."""

    use: Optional[str] = None
    type: Optional[CodeableConcept] = None
    system: Optional[str] = None
    value: Optional[str] = None


@strawberry.type(description="Resource metadata")
class Meta:
    """FHIR Meta type for resource metadata."""

    versionId: Optional[str] = None
    lastUpdated: Optional[str] = None
    source: Optional[str] = None
    profile: Optional[list[str]] = None
    tag: Optional[list[Coding]] = None


@strawberry.type(description="Time period")
class Period:
    """FHIR Period type."""

    start: Optional[str] = None
    end: Optional[str] = None


@strawberry.type(description="Quantity with value and unit")
class Quantity:
    """FHIR Quantity type."""

    value: Optional[float] = None
    comparator: Optional[str] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None


# =============================================================================
# Generic Resource Type
# =============================================================================


@strawberry.type(description="A FHIR resource with all fields as JSON")
class Resource:
    """Generic FHIR resource type.

    This type provides a flexible representation of any FHIR resource,
    with common fields typed and the full resource available as JSON.
    """

    resourceType: str = strawberry.field(description="The type of resource (e.g., 'Patient')")
    id: Optional[str] = strawberry.field(default=None, description="Logical id of the resource")
    meta: Optional[Meta] = strawberry.field(default=None, description="Resource metadata")

    # Store the raw data for JSON access
    _raw_data: strawberry.Private[dict[str, Any]]

    @strawberry.field(description="Full resource as JSON")
    def data(self) -> JSON:
        """Return the full resource as JSON."""
        return self._raw_data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Resource":
        """Create a Resource from a dictionary.

        Args:
            data: FHIR resource as dictionary

        Returns:
            Resource instance
        """
        meta_data = data.get("meta")
        meta = None
        if meta_data:
            meta = Meta(
                versionId=meta_data.get("versionId"),
                lastUpdated=meta_data.get("lastUpdated"),
                source=meta_data.get("source"),
                profile=meta_data.get("profile"),
                tag=[
                    Coding(
                        system=t.get("system"),
                        code=t.get("code"),
                        display=t.get("display"),
                    )
                    for t in meta_data.get("tag", [])
                ]
                if meta_data.get("tag")
                else None,
            )

        return cls(
            resourceType=data.get("resourceType", "Unknown"),
            id=data.get("id"),
            meta=meta,
            _raw_data=data,
        )


# =============================================================================
# Connection/Pagination Types (per FHIR GraphQL spec)
# =============================================================================


@strawberry.type(description="Information about the current page of results")
class PageInfo:
    """GraphQL Connection PageInfo type."""

    hasNextPage: bool = strawberry.field(description="Whether there are more results after this page")
    hasPreviousPage: bool = strawberry.field(description="Whether there are results before this page")
    startCursor: Optional[str] = strawberry.field(default=None, description="Cursor for the first item in this page")
    endCursor: Optional[str] = strawberry.field(default=None, description="Cursor for the last item in this page")


@strawberry.type(description="Search result metadata per FHIR spec")
class SearchEntryMode:
    """FHIR search entry mode information."""

    mode: str = strawberry.field(default="match", description="Whether this is a 'match' or 'include' result")
    score: Optional[float] = strawberry.field(default=None, description="Search relevance score")


@strawberry.type(description="An edge in a connection (resource + cursor)")
class ResourceEdge:
    """GraphQL Connection Edge type for FHIR resources."""

    cursor: str = strawberry.field(description="Cursor for this item (for pagination)")
    node: Resource = strawberry.field(description="The resource at this edge")
    search: Optional[SearchEntryMode] = strawberry.field(default=None, description="Search result metadata")


@strawberry.type(description="A paginated connection of FHIR resources")
class ResourceConnection:
    """GraphQL Connection type for paginated FHIR resources.

    Implements the Relay-style connection pattern adapted for FHIR.
    """

    edges: list[ResourceEdge] = strawberry.field(description="List of edges (resources with cursors)")
    pageInfo: PageInfo = strawberry.field(description="Pagination information")
    total: Optional[int] = strawberry.field(
        default=None, description="Total count of matching resources (if available)"
    )


# =============================================================================
# Cursor Utilities
# =============================================================================


def encode_cursor(offset: int) -> str:
    """Encode an offset as a cursor string.

    Args:
        offset: The numeric offset to encode

    Returns:
        Base64-encoded cursor string
    """
    return base64.b64encode(f"offset:{offset}".encode()).decode()


def decode_cursor(cursor: str) -> int:
    """Decode a cursor string to an offset.

    Args:
        cursor: Base64-encoded cursor string

    Returns:
        The decoded offset, or 0 if invalid
    """
    try:
        decoded = base64.b64decode(cursor.encode()).decode()
        if decoded.startswith("offset:"):
            return int(decoded[7:])
    except Exception:
        pass
    return 0


# =============================================================================
# Input Types for Mutations
# =============================================================================


@strawberry.input(description="Input for creating or updating a FHIR resource")
class ResourceInput:
    """Generic input type for FHIR resource mutations.

    Since FHIR resources have varying structures, we accept the full
    resource as JSON and validate server-side.
    """

    resourceType: str = strawberry.field(description="The type of resource")
    data: JSON = strawberry.field(description="Full resource data as JSON")


# =============================================================================
# Helper Functions
# =============================================================================


def dict_to_reference(data: dict[str, Any] | None) -> Reference | None:
    """Convert a dictionary to a Reference type.

    Args:
        data: Reference data as dictionary

    Returns:
        Reference instance or None
    """
    if not data:
        return None
    return Reference(
        reference=data.get("reference"),
        type=data.get("type"),
        display=data.get("display"),
    )


def dict_to_codeable_concept(data: dict[str, Any] | None) -> CodeableConcept | None:
    """Convert a dictionary to a CodeableConcept type.

    Args:
        data: CodeableConcept data as dictionary

    Returns:
        CodeableConcept instance or None
    """
    if not data:
        return None
    coding = None
    if data.get("coding"):
        coding = [
            Coding(
                system=c.get("system"),
                version=c.get("version"),
                code=c.get("code"),
                display=c.get("display"),
                userSelected=c.get("userSelected"),
            )
            for c in data["coding"]
        ]
    return CodeableConcept(coding=coding, text=data.get("text"))
