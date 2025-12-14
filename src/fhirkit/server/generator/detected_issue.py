"""DetectedIssue resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class DetectedIssueGenerator(FHIRResourceGenerator):
    """Generator for FHIR DetectedIssue resources.

    DetectedIssue represents clinical decision support alerts and warnings,
    such as drug-drug interactions, duplicate therapy, or contraindications.
    """

    # Issue statuses
    STATUSES: list[str] = [
        "final",
        "final",
        "final",
        "preliminary",
        "registered",
    ]

    # Severity levels
    SEVERITIES: list[str] = ["high", "moderate", "low"]

    # Issue types
    ISSUE_TYPES: list[dict[str, Any]] = [
        {
            "code": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "DRG",
                "display": "Drug Interaction Alert",
            },
            "detail": "Potential drug-drug interaction detected",
            "severity": "high",
        },
        {
            "code": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "DUPTHPY",
                "display": "Duplicate Therapy Alert",
            },
            "detail": "Duplicate therapeutic class detected",
            "severity": "moderate",
        },
        {
            "code": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "ALGY",
                "display": "Allergy Alert",
            },
            "detail": "Patient has documented allergy to this medication class",
            "severity": "high",
        },
        {
            "code": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "DACT",
                "display": "Drug Action Detected Issue",
            },
            "detail": "Contraindication based on patient condition",
            "severity": "high",
        },
        {
            "code": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "DOSEHIGH",
                "display": "Dosage High Alert",
            },
            "detail": "Prescribed dose exceeds recommended maximum",
            "severity": "moderate",
        },
        {
            "code": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "DOSELOW",
                "display": "Dosage Low Alert",
            },
            "detail": "Prescribed dose below therapeutic threshold",
            "severity": "low",
        },
        {
            "code": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "COMPLY",
                "display": "Compliance Alert",
            },
            "detail": "Patient non-compliance with prescribed regimen",
            "severity": "moderate",
        },
        {
            "code": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "INTERVAL",
                "display": "Dosing Interval Issue",
            },
            "detail": "Dosing interval inconsistent with guidelines",
            "severity": "low",
        },
    ]

    # Mitigation actions
    MITIGATION_ACTIONS: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "OE", "display": "Order entry"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "D", "display": "Discontinued"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "DOSEH", "display": "Dosage Changed"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "NOTACTN", "display": "No Action Taken"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        issue_id: str | None = None,
        patient_ref: str | None = None,
        practitioner_ref: str | None = None,
        implicated_refs: list[str] | None = None,
        status: str | None = None,
        issue_type: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DetectedIssue resource.

        Args:
            issue_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference
            practitioner_ref: Author reference
            implicated_refs: List of implicated resource references
            status: Issue status
            issue_type: Specific issue type configuration

        Returns:
            DetectedIssue FHIR resource
        """
        if issue_id is None:
            issue_id = self._generate_id()

        if status is None:
            status = self.faker.random_element(self.STATUSES)

        if issue_type is None:
            issue_type = self.faker.random_element(self.ISSUE_TYPES)

        # Generate identified time
        identified_datetime = self.faker.date_time_between(
            start_date="-7d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        issue: dict[str, Any] = {
            "resourceType": "DetectedIssue",
            "id": issue_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/detected-issue-ids",
                    value=f"DI-{self.faker.numerify('########')}",
                )
            ],
            "status": status,
            "code": make_codeable_concept(issue_type["code"]),
            "severity": issue_type["severity"],
            "identifiedDateTime": identified_datetime.isoformat(),
            "detail": issue_type["detail"],
        }

        # Add evidence (reference to relevant documentation)
        issue["evidence"] = [
            {
                "code": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/evidence-quality",
                                "code": "high",
                                "display": "High quality evidence",
                            }
                        ]
                    }
                ]
            }
        ]

        # Add mitigation (60% of issues have mitigation documented)
        if self.faker.boolean(chance_of_getting_true=60):
            mitigation_action = self.faker.random_element(self.MITIGATION_ACTIONS)
            mitigation_time = self.faker.date_time_between(
                start_date=identified_datetime,
                end_date="now",
                tzinfo=timezone.utc,
            )
            issue["mitigation"] = [
                {
                    "action": make_codeable_concept(mitigation_action),
                    "date": mitigation_time.isoformat(),
                }
            ]

            if practitioner_ref:
                issue["mitigation"][0]["author"] = {"reference": practitioner_ref}

        if patient_ref:
            issue["patient"] = {"reference": patient_ref}

        if practitioner_ref:
            issue["author"] = {"reference": practitioner_ref}

        if implicated_refs:
            issue["implicated"] = [{"reference": ref} for ref in implicated_refs]

        return issue
