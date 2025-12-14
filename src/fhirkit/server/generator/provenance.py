"""Provenance resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class ProvenanceGenerator(FHIRResourceGenerator):
    """Generator for FHIR Provenance resources.

    Provenance tracks the origin and history of resources, including
    who created or modified them, when, and why.
    """

    # Activity types
    ACTIVITY_TYPES: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/v3-DataOperation", "code": "CREATE", "display": "create"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-DataOperation", "code": "UPDATE", "display": "revise"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-DataOperation", "code": "DELETE", "display": "delete"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-DataOperation", "code": "APPEND", "display": "append"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-DocumentCompletion",
            "code": "AU",
            "display": "authenticated",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-DocumentCompletion",
            "code": "LA",
            "display": "legally authenticated",
        },
    ]

    # Agent types/roles
    AGENT_TYPES: list[dict[str, str]] = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
            "code": "author",
            "display": "Author",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
            "code": "performer",
            "display": "Performer",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
            "code": "verifier",
            "display": "Verifier",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
            "code": "attester",
            "display": "Attester",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
            "code": "informant",
            "display": "Informant",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
            "code": "custodian",
            "display": "Custodian",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
            "code": "assembler",
            "display": "Assembler",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
            "code": "composer",
            "display": "Composer",
        },
    ]

    # Entity roles
    ENTITY_ROLES: list[str] = ["derivation", "revision", "quotation", "source", "removal"]

    # Reasons
    REASONS: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "TREAT", "display": "treatment"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
            "code": "HPAYMT",
            "display": "healthcare payment",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
            "code": "HOPERAT",
            "display": "healthcare operations",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "PUBHLTH", "display": "public health"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
            "code": "HRESCH",
            "display": "healthcare research",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
            "code": "ETREAT",
            "display": "emergency treatment",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        provenance_id: str | None = None,
        target_ref: str | None = None,
        agent_ref: str | None = None,
        organization_ref: str | None = None,
        entity_ref: str | None = None,
        activity_type: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Provenance resource.

        Args:
            provenance_id: Resource ID (generates UUID if None)
            target_ref: Target resource reference
            agent_ref: Agent (Practitioner/Patient) reference
            organization_ref: Organization on whose behalf agent acted
            entity_ref: Entity that was used/modified
            activity_type: Specific activity type

        Returns:
            Provenance FHIR resource
        """
        if provenance_id is None:
            provenance_id = self._generate_id()

        if activity_type is None:
            activity_type = self.faker.random_element(self.ACTIVITY_TYPES)

        # Generate times
        occurred_datetime = self.faker.date_time_between(
            start_date="-30d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        recorded = self.faker.date_time_between(
            start_date=occurred_datetime,
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Select agent type and reason
        agent_type = self.faker.random_element(self.AGENT_TYPES)
        reason = self.faker.random_element(self.REASONS)

        provenance: dict[str, Any] = {
            "resourceType": "Provenance",
            "id": provenance_id,
            "meta": self._generate_meta(),
            "occurredDateTime": occurred_datetime.isoformat(),
            "recorded": recorded.isoformat(),
            "activity": make_codeable_concept(activity_type),
            "reason": [make_codeable_concept(reason)],
        }

        # Add target
        if target_ref:
            provenance["target"] = [{"reference": target_ref}]
        else:
            # Generate a placeholder target
            provenance["target"] = [{"reference": f"Patient/{self._generate_id()}"}]

        # Add agent
        agent: dict[str, Any] = {
            "type": make_codeable_concept(agent_type),
        }

        if agent_ref:
            agent["who"] = {"reference": agent_ref}
        else:
            agent["who"] = {"display": self.faker.name()}

        if organization_ref:
            agent["onBehalfOf"] = {"reference": organization_ref}

        provenance["agent"] = [agent]

        # Add entity if provided (50% chance if not provided)
        if entity_ref or self.faker.boolean(chance_of_getting_true=50):
            entity_role = self.faker.random_element(self.ENTITY_ROLES)
            entity: dict[str, Any] = {
                "role": entity_role,
            }

            if entity_ref:
                entity["what"] = {"reference": entity_ref}
            else:
                entity["what"] = {"display": "Source document"}

            provenance["entity"] = [entity]

        # Add location (30% chance)
        if self.faker.boolean(chance_of_getting_true=30):
            provenance["location"] = {
                "display": self.faker.company() + " Medical Center",
            }

        # Add signature (20% chance for authenticated activities)
        if activity_type["code"] in ["AU", "LA"] and self.faker.boolean(chance_of_getting_true=60):
            provenance["signature"] = [
                {
                    "type": [
                        {
                            "system": "urn:iso-astm:E1762-95:2013",
                            "code": "1.2.840.10065.1.12.1.1",
                            "display": "Author's Signature",
                        }
                    ],
                    "when": recorded.isoformat(),
                    "who": agent.get("who", {"display": self.faker.name()}),
                    "sigFormat": "application/signature+xml",
                }
            ]

        return provenance
