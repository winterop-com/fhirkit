"""Math functions."""

import math
from decimal import Decimal
from typing import Any

from ...context import EvaluationContext
from ...functions import FunctionRegistry


@FunctionRegistry.register("abs")
def fn_abs(ctx: EvaluationContext, collection: list[Any]) -> list[Any]:
    """Returns the absolute value."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)):
        return [abs(value)]
    return []


@FunctionRegistry.register("ceiling")
def fn_ceiling(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the smallest integer >= value."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)):
        return [math.ceil(value)]
    return []


@FunctionRegistry.register("floor")
def fn_floor(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the largest integer <= value."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)):
        return [math.floor(value)]
    return []


@FunctionRegistry.register("round")
def fn_round(ctx: EvaluationContext, collection: list[Any], precision: int = 0) -> list[Any]:
    """Rounds to the specified precision."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)):
        return [round(float(value), int(precision))]
    return []


@FunctionRegistry.register("truncate")
def fn_truncate(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Truncates to integer by removing decimal portion."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)):
        return [int(value)]
    return []


@FunctionRegistry.register("sqrt")
def fn_sqrt(ctx: EvaluationContext, collection: list[Any]) -> list[float]:
    """Returns the square root."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)) and value >= 0:
        return [math.sqrt(float(value))]
    return []


@FunctionRegistry.register("ln")
def fn_ln(ctx: EvaluationContext, collection: list[Any]) -> list[float]:
    """Returns the natural logarithm."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)) and value > 0:
        return [math.log(float(value))]
    return []


@FunctionRegistry.register("log")
def fn_log(ctx: EvaluationContext, collection: list[Any], base: float) -> list[float]:
    """Returns the logarithm with given base."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)) and value > 0:
        return [math.log(float(value), float(base))]
    return []


@FunctionRegistry.register("power")
def fn_power(ctx: EvaluationContext, collection: list[Any], exponent: float) -> list[float]:
    """Returns value raised to the exponent."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)):
        return [math.pow(float(value), float(exponent))]
    return []


@FunctionRegistry.register("exp")
def fn_exp(ctx: EvaluationContext, collection: list[Any]) -> list[float]:
    """Returns e raised to the power of value."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, (int, float, Decimal)):
        return [math.exp(float(value))]
    return []


# Aggregate functions


@FunctionRegistry.register("min")
def fn_min(ctx: EvaluationContext, collection: list[Any]) -> list[Any]:
    """Returns the minimum value in the collection.

    Works with integers, decimals, strings, dates, datetimes, times, and quantities.
    Returns empty if the collection is empty or contains incomparable types.
    """
    if not collection:
        return []

    # Filter to comparable values only
    comparable = [v for v in collection if _is_comparable(v)]
    if not comparable:
        return []

    # Check all values are of compatible types
    first_type = _get_comparison_type(comparable[0])
    if not all(_get_comparison_type(v) == first_type for v in comparable):
        return []  # Mixed types not comparable

    try:
        return [min(comparable, key=_comparison_key)]
    except (TypeError, ValueError):
        return []


@FunctionRegistry.register("max")
def fn_max(ctx: EvaluationContext, collection: list[Any]) -> list[Any]:
    """Returns the maximum value in the collection.

    Works with integers, decimals, strings, dates, datetimes, times, and quantities.
    Returns empty if the collection is empty or contains incomparable types.
    """
    if not collection:
        return []

    # Filter to comparable values only
    comparable = [v for v in collection if _is_comparable(v)]
    if not comparable:
        return []

    # Check all values are of compatible types
    first_type = _get_comparison_type(comparable[0])
    if not all(_get_comparison_type(v) == first_type for v in comparable):
        return []  # Mixed types not comparable

    try:
        return [max(comparable, key=_comparison_key)]
    except (TypeError, ValueError):
        return []


@FunctionRegistry.register("sum")
def fn_sum(ctx: EvaluationContext, collection: list[Any]) -> list[Any]:
    """Returns the sum of all values in the collection.

    Works with integers and decimals. Returns 0 for empty collection.
    For quantities, all must have the same unit.
    """
    from ...types import Quantity

    if not collection:
        return [0]

    # Check if all are quantities
    if all(isinstance(v, Quantity) for v in collection):
        units = {v.unit for v in collection}
        if len(units) != 1:
            return []  # Mixed units
        total = sum(v.value for v in collection)
        return [Quantity(value=total, unit=collection[0].unit)]

    # Filter to numeric values
    numeric = [v for v in collection if isinstance(v, (int, float, Decimal))]
    if not numeric:
        return [0]

    # Use Decimal for precision if any Decimals present
    if any(isinstance(v, Decimal) for v in numeric):
        return [sum(Decimal(str(v)) for v in numeric)]

    return [sum(numeric)]


@FunctionRegistry.register("avg")
def fn_avg(ctx: EvaluationContext, collection: list[Any]) -> list[Any]:
    """Returns the average of all values in the collection.

    Works with integers and decimals. Returns empty for empty collection.
    For quantities, all must have the same unit.
    """
    from ...types import Quantity

    if not collection:
        return []

    # Check if all are quantities
    if all(isinstance(v, Quantity) for v in collection):
        units = {v.unit for v in collection}
        if len(units) != 1:
            return []  # Mixed units
        total = sum(v.value for v in collection)
        avg_value = total / len(collection)
        return [Quantity(value=avg_value, unit=collection[0].unit)]

    # Filter to numeric values
    numeric = [v for v in collection if isinstance(v, (int, float, Decimal))]
    if not numeric:
        return []

    # Use Decimal for precision if any Decimals present
    if any(isinstance(v, Decimal) for v in numeric):
        total = sum(Decimal(str(v)) for v in numeric)
        return [total / len(numeric)]

    return [sum(numeric) / len(numeric)]


def _is_comparable(value: Any) -> bool:
    """Check if a value can be compared for min/max."""
    from ...types import FHIRDate, FHIRDateTime, FHIRTime, Quantity

    return isinstance(value, (int, float, Decimal, str, FHIRDate, FHIRDateTime, FHIRTime, Quantity))


def _get_comparison_type(value: Any) -> str:
    """Get the comparison type category for a value."""
    from ...types import FHIRDate, FHIRDateTime, FHIRTime, Quantity

    if isinstance(value, (int, float, Decimal)):
        return "numeric"
    if isinstance(value, str):
        return "string"
    if isinstance(value, FHIRDate):
        return "date"
    if isinstance(value, FHIRDateTime):
        return "datetime"
    if isinstance(value, FHIRTime):
        return "time"
    if isinstance(value, Quantity):
        return f"quantity:{value.unit}"
    return "unknown"


def _comparison_key(value: Any) -> Any:
    """Get a sortable key for a value."""
    from ...types import FHIRDate, FHIRDateTime, FHIRTime, Quantity

    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, str):
        return value
    if isinstance(value, FHIRDate):
        # Convert to tuple for comparison (handle None as 0)
        return (value.year, value.month or 0, value.day or 0)
    if isinstance(value, FHIRDateTime):
        return (
            value.year,
            value.month or 0,
            value.day or 0,
            value.hour or 0,
            value.minute or 0,
            value.second or 0,
            value.millisecond or 0,
        )
    if isinstance(value, FHIRTime):
        return (value.hour, value.minute or 0, value.second or 0, value.millisecond or 0)
    if isinstance(value, Quantity):
        return float(value.value)
    return value
