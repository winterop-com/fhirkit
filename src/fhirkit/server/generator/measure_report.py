"""MeasureReport resource generator."""

from datetime import date, timedelta
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    MEASURE_POPULATION_CODES,
    MEASURE_REPORT_STATUS_CODES,
    MEASURE_REPORT_TYPE_CODES,
)


class MeasureReportGenerator(FHIRResourceGenerator):
    """Generator for FHIR MeasureReport resources.

    MeasureReport resources contain the results of evaluating a Measure
    against a subject (patient or population).
    """

    def __init__(self, faker: Faker | None = None, seed: int | None = None) -> None:
        """Initialize the generator.

        Args:
            faker: Faker instance to use
            seed: Optional random seed for reproducibility
        """
        super().__init__(faker, seed)

    def generate(
        self,
        *,
        measure_ref: str | None = None,
        patient_ref: str | None = None,
        reporter_ref: str | None = None,
        report_type: str | None = None,
        status: str | None = None,
        period_start: str | None = None,
        period_end: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a MeasureReport resource.

        Args:
            measure_ref: Canonical reference to the Measure
            patient_ref: Reference to subject Patient (for individual reports)
            reporter_ref: Reference to reporting Organization/Practitioner
            report_type: individual | subject-list | summary | data-collection
            status: complete | pending | error
            period_start: Start of measurement period
            period_end: End of measurement period

        Returns:
            A FHIR MeasureReport resource
        """
        resource_id = self._generate_id()
        report_status = status or self.faker.random_element(MEASURE_REPORT_STATUS_CODES)

        # Determine report type
        type_info = None
        if report_type:
            type_info = next(
                (t for t in MEASURE_REPORT_TYPE_CODES if t["code"] == report_type),
                None,
            )
        if not type_info:
            type_info = self.faker.random_element(MEASURE_REPORT_TYPE_CODES)

        # Generate measurement period
        today = date.today()
        if period_end:
            end_date = date.fromisoformat(period_end)
        else:
            end_date = today - timedelta(days=self.faker.random_int(1, 30))

        if period_start:
            start_date = date.fromisoformat(period_start)
        else:
            start_date = end_date - timedelta(days=365)

        # Build resource
        resource: dict[str, Any] = {
            "resourceType": "MeasureReport",
            "id": resource_id,
            "meta": self._generate_meta(),
            "identifier": [
                {
                    "system": "http://example.org/fhir/measurereport-identifier",
                    "value": resource_id,
                }
            ],
            "status": report_status,
            "type": type_info["code"],
            "date": self._generate_datetime(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

        # Add measure reference
        if measure_ref:
            resource["measure"] = measure_ref

        # Add subject for individual reports
        if patient_ref and type_info["code"] == "individual":
            resource["subject"] = {"reference": patient_ref}

        # Add reporter
        if reporter_ref:
            resource["reporter"] = {"reference": reporter_ref}

        # Add improvement notation
        resource["improvementNotation"] = {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/measure-improvement-notation",
                    "code": "increase",
                    "display": "Increased score indicates improvement",
                }
            ]
        }

        # Generate group results based on report type
        if type_info["code"] == "individual":
            resource["group"] = self._generate_individual_results()
        elif type_info["code"] == "summary":
            resource["group"] = self._generate_summary_results()
        else:
            resource["group"] = self._generate_individual_results()

        return resource

    def _generate_individual_results(self) -> list[dict[str, Any]]:
        """Generate results for an individual report.

        Returns:
            List of group results
        """
        # For individual reports, counts are 0 or 1
        populations = [
            self._make_population_result("initial-population", 1),
            self._make_population_result("denominator", 1),
            self._make_population_result("denominator-exclusion", 0),
            self._make_population_result("numerator", self.faker.random_element([0, 1])),
        ]

        # Calculate measure score
        numerator = next(p for p in populations if "numerator" in str(p["code"]))
        denominator = next(p for p in populations if p["code"]["coding"][0]["code"] == "denominator")

        num_count = numerator.get("count", 0)
        denom_count = denominator.get("count", 1)

        score = num_count / denom_count if denom_count > 0 else 0.0

        return [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://example.org/fhir/measure-group",
                            "code": "main-group",
                            "display": "Main Population Group",
                        }
                    ]
                },
                "population": populations,
                "measureScore": {
                    "value": score,
                },
            }
        ]

    def _generate_summary_results(self) -> list[dict[str, Any]]:
        """Generate results for a summary/population report.

        Returns:
            List of group results
        """
        # Generate realistic population counts
        initial_pop = self.faker.random_int(100, 1000)
        denominator = int(initial_pop * self.faker.pyfloat(min_value=0.7, max_value=0.95))
        denom_exclusion = int(initial_pop * self.faker.pyfloat(min_value=0.02, max_value=0.1))
        numerator = int(denominator * self.faker.pyfloat(min_value=0.5, max_value=0.9))

        populations = [
            self._make_population_result("initial-population", initial_pop),
            self._make_population_result("denominator", denominator),
            self._make_population_result("denominator-exclusion", denom_exclusion),
            self._make_population_result("numerator", numerator),
        ]

        # Calculate measure score
        score = numerator / denominator if denominator > 0 else 0.0

        return [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://example.org/fhir/measure-group",
                            "code": "main-group",
                            "display": "Main Population Group",
                        }
                    ]
                },
                "population": populations,
                "measureScore": {
                    "value": round(score, 4),
                },
            }
        ]

    def _make_population_result(self, code: str, count: int) -> dict[str, Any]:
        """Create a population result.

        Args:
            code: Population code
            count: Population count

        Returns:
            Population result
        """
        pop_info = next(
            (p for p in MEASURE_POPULATION_CODES if p["code"] == code),
            {"code": code, "display": code.replace("-", " ").title()},
        )

        return {
            "code": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/measure-population",
                        "code": pop_info["code"],
                        "display": pop_info["display"],
                    }
                ]
            },
            "count": count,
        }

    def generate_individual_report(
        self,
        *,
        measure_ref: str,
        patient_ref: str,
        reporter_ref: str | None = None,
        period_start: str | None = None,
        period_end: str | None = None,
    ) -> dict[str, Any]:
        """Generate an individual patient measure report.

        Args:
            measure_ref: Canonical reference to the Measure
            patient_ref: Reference to the Patient
            reporter_ref: Reference to reporting entity
            period_start: Start of measurement period
            period_end: End of measurement period

        Returns:
            An individual MeasureReport resource
        """
        return self.generate(
            measure_ref=measure_ref,
            patient_ref=patient_ref,
            reporter_ref=reporter_ref,
            report_type="individual",
            status="complete",
            period_start=period_start,
            period_end=period_end,
        )

    def generate_summary_report(
        self,
        *,
        measure_ref: str,
        reporter_ref: str | None = None,
        period_start: str | None = None,
        period_end: str | None = None,
    ) -> dict[str, Any]:
        """Generate a population summary measure report.

        Args:
            measure_ref: Canonical reference to the Measure
            reporter_ref: Reference to reporting entity
            period_start: Start of measurement period
            period_end: End of measurement period

        Returns:
            A summary MeasureReport resource
        """
        return self.generate(
            measure_ref=measure_ref,
            reporter_ref=reporter_ref,
            report_type="summary",
            status="complete",
            period_start=period_start,
            period_end=period_end,
        )

    def generate_batch(
        self,
        count: int = 10,
        measure_ref: str | None = None,
        patient_refs: list[str] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Generate multiple MeasureReport resources.

        Args:
            count: Number of reports to generate
            measure_ref: Optional measure reference for all reports
            patient_refs: Optional list of patient references (cycles through)

        Returns:
            List of MeasureReport resources
        """
        reports = []
        for i in range(count):
            patient_ref = None
            if patient_refs:
                patient_ref = patient_refs[i % len(patient_refs)]

            reports.append(
                self.generate(
                    measure_ref=measure_ref,
                    patient_ref=patient_ref,
                    report_type="individual" if patient_ref else "summary",
                )
            )
        return reports
