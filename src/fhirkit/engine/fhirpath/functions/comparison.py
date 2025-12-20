"""Comparison functions and operators."""

from decimal import Decimal
from typing import Any

from ...context import EvaluationContext
from ...functions import FunctionRegistry
from ...types import FHIRDate, FHIRDateTime, FHIRTime


def _normalize_for_comparison(value: Any) -> Any:
    """Normalize a value for comparison.

    Converts date strings to FHIRDate/FHIRDateTime for proper comparison.
    """
    if isinstance(value, str):
        # Try to parse as date or datetime
        if "T" in value or len(value) > 10:
            # Might be a datetime
            try:
                return FHIRDateTime.parse(value)
            except (ValueError, AttributeError):
                pass
        # Try as date
        try:
            return FHIRDate.parse(value)
        except (ValueError, AttributeError):
            pass
    return value


def equals(left: Any, right: Any) -> bool | None:
    """
    FHIRPath equality comparison.

    Returns None if either operand is empty/null.
    """
    if left is None or right is None:
        return None

    # Handle lists (should be singletons for comparison)
    if isinstance(left, list):
        if not left:
            return None
        left = left[0]
    if isinstance(right, list):
        if not right:
            return None
        right = right[0]

    # Normalize date strings to FHIRDate/FHIRDateTime
    left = _normalize_for_comparison(left)
    right = _normalize_for_comparison(right)

    # Type-specific comparison
    if type(left) is not type(right):
        # Different types are not equal (with some exceptions)
        # int, float, and Decimal can be compared
        if isinstance(left, (int, float, Decimal)) and isinstance(right, (int, float, Decimal)):
            return float(left) == float(right)
        return False

    return left == right


def equivalent(left: Any, right: Any) -> bool:
    """
    FHIRPath equivalence comparison (~).

    Empty collections are equivalent to empty collections.
    Comparison is case-insensitive for strings.
    """
    # Handle lists
    if isinstance(left, list):
        left = left[0] if len(left) == 1 else (None if not left else left)
    if isinstance(right, list):
        right = right[0] if len(right) == 1 else (None if not right else right)

    # Both empty/null are equivalent
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False

    # String comparison is case-insensitive
    if isinstance(left, str) and isinstance(right, str):
        return left.lower() == right.lower()

    return left == right


def compare(left: Any, right: Any) -> int | None:
    """
    Compare two values.

    Returns:
        -1 if left < right
        0 if left == right
        1 if left > right
        None if not comparable
    """
    if left is None or right is None:
        return None

    # Handle lists (should be singletons)
    if isinstance(left, list):
        if not left:
            return None
        left = left[0]
    if isinstance(right, list):
        if not right:
            return None
        right = right[0]

    # Normalize date strings to FHIRDate/FHIRDateTime
    left = _normalize_for_comparison(left)
    right = _normalize_for_comparison(right)

    try:
        if left < right:
            return -1
        elif left > right:
            return 1
        else:
            return 0
    except TypeError:
        return None


@FunctionRegistry.register("=")
def fn_equals(ctx: EvaluationContext, left: list[Any], right: list[Any]) -> list[bool]:
    """Equality operator."""
    result = equals(left, right)
    if result is None:
        return []
    return [result]


@FunctionRegistry.register("!=")
def fn_not_equals(ctx: EvaluationContext, left: list[Any], right: list[Any]) -> list[bool]:
    """Inequality operator."""
    result = equals(left, right)
    if result is None:
        return []
    return [not result]


@FunctionRegistry.register("~")
def fn_equivalent(ctx: EvaluationContext, left: list[Any], right: list[Any]) -> list[bool]:
    """Equivalence operator."""
    return [equivalent(left, right)]


@FunctionRegistry.register("!~")
def fn_not_equivalent(ctx: EvaluationContext, left: list[Any], right: list[Any]) -> list[bool]:
    """Not equivalent operator."""
    return [not equivalent(left, right)]


@FunctionRegistry.register("<")
def fn_less_than(ctx: EvaluationContext, left: list[Any], right: list[Any]) -> list[bool]:
    """Less than operator."""
    result = compare(left, right)
    if result is None:
        return []
    return [result < 0]


@FunctionRegistry.register(">")
def fn_greater_than(ctx: EvaluationContext, left: list[Any], right: list[Any]) -> list[bool]:
    """Greater than operator."""
    result = compare(left, right)
    if result is None:
        return []
    return [result > 0]


@FunctionRegistry.register("<=")
def fn_less_or_equal(ctx: EvaluationContext, left: list[Any], right: list[Any]) -> list[bool]:
    """Less than or equal operator."""
    result = compare(left, right)
    if result is None:
        return []
    return [result <= 0]


@FunctionRegistry.register(">=")
def fn_greater_or_equal(ctx: EvaluationContext, left: list[Any], right: list[Any]) -> list[bool]:
    """Greater than or equal operator."""
    result = compare(left, right)
    if result is None:
        return []
    return [result >= 0]
