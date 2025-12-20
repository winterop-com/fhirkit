"""MolecularSequence resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class MolecularSequenceGenerator(FHIRResourceGenerator):
    """Generator for FHIR MolecularSequence resources."""

    SEQUENCE_TYPES = ["aa", "dna", "rna"]

    CHROMOSOME_CODES = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "X",
        "Y",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        sequence_id: str | None = None,
        sequence_type: str | None = None,
        coordinate_system: int = 0,
        patient_reference: str | None = None,
        specimen_reference: str | None = None,
        observed_seq: str | None = None,
        reference_seq: dict[str, Any] | None = None,
        variant: list[dict[str, Any]] | None = None,
        quality: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MolecularSequence resource.

        Args:
            sequence_id: Resource ID (generates UUID if None)
            sequence_type: Type of sequence (aa, dna, rna)
            coordinate_system: Coordinate system (0 or 1)
            patient_reference: Reference to Patient
            specimen_reference: Reference to Specimen
            observed_seq: Observed sequence string
            reference_seq: Reference sequence details
            variant: Variant information
            quality: Quality scores

        Returns:
            MolecularSequence FHIR resource
        """
        if sequence_id is None:
            sequence_id = self._generate_id()

        if sequence_type is None:
            sequence_type = self.faker.random_element(self.SEQUENCE_TYPES)

        molecular_sequence: dict[str, Any] = {
            "resourceType": "MolecularSequence",
            "id": sequence_id,
            "meta": self._generate_meta(),
            "type": sequence_type,
            "coordinateSystem": coordinate_system,
        }

        # Add identifier
        molecular_sequence["identifier"] = [
            {
                "system": "http://example.org/molecular-sequences",
                "value": f"SEQ-{self.faker.random_number(digits=8, fix_len=True)}",
            }
        ]

        # Add patient reference
        if patient_reference:
            molecular_sequence["patient"] = {"reference": patient_reference}
        else:
            molecular_sequence["patient"] = {"reference": f"Patient/{self._generate_id()}"}

        # Add specimen reference
        if specimen_reference:
            molecular_sequence["specimen"] = {"reference": specimen_reference}

        # Add reference sequence
        if reference_seq:
            molecular_sequence["referenceSeq"] = reference_seq
        else:
            molecular_sequence["referenceSeq"] = self._generate_reference_seq(sequence_type)

        # Add observed sequence
        if observed_seq:
            molecular_sequence["observedSeq"] = observed_seq
        else:
            molecular_sequence["observedSeq"] = self._generate_sequence(sequence_type)

        # Add variant
        if variant:
            molecular_sequence["variant"] = variant
        elif self.faker.boolean(chance_of_getting_true=60):
            molecular_sequence["variant"] = self._generate_variants()

        # Add quality
        if quality:
            molecular_sequence["quality"] = quality
        elif self.faker.boolean(chance_of_getting_true=50):
            molecular_sequence["quality"] = self._generate_quality()

        return molecular_sequence

    def _generate_sequence(self, seq_type: str, length: int = 50) -> str:
        """Generate a random sequence string."""
        if seq_type == "aa":
            chars = "ACDEFGHIKLMNPQRSTVWY"
        elif seq_type == "dna":
            chars = "ACGT"
        else:  # rna
            chars = "ACGU"

        return "".join(self.faker.random_element(chars) for _ in range(length))

    def _generate_reference_seq(self, seq_type: str) -> dict[str, Any]:
        """Generate reference sequence information."""
        ref_seq: dict[str, Any] = {
            "windowStart": self.faker.random_int(1, 1000),
            "windowEnd": self.faker.random_int(1001, 2000),
        }

        if seq_type == "dna":
            chromosome = self.faker.random_element(self.CHROMOSOME_CODES)
            ref_seq["chromosome"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/chromosome-human",
                        "code": chromosome,
                        "display": f"chromosome {chromosome}",
                    }
                ]
            }
            ref_seq["genomeBuild"] = "GRCh38"

        return ref_seq

    def _generate_variants(self) -> list[dict[str, Any]]:
        """Generate variant information."""
        start = self.faker.random_int(100, 500)
        return [
            {
                "start": start,
                "end": start + 1,
                "observedAllele": self.faker.random_element(["A", "C", "G", "T"]),
                "referenceAllele": self.faker.random_element(["A", "C", "G", "T"]),
            }
        ]

    def _generate_quality(self) -> list[dict[str, Any]]:
        """Generate quality information."""
        return [
            {
                "type": "snp",
                "standardSequence": {
                    "coding": [
                        {
                            "system": "https://precision.fda.gov/files/",
                            "code": "file-Bk50V4Q0qVb65P0v2VPbfYPZ",
                        }
                    ]
                },
                "start": self.faker.random_int(1, 100),
                "end": self.faker.random_int(101, 200),
                "score": {"value": round(self.faker.pyfloat(min_value=0.9, max_value=1.0), 3)},
                "truthTP": float(self.faker.random_int(90, 100)),
                "queryTP": float(self.faker.random_int(90, 100)),
                "truthFN": float(self.faker.random_int(0, 10)),
                "queryFP": float(self.faker.random_int(0, 10)),
            }
        ]

    def generate_for_patient(
        self,
        patient_id: str,
        sequence_type: str = "dna",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MolecularSequence for a specific patient.

        Args:
            patient_id: Patient ID
            sequence_type: Type of sequence

        Returns:
            MolecularSequence FHIR resource
        """
        return self.generate(
            patient_reference=f"Patient/{patient_id}",
            sequence_type=sequence_type,
            **kwargs,
        )
