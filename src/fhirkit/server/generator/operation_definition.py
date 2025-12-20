"""OperationDefinition resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class OperationDefinitionGenerator(FHIRResourceGenerator):
    """Generator for FHIR OperationDefinition resources."""

    # Publication status codes
    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    # Operation kinds
    KIND_CODES = ["operation", "query"]

    # Parameter use codes
    PARAMETER_USE = ["in", "out"]

    # Common operation examples
    OPERATION_EXAMPLES = [
        {
            "code": "validate",
            "name": "Validate",
            "system": False,
            "type": True,
            "instance": True,
            "description": "Validate a resource",
        },
        {
            "code": "expand",
            "name": "Expand",
            "system": False,
            "type": True,
            "instance": True,
            "description": "Expand a ValueSet",
        },
        {
            "code": "lookup",
            "name": "Lookup",
            "system": False,
            "type": True,
            "instance": False,
            "description": "Lookup a code in a CodeSystem",
        },
        {
            "code": "everything",
            "name": "Everything",
            "system": False,
            "type": True,
            "instance": True,
            "description": "Fetch patient record",
        },
        {
            "code": "translate",
            "name": "Translate",
            "system": False,
            "type": True,
            "instance": True,
            "description": "Translate a code",
        },
        {
            "code": "subsumes",
            "name": "Subsumes",
            "system": False,
            "type": True,
            "instance": False,
            "description": "Check subsumption relationship",
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        op_id: str | None = None,
        name: str | None = None,
        code: str | None = None,
        kind: str = "operation",
        status: str = "active",
        system: bool = False,
        type_level: bool = True,
        instance: bool = True,
        resource: list[str] | None = None,
        parameters: list[dict[str, Any]] | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an OperationDefinition resource.

        Args:
            op_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            code: Operation code (e.g., "$validate")
            kind: operation or query
            status: Publication status
            system: Invoke at system level
            type_level: Invoke at type level
            instance: Invoke at instance level
            resource: Resource types this applies to
            parameters: Operation parameters
            description: Description of the operation

        Returns:
            OperationDefinition FHIR resource
        """
        if op_id is None:
            op_id = self._generate_id()

        # Use example operation if not specified
        if name is None or code is None:
            example = self.faker.random_element(self.OPERATION_EXAMPLES)
            name = name or str(example["name"])
            code = code or str(example["code"])
            system = bool(example.get("system", system))
            type_level = bool(example.get("type", type_level))
            instance = bool(example.get("instance", instance))
            desc = example.get("description")
            description = description or (str(desc) if desc else None)

        if resource is None:
            resource = ["Resource"]

        operation_definition: dict[str, Any] = {
            "resourceType": "OperationDefinition",
            "id": op_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/OperationDefinition/{code}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": f"{name} Operation",
            "status": status,
            "kind": kind,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
            "description": description or f"Operation to {name.lower() if name else 'execute'}",
            "code": code or "execute",
            "resource": resource,
            "system": system,
            "type": type_level,
            "instance": instance,
        }

        # Add parameters
        if parameters:
            operation_definition["parameter"] = parameters
        else:
            # Generate default parameters based on operation
            op_code = code or "execute"
            operation_definition["parameter"] = self._generate_default_parameters(op_code)

        return operation_definition

    def _generate_default_parameters(self, code: str) -> list[dict[str, Any]]:
        """Generate default parameters for common operations."""
        params: list[dict[str, Any]] = []

        if code == "validate":
            params = [
                {
                    "name": "resource",
                    "use": "in",
                    "min": 0,
                    "max": "1",
                    "type": "Resource",
                    "documentation": "Resource to validate",
                },
                {
                    "name": "return",
                    "use": "out",
                    "min": 1,
                    "max": "1",
                    "type": "OperationOutcome",
                    "documentation": "Validation results",
                },
            ]
        elif code == "expand":
            params = [
                {
                    "name": "url",
                    "use": "in",
                    "min": 0,
                    "max": "1",
                    "type": "uri",
                    "documentation": "ValueSet URL",
                },
                {
                    "name": "filter",
                    "use": "in",
                    "min": 0,
                    "max": "1",
                    "type": "string",
                    "documentation": "Filter criteria",
                },
                {
                    "name": "return",
                    "use": "out",
                    "min": 1,
                    "max": "1",
                    "type": "ValueSet",
                    "documentation": "Expanded ValueSet",
                },
            ]
        elif code == "everything":
            params = [
                {
                    "name": "start",
                    "use": "in",
                    "min": 0,
                    "max": "1",
                    "type": "date",
                    "documentation": "Start date filter",
                },
                {
                    "name": "end",
                    "use": "in",
                    "min": 0,
                    "max": "1",
                    "type": "date",
                    "documentation": "End date filter",
                },
                {
                    "name": "return",
                    "use": "out",
                    "min": 1,
                    "max": "1",
                    "type": "Bundle",
                    "documentation": "Patient record bundle",
                },
            ]
        else:
            # Generic parameters
            params = [
                {
                    "name": "return",
                    "use": "out",
                    "min": 1,
                    "max": "1",
                    "type": "Resource",
                    "documentation": "Operation result",
                },
            ]

        return params
