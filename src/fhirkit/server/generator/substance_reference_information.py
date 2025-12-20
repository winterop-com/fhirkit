"""SubstanceReferenceInformation resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SubstanceReferenceInformationGenerator(FHIRResourceGenerator):
    """Generator for FHIR SubstanceReferenceInformation resources."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        reference_info_id: str | None = None,
        comment: str | None = None,
        gene: list[dict[str, Any]] | None = None,
        gene_element: list[dict[str, Any]] | None = None,
        classification: list[dict[str, Any]] | None = None,
        target: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SubstanceReferenceInformation resource.

        Args:
            reference_info_id: Resource ID (generates UUID if None)
            comment: General comment
            gene: Gene information
            gene_element: Gene element information
            classification: Classification information
            target: Target information

        Returns:
            SubstanceReferenceInformation FHIR resource
        """
        if reference_info_id is None:
            reference_info_id = self._generate_id()

        substance_ref_info: dict[str, Any] = {
            "resourceType": "SubstanceReferenceInformation",
            "id": reference_info_id,
            "meta": self._generate_meta(),
        }

        # Add comment
        if comment:
            substance_ref_info["comment"] = comment
        else:
            substance_ref_info["comment"] = f"Reference information for substance: {self.faker.word()}"

        # Add gene if provided
        if gene:
            substance_ref_info["gene"] = gene

        # Add gene element if provided
        if gene_element:
            substance_ref_info["geneElement"] = gene_element

        # Add classification if provided
        if classification:
            substance_ref_info["classification"] = classification

        # Add target if provided
        if target:
            substance_ref_info["target"] = target

        return substance_ref_info
