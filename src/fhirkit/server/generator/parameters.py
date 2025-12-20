"""Parameters resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ParametersGenerator(FHIRResourceGenerator):
    """Generator for FHIR Parameters resources."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        params_id: str | None = None,
        parameters: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Parameters resource.

        Args:
            params_id: Resource ID (generates UUID if None)
            parameters: List of parameter entries

        Returns:
            Parameters FHIR resource
        """
        if params_id is None:
            params_id = self._generate_id()

        params_resource: dict[str, Any] = {
            "resourceType": "Parameters",
            "id": params_id,
        }

        if parameters:
            params_resource["parameter"] = parameters

        return params_resource

    def generate_with_values(
        self,
        values: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate Parameters from a dictionary of name-value pairs.

        Args:
            values: Dictionary of parameter names to values

        Returns:
            Parameters FHIR resource
        """
        parameters = []

        for name, value in values.items():
            param: dict[str, Any] = {"name": name}

            # Determine value type and add appropriate field
            if isinstance(value, str):
                param["valueString"] = value
            elif isinstance(value, bool):
                param["valueBoolean"] = value
            elif isinstance(value, int):
                param["valueInteger"] = value
            elif isinstance(value, float):
                param["valueDecimal"] = value
            elif isinstance(value, dict):
                if "resourceType" in value:
                    param["resource"] = value
                elif "coding" in value:
                    param["valueCodeableConcept"] = value
                elif "reference" in value:
                    param["valueReference"] = value
                else:
                    # Nested parameters
                    param["part"] = self._dict_to_parts(value)
            elif isinstance(value, list):
                # Multiple values with same name
                for v in value:
                    sub_param: dict[str, Any] = {"name": name}
                    if isinstance(v, str):
                        sub_param["valueString"] = v
                    elif isinstance(v, dict) and "resourceType" in v:
                        sub_param["resource"] = v
                    parameters.append(sub_param)
                continue

            parameters.append(param)

        return self.generate(parameters=parameters, **kwargs)

    def _dict_to_parts(self, d: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert a dictionary to parameter parts."""
        parts = []
        for name, value in d.items():
            part: dict[str, Any] = {"name": name}
            if isinstance(value, str):
                part["valueString"] = value
            elif isinstance(value, bool):
                part["valueBoolean"] = value
            elif isinstance(value, int):
                part["valueInteger"] = value
            elif isinstance(value, dict):
                if "resourceType" in value:
                    part["resource"] = value
                else:
                    part["part"] = self._dict_to_parts(value)
            parts.append(part)
        return parts

    def generate_operation_input(
        self,
        operation_code: str,
        **input_params: Any,
    ) -> dict[str, Any]:
        """Generate input Parameters for an operation.

        Args:
            operation_code: The operation code (for context)
            **input_params: Named input parameters

        Returns:
            Parameters FHIR resource
        """
        return self.generate_with_values(input_params)

    def generate_operation_output(
        self,
        result: dict[str, Any] | None = None,
        **output_params: Any,
    ) -> dict[str, Any]:
        """Generate output Parameters for an operation.

        Args:
            result: Main result resource
            **output_params: Named output parameters

        Returns:
            Parameters FHIR resource
        """
        parameters = []

        if result:
            parameters.append(
                {
                    "name": "return",
                    "resource": result,
                }
            )

        for name, value in output_params.items():
            param: dict[str, Any] = {"name": name}
            if isinstance(value, str):
                param["valueString"] = value
            elif isinstance(value, bool):
                param["valueBoolean"] = value
            elif isinstance(value, dict) and "resourceType" in value:
                param["resource"] = value
            parameters.append(param)

        return self.generate(parameters=parameters)
