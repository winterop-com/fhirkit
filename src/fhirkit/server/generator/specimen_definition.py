"""SpecimenDefinition resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SpecimenDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR SpecimenDefinition resources."""

    # Specimen types
    SPECIMEN_TYPES = [
        {
            "system": "http://snomed.info/sct",
            "code": "122555007",
            "display": "Venous blood specimen",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "119361006",
            "display": "Plasma specimen",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "119364003",
            "display": "Serum specimen",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "122575003",
            "display": "Urine specimen",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "119376003",
            "display": "Tissue specimen",
        },
    ]

    # Container types
    CONTAINER_TYPES = [
        {
            "system": "http://snomed.info/sct",
            "code": "706047007",
            "display": "Fecal specimen container",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "702224000",
            "display": "Vacuum blood collection tube",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "434746001",
            "display": "Specimen container",
        },
    ]

    # Container cap colors
    CAP_COLORS = [
        {"system": "urn:iso:std:iso:6710:2017", "code": "red"},
        {"system": "urn:iso:std:iso:6710:2017", "code": "green"},
        {"system": "urn:iso:std:iso:6710:2017", "code": "lavender"},
        {"system": "urn:iso:std:iso:6710:2017", "code": "yellow"},
        {"system": "urn:iso:std:iso:6710:2017", "code": "blue"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        definition_id: str | None = None,
        type_collected: dict[str, Any] | None = None,
        patient_preparation: list[dict[str, Any]] | None = None,
        time_aspect: str | None = None,
        collection: list[dict[str, Any]] | None = None,
        type_tested: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SpecimenDefinition resource.

        Args:
            definition_id: Resource ID (generates UUID if None)
            type_collected: Type of specimen to be collected
            patient_preparation: Patient preparation instructions
            time_aspect: Time aspect for collection
            collection: Collection requirements
            type_tested: Specimen types that can be tested

        Returns:
            SpecimenDefinition FHIR resource
        """
        if definition_id is None:
            definition_id = self._generate_id()

        if type_collected is None:
            specimen_type = self.faker.random_element(self.SPECIMEN_TYPES)
            type_collected = {"coding": [specimen_type], "text": specimen_type["display"]}

        specimen_definition: dict[str, Any] = {
            "resourceType": "SpecimenDefinition",
            "id": definition_id,
            "meta": self._generate_meta(),
            "typeCollected": type_collected,
        }

        # Add identifier
        specimen_definition["identifier"] = {
            "system": "http://example.org/specimen-definitions",
            "value": f"SPEC-{self.faker.random_number(digits=6, fix_len=True)}",
        }

        # Add patient preparation
        if patient_preparation:
            specimen_definition["patientPreparation"] = patient_preparation
        elif self.faker.boolean(chance_of_getting_true=60):
            specimen_definition["patientPreparation"] = [
                {"text": "Fasting for 12 hours recommended"},
                {"text": "Avoid alcohol for 24 hours"},
            ]

        # Add time aspect
        if time_aspect:
            specimen_definition["timeAspect"] = time_aspect
        elif self.faker.boolean(chance_of_getting_true=50):
            specimen_definition["timeAspect"] = self.faker.random_element(["morning", "fasting", "random"])

        # Add collection
        if collection:
            specimen_definition["collection"] = collection
        else:
            specimen_definition["collection"] = [self._generate_collection()]

        # Add type tested
        if type_tested:
            specimen_definition["typeTested"] = type_tested
        else:
            specimen_definition["typeTested"] = [self._generate_type_tested()]

        return specimen_definition

    def _generate_collection(self) -> dict[str, Any]:
        """Generate collection requirements."""
        return {
            "collectedDateTime": "morning",
        }

    def _generate_type_tested(self) -> dict[str, Any]:
        """Generate type tested information."""
        specimen_type = self.faker.random_element(self.SPECIMEN_TYPES)
        container_type = self.faker.random_element(self.CONTAINER_TYPES)
        cap = self.faker.random_element(self.CAP_COLORS)

        return {
            "type": {"coding": [specimen_type], "text": specimen_type["display"]},
            "preference": "preferred",
            "container": {
                "type": {"coding": [container_type], "text": container_type["display"]},
                "cap": {"coding": [cap], "text": cap["code"].title()},
                "minimumVolumeQuantity": {
                    "value": float(self.faker.random_int(1, 10)),
                    "unit": "mL",
                    "system": "http://unitsofmeasure.org",
                    "code": "mL",
                },
            },
            "handling": [
                {
                    "temperatureQualifier": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/handling-condition",
                                "code": "room",
                                "display": "Room Temperature",
                            }
                        ]
                    },
                    "maxDuration": {
                        "value": 24,
                        "unit": "hours",
                        "system": "http://unitsofmeasure.org",
                        "code": "h",
                    },
                }
            ],
        }

    def generate_blood_specimen_definition(
        self,
        cap_color: str = "lavender",
        volume_ml: float = 5.0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SpecimenDefinition for blood collection.

        Args:
            cap_color: Tube cap color
            volume_ml: Minimum volume in mL

        Returns:
            SpecimenDefinition FHIR resource
        """
        type_collected = {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "122555007",
                    "display": "Venous blood specimen",
                }
            ],
            "text": "Venous blood specimen",
        }

        type_tested = [
            {
                "type": type_collected,
                "preference": "preferred",
                "container": {
                    "type": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "702224000",
                                "display": "Vacuum blood collection tube",
                            }
                        ]
                    },
                    "cap": {
                        "coding": [{"system": "urn:iso:std:iso:6710:2017", "code": cap_color}],
                        "text": cap_color.title(),
                    },
                    "minimumVolumeQuantity": {
                        "value": volume_ml,
                        "unit": "mL",
                        "system": "http://unitsofmeasure.org",
                        "code": "mL",
                    },
                },
            }
        ]

        return self.generate(
            type_collected=type_collected,
            type_tested=type_tested,
            **kwargs,
        )
