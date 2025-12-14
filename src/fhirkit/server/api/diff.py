"""Resource diff implementation for FHIR $diff operation.

This module provides functionality to compare two FHIR resources or
two versions of the same resource and return the differences as
JSON Patch-style operations.
"""

from typing import Any


def compute_diff(source: dict[str, Any], target: dict[str, Any]) -> list[dict[str, Any]]:
    """Compute differences between two resources.

    Returns a list of JSON Patch-style operations that would transform
    the source into the target.

    Args:
        source: The original/older resource
        target: The new/current resource

    Returns:
        List of operations with 'op', 'path', and optionally 'value' keys
    """
    operations: list[dict[str, Any]] = []

    def compare(path: str, old_val: Any, new_val: Any) -> None:
        """Recursively compare values and collect differences."""
        # If values are equal, no operation needed
        if old_val == new_val:
            return

        # Handle None cases
        if old_val is None and new_val is not None:
            operations.append({"op": "add", "path": path, "value": new_val})
            return

        if old_val is not None and new_val is None:
            operations.append({"op": "remove", "path": path})
            return

        # Handle type mismatches
        if type(old_val) is not type(new_val):
            operations.append({"op": "replace", "path": path, "value": new_val})
            return

        # Handle dicts - recurse into them
        if isinstance(old_val, dict):
            all_keys = set(old_val.keys()) | set(new_val.keys())
            for key in sorted(all_keys):  # Sort for consistent output
                child_path = f"{path}/{key}" if path else f"/{key}"
                compare(child_path, old_val.get(key), new_val.get(key))
            return

        # Handle lists - simplified comparison
        if isinstance(old_val, list):
            # For arrays, we do a simple element-by-element comparison
            # This is simplified; a full diff would use LCS algorithm
            max_len = max(len(old_val), len(new_val))

            for i in range(max_len):
                child_path = f"{path}/{i}"

                if i >= len(old_val):
                    # New element added
                    operations.append({"op": "add", "path": child_path, "value": new_val[i]})
                elif i >= len(new_val):
                    # Element removed - we need to remove from the end first
                    # so indices don't shift during application
                    pass  # Handle below
                else:
                    # Both exist - compare them
                    compare(child_path, old_val[i], new_val[i])

            # Handle removals (in reverse order to preserve indices)
            if len(new_val) < len(old_val):
                for i in range(len(old_val) - 1, len(new_val) - 1, -1):
                    operations.append({"op": "remove", "path": f"{path}/{i}"})
            return

        # Primitive types - simple replacement
        operations.append({"op": "replace", "path": path, "value": new_val})

    # Start comparison at root
    compare("", source, target)

    return operations


def diff_to_parameters(operations: list[dict[str, Any]], include_values: bool = True) -> dict[str, Any]:
    """Convert diff operations to a FHIR Parameters resource.

    Args:
        operations: List of diff operations
        include_values: Whether to include full values (can be large)

    Returns:
        FHIR Parameters resource
    """
    parameters = []

    for op in operations:
        parts = [
            {"name": "type", "valueCode": op["op"]},
            {"name": "path", "valueString": op["path"]},
        ]

        if include_values and "value" in op:
            value = op["value"]
            # Handle different value types
            if isinstance(value, bool):
                parts.append({"name": "value", "valueBoolean": value})
            elif isinstance(value, int):
                parts.append({"name": "value", "valueInteger": value})
            elif isinstance(value, float):
                parts.append({"name": "value", "valueDecimal": value})
            elif isinstance(value, str):
                parts.append({"name": "value", "valueString": value})
            elif isinstance(value, (dict, list)):
                # Complex types - serialize as string for display
                import json

                parts.append({"name": "value", "valueString": json.dumps(value)})

        parameters.append({"name": "operation", "part": parts})

    return {
        "resourceType": "Parameters",
        "parameter": parameters,
    }
