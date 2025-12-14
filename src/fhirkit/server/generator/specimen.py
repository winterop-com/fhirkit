"""Specimen resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class SpecimenGenerator(FHIRResourceGenerator):
    """Generator for FHIR Specimen resources.

    Specimen represents a sample to be used for analysis, such as blood,
    urine, tissue, or other biological materials.
    """

    # Specimen types
    SPECIMEN_TYPES: list[dict[str, Any]] = [
        {
            "code": {"system": "http://snomed.info/sct", "code": "119297000", "display": "Blood specimen"},
            "body_site": {"system": "http://snomed.info/sct", "code": "53120007", "display": "Arm"},
            "collection_method": "Venipuncture",
            "container": "Vacutainer tube",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "119364003", "display": "Serum specimen"},
            "body_site": {"system": "http://snomed.info/sct", "code": "53120007", "display": "Arm"},
            "collection_method": "Venipuncture",
            "container": "Red top tube",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "119361006", "display": "Plasma specimen"},
            "body_site": {"system": "http://snomed.info/sct", "code": "53120007", "display": "Arm"},
            "collection_method": "Venipuncture",
            "container": "Lavender top tube",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "122575003", "display": "Urine specimen"},
            "body_site": {"system": "http://snomed.info/sct", "code": "64033007", "display": "Kidney"},
            "collection_method": "Clean catch midstream",
            "container": "Specimen cup",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "119339001", "display": "Stool specimen"},
            "body_site": {"system": "http://snomed.info/sct", "code": "34402009", "display": "Rectum"},
            "collection_method": "Patient collection",
            "container": "Stool container",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "119342007", "display": "Saliva specimen"},
            "body_site": {"system": "http://snomed.info/sct", "code": "123851003", "display": "Mouth"},
            "collection_method": "Spit collection",
            "container": "Saliva collection tube",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "119295008", "display": "Nasal swab"},
            "body_site": {"system": "http://snomed.info/sct", "code": "45206002", "display": "Nasal cavity"},
            "collection_method": "Nasopharyngeal swab",
            "container": "Transport medium tube",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "119380008", "display": "Throat swab"},
            "body_site": {"system": "http://snomed.info/sct", "code": "49928004", "display": "Pharynx"},
            "collection_method": "Throat swab",
            "container": "Transport medium tube",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "119359002", "display": "Wound swab"},
            "body_site": {"system": "http://snomed.info/sct", "code": "39937001", "display": "Skin"},
            "collection_method": "Wound swab",
            "container": "Culture tube",
        },
        {
            "code": {
                "system": "http://snomed.info/sct",
                "code": "258450006",
                "display": "Cerebrospinal fluid specimen",
            },
            "body_site": {"system": "http://snomed.info/sct", "code": "421060004", "display": "Lumbar spine"},
            "collection_method": "Lumbar puncture",
            "container": "CSF tube",
        },
    ]

    # Container additives
    CONTAINER_ADDITIVES: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/v2-0371", "code": "EDTA", "display": "EDTA"},
        {"system": "http://terminology.hl7.org/CodeSystem/v2-0371", "code": "HEP", "display": "Heparin"},
        {"system": "http://terminology.hl7.org/CodeSystem/v2-0371", "code": "SST", "display": "Serum separator tube"},
        {"system": "http://terminology.hl7.org/CodeSystem/v2-0371", "code": "NONE", "display": "None"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        specimen_id: str | None = None,
        patient_ref: str | None = None,
        collector_ref: str | None = None,
        service_request_ref: str | None = None,
        status: str | None = None,
        specimen_type: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Specimen resource.

        Args:
            specimen_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            collector_ref: Practitioner who collected the specimen
            service_request_ref: Reference to the ServiceRequest
            status: Specimen status
            specimen_type: Specific specimen type to use

        Returns:
            Specimen FHIR resource
        """
        if specimen_id is None:
            specimen_id = self._generate_id()

        # Generate status (weighted towards available)
        if status is None:
            status = self.faker.random_element(
                elements=["available", "available", "available", "unavailable", "unsatisfactory"]
            )

        # Select specimen type
        if specimen_type is None:
            specimen_type = self.faker.random_element(self.SPECIMEN_TYPES)

        # Generate collection time
        collection_time = self.faker.date_time_between(
            start_date="-7d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Generate received time (slightly after collection)
        received_time = self.faker.date_time_between(
            start_date=collection_time,
            end_date="now",
            tzinfo=timezone.utc,
        )

        specimen: dict[str, Any] = {
            "resourceType": "Specimen",
            "id": specimen_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/specimen-ids",
                    value=f"SP-{self.faker.numerify('########')}",
                )
            ],
            "accessionIdentifier": self._generate_identifier(
                system="http://example.org/accession",
                value=f"ACC-{self.faker.numerify('######')}",
            ),
            "status": status,
            "type": make_codeable_concept(specimen_type["code"]),
            "receivedTime": received_time.isoformat(),
            "collection": {
                "collectedDateTime": collection_time.isoformat(),
                "method": {
                    "text": specimen_type["collection_method"],
                },
                "bodySite": make_codeable_concept(specimen_type["body_site"]),
            },
            "container": [
                {
                    "description": specimen_type["container"],
                    "type": {
                        "text": specimen_type["container"],
                    },
                    "capacity": {
                        "value": self.faker.random_element([5, 10, 15, 30, 50]),
                        "unit": "mL",
                        "system": "http://unitsofmeasure.org",
                        "code": "mL",
                    },
                }
            ],
        }

        # Add condition for unsatisfactory specimens
        if status == "unsatisfactory":
            specimen["condition"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0493",
                            "code": self.faker.random_element(["HEM", "CLOT", "LIPEMIC", "ICTERIC"]),
                            "display": self.faker.random_element(["Hemolyzed", "Clotted", "Lipemic", "Icteric"]),
                        }
                    ]
                }
            ]

        if patient_ref:
            specimen["subject"] = {"reference": patient_ref}

        if collector_ref:
            specimen["collection"]["collector"] = {"reference": collector_ref}

        if service_request_ref:
            specimen["request"] = [{"reference": service_request_ref}]

        return specimen
