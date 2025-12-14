"""FamilyMemberHistory resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class FamilyMemberHistoryGenerator(FHIRResourceGenerator):
    """Generator for FHIR FamilyMemberHistory resources.

    FamilyMemberHistory records significant health information about
    a patient's relatives, relevant for understanding genetic and
    familial disease risk.
    """

    # Family relationships
    RELATIONSHIPS: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "FTH", "display": "Father"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "MTH", "display": "Mother"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "BRO", "display": "Brother"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "SIS", "display": "Sister"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "GRFTH", "display": "Grandfather"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "GRMTH", "display": "Grandmother"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "UNCLE", "display": "Uncle"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "AUNT", "display": "Aunt"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "SON", "display": "Son"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "DAU", "display": "Daughter"},
    ]

    # Common familial conditions
    FAMILIAL_CONDITIONS: list[dict[str, Any]] = [
        {
            "code": {"system": "http://snomed.info/sct", "code": "73211009", "display": "Diabetes mellitus"},
            "onset_age_range": (40, 70),
            "outcome": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "38341003", "display": "Hypertension"},
            "onset_age_range": (35, 65),
            "outcome": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "53741008", "display": "Coronary artery disease"},
            "onset_age_range": (45, 75),
            "outcome": {"system": "http://snomed.info/sct", "code": "419099009", "display": "Deceased"},
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "254837009", "display": "Breast cancer"},
            "onset_age_range": (40, 65),
            "outcome": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "363406005", "display": "Colon cancer"},
            "onset_age_range": (50, 70),
            "outcome": {"system": "http://snomed.info/sct", "code": "419099009", "display": "Deceased"},
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "93761005", "display": "Lung cancer"},
            "onset_age_range": (55, 75),
            "outcome": {"system": "http://snomed.info/sct", "code": "419099009", "display": "Deceased"},
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "230690007", "display": "Stroke"},
            "onset_age_range": (55, 80),
            "outcome": {"system": "http://snomed.info/sct", "code": "419099009", "display": "Deceased"},
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "35489007", "display": "Depression"},
            "onset_age_range": (20, 50),
            "outcome": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "69322001", "display": "Anxiety disorder"},
            "onset_age_range": (18, 45),
            "outcome": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "195967001", "display": "Asthma"},
            "onset_age_range": (5, 30),
            "outcome": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "396275006", "display": "Osteoarthritis"},
            "onset_age_range": (50, 75),
            "outcome": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "64859006", "display": "Osteoporosis"},
            "onset_age_range": (55, 80),
            "outcome": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "26929004", "display": "Alzheimer's disease"},
            "onset_age_range": (65, 90),
            "outcome": {"system": "http://snomed.info/sct", "code": "419099009", "display": "Deceased"},
        },
    ]

    # Sex codes
    SEX_CODES: list[dict[str, str]] = [
        {"system": "http://hl7.org/fhir/administrative-gender", "code": "male", "display": "Male"},
        {"system": "http://hl7.org/fhir/administrative-gender", "code": "female", "display": "Female"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        history_id: str | None = None,
        patient_ref: str | None = None,
        relationship: dict[str, str] | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a FamilyMemberHistory resource.

        Args:
            history_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            relationship: Specific relationship to use
            status: History status

        Returns:
            FamilyMemberHistory FHIR resource
        """
        if history_id is None:
            history_id = self._generate_id()

        # Generate status (weighted towards completed)
        if status is None:
            status = self.faker.random_element(
                elements=["completed", "completed", "completed", "partial", "health-unknown"]
            )

        # Select relationship
        if relationship is None:
            relationship = self.faker.random_element(self.RELATIONSHIPS)

        # Determine sex based on relationship
        relationship_code = relationship["code"]
        if relationship_code in ["FTH", "BRO", "GRFTH", "UNCLE", "SON"]:
            sex = self.SEX_CODES[0]  # male
        elif relationship_code in ["MTH", "SIS", "GRMTH", "AUNT", "DAU"]:
            sex = self.SEX_CODES[1]  # female
        else:
            sex = self.faker.random_element(self.SEX_CODES)

        # Generate age
        if relationship_code in ["GRFTH", "GRMTH"]:
            age = self.faker.random_int(65, 95)
        elif relationship_code in ["FTH", "MTH", "UNCLE", "AUNT"]:
            age = self.faker.random_int(45, 80)
        elif relationship_code in ["BRO", "SIS"]:
            age = self.faker.random_int(25, 70)
        else:
            age = self.faker.random_int(20, 60)

        # Determine if deceased
        deceased = self.faker.boolean(chance_of_getting_true=30)

        history: dict[str, Any] = {
            "resourceType": "FamilyMemberHistory",
            "id": history_id,
            "meta": self._generate_meta(),
            "status": status,
            "relationship": make_codeable_concept(relationship),
            "sex": make_codeable_concept(sex),
            "date": self._generate_date(),
        }

        # Add age or deceased info
        if deceased:
            history["deceasedAge"] = {
                "value": age,
                "unit": "years",
                "system": "http://unitsofmeasure.org",
                "code": "a",
            }
        else:
            history["ageAge"] = {
                "value": age,
                "unit": "years",
                "system": "http://unitsofmeasure.org",
                "code": "a",
            }

        # Add conditions (1-3 conditions)
        if status != "health-unknown":
            num_conditions = self.faker.random_int(0, 3)
            if num_conditions > 0:
                conditions = self.faker.random_elements(
                    elements=self.FAMILIAL_CONDITIONS,
                    length=num_conditions,
                    unique=True,
                )

                history["condition"] = []
                for cond in conditions:
                    onset_min, onset_max = cond["onset_age_range"]
                    onset_age = self.faker.random_int(onset_min, min(onset_max, age))

                    condition_entry: dict[str, Any] = {
                        "code": make_codeable_concept(cond["code"]),
                        "onsetAge": {
                            "value": onset_age,
                            "unit": "years",
                            "system": "http://unitsofmeasure.org",
                            "code": "a",
                        },
                    }

                    # Add outcome if deceased and condition has outcome
                    if deceased and cond.get("outcome"):
                        condition_entry["outcome"] = make_codeable_concept(cond["outcome"])

                    history["condition"].append(condition_entry)

        if patient_ref:
            history["patient"] = {"reference": patient_ref}

        return history
