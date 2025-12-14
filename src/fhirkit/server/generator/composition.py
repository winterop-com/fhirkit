"""Composition resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CompositionGenerator(FHIRResourceGenerator):
    """Generator for FHIR Composition resources.

    Composition is the basic structure from which a FHIR Document is built.
    It defines the structure and narrative content necessary for a document.
    """

    # LOINC document type codes
    DOCUMENT_TYPES: list[dict[str, str]] = [
        {"code": "11488-4", "display": "Consultation note"},
        {"code": "34117-2", "display": "History and physical note"},
        {"code": "18842-5", "display": "Discharge summary"},
        {"code": "11506-3", "display": "Progress note"},
        {"code": "57133-1", "display": "Referral note"},
        {"code": "60591-5", "display": "Patient summary"},
        {"code": "34133-9", "display": "Summary of episode note"},
        {"code": "34108-1", "display": "Outpatient note"},
        {"code": "34109-9", "display": "Emergency department note"},
        {"code": "11504-8", "display": "Surgical operation note"},
    ]

    # Section codes from LOINC
    SECTION_CODES: list[dict[str, str]] = [
        {"code": "10164-2", "display": "History of present illness"},
        {"code": "10154-3", "display": "Chief complaint"},
        {"code": "11348-0", "display": "History of past illness"},
        {"code": "10160-0", "display": "History of medication use"},
        {"code": "48765-2", "display": "Allergies and adverse reactions"},
        {"code": "8716-3", "display": "Vital signs"},
        {"code": "29545-1", "display": "Physical examination"},
        {"code": "30954-2", "display": "Diagnostic studies"},
        {"code": "11450-4", "display": "Problem list"},
        {"code": "46240-8", "display": "Assessment and plan"},
        {"code": "29549-3", "display": "Medications administered"},
        {"code": "47519-4", "display": "Procedures"},
        {"code": "18776-5", "display": "Plan of care"},
        {"code": "8648-8", "display": "Hospital course"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        composition_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        author_ref: str | None = None,
        custodian_ref: str | None = None,
        document_type: str | None = None,
        section_refs: dict[str, list[str]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Composition resource.

        Args:
            composition_id: Resource ID (generates UUID if None)
            patient_ref: Reference to subject Patient (e.g., "Patient/123")
            encounter_ref: Reference to Encounter context
            author_ref: Reference to author (Practitioner, PractitionerRole, Organization)
            custodian_ref: Reference to custodian Organization
            document_type: LOINC code for document type (random if None)
            section_refs: Dict mapping section codes to lists of resource references

        Returns:
            Composition FHIR resource
        """
        if composition_id is None:
            composition_id = self._generate_id()

        if patient_ref is None:
            patient_ref = f"Patient/{self._generate_id()}"

        if author_ref is None:
            author_ref = f"Practitioner/{self._generate_id()}"

        # Select document type
        if document_type:
            doc_type = next(
                (dt for dt in self.DOCUMENT_TYPES if dt["code"] == document_type),
                self.faker.random_element(self.DOCUMENT_TYPES),
            )
        else:
            doc_type = self.faker.random_element(self.DOCUMENT_TYPES)

        # Generate composition timestamp
        comp_date = self.faker.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)

        composition: dict[str, Any] = {
            "resourceType": "Composition",
            "id": composition_id,
            "meta": self._generate_meta(),
            "identifier": self._generate_identifier(
                system="http://example.org/fhir/composition",
                value=f"COMP-{composition_id[:8].upper()}",
            ),
            "status": "final",
            "type": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": doc_type["code"],
                        "display": doc_type["display"],
                    }
                ],
                "text": doc_type["display"],
            },
            "subject": {"reference": patient_ref},
            "date": comp_date.isoformat(),
            "author": [{"reference": author_ref}],
            "title": doc_type["display"],
        }

        # Add encounter if provided
        if encounter_ref:
            composition["encounter"] = {"reference": encounter_ref}

        # Add custodian if provided
        if custodian_ref:
            composition["custodian"] = {"reference": custodian_ref}

        # Generate sections
        composition["section"] = self._generate_sections(
            patient_ref=patient_ref,
            section_refs=section_refs,
            doc_type_code=doc_type["code"],
        )

        return composition

    def _generate_sections(
        self,
        patient_ref: str,
        section_refs: dict[str, list[str]] | None = None,
        doc_type_code: str | None = None,
    ) -> list[dict[str, Any]]:
        """Generate document sections.

        Args:
            patient_ref: Patient reference for narrative
            section_refs: Pre-defined section references
            doc_type_code: Document type to determine relevant sections

        Returns:
            List of section dictionaries
        """
        sections: list[dict[str, Any]] = []

        # Select sections based on document type
        if doc_type_code in ["18842-5", "34133-9"]:  # Discharge summary, episode note
            section_types = ["8648-8", "11450-4", "10160-0", "18776-5"]  # Hospital course, problems, meds, plan
        elif doc_type_code in ["34117-2"]:  # H&P
            section_types = ["10154-3", "10164-2", "11348-0", "8716-3", "29545-1", "46240-8"]
        elif doc_type_code in ["11506-3"]:  # Progress note
            section_types = ["10164-2", "46240-8", "18776-5"]
        else:
            # Random selection for other types
            num_sections = self.faker.random_int(min=3, max=6)
            section_types = [
                s["code"] for s in self.faker.random_elements(self.SECTION_CODES, length=num_sections, unique=True)
            ]

        for section_code in section_types:
            section_info = next(
                (s for s in self.SECTION_CODES if s["code"] == section_code),
                {"code": section_code, "display": "Section"},
            )

            section: dict[str, Any] = {
                "title": section_info["display"],
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": section_info["code"],
                            "display": section_info["display"],
                        }
                    ]
                },
                "text": {
                    "status": "generated",
                    "div": f'<div xmlns="http://www.w3.org/1999/xhtml"><p>{self._generate_section_narrative(section_info["display"])}</p></div>',
                },
            }

            # Add references if provided
            if section_refs and section_code in section_refs:
                section["entry"] = [{"reference": ref} for ref in section_refs[section_code]]

            sections.append(section)

        return sections

    def _generate_section_narrative(self, section_title: str) -> str:
        """Generate placeholder narrative text for a section.

        Args:
            section_title: The section title

        Returns:
            Generated narrative text
        """
        narratives = {
            "History of present illness": "Patient presents with symptoms as described. " + self.faker.sentence(),
            "Chief complaint": self.faker.sentence(),
            "History of past illness": "Medical history includes previous conditions. " + self.faker.sentence(),
            "History of medication use": "Current medications reviewed. " + self.faker.sentence(),
            "Allergies and adverse reactions": "Allergies documented and verified. " + self.faker.sentence(),
            "Vital signs": "Vital signs within normal limits. " + self.faker.sentence(),
            "Physical examination": "Physical examination performed. " + self.faker.sentence(),
            "Diagnostic studies": "Diagnostic tests ordered and reviewed. " + self.faker.sentence(),
            "Problem list": "Active problems identified and addressed. " + self.faker.sentence(),
            "Assessment and plan": "Assessment completed with plan documented. " + self.faker.sentence(),
            "Medications administered": "Medications administered as prescribed. " + self.faker.sentence(),
            "Procedures": "Procedures performed as indicated. " + self.faker.sentence(),
            "Plan of care": "Care plan established. " + self.faker.sentence(),
            "Hospital course": "Hospital course documented. " + self.faker.sentence(),
        }

        return narratives.get(section_title, self.faker.paragraph(nb_sentences=2))

    def generate_discharge_summary(
        self,
        patient_ref: str,
        encounter_ref: str | None = None,
        author_ref: str | None = None,
        condition_refs: list[str] | None = None,
        medication_refs: list[str] | None = None,
        procedure_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate a discharge summary Composition.

        Args:
            patient_ref: Reference to the Patient
            encounter_ref: Reference to the hospital Encounter
            author_ref: Reference to the authoring Practitioner
            condition_refs: References to Condition resources
            medication_refs: References to MedicationRequest resources
            procedure_refs: References to Procedure resources

        Returns:
            Discharge summary Composition resource
        """
        section_refs: dict[str, list[str]] = {}

        if condition_refs:
            section_refs["11450-4"] = condition_refs  # Problem list

        if medication_refs:
            section_refs["10160-0"] = medication_refs  # Medication use

        if procedure_refs:
            section_refs["47519-4"] = procedure_refs  # Procedures

        return self.generate(
            patient_ref=patient_ref,
            encounter_ref=encounter_ref,
            author_ref=author_ref,
            document_type="18842-5",  # Discharge summary
            section_refs=section_refs,
        )

    def generate_consultation_note(
        self,
        patient_ref: str,
        encounter_ref: str | None = None,
        author_ref: str | None = None,
        observation_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate a consultation note Composition.

        Args:
            patient_ref: Reference to the Patient
            encounter_ref: Reference to the Encounter
            author_ref: Reference to the consulting Practitioner
            observation_refs: References to Observation resources

        Returns:
            Consultation note Composition resource
        """
        section_refs: dict[str, list[str]] = {}

        if observation_refs:
            section_refs["8716-3"] = observation_refs  # Vital signs / observations

        return self.generate(
            patient_ref=patient_ref,
            encounter_ref=encounter_ref,
            author_ref=author_ref,
            document_type="11488-4",  # Consultation note
            section_refs=section_refs,
        )
