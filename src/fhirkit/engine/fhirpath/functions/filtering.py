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
    """Check if an item is of the specified FHIRPath type."""
    from decimal import Decimal as PyDecimal

    from ...types import FHIRDate, FHIRDateTime, FHIRTime, Quantity

    # Handle FHIRPath system types
    if type_name == "DateTime":
        return isinstance(item, FHIRDateTime)
    elif type_name == "Date":
        return isinstance(item, FHIRDate)
    elif type_name == "Time":
        return isinstance(item, FHIRTime)
    elif type_name == "String":
        return isinstance(item, str)
    elif type_name == "Boolean":
        return isinstance(item, bool)
    elif type_name == "Integer":
        return isinstance(item, int) and not isinstance(item, bool)
    elif type_name == "Decimal":
        return isinstance(item, (float, PyDecimal)) and not isinstance(item, bool)
    elif type_name == "Quantity":
        return isinstance(item, (Quantity, dict)) and (not isinstance(item, dict) or "value" in item)
    elif isinstance(item, dict):
        # Check resourceType for FHIR resources
        return item.get("resourceType") == type_name
    return False


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


@FunctionRegistry.register("ofType")
def fn_of_type(ctx: EvaluationContext, collection: list[Any], type_name: str) -> list[Any]:
    """
    Filters to elements that are of the specified type.

    Args:
        type_name: The FHIR type name to filter by
    """
    return [item for item in collection if _is_type(item, type_name)]
