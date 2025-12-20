"""TerminologyCapabilities resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class TerminologyCapabilitiesGenerator(FHIRResourceGenerator):
    """Generator for FHIR TerminologyCapabilities resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    CODE_SEARCH_SUPPORT = ["explicit", "all"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        capabilities_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        kind: str = "instance",
        code_systems: list[dict[str, Any]] | None = None,
        expansion: dict[str, Any] | None = None,
        code_search: str | None = None,
        validate_code: dict[str, Any] | None = None,
        translation: dict[str, Any] | None = None,
        closure: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a TerminologyCapabilities resource.

        Args:
            capabilities_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            kind: instance | capability | requirements
            code_systems: Supported code systems
            expansion: Expansion parameters
            code_search: Code search support
            validate_code: Code validation support
            translation: Translation support
            closure: Closure support

        Returns:
            TerminologyCapabilities FHIR resource
        """
        if capabilities_id is None:
            capabilities_id = self._generate_id()

        if name is None:
            name = f"TerminologyCapabilities{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = "Terminology Server Capabilities"

        terminology_capabilities: dict[str, Any] = {
            "resourceType": "TerminologyCapabilities",
            "id": capabilities_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/TerminologyCapabilities/{capabilities_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "kind": kind,
        }

        if description:
            terminology_capabilities["description"] = description
        else:
            terminology_capabilities["description"] = "Terminology server capabilities statement"

        # Add code systems
        if code_systems:
            terminology_capabilities["codeSystem"] = code_systems
        else:
            terminology_capabilities["codeSystem"] = self._generate_code_systems()

        # Add expansion
        if expansion:
            terminology_capabilities["expansion"] = expansion
        else:
            terminology_capabilities["expansion"] = {
                "hierarchical": True,
                "paging": True,
                "incomplete": False,
            }

        # Add code search support
        if code_search:
            terminology_capabilities["codeSearch"] = code_search
        else:
            terminology_capabilities["codeSearch"] = self.faker.random_element(self.CODE_SEARCH_SUPPORT)

        # Add validate code support
        if validate_code:
            terminology_capabilities["validateCode"] = validate_code
        else:
            terminology_capabilities["validateCode"] = {"translations": True}

        # Add translation support
        if translation:
            terminology_capabilities["translation"] = translation
        elif self.faker.boolean(chance_of_getting_true=70):
            terminology_capabilities["translation"] = {"needsMap": True}

        # Add closure support
        if closure:
            terminology_capabilities["closure"] = closure
        elif self.faker.boolean(chance_of_getting_true=50):
            terminology_capabilities["closure"] = {"translation": True}

        return terminology_capabilities

    def _generate_code_systems(self) -> list[dict[str, Any]]:
        """Generate supported code systems."""
        systems = [
            {"uri": "http://snomed.info/sct", "name": "SNOMED CT"},
            {"uri": "http://loinc.org", "name": "LOINC"},
            {"uri": "http://hl7.org/fhir/sid/icd-10", "name": "ICD-10"},
            {"uri": "http://www.nlm.nih.gov/research/umls/rxnorm", "name": "RxNorm"},
        ]

        selected = self.faker.random_elements(systems, length=self.faker.random_int(1, 4))
        return [
            {
                "uri": sys["uri"],
                "version": [
                    {
                        "code": self.faker.date_this_year().strftime("%Y%m"),
                        "isDefault": True,
                    }
                ],
            }
            for sys in selected
        ]

    def generate_basic_capabilities(self, **kwargs: Any) -> dict[str, Any]:
        """Generate basic terminology capabilities.

        Returns:
            TerminologyCapabilities FHIR resource
        """
        return self.generate(
            title="Basic Terminology Server",
            code_search="explicit",
            expansion={"hierarchical": False, "paging": False, "incomplete": False},
            **kwargs,
        )
