"""SubstanceProtein resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SubstanceProteinGenerator(FHIRResourceGenerator):
    """Generator for FHIR SubstanceProtein resources."""

    SEQUENCE_TYPES = [
        {
            "system": "http://hl7.org/fhir/substance-protein-type",
            "code": "UniProtKB",
            "display": "UniProtKB protein",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        protein_id: str | None = None,
        sequence_type: dict[str, Any] | None = None,
        number_of_subunits: int | None = None,
        disulfide_linkage: list[str] | None = None,
        subunit: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SubstanceProtein resource.

        Args:
            protein_id: Resource ID (generates UUID if None)
            sequence_type: Type of protein sequence
            number_of_subunits: Number of subunits
            disulfide_linkage: Disulfide linkage information
            subunit: Subunit details

        Returns:
            SubstanceProtein FHIR resource
        """
        if protein_id is None:
            protein_id = self._generate_id()

        substance_protein: dict[str, Any] = {
            "resourceType": "SubstanceProtein",
            "id": protein_id,
            "meta": self._generate_meta(),
        }

        # Add sequence type
        if sequence_type:
            substance_protein["sequenceType"] = sequence_type
        else:
            seq_type = self.faker.random_element(self.SEQUENCE_TYPES)
            substance_protein["sequenceType"] = {
                "coding": [seq_type],
                "text": seq_type["display"],
            }

        # Add number of subunits
        if number_of_subunits:
            substance_protein["numberOfSubunits"] = number_of_subunits
        else:
            substance_protein["numberOfSubunits"] = self.faker.random_int(1, 4)

        # Add disulfide linkage
        if disulfide_linkage:
            substance_protein["disulfideLinkage"] = disulfide_linkage

        # Add subunit
        if subunit:
            substance_protein["subunit"] = subunit
        else:
            substance_protein["subunit"] = self._generate_subunits()

        return substance_protein

    def _generate_subunits(self) -> list[dict[str, Any]]:
        """Generate subunit information."""
        subunits = []
        num_subunits = self.faker.random_int(1, 2)

        for i in range(num_subunits):
            # Generate a random amino acid sequence
            amino_acids = list("ACDEFGHIKLMNPQRSTVWY")
            sequence = "".join(self.faker.random_elements(amino_acids, length=30))

            subunits.append(
                {
                    "subunit": i + 1,
                    "sequence": sequence,
                    "length": len(sequence),
                }
            )

        return subunits
