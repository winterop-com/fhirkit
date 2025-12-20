"""SubstanceNucleicAcid resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SubstanceNucleicAcidGenerator(FHIRResourceGenerator):
    """Generator for FHIR SubstanceNucleicAcid resources."""

    SEQUENCE_TYPES = [
        {
            "system": "http://hl7.org/fhir/substance-nucleic-acid-type",
            "code": "DNA",
            "display": "Deoxyribonucleic acid",
        },
        {
            "system": "http://hl7.org/fhir/substance-nucleic-acid-type",
            "code": "RNA",
            "display": "Ribonucleic acid",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        nucleic_acid_id: str | None = None,
        sequence_type: dict[str, Any] | None = None,
        number_of_subunits: int | None = None,
        area_of_hybridisation: str | None = None,
        subunit: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SubstanceNucleicAcid resource.

        Args:
            nucleic_acid_id: Resource ID (generates UUID if None)
            sequence_type: Type of nucleic acid (DNA, RNA)
            number_of_subunits: Number of subunits
            area_of_hybridisation: Area of hybridisation
            subunit: Subunit details

        Returns:
            SubstanceNucleicAcid FHIR resource
        """
        if nucleic_acid_id is None:
            nucleic_acid_id = self._generate_id()

        substance_nucleic_acid: dict[str, Any] = {
            "resourceType": "SubstanceNucleicAcid",
            "id": nucleic_acid_id,
            "meta": self._generate_meta(),
        }

        # Add sequence type
        if sequence_type:
            substance_nucleic_acid["sequenceType"] = sequence_type
        else:
            seq_type = self.faker.random_element(self.SEQUENCE_TYPES)
            substance_nucleic_acid["sequenceType"] = {
                "coding": [seq_type],
                "text": seq_type["display"],
            }

        # Add number of subunits
        if number_of_subunits:
            substance_nucleic_acid["numberOfSubunits"] = number_of_subunits
        else:
            substance_nucleic_acid["numberOfSubunits"] = self.faker.random_int(1, 4)

        # Add area of hybridisation
        if area_of_hybridisation:
            substance_nucleic_acid["areaOfHybridisation"] = area_of_hybridisation

        # Add subunit
        if subunit:
            substance_nucleic_acid["subunit"] = subunit
        else:
            substance_nucleic_acid["subunit"] = self._generate_subunits()

        return substance_nucleic_acid

    def _generate_subunits(self) -> list[dict[str, Any]]:
        """Generate subunit information."""
        subunits = []
        num_subunits = self.faker.random_int(1, 2)

        for i in range(num_subunits):
            # Generate a random nucleotide sequence
            bases = ["A", "T", "G", "C"]
            sequence = "".join(self.faker.random_elements(bases, length=20))

            subunits.append(
                {
                    "subunit": i + 1,
                    "sequence": sequence,
                    "length": len(sequence),
                }
            )

        return subunits
