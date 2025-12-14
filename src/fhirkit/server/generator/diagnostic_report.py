"""DiagnosticReport resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    DIAGNOSTIC_REPORT_CATEGORIES,
    DIAGNOSTIC_REPORT_CONCLUSION_CODES,
    DIAGNOSTIC_REPORT_TYPES,
    LOINC_SYSTEM,
    CodingTemplate,
)


class DiagnosticReportGenerator(FHIRResourceGenerator):
    """Generator for FHIR DiagnosticReport resources.

    DiagnosticReports group observations and interpretations into clinical reports
    such as laboratory panels, radiology studies, or pathology reports.
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        report_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        performer_ref: str | None = None,
        result_refs: list[str] | None = None,
        report_category: str | None = None,
        effective_date: str | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a DiagnosticReport resource.

        Args:
            report_id: Report ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            performer_ref: Performer reference (e.g., "Practitioner/456")
            result_refs: List of Observation references that are part of this report
            report_category: Category of report ("LAB", "RAD", "PAT", or None for random)
            effective_date: Effective datetime (random if None)
            status: Report status (random weighted if None)

        Returns:
            DiagnosticReport FHIR resource
        """
        if report_id is None:
            report_id = self._generate_id()

        if effective_date is None:
            effective_dt = self.faker.date_time_between(
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            )
            effective_date = effective_dt.isoformat()

        # Select report type based on category
        if report_category:
            matching_types = [t for t in DIAGNOSTIC_REPORT_TYPES if t.get("category") == report_category]
            if matching_types:
                report_type = self.faker.random_element(matching_types)
            else:
                report_type = self.faker.random_element(DIAGNOSTIC_REPORT_TYPES)
        else:
            report_type = self.faker.random_element(DIAGNOSTIC_REPORT_TYPES)

        # Get category from report type
        category_code = report_type.get("category", "LAB")
        category = next((c for c in DIAGNOSTIC_REPORT_CATEGORIES if c["code"] == category_code), None)

        # Status with weighted distribution (most are final)
        if status is None:
            status = self.faker.random_element(
                elements=["final"] * 70 + ["preliminary"] * 15 + ["amended"] * 10 + ["registered"] * 5
            )

        # Generate issued datetime (slightly after effective)
        effective_dt = datetime.fromisoformat(effective_date.replace("Z", "+00:00"))
        issued_dt = effective_dt + self.faker.time_delta(end_datetime=effective_dt)
        if issued_dt <= effective_dt:
            issued_dt = effective_dt

        report: dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "id": report_id,
            "meta": self._generate_meta(),
            "status": status,
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                            "code": category["code"] if category else "LAB",
                            "display": category["display"] if category else "Laboratory",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": LOINC_SYSTEM,
                        "code": report_type["code"],
                        "display": report_type["display"],
                    }
                ],
                "text": report_type["display"],
            },
            "effectiveDateTime": effective_date,
            "issued": issued_dt.isoformat(),
        }

        if patient_ref:
            report["subject"] = {"reference": patient_ref}

        if encounter_ref:
            report["encounter"] = {"reference": encounter_ref}

        if performer_ref:
            report["performer"] = [{"reference": performer_ref}]

        if result_refs:
            report["result"] = [{"reference": ref} for ref in result_refs]

        # Add conclusion for final reports (70% chance)
        if status == "final" and self.faker.random.random() < 0.7:
            conclusion_code = self.faker.random_element(DIAGNOSTIC_REPORT_CONCLUSION_CODES)
            report["conclusion"] = self._generate_conclusion_text(report_type, conclusion_code)
            report["conclusionCode"] = [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": conclusion_code["code"],
                            "display": conclusion_code["display"],
                        }
                    ]
                }
            ]

        return report

    def _generate_conclusion_text(self, report_type: CodingTemplate, conclusion_code: CodingTemplate) -> str:
        """Generate a realistic conclusion text based on report type and conclusion."""
        report_display = report_type.get("display", "Report")
        conclusion_display = conclusion_code.get("display", "Normal")

        if conclusion_display == "Normal":
            templates = [
                f"{report_display} results within normal limits.",
                f"No significant abnormalities identified on {report_display}.",
                f"{report_display} shows no evidence of acute pathology.",
            ]
        elif conclusion_display == "Abnormal":
            templates = [
                f"{report_display} shows findings that require clinical correlation.",
                f"Abnormal findings on {report_display}. Please see detailed results.",
                f"{report_display} demonstrates abnormalities as detailed in results.",
            ]
        else:
            templates = [
                f"{report_display} interpretation: {conclusion_display}.",
                f"Findings: {conclusion_display}. Clinical correlation recommended.",
            ]

        return self.faker.random_element(templates)

    def generate_lab_panel(
        self,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        performer_ref: str | None = None,
        result_refs: list[str] | None = None,
        effective_date: str | None = None,
    ) -> dict[str, Any]:
        """Generate a laboratory panel DiagnosticReport.

        Returns:
            DiagnosticReport for a laboratory panel
        """
        return self.generate(
            patient_ref=patient_ref,
            encounter_ref=encounter_ref,
            performer_ref=performer_ref,
            result_refs=result_refs,
            report_category="LAB",
            effective_date=effective_date,
            status="final",
        )

    def generate_radiology_report(
        self,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        performer_ref: str | None = None,
        effective_date: str | None = None,
    ) -> dict[str, Any]:
        """Generate a radiology DiagnosticReport.

        Returns:
            DiagnosticReport for a radiology study
        """
        return self.generate(
            patient_ref=patient_ref,
            encounter_ref=encounter_ref,
            performer_ref=performer_ref,
            report_category="RAD",
            effective_date=effective_date,
            status="final",
        )

    def generate_pathology_report(
        self,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        performer_ref: str | None = None,
        effective_date: str | None = None,
    ) -> dict[str, Any]:
        """Generate a pathology DiagnosticReport.

        Returns:
            DiagnosticReport for a pathology study
        """
        return self.generate(
            patient_ref=patient_ref,
            encounter_ref=encounter_ref,
            performer_ref=performer_ref,
            report_category="PAT",
            effective_date=effective_date,
            status="final",
        )
