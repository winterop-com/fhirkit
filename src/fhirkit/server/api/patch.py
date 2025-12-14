"""JSON Patch implementation for FHIR resources (RFC 6902).

This module provides JSON Patch operations as defined in RFC 6902 for
partial updates to FHIR resources.

Supported operations:
- add: Add a value at a path
- remove: Remove a value at a path
- replace: Replace a value at a path
- move: Move a value from one path to another
- copy: Copy a value from one path to another
- test: Test that a value equals the expected value

Example:
    from fhirkit.server.api.patch import apply_json_patch, PatchError

    resource = {"resourceType": "Patient", "active": True, "name": [{"family": "Smith"}]}
    operations = [
        {"op": "replace", "path": "/active", "value": False},
        {"op": "add", "path": "/name/0/given", "value": ["John"]}
    ]

    try:
        patched = apply_json_patch(resource, operations)
    except PatchError as e:
        print(f"Patch failed: {e}")
"""

import copy
from typing import Any


class PatchError(Exception):
    """Exception raised when a JSON Patch operation fails."""

    def __init__(self, message: str, path: str | None = None):
        self.message = message
        self.path = path
        super().__init__(message)


def apply_json_patch(resource: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply JSON Patch operations to a resource.

    Args:
        resource: The FHIR resource to patch
        operations: List of JSON Patch operations

    Returns:
        The patched resource (new copy)

    Raises:
        PatchError: If any operation fails
    """
    result = copy.deepcopy(resource)

    for i, op in enumerate(operations):
        operation = op.get("op")
        path = op.get("path", "")

        if not operation:
            raise PatchError(f"Operation {i}: missing 'op' field")

        try:
            if operation == "add":
                if "value" not in op:
                    raise PatchError(f"Operation {i}: 'add' requires 'value'", path)
                result = _apply_add(result, path, op["value"])

            elif operation == "remove":
                result = _apply_remove(result, path)

            elif operation == "replace":
                if "value" not in op:
                    raise PatchError(f"Operation {i}: 'replace' requires 'value'", path)
                result = _apply_replace(result, path, op["value"])

            elif operation == "move":
                from_path = op.get("from")
                if not from_path:
                    raise PatchError(f"Operation {i}: 'move' requires 'from'", path)
                result = _apply_move(result, from_path, path)

            elif operation == "copy":
                from_path = op.get("from")
                if not from_path:
                    raise PatchError(f"Operation {i}: 'copy' requires 'from'", path)
                result = _apply_copy(result, from_path, path)

            elif operation == "test":
                if "value" not in op:
                    raise PatchError(f"Operation {i}: 'test' requires 'value'", path)
                _apply_test(result, path, op["value"])

            else:
                raise PatchError(f"Operation {i}: unknown operation '{operation}'")

        except PatchError:
            raise
        except Exception as e:
            raise PatchError(f"Operation {i} ({operation}): {e}", path) from e

    return result


def _parse_path(path: str) -> list[str | int]:
    """Parse a JSON Pointer path into segments.

    Args:
        path: JSON Pointer path (e.g., "/name/0/family")

    Returns:
        List of path segments

    Raises:
        PatchError: If path is invalid
    """
    if not path:
        return []

    if not path.startswith("/"):
        raise PatchError(f"Invalid path: must start with '/' (got '{path}')", path)

    segments: list[str | int] = []
    for part in path[1:].split("/"):
        # Unescape JSON Pointer special characters
        part = part.replace("~1", "/").replace("~0", "~")

        # Check if it's an array index
        if part.isdigit():
            segments.append(int(part))
        elif part == "-":
            # Special case: append to array
            segments.append("-")
        else:
            segments.append(part)

    return segments


def _get_value(obj: Any, path: str) -> Any:
    """Get value at a JSON Pointer path.

    Args:
        obj: The object to traverse
        path: JSON Pointer path

    Returns:
        Value at the path

    Raises:
        PatchError: If path doesn't exist
    """
    segments = _parse_path(path)
    current = obj

    for i, segment in enumerate(segments):
        current_path = "/" + "/".join(str(s) for s in segments[: i + 1])

        if isinstance(current, dict):
            if not isinstance(segment, str):
                raise PatchError(f"Expected string key for object at {current_path}", path)
            if segment not in current:
                raise PatchError(f"Path not found: {current_path}", path)
            current = current[segment]

        elif isinstance(current, list):
            if not isinstance(segment, int):
                raise PatchError(f"Expected integer index for array at {current_path}", path)
            if segment < 0 or segment >= len(current):
                raise PatchError(f"Array index out of bounds: {segment} at {current_path}", path)
            current = current[segment]

        else:
            raise PatchError(f"Cannot traverse into {type(current).__name__} at {current_path}", path)

    return current


def _set_value(obj: Any, path: str, value: Any) -> Any:
    """Set value at a JSON Pointer path.

    Args:
        obj: The object to modify
        path: JSON Pointer path
        value: Value to set

    Returns:
        Modified object

    Raises:
        PatchError: If path is invalid
    """
    segments = _parse_path(path)

    if not segments:
        # Replace entire object
        return value

    # Navigate to parent
    current = obj
    for i, segment in enumerate(segments[:-1]):
        current_path = "/" + "/".join(str(s) for s in segments[: i + 1])

        if isinstance(current, dict):
            if not isinstance(segment, str):
                raise PatchError(f"Expected string key for object at {current_path}", path)
            if segment not in current:
                raise PatchError(f"Path not found: {current_path}", path)
            current = current[segment]

        elif isinstance(current, list):
            if not isinstance(segment, int):
                raise PatchError(f"Expected integer index for array at {current_path}", path)
            if segment < 0 or segment >= len(current):
                raise PatchError(f"Array index out of bounds: {segment}", path)
            current = current[segment]

        else:
            raise PatchError(f"Cannot traverse into {type(current).__name__}", path)

    # Set value on parent
    last_segment = segments[-1]

    if isinstance(current, dict):
        if not isinstance(last_segment, str):
            raise PatchError("Expected string key for object", path)
        current[last_segment] = value

    elif isinstance(current, list):
        if last_segment == "-":
            current.append(value)
        elif isinstance(last_segment, int):
            if last_segment < 0 or last_segment > len(current):
                raise PatchError(f"Array index out of bounds: {last_segment}", path)
            current.insert(last_segment, value)
        else:
            raise PatchError("Expected integer index or '-' for array", path)

    else:
        raise PatchError(f"Cannot set value on {type(current).__name__}", path)

    return obj


def _remove_value(obj: Any, path: str) -> Any:
    """Remove value at a JSON Pointer path.

    Args:
        obj: The object to modify
        path: JSON Pointer path

    Returns:
        Modified object

    Raises:
        PatchError: If path doesn't exist
    """
    segments = _parse_path(path)

    if not segments:
        raise PatchError("Cannot remove root document", path)

    # Navigate to parent
    current = obj
    for i, segment in enumerate(segments[:-1]):
        current_path = "/" + "/".join(str(s) for s in segments[: i + 1])

        if isinstance(current, dict):
            if segment not in current:
                raise PatchError(f"Path not found: {current_path}", path)
            current = current[segment]

        elif isinstance(current, list):
            if not isinstance(segment, int) or segment < 0 or segment >= len(current):
                raise PatchError(f"Invalid array index at {current_path}", path)
            current = current[segment]

        else:
            raise PatchError(f"Cannot traverse into {type(current).__name__}", path)

    # Remove from parent
    last_segment = segments[-1]

    if isinstance(current, dict):
        if last_segment not in current:
            raise PatchError(f"Path not found: {path}", path)
        del current[last_segment]

    elif isinstance(current, list):
        if not isinstance(last_segment, int) or last_segment < 0 or last_segment >= len(current):
            raise PatchError(f"Array index out of bounds: {last_segment}", path)
        del current[last_segment]

    else:
        raise PatchError(f"Cannot remove from {type(current).__name__}", path)

    return obj


def _apply_add(obj: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """Apply an 'add' operation.

    The 'add' operation adds a value to an object or array.
    For arrays, use '-' to append or an index to insert.
    """
    return _set_value(obj, path, value)


def _apply_remove(obj: dict[str, Any], path: str) -> dict[str, Any]:
    """Apply a 'remove' operation.

    The 'remove' operation removes a value at the specified path.
    """
    return _remove_value(obj, path)


def _apply_replace(obj: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """Apply a 'replace' operation.

    The 'replace' operation replaces an existing value.
    Unlike 'add', the path must already exist.
    """
    # Verify path exists first
    _get_value(obj, path)

    # Now set the value
    segments = _parse_path(path)

    if not segments:
        return value

    # Navigate to parent
    current: Any = obj
    for segment in segments[:-1]:
        if isinstance(current, dict) and isinstance(segment, str):
            current = current[segment]
        elif isinstance(current, list) and isinstance(segment, int):
            current = current[segment]

    # Replace value
    last_segment = segments[-1]
    if isinstance(current, dict) and isinstance(last_segment, str):
        current[last_segment] = value
    elif isinstance(current, list) and isinstance(last_segment, int):
        current[last_segment] = value

    return obj


def _apply_move(obj: dict[str, Any], from_path: str, to_path: str) -> dict[str, Any]:
    """Apply a 'move' operation.

    The 'move' operation removes the value at 'from' and adds it to 'path'.
    """
    # Get value from source
    value = _get_value(obj, from_path)

    # Remove from source
    obj = _remove_value(obj, from_path)

    # Add to destination
    return _set_value(obj, to_path, value)


def _apply_copy(obj: dict[str, Any], from_path: str, to_path: str) -> dict[str, Any]:
    """Apply a 'copy' operation.

    The 'copy' operation copies the value at 'from' to 'path'.
    """
    # Get value from source (deep copy to avoid shared references)
    value = copy.deepcopy(_get_value(obj, from_path))

    # Add to destination
    return _set_value(obj, to_path, value)


def _apply_test(obj: dict[str, Any], path: str, expected: Any) -> None:
    """Apply a 'test' operation.

    The 'test' operation checks that the value at 'path' equals 'value'.
    Raises PatchError if the test fails.
    """
    actual = _get_value(obj, path)

    if actual != expected:
        raise PatchError(f"Test failed: expected {expected!r}, got {actual!r}", path)
