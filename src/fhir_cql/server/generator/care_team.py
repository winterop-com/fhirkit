"""CareTeam resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CareTeamGenerator(FHIRResourceGenerator):
    """Generator for FHIR CareTeam resources."""

    # Care team categories
    CATEGORY_CODES = [
        {"code": "event", "display": "Event", "system": "http://loinc.org"},
        {"code": "encounter", "display": "Encounter", "system": "http://loinc.org"},
        {"code": "episode", "display": "Episode", "system": "http://loinc.org"},
        {"code": "longitudinal", "display": "Longitudinal", "system": "http://loinc.org"},
    ]

    # Participant roles
    PARTICIPANT_ROLES = [
        {"code": "primary", "display": "Primary Care Provider", "system": "http://terminology.hl7.org/CodeSystem/participant-role"},
        {"code": "secondary", "display": "Secondary Care Provider", "system": "http://terminology.hl7.org/CodeSystem/participant-role"},
        {"code": "specialist", "display": "Specialist", "system": "http://terminology.hl7.org/CodeSystem/participant-role"},
        {"code": "coordinator", "display": "Care Coordinator", "system": "http://terminology.hl7.org/CodeSystem/participant-role"},
    ]

    # Care team name patterns
    NAME_PATTERNS = [
        "{patient} Care Team",
        "{condition} Management Team",
        "Primary Care Team - {patient}",
        "{specialty} Care Team",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        care_team_id: str | None = None,
        patient_ref: str | None = None,
        practitioner_refs: list[str] | None = None,
        encounter_ref: str | None = None,
        status: str = "active",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CareTeam resource.

        Args:
            care_team_id: CareTeam ID (generates UUID if None)
            patient_ref: Reference to Patient
            practitioner_refs: List of Practitioner references
            encounter_ref: Reference to Encounter
            status: Team status (proposed, active, suspended, inactive, entered-in-error)

        Returns:
            CareTeam FHIR resource
        """
        if care_team_id is None:
            care_team_id = self._generate_id()

        category = self.faker.random_element(self.CATEGORY_CODES)

        # Generate name
        pattern = self.faker.random_element(self.NAME_PATTERNS)
        name = pattern.format(
            patient=self.faker.last_name(),
            condition=self.faker.random_element(["Diabetes", "Cardiac", "Oncology", "Respiratory"]),
            specialty=self.faker.random_element(["Primary Care", "Specialty", "Home Health"]),
        )

        care_team: dict[str, Any] = {
            "resourceType": "CareTeam",
            "id": care_team_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/care-team-ids",
                    value=f"CT-{self.faker.numerify('######')}",
                ),
            ],
            "status": status,
            "category": [
                {
                    "coding": [category],
                    "text": category["display"],
                }
            ],
            "name": name,
            "period": {
                "start": self._generate_date(),
            },
        }

        if patient_ref:
            care_team["subject"] = {"reference": patient_ref}

        if encounter_ref:
            care_team["encounter"] = {"reference": encounter_ref}

        # Add participants
        if practitioner_refs:
            participants = []
            for i, prac_ref in enumerate(practitioner_refs):
                role = self.PARTICIPANT_ROLES[i % len(self.PARTICIPANT_ROLES)]
                participants.append({
                    "role": [{"coding": [role], "text": role["display"]}],
                    "member": {"reference": prac_ref},
                })
            care_team["participant"] = participants
        else:
            # Generate at least one participant placeholder
            role = self.faker.random_element(self.PARTICIPANT_ROLES)
            care_team["participant"] = [
                {
                    "role": [{"coding": [role], "text": role["display"]}],
                }
            ]

        return care_team
