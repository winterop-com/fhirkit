"""GuidanceResponse resource generator."""

from datetime import datetime
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class GuidanceResponseGenerator(FHIRResourceGenerator):
    """Generator for FHIR GuidanceResponse resources."""

    STATUS_CODES = [
        "success",
        "data-requested",
        "data-required",
        "in-progress",
        "failure",
        "entered-in-error",
    ]

    REASON_CODES = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/guidance-reason",
            "code": "drug-drug-interaction",
            "display": "Drug-Drug Interaction",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/guidance-reason",
            "code": "dosage-concern",
            "display": "Dosage Concern",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/guidance-reason",
            "code": "contraindication",
            "display": "Contraindication",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/guidance-reason",
            "code": "duplicate-therapy",
            "display": "Duplicate Therapy",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        response_id: str | None = None,
        request_identifier: str | None = None,
        module_uri: str | None = None,
        module_canonical: str | None = None,
        status: str | None = None,
        subject_reference: str | None = None,
        encounter_reference: str | None = None,
        occurrence_datetime: str | None = None,
        performer_reference: str | None = None,
        reason_codes: list[dict[str, Any]] | None = None,
        output_parameters_reference: str | None = None,
        result_reference: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a GuidanceResponse resource.

        Args:
            response_id: Resource ID (generates UUID if None)
            request_identifier: Identifier of the request
            module_uri: URI of the guidance module
            module_canonical: Canonical URL of the guidance module
            status: Response status
            subject_reference: Reference to subject Patient
            encounter_reference: Reference to Encounter
            occurrence_datetime: When guidance was invoked
            performer_reference: Reference to performer Device
            reason_codes: Reason codes for the guidance
            output_parameters_reference: Reference to output Parameters
            result_reference: Reference to result CarePlan/RequestGroup

        Returns:
            GuidanceResponse FHIR resource
        """
        if response_id is None:
            response_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES[:2])

        if occurrence_datetime is None:
            occurrence_datetime = datetime.now().isoformat()

        if request_identifier is None:
            request_identifier = str(self.faker.uuid4())

        response: dict[str, Any] = {
            "resourceType": "GuidanceResponse",
            "id": response_id,
            "requestIdentifier": {
                "system": "http://example.org/request-ids",
                "value": request_identifier,
            },
            "status": status,
            "occurrenceDateTime": occurrence_datetime,
        }

        # Add module reference (one of moduleUri, moduleCanonical, moduleCodeableConcept)
        if module_canonical:
            response["moduleCanonical"] = module_canonical
        elif module_uri:
            response["moduleUri"] = module_uri
        else:
            response["moduleUri"] = f"http://example.org/guidance/{self.faker.word()}-module"

        # Add subject reference
        if subject_reference:
            response["subject"] = {"reference": subject_reference}

        # Add encounter reference
        if encounter_reference:
            response["encounter"] = {"reference": encounter_reference}

        # Add performer reference
        if performer_reference:
            response["performer"] = {"reference": performer_reference}
        elif self.faker.boolean(chance_of_getting_true=50):
            response["performer"] = {
                "reference": f"Device/{self._generate_id()}",
                "display": "CDS Engine",
            }

        # Add reason codes for success responses
        if status == "success":
            if reason_codes:
                response["reasonCode"] = [{"coding": [code], "text": code["display"]} for code in reason_codes]
            elif self.faker.boolean(chance_of_getting_true=70):
                reason = self.faker.random_element(self.REASON_CODES)
                response["reasonCode"] = [{"coding": [reason], "text": reason["display"]}]

        # Add output parameters reference
        if output_parameters_reference:
            response["outputParameters"] = {"reference": output_parameters_reference}

        # Add result reference
        if result_reference:
            response["result"] = {"reference": result_reference}

        # Add notes for certain statuses
        if status in ["data-requested", "data-required"]:
            response["note"] = [{"text": "Additional data is required to complete the evaluation"}]

        return response

    def generate_for_patient(
        self,
        patient_id: str,
        module_uri: str | None = None,
        status: str = "success",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a GuidanceResponse for a specific patient.

        Args:
            patient_id: Patient ID
            module_uri: URI of the guidance module
            status: Response status

        Returns:
            GuidanceResponse FHIR resource
        """
        return self.generate(
            subject_reference=f"Patient/{patient_id}",
            module_uri=module_uri,
            status=status,
            **kwargs,
        )
