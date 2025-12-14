"""Consent resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ConsentGenerator(FHIRResourceGenerator):
    """Generator for FHIR Consent resources."""

    # Consent scopes
    CONSENT_SCOPES = [
        {
            "code": "patient-privacy",
            "display": "Privacy Consent",
            "system": "http://terminology.hl7.org/CodeSystem/consentscope",
        },
        {
            "code": "research",
            "display": "Research",
            "system": "http://terminology.hl7.org/CodeSystem/consentscope",
        },
        {
            "code": "treatment",
            "display": "Treatment",
            "system": "http://terminology.hl7.org/CodeSystem/consentscope",
        },
        {
            "code": "adr",
            "display": "Advance Directive",
            "system": "http://terminology.hl7.org/CodeSystem/consentscope",
        },
    ]

    # Consent categories
    CONSENT_CATEGORIES = [
        {
            "code": "59284-0",
            "display": "Patient Consent",
            "system": "http://loinc.org",
        },
        {
            "code": "57016-8",
            "display": "Privacy Policy Acknowledgment Document",
            "system": "http://loinc.org",
        },
        {
            "code": "57017-6",
            "display": "Privacy Policy Organization Document",
            "system": "http://loinc.org",
        },
        {
            "code": "64292-6",
            "display": "Release of Information Consent",
            "system": "http://loinc.org",
        },
    ]

    # Policy types
    POLICY_RULES = [
        {
            "code": "OPTIN",
            "display": "Opt In",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "OPTOUT",
            "display": "Opt Out",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "OPTINR",
            "display": "Opt In with Restrictions",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
    ]

    # Data access classes for provisions
    DATA_CLASSES = [
        {
            "code": "PHR",
            "display": "Personal Health Record",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "PSYCH",
            "display": "Psychiatry Disorder Information",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {"code": "SOC", "display": "Social Worker Note", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
        {
            "code": "HIV",
            "display": "HIV/AIDS Information",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "STD",
            "display": "Sexually Transmitted Disease Information",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
        {
            "code": "SUD",
            "display": "Substance Use Disorder Information",
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        },
    ]

    # Action codes for provisions
    PROVISION_ACTIONS = [
        {"code": "access", "display": "Access", "system": "http://terminology.hl7.org/CodeSystem/consentaction"},
        {"code": "collect", "display": "Collect", "system": "http://terminology.hl7.org/CodeSystem/consentaction"},
        {"code": "use", "display": "Use", "system": "http://terminology.hl7.org/CodeSystem/consentaction"},
        {"code": "disclose", "display": "Disclose", "system": "http://terminology.hl7.org/CodeSystem/consentaction"},
        {"code": "correct", "display": "Correct", "system": "http://terminology.hl7.org/CodeSystem/consentaction"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        consent_id: str | None = None,
        patient_ref: str | None = None,
        organization_ref: str | None = None,
        performer_ref: str | None = None,
        status: str = "active",
        scope: str | None = None,
        category_code: str | None = None,
        include_provision: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Consent resource.

        Args:
            consent_id: Consent ID (generates UUID if None)
            patient_ref: Reference to Patient (subject of consent)
            organization_ref: Reference to Organization (custodian)
            performer_ref: Reference to who is consenting (usually Patient)
            status: Consent status (draft, proposed, active, rejected, inactive, entered-in-error)
            scope: Consent scope code (patient-privacy, research, treatment, adr)
            category_code: LOINC category code
            include_provision: Whether to include detailed provision rules

        Returns:
            Consent FHIR resource
        """
        if consent_id is None:
            consent_id = self._generate_id()

        # Select scope
        if scope:
            scope_coding = next(
                (s for s in self.CONSENT_SCOPES if s["code"] == scope),
                self.faker.random_element(self.CONSENT_SCOPES),
            )
        else:
            scope_coding = self.faker.random_element(self.CONSENT_SCOPES)

        # Select category
        if category_code:
            category_coding = next(
                (c for c in self.CONSENT_CATEGORIES if c["code"] == category_code),
                self.faker.random_element(self.CONSENT_CATEGORIES),
            )
        else:
            category_coding = self.faker.random_element(self.CONSENT_CATEGORIES)

        # Select policy rule
        policy_rule = self.faker.random_element(self.POLICY_RULES)

        consent: dict[str, Any] = {
            "resourceType": "Consent",
            "id": consent_id,
            "meta": self._generate_meta(),
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/consent-ids",
                    value=f"CONSENT-{self.faker.numerify('########')}",
                ),
            ],
            "status": status,
            "scope": {
                "coding": [scope_coding],
                "text": scope_coding["display"],
            },
            "category": [
                {
                    "coding": [category_coding],
                    "text": category_coding["display"],
                }
            ],
            "dateTime": self._generate_datetime(),
            "policyRule": {
                "coding": [policy_rule],
                "text": policy_rule["display"],
            },
        }

        if patient_ref:
            consent["patient"] = {"reference": patient_ref}
            # Default performer to patient
            if not performer_ref:
                consent["performer"] = [{"reference": patient_ref}]

        if performer_ref:
            consent["performer"] = [{"reference": performer_ref}]

        if organization_ref:
            consent["organization"] = [{"reference": organization_ref}]

        # Add verification (signature tracking)
        consent["verification"] = [
            {
                "verified": True,
                "verifiedWith": consent.get("performer", [{"display": "Patient"}])[0],
                "verificationDate": self._generate_datetime(),
            }
        ]

        # Add provision details
        if include_provision:
            consent["provision"] = self._generate_provision(policy_rule["code"])

        return consent

    def _generate_provision(self, policy_type: str) -> dict[str, Any]:
        """Generate consent provision rules.

        Args:
            policy_type: OPTIN, OPTOUT, or OPTINR

        Returns:
            Provision structure
        """
        # Base provision type
        provision_type = "permit" if policy_type in ["OPTIN", "OPTINR"] else "deny"

        provision: dict[str, Any] = {
            "type": provision_type,
            "period": {
                "start": self._generate_date(),
                "end": f"{self.faker.random_int(min=2025, max=2030)}-12-31",
            },
            "action": [
                {
                    "coding": [self.faker.random_element(self.PROVISION_ACTIONS)],
                }
                for _ in range(self.faker.random_int(min=1, max=3))
            ],
        }

        # For opt-in with restrictions, add some nested deny provisions
        if policy_type == "OPTINR":
            # Add some specific restrictions
            restricted_class = self.faker.random_element(self.DATA_CLASSES)
            provision["provision"] = [
                {
                    "type": "deny",
                    "class": [
                        {
                            "system": restricted_class["system"],
                            "code": restricted_class["code"],
                            "display": restricted_class["display"],
                        }
                    ],
                }
            ]

        return provision
