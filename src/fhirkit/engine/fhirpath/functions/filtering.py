"""Filtering functions: where, select, ofType, repeat."""

from typing import Any

from ...context import EvaluationContext
from ...functions import FunctionRegistry

# Note: where() is handled specially in the visitor because it needs
# to evaluate the criteria expression for each item with $this bound.
# We register a placeholder here for documentation purposes.


@FunctionRegistry.register("where")
def fn_where(ctx: EvaluationContext, collection: list[Any], *args: Any) -> list[Any]:
    """
    Filters the collection based on criteria.

    Note: This is handled by the visitor to properly evaluate criteria
    with $this bound to each element.
    """
    # Actual implementation is in the visitor
    raise NotImplementedError("where() is handled by the visitor")


@FunctionRegistry.register("select")
def fn_select(ctx: EvaluationContext, collection: list[Any], *args: Any) -> list[Any]:
    """
    Projects each element through an expression.

    Note: This is handled by the visitor to properly evaluate the
    projection expression with $this bound to each element.
    """
    # Actual implementation is in the visitor
    raise NotImplementedError("select() is handled by the visitor")


@FunctionRegistry.register("repeat")
def fn_repeat(ctx: EvaluationContext, collection: list[Any], *args: Any) -> list[Any]:
    """
    Repeatedly evaluates expression on each item until no new items.

    Note: This is handled by the visitor.
    """
    # Actual implementation is in the visitor
    raise NotImplementedError("repeat() is handled by the visitor")


def _is_type(item: Any, type_name: str) -> bool:
    """Check if an item is of the specified FHIRPath type.

    FHIRPath distinguishes between FHIR types and System types:
    - FHIR types: lowercase (boolean, integer, string, etc.)
    - System types: PascalCase (Boolean, Integer, String, etc.)

    These are NOT equivalent:
    - Patient.active.is(boolean) = true (FHIR boolean)
    - Patient.active.is(Boolean) = false (System Boolean)
    """
    from decimal import Decimal as PyDecimal

    from ...types import FHIRDate, FHIRDateTime, FHIRTime, Quantity

    # Parse namespace prefix
    namespace = None
    if type_name.startswith("System."):
        namespace = "System"
        type_name = type_name[7:]
    elif type_name.startswith("FHIR."):
        namespace = "FHIR"
        type_name = type_name[5:]

    # Get the actual type info of the item
    item_namespace, item_type = _get_type_info(item)

    # Handle FHIRPath System types (PascalCase)
    if type_name == "DateTime":
        return isinstance(item, FHIRDateTime)
    elif type_name == "Date":
        return isinstance(item, FHIRDate)
    elif type_name == "Time":
        return isinstance(item, FHIRTime)
    elif type_name == "Boolean":
        # System.Boolean - only match if explicitly System namespace or no FHIR values
        if namespace == "FHIR":
            return False  # FHIR.Boolean is not a valid type
        if namespace == "System":
            return False  # FHIR boolean is not System.Boolean
        # No namespace - check if it's a System type (should not match FHIR boolean)
        return False  # Don't match FHIR booleans with System.Boolean
    elif type_name == "Integer":
        if namespace == "FHIR":
            return False
        if namespace == "System":
            return False
        return False
    elif type_name == "Decimal":
        if namespace == "FHIR":
            return False
        if namespace == "System":
            return False
        return False
    elif type_name == "String":
        if namespace == "FHIR":
            return False
        if namespace == "System":
            return False
        return False
    elif type_name == "Quantity":
        return isinstance(item, (Quantity, dict)) and (not isinstance(item, dict) or "value" in item)

    # Handle FHIR primitive types (lowercase)
    if type_name == "boolean":
        if namespace == "System":
            return False  # System.boolean is not valid
        return isinstance(item, bool)
    elif type_name == "integer":
        if namespace == "System":
            return False
        return isinstance(item, int) and not isinstance(item, bool)
    elif type_name == "decimal":
        if namespace == "System":
            return False
        return isinstance(item, (float, PyDecimal)) and not isinstance(item, bool)
    elif type_name == "string":
        if namespace == "System":
            return False
        return isinstance(item, str)

    # Handle FHIR string-based element types (subtypes of string)
    if type_name in ("code", "id", "uri", "url", "canonical", "oid", "uuid", "markdown", "xhtml", "base64Binary"):
        # These are NOT equivalent to each other - a code is not an id
        # Without type metadata, we can't distinguish them from plain strings
        # Return False for specific subtypes to avoid false positives
        return False

    # Handle FHIR numeric element types (subtypes of Integer)
    if type_name == "positiveInt":
        return isinstance(item, int) and not isinstance(item, bool) and item > 0
    if type_name == "unsignedInt":
        return isinstance(item, int) and not isinstance(item, bool) and item >= 0
    if type_name == "integer64":
        return isinstance(item, int) and not isinstance(item, bool)

    # Handle "Element" - base type for all FHIR elements
    if type_name == "Element":
        return True

    # Handle "Resource" - base type for all resources
    if type_name == "Resource":
        return isinstance(item, dict) and "resourceType" in item

    if isinstance(item, dict):
        # Check resourceType for FHIR resources
        if item.get("resourceType") == type_name:
            return True
        # Check for complex types by their characteristic fields
        if type_name == "Coding" and "code" in item:
            return True
        if type_name == "CodeableConcept" and ("coding" in item or "text" in item):
            return True
        if type_name == "Reference" and ("reference" in item or "type" in item):
            return True
        if type_name == "Identifier" and ("value" in item or "system" in item):
            return True
        if type_name == "Period" and ("start" in item or "end" in item):
            return True
        if type_name == "HumanName" and ("family" in item or "given" in item or "text" in item):
            return True
        if type_name == "Address" and ("line" in item or "city" in item or "postalCode" in item):
            return True
        if type_name == "ContactPoint" and ("system" in item or "value" in item):
            return True
    return False


def _get_type_info(item: Any) -> tuple[str, str]:
    """Get the FHIRPath type info (namespace, name) for an item.

    Returns a tuple of (namespace, type_name).
    For FHIR elements, returns FHIR namespace with lowercase type names.
    For FHIRPath system types, returns System namespace with PascalCase names.
    """
    from decimal import Decimal as PyDecimal

    from ...types import FHIRDate, FHIRDateTime, FHIRTime, Quantity

    if isinstance(item, FHIRDateTime):
        return ("System", "DateTime")
    elif isinstance(item, FHIRDate):
        return ("System", "Date")
    elif isinstance(item, FHIRTime):
        return ("System", "Time")
    elif isinstance(item, bool):
        # FHIR boolean elements - use FHIR namespace
        return ("FHIR", "boolean")
    elif isinstance(item, int):
        # FHIR integer elements - use FHIR namespace
        return ("FHIR", "integer")
    elif isinstance(item, (float, PyDecimal)):
        # FHIR decimal elements - use FHIR namespace
        return ("FHIR", "decimal")
    elif isinstance(item, str):
        # FHIR string elements - use FHIR namespace
        return ("FHIR", "string")
    elif isinstance(item, Quantity):
        return ("System", "Quantity")
    elif isinstance(item, dict):
        resource_type = item.get("resourceType")
        if resource_type:
            return ("FHIR", resource_type)
        return ("FHIR", "Element")
    return ("System", "Any")


def _get_type_name(item: Any) -> str:
    """Get the FHIRPath type name of an item (for backwards compatibility)."""
    _, name = _get_type_info(item)
    return name


@FunctionRegistry.register("type")
def fn_type(ctx: EvaluationContext, collection: list[Any]) -> list[dict[str, str]]:
    """
    Returns the type of the input as a type specifier.

    Returns a collection of type information for each element.
    """
    if not collection:
        return []
    item = collection[0]
    namespace, type_name = _get_type_info(item)
    # Return as a type specifier structure
    return [{"namespace": namespace, "name": type_name}]


@FunctionRegistry.register("is")
def fn_is(ctx: EvaluationContext, collection: list[Any], type_name: str) -> list[bool]:
    """
    Returns true if the input is of the specified type.

    According to FHIRPath spec:
    - Returns empty if collection is empty
    - Returns true/false based on type check for single element
    - Multiple elements is an error (not implemented here, just use first)

    Args:
        type_name: The FHIRPath type name to check
    """
    if not collection:
        return []
    # For single element, return boolean result
    item = collection[0]
    return [_is_type(item, type_name)]


@FunctionRegistry.register("as")
def fn_as(ctx: EvaluationContext, collection: list[Any], type_name: str) -> list[Any]:
    """
    Casts a value to the specified type (or returns empty if not castable).

    Note: This is a simplified implementation that just checks if the value
    is already of the target type.
    """
    if not collection:
        return []
    item = collection[0]
    if _is_type(item, type_name):
        return [item]
    return []


@FunctionRegistry.register("ofType")
def fn_of_type(ctx: EvaluationContext, collection: list[Any], type_name: str) -> list[Any]:
    """
    Filters to elements that are of the specified type.

    Args:
        type_name: The FHIR type name to filter by
    """
    return [item for item in collection if _is_type(item, type_name)]
