"""SearchParameter resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class SearchParameterGenerator(FHIRResourceGenerator):
    """Generator for FHIR SearchParameter resources."""

    # Publication status codes
    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    # Search parameter type codes
    TYPE_CODES = [
        "number",
        "date",
        "string",
        "token",
        "reference",
        "composite",
        "quantity",
        "uri",
        "special",
    ]

    # XPath usage codes
    XPATH_USAGE_CODES = ["normal", "phonetic", "nearby", "distance", "other"]

    # Comparator codes
    COMPARATOR_CODES = ["eq", "ne", "gt", "lt", "ge", "le", "sa", "eb", "ap"]

    # Modifier codes
    MODIFIER_CODES = [
        "missing",
        "exact",
        "contains",
        "not",
        "text",
        "in",
        "not-in",
        "below",
        "above",
        "type",
        "identifier",
        "ofType",
    ]

    # Common resource types for base
    BASE_RESOURCE_TYPES = [
        "Patient",
        "Observation",
        "Condition",
        "Procedure",
        "Encounter",
        "MedicationRequest",
        "DiagnosticReport",
        "Practitioner",
        "Organization",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        param_id: str | None = None,
        url: str | None = None,
        name: str | None = None,
        code: str | None = None,
        param_type: str | None = None,
        base: list[str] | None = None,
        status: str = "active",
        expression: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SearchParameter resource.

        Args:
            param_id: Resource ID (generates UUID if None)
            url: Canonical URL for the search parameter
            name: Computer-friendly name
            code: Code used in URL
            param_type: Type of search parameter
            base: Resource types this applies to
            status: Publication status
            expression: FHIRPath expression
            description: Natural language description

        Returns:
            SearchParameter FHIR resource
        """
        if param_id is None:
            param_id = self._generate_id()

        if name is None:
            name = f"{self.faker.word().lower()}-{self.faker.word().lower()}"

        if code is None:
            code = name.replace("-", "_")

        if param_type is None:
            param_type = self.faker.random_element(self.TYPE_CODES)

        if base is None:
            base = [self.faker.random_element(self.BASE_RESOURCE_TYPES)]

        if url is None:
            url = f"http://example.org/fhir/SearchParameter/{name}"

        if description is None:
            description = f"Search parameter for {', '.join(base)} by {code}"

        search_parameter: dict[str, Any] = {
            "resourceType": "SearchParameter",
            "id": param_id,
            "meta": self._generate_meta(),
            "url": url,
            "version": f"{self.faker.random_int(1, 5)}.0.0",
            "name": name,
            "status": status,
            "experimental": self.faker.boolean(chance_of_getting_true=30),
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "description": description,
            "code": code,
            "base": base,
            "type": param_type,
        }

        # Add expression for supported types
        if expression:
            search_parameter["expression"] = expression
        elif param_type in ["token", "string", "reference", "date"]:
            # Generate a reasonable FHIRPath expression
            field_names = {
                "token": ["code", "status", "identifier", "type"],
                "string": ["name", "description", "title", "text"],
                "reference": ["subject", "patient", "author", "performer"],
                "date": ["date", "effectiveDateTime", "authoredOn", "issued"],
            }
            field = self.faker.random_element(field_names.get(param_type, ["value"]))
            search_parameter["expression"] = f"{base[0]}.{field}"

        # Add target for reference types
        if param_type == "reference":
            search_parameter["target"] = [self.faker.random_element(self.BASE_RESOURCE_TYPES)]

        # Add modifiers for applicable types
        if param_type in ["string", "token", "reference"]:
            applicable_modifiers = {
                "string": ["exact", "contains", "missing"],
                "token": ["text", "not", "in", "not-in", "missing"],
                "reference": ["type", "identifier", "missing"],
            }
            search_parameter["modifier"] = applicable_modifiers[param_type]

        # Add comparators for numeric and date types
        if param_type in ["number", "date", "quantity"]:
            search_parameter["comparator"] = ["eq", "ne", "gt", "lt", "ge", "le"]

        # Add multiple OR/AND support
        search_parameter["multipleOr"] = True
        search_parameter["multipleAnd"] = True

        return search_parameter

    def generate_for_resource(
        self,
        resource_type: str,
        field_name: str,
        param_type: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a SearchParameter for a specific resource field.

        Args:
            resource_type: The resource type (e.g., "Patient")
            field_name: The field to search on
            param_type: Type of search parameter

        Returns:
            SearchParameter FHIR resource
        """
        code = field_name.lower().replace("_", "-")
        name = f"{resource_type.lower()}-{code}"

        return self.generate(
            name=name,
            code=code,
            param_type=param_type,
            base=[resource_type],
            expression=f"{resource_type}.{field_name}",
            description=f"Search {resource_type} by {field_name}",
            **kwargs,
        )
