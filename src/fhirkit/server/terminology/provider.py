"""Abstract terminology provider interface."""

from abc import ABC, abstractmethod
from typing import Any


class TerminologyProvider(ABC):
    """Abstract interface for terminology operations.

    Implementations provide terminology services using different backends
    (e.g., FHIRStore, remote FHIR server).
    """

    @abstractmethod
    def expand_valueset(
        self,
        url: str | None = None,
        valueset_id: str | None = None,
        filter_text: str | None = None,
        count: int = 100,
        offset: int = 0,
    ) -> dict[str, Any] | None:
        """Expand a ValueSet to list all codes.

        Args:
            url: ValueSet URL (canonical identifier)
            valueset_id: ValueSet resource ID
            filter_text: Filter to apply to code/display
            count: Maximum number of codes to return
            offset: Offset for pagination

        Returns:
            Expanded ValueSet resource with expansion element, or None if not found
        """

    @abstractmethod
    def validate_code(
        self,
        valueset_url: str | None = None,
        valueset_id: str | None = None,
        code: str | None = None,
        system: str | None = None,
        coding: dict[str, Any] | None = None,
        codeable_concept: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Validate a code against a ValueSet.

        Args:
            valueset_url: ValueSet URL
            valueset_id: ValueSet resource ID
            code: Code value to validate
            system: Code system URI
            coding: FHIR Coding object
            codeable_concept: FHIR CodeableConcept object

        Returns:
            Parameters resource with result (boolean) and optional display/message
        """

    @abstractmethod
    def lookup_code(
        self,
        system: str,
        code: str,
        version: str | None = None,
    ) -> dict[str, Any] | None:
        """Look up code information from a CodeSystem.

        Args:
            system: CodeSystem URL
            code: Code value
            version: Optional CodeSystem version

        Returns:
            Parameters resource with code details, or None if not found
        """

    @abstractmethod
    def subsumes(
        self,
        system: str,
        code_a: str,
        code_b: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """Check subsumption relationship between two codes.

        Args:
            system: CodeSystem URL
            code_a: First code (potential parent/ancestor)
            code_b: Second code (potential child/descendant)
            version: Optional CodeSystem version

        Returns:
            Parameters resource with outcome:
            - equivalent: codes are the same
            - subsumes: code_a subsumes code_b (code_a is ancestor)
            - subsumed-by: code_a is subsumed by code_b (code_b is ancestor)
            - not-subsumed: no hierarchical relationship
        """

    @abstractmethod
    def member_of(
        self,
        valueset_url: str,
        code: str,
        system: str,
    ) -> bool:
        """Check if code is a member of a ValueSet.

        Args:
            valueset_url: ValueSet URL
            code: Code value
            system: Code system URI

        Returns:
            True if code is in the ValueSet, False otherwise
        """
