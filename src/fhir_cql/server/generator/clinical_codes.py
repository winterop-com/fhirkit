"""Clinical code templates for synthetic data generation.

Loads SNOMED CT, LOINC, RxNorm, and other standard code sets from JSON fixtures.
"""

import json
from pathlib import Path
from typing import Any, TypedDict


class CodingTemplate(TypedDict, total=False):
    """Template for a FHIR Coding element."""

    system: str
    code: str
    display: str


class VitalSignTemplate(TypedDict):
    """Template for vital sign observations."""

    code: str
    display: str
    unit: str
    normal_low: float
    normal_high: float
    abnormal_low: float | None
    abnormal_high: float | None


class LabTemplate(TypedDict):
    """Template for lab observations."""

    code: str
    display: str
    unit: str
    normal_low: float
    normal_high: float
    category: str


# =============================================================================
# Fixture Loading
# =============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture file."""
    path = FIXTURES_DIR / f"{name}.json"
    with open(path) as f:
        return json.load(f)


def _load_codes_with_system(data: dict[str, Any]) -> list[CodingTemplate]:
    """Convert fixture data to CodingTemplate list with system."""
    system = data.get("system", "")
    codes = data.get("codes", [])
    return [{"system": system, "code": c["code"], "display": c["display"]} for c in codes]


def _load_vital_signs(data: dict[str, Any]) -> list[VitalSignTemplate]:
    """Load vital signs with their value ranges."""
    codes = data.get("codes", [])
    return [
        {
            "code": c["code"],
            "display": c["display"],
            "unit": c["unit"],
            "normal_low": c["normal_low"],
            "normal_high": c["normal_high"],
            "abnormal_low": c.get("abnormal_low"),
            "abnormal_high": c.get("abnormal_high"),
        }
        for c in codes
    ]


def _load_lab_tests(data: dict[str, Any]) -> list[LabTemplate]:
    """Load lab tests with their value ranges and categories."""
    codes = data.get("codes", [])
    return [
        {
            "code": c["code"],
            "display": c["display"],
            "unit": c["unit"],
            "normal_low": c["normal_low"],
            "normal_high": c["normal_high"],
            "category": c["category"],
        }
        for c in codes
    ]


# =============================================================================
# Load Fixtures on Import
# =============================================================================

# Load conditions
_conditions_data = _load_fixture("conditions")
SNOMED_SYSTEM = _conditions_data.get("system", "http://snomed.info/sct")
CONDITIONS_SNOMED: list[CodingTemplate] = _load_codes_with_system(_conditions_data)

# Load vital signs
_vitals_data = _load_fixture("vital_signs")
LOINC_SYSTEM = _vitals_data.get("system", "http://loinc.org")
VITAL_SIGNS: list[VitalSignTemplate] = _load_vital_signs(_vitals_data)

# Load lab tests
_labs_data = _load_fixture("lab_tests")
LAB_TESTS: list[LabTemplate] = _load_lab_tests(_labs_data)

# Load medications
_meds_data = _load_fixture("medications")
RXNORM_SYSTEM = _meds_data.get("system", "http://www.nlm.nih.gov/research/umls/rxnorm")
MEDICATIONS_RXNORM: list[CodingTemplate] = _load_codes_with_system(_meds_data)

# Load procedures
_procedures_data = _load_fixture("procedures")
PROCEDURES_SNOMED: list[CodingTemplate] = _load_codes_with_system(_procedures_data)

# Load encounter codes
_encounter_data = _load_fixture("encounter_codes")
ENCOUNTER_CLASSES: list[CodingTemplate] = _load_codes_with_system(_encounter_data["encounter_classes"])
ENCOUNTER_TYPES: list[CodingTemplate] = _load_codes_with_system(_encounter_data["encounter_types"])

# Load status codes
_status_data = _load_fixture("status_codes")
OBSERVATION_CATEGORIES: list[CodingTemplate] = _load_codes_with_system(_status_data["observation_categories"])
CONDITION_CLINICAL_STATUS: list[CodingTemplate] = _load_codes_with_system(_status_data["condition_clinical_status"])
CONDITION_VERIFICATION_STATUS: list[CodingTemplate] = _load_codes_with_system(
    _status_data["condition_verification_status"]
)

# Load practitioner codes
_practitioner_data = _load_fixture("practitioner_codes")
PRACTITIONER_SPECIALTIES: list[CodingTemplate] = _load_codes_with_system(_practitioner_data["specialties"])

# Load patient-specific codes
_patient_data = _load_fixture("patient_codes")

# Contact relationships
CONTACT_RELATIONSHIP_SYSTEM = _patient_data["contact_relationships"]["system"]
CONTACT_RELATIONSHIPS: list[CodingTemplate] = _load_codes_with_system(_patient_data["contact_relationships"])

PERSONAL_RELATIONSHIP_SYSTEM = _patient_data["personal_relationships"]["system"]
PERSONAL_RELATIONSHIPS: list[CodingTemplate] = _load_codes_with_system(_patient_data["personal_relationships"])

# Identifier types
IDENTIFIER_TYPE_SYSTEM = _patient_data["identifier_types"]["system"]
IDENTIFIER_TYPES: list[CodingTemplate] = _load_codes_with_system(_patient_data["identifier_types"])

# Birth sex
BIRTH_SEX_EXTENSION_URL = _patient_data["birth_sex"]["extension_url"]
BIRTH_SEX_CODES: list[tuple[str, str]] = [(c["code"], c["display"]) for c in _patient_data["birth_sex"]["codes"]]

# Gender identity
GENDER_IDENTITY_EXTENSION_URL = _patient_data["gender_identity"]["extension_url"]
GENDER_IDENTITY_SYSTEM = _patient_data["gender_identity"]["system"]
GENDER_IDENTITY_CODES: list[CodingTemplate] = _load_codes_with_system(_patient_data["gender_identity"])

# Simple lists
NAME_SUFFIXES: list[str] = _patient_data["name_suffixes"]
ADDRESS_USE_CODES: list[str] = _patient_data["address_use_codes"]
ADDRESS_TYPE_CODES: list[str] = _patient_data["address_type_codes"]
NAME_USE_CODES: list[str] = _patient_data["name_use_codes"]


# =============================================================================
# Helper Functions
# =============================================================================


def make_codeable_concept(coding: CodingTemplate | dict[str, str], text: str | None = None) -> dict:
    """Create a FHIR CodeableConcept from a coding template."""
    result: dict = {"coding": [dict(coding)]}
    if text:
        result["text"] = text
    elif "display" in coding:
        result["text"] = coding["display"]
    return result


def make_coding(template: CodingTemplate | dict[str, str]) -> dict:
    """Create a FHIR Coding from a template."""
    return dict(template)
