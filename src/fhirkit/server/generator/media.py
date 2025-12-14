"""Media resource generator."""

import base64
from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class MediaGenerator(FHIRResourceGenerator):
    """Generator for FHIR Media resources.

    Media represents images, video, audio, or other multimedia content
    captured or used in healthcare contexts.
    """

    # Media statuses
    STATUSES: list[str] = [
        "completed",
        "completed",
        "completed",
        "preparation",
        "in-progress",
    ]

    # Media types and modalities
    MEDIA_TYPES: list[dict[str, Any]] = [
        {
            "type": {"system": "http://terminology.hl7.org/CodeSystem/media-type", "code": "image", "display": "Image"},
            "modality": {
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": "CR",
                "display": "Computed Radiography",
            },
            "body_site": {"system": "http://snomed.info/sct", "code": "51185008", "display": "Thorax"},
            "content_type": "image/jpeg",
            "description": "Chest X-ray",
        },
        {
            "type": {"system": "http://terminology.hl7.org/CodeSystem/media-type", "code": "image", "display": "Image"},
            "modality": {
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": "CT",
                "display": "Computed Tomography",
            },
            "body_site": {"system": "http://snomed.info/sct", "code": "818983003", "display": "Abdomen"},
            "content_type": "image/dicom",
            "description": "Abdominal CT scan",
        },
        {
            "type": {"system": "http://terminology.hl7.org/CodeSystem/media-type", "code": "image", "display": "Image"},
            "modality": {
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": "MR",
                "display": "Magnetic Resonance",
            },
            "body_site": {"system": "http://snomed.info/sct", "code": "12738006", "display": "Brain"},
            "content_type": "image/dicom",
            "description": "Brain MRI",
        },
        {
            "type": {"system": "http://terminology.hl7.org/CodeSystem/media-type", "code": "image", "display": "Image"},
            "modality": {
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": "US",
                "display": "Ultrasound",
            },
            "body_site": {"system": "http://snomed.info/sct", "code": "818983003", "display": "Abdomen"},
            "content_type": "image/jpeg",
            "description": "Abdominal ultrasound",
        },
        {
            "type": {"system": "http://terminology.hl7.org/CodeSystem/media-type", "code": "image", "display": "Image"},
            "modality": {
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": "XC",
                "display": "External-camera Photography",
            },
            "body_site": {"system": "http://snomed.info/sct", "code": "39937001", "display": "Skin"},
            "content_type": "image/jpeg",
            "description": "Clinical photograph - skin lesion",
        },
        {
            "type": {"system": "http://terminology.hl7.org/CodeSystem/media-type", "code": "image", "display": "Image"},
            "modality": {
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": "XC",
                "display": "External-camera Photography",
            },
            "body_site": {"system": "http://snomed.info/sct", "code": "13648007", "display": "Wound"},
            "content_type": "image/jpeg",
            "description": "Wound documentation photograph",
        },
        {
            "type": {"system": "http://terminology.hl7.org/CodeSystem/media-type", "code": "video", "display": "Video"},
            "modality": {
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": "ES",
                "display": "Endoscopy",
            },
            "body_site": {"system": "http://snomed.info/sct", "code": "69695003", "display": "Stomach"},
            "content_type": "video/mp4",
            "description": "Gastroscopy video",
        },
        {
            "type": {"system": "http://terminology.hl7.org/CodeSystem/media-type", "code": "audio", "display": "Audio"},
            "modality": None,
            "body_site": {"system": "http://snomed.info/sct", "code": "80891009", "display": "Heart"},
            "content_type": "audio/mpeg",
            "description": "Heart sounds recording",
        },
    ]

    # View codes for imaging
    VIEW_CODES: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "260421001", "display": "Anteroposterior"},
        {"system": "http://snomed.info/sct", "code": "272485002", "display": "Lateral"},
        {"system": "http://snomed.info/sct", "code": "399067008", "display": "Oblique"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        media_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        practitioner_ref: str | None = None,
        device_ref: str | None = None,
        status: str | None = None,
        media_type: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Media resource.

        Args:
            media_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference
            encounter_ref: Encounter reference
            practitioner_ref: Operator reference
            device_ref: Device reference
            status: Media status
            media_type: Specific media type configuration

        Returns:
            Media FHIR resource
        """
        if media_id is None:
            media_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUSES)

        if media_type is None:
            media_type = self.faker.random_element(self.MEDIA_TYPES)

        # Generate creation time
        created_datetime = self.faker.date_time_between(
            start_date="-30d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        media: dict[str, Any] = {
            "resourceType": "Media",
            "id": media_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/media-ids",
                    value=f"MED-{self.faker.numerify('########')}",
                )
            ],
            "status": status,
            "type": make_codeable_concept(media_type["type"]),
            "createdDateTime": created_datetime.isoformat(),
            "bodySite": make_codeable_concept(media_type["body_site"]),
            "content": {
                "contentType": media_type["content_type"],
                "title": media_type["description"],
                "creation": created_datetime.isoformat(),
            },
        }

        # Add modality if present
        if media_type.get("modality"):
            media["modality"] = make_codeable_concept(media_type["modality"])

        # Add view for images
        if media_type["type"]["code"] == "image":
            media["view"] = make_codeable_concept(self.faker.random_element(self.VIEW_CODES))

            # Add dimensions for images
            media["width"] = self.faker.random_element([512, 1024, 2048, 4096])
            media["height"] = self.faker.random_element([512, 1024, 2048, 4096])
            media["frames"] = 1

        # Add duration for video/audio
        if media_type["type"]["code"] in ["video", "audio"]:
            media["duration"] = self.faker.random_int(min=10, max=600)  # seconds

        # Add a placeholder data (base64 encoded minimal content)
        # In real usage, this would be actual media content
        media["content"]["data"] = base64.b64encode(b"placeholder").decode("utf-8")
        media["content"]["size"] = self.faker.random_int(min=1000, max=10000000)

        # Add reason code
        media["reasonCode"] = [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "165197003",
                        "display": "Diagnostic imaging",
                    }
                ]
            }
        ]

        if patient_ref:
            media["subject"] = {"reference": patient_ref}

        if encounter_ref:
            media["encounter"] = {"reference": encounter_ref}

        if practitioner_ref:
            media["operator"] = {"reference": practitioner_ref}

        if device_ref:
            media["device"] = {"reference": device_ref}

        return media
