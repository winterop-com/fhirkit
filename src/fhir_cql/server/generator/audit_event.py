"""AuditEvent resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class AuditEventGenerator(FHIRResourceGenerator):
    """Generator for FHIR AuditEvent resources.

    AuditEvent records security-relevant events for compliance and
    security monitoring purposes.
    """

    # Event types
    EVENT_TYPES: list[dict[str, str]] = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/audit-event-type",
            "code": "rest",
            "display": "RESTful Operation",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/audit-event-type", "code": "110106", "display": "Export"},
        {"system": "http://terminology.hl7.org/CodeSystem/audit-event-type", "code": "110107", "display": "Import"},
        {"system": "http://terminology.hl7.org/CodeSystem/audit-event-type", "code": "110112", "display": "Query"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/audit-event-type",
            "code": "110113",
            "display": "Security Alert",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/audit-event-type",
            "code": "110114",
            "display": "User Authentication",
        },
    ]

    # Subtypes for REST operations
    REST_SUBTYPES: list[dict[str, str]] = [
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "create", "display": "create"},
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "read", "display": "read"},
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "update", "display": "update"},
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "delete", "display": "delete"},
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "search-type", "display": "search"},
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "vread", "display": "vread"},
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "history-instance", "display": "history"},
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "batch", "display": "batch"},
        {"system": "http://hl7.org/fhir/restful-interaction", "code": "transaction", "display": "transaction"},
    ]

    # Actions
    ACTIONS: list[str] = ["C", "R", "U", "D", "E"]  # Create, Read, Update, Delete, Execute

    # Outcomes (0=success, 4=minor failure, 8=serious failure, 12=major failure)
    OUTCOMES: list[str] = ["0", "0", "0", "0", "4", "8", "12"]  # Weighted towards success

    # Agent types
    AGENT_TYPES: list[dict[str, str]] = [
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
            "code": "IRCP",
            "display": "information recipient",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
            "code": "AUT",
            "display": "author (originator)",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": "INF", "display": "informant"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": "CST", "display": "custodian"},
    ]

    # Source types
    SOURCE_TYPES: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/security-source-type", "code": "1", "display": "User Device"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/security-source-type",
            "code": "2",
            "display": "Data Interface",
        },
        {"system": "http://terminology.hl7.org/CodeSystem/security-source-type", "code": "3", "display": "Web Server"},
        {
            "system": "http://terminology.hl7.org/CodeSystem/security-source-type",
            "code": "4",
            "display": "Application Server",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/security-source-type",
            "code": "5",
            "display": "Database Server",
        },
        {
            "system": "http://terminology.hl7.org/CodeSystem/security-source-type",
            "code": "6",
            "display": "Security Server",
        },
    ]

    # Entity types
    ENTITY_TYPES: list[dict[str, str]] = [
        {"system": "http://terminology.hl7.org/CodeSystem/audit-entity-type", "code": "1", "display": "Person"},
        {"system": "http://terminology.hl7.org/CodeSystem/audit-entity-type", "code": "2", "display": "System Object"},
        {"system": "http://terminology.hl7.org/CodeSystem/audit-entity-type", "code": "3", "display": "Organization"},
        {"system": "http://terminology.hl7.org/CodeSystem/audit-entity-type", "code": "4", "display": "Other"},
    ]

    # Purpose of use
    PURPOSE_OF_USE: list[dict[str, str]] = [
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
        audit_id: str | None = None,
        agent_ref: str | None = None,
        patient_ref: str | None = None,
        entity_ref: str | None = None,
        event_type: dict[str, str] | None = None,
        action: str | None = None,
        outcome: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an AuditEvent resource.

        Args:
            audit_id: Resource ID (generates UUID if None)
            agent_ref: Agent (Practitioner/Device) reference
            patient_ref: Patient reference (entity)
            entity_ref: Entity resource reference
            event_type: Specific event type
            action: Action code (C, R, U, D, E)
            outcome: Outcome code (0, 4, 8, 12)

        Returns:
            AuditEvent FHIR resource
        """
        if audit_id is None:
            audit_id = self._generate_id()

        if event_type is None:
            event_type = self.faker.random_element(self.EVENT_TYPES)

        if action is None:
            action = self.faker.random_element(self.ACTIONS)

        if outcome is None:
            outcome = self.faker.random_element(self.OUTCOMES)

        # Generate recorded time
        recorded = self.faker.date_time_between(
            start_date="-7d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        # Select related codes
        agent_type = self.faker.random_element(self.AGENT_TYPES)
        source_type = self.faker.random_element(self.SOURCE_TYPES)
        purpose = self.faker.random_element(self.PURPOSE_OF_USE)

        audit: dict[str, Any] = {
            "resourceType": "AuditEvent",
            "id": audit_id,
            "meta": self._generate_meta(),
            "type": make_codeable_concept(event_type),
            "action": action,
            "recorded": recorded.isoformat(),
            "outcome": outcome,
            "purposeOfEvent": [make_codeable_concept(purpose)],
        }

        # Add subtype for REST operations
        if event_type["code"] == "rest":
            subtype = self.faker.random_element(self.REST_SUBTYPES)
            audit["subtype"] = [make_codeable_concept(subtype)]

        # Add outcome description for failures
        if outcome != "0":
            outcome_descriptions = {
                "4": "Minor operational failure",
                "8": "Serious operational failure",
                "12": "Major operational failure",
            }
            audit["outcomeDesc"] = outcome_descriptions.get(outcome, "Unknown failure")

        # Add agent
        agent: dict[str, Any] = {
            "type": make_codeable_concept(agent_type),
            "requestor": self.faker.boolean(chance_of_getting_true=70),
        }

        if agent_ref:
            agent["who"] = {"reference": agent_ref}
        else:
            agent["who"] = {"display": self.faker.name()}

        # Add network info
        agent["network"] = {
            "address": self.faker.ipv4(),
            "type": "2",  # IP Address
        }

        audit["agent"] = [agent]

        # Add source
        audit["source"] = {
            "observer": {"display": "FHIR Server"},
            "type": [make_codeable_concept(source_type)],
        }

        # Add entity (the resource being accessed)
        entities = []

        if patient_ref:
            entities.append(
                {
                    "what": {"reference": patient_ref},
                    "type": make_codeable_concept(
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/audit-entity-type",
                            "code": "1",
                            "display": "Person",
                        }
                    ),
                    "role": make_codeable_concept(
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/object-role",
                            "code": "1",
                            "display": "Patient",
                        }
                    ),
                }
            )

        if entity_ref:
            entity_type = self.faker.random_element(self.ENTITY_TYPES)
            entities.append(
                {
                    "what": {"reference": entity_ref},
                    "type": make_codeable_concept(entity_type),
                }
            )

        # Always have at least one entity
        if not entities:
            entities.append(
                {
                    "what": {"display": "System resource"},
                    "type": make_codeable_concept(
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/audit-entity-type",
                            "code": "2",
                            "display": "System Object",
                        }
                    ),
                }
            )

        audit["entity"] = entities

        return audit
