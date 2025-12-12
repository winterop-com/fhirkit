"""Boolean and logic functions."""

from typing import Any

from ...context import EvaluationContext
from ...functions import FunctionRegistry


@FunctionRegistry.register("not")
def fn_not(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Returns the boolean negation of the input."""
    if not collection:
        return []
    value = collection[0]
    if isinstance(value, bool):
        return [not value]
    return []


@FunctionRegistry.register("iif")
def fn_iif(
    ctx: EvaluationContext,
    collection: list[Any],
    true_result: Any = None,
    otherwise_result: Any = None,
) -> list[Any]:
    """
    If-then-else function.

    Note: This is handled specially by the visitor because the branches
    should only be evaluated based on the condition.
    """
    # Simple implementation - visitor may override for lazy evaluation
    if not collection:
        if otherwise_result is not None:
            return [otherwise_result] if not isinstance(otherwise_result, list) else otherwise_result
        return []

    condition = collection[0]
    if isinstance(condition, bool) and condition:
        if true_result is not None:
            return [true_result] if not isinstance(true_result, list) else true_result
        return []
    else:
        if otherwise_result is not None:
            return [otherwise_result] if not isinstance(otherwise_result, list) else otherwise_result
        return []


@FunctionRegistry.register("trace")
def fn_trace(ctx: EvaluationContext, collection: list[Any], name: str = "", *args: Any) -> list[Any]:
    """
    Logs the collection for debugging and returns it unchanged.

    In production, this is typically a no-op.
    """
    # In debug mode, this could log to a handler
    return collection


@FunctionRegistry.register("toBoolean")
def fn_to_boolean(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Converts the input to a boolean."""
    if not collection:
        return []

    value = collection[0]

    if isinstance(value, bool):
        return [value]

    if isinstance(value, str):
        lower = value.lower()
        if lower in ("true", "t", "yes", "y", "1", "1.0"):
            return [True]
        if lower in ("false", "f", "no", "n", "0", "0.0"):
            return [False]
        return []

    if isinstance(value, int):
        if value == 1:
            return [True]
        if value == 0:
            return [False]
        return []

    if isinstance(value, float):
        if value == 1.0:
            return [True]
        if value == 0.0:
            return [False]
        return []

    return []


@FunctionRegistry.register("convertsToBoolean")
def fn_converts_to_boolean(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Returns true if the input can be converted to a boolean."""
    result = fn_to_boolean(ctx, collection)
    return [len(result) > 0]


@FunctionRegistry.register("toInteger")
def fn_to_integer(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Converts the input to an integer."""
    if not collection:
        return []

    value = collection[0]

    if isinstance(value, bool):
        return [1 if value else 0]

    if isinstance(value, int):
        return [value]

    if isinstance(value, float):
        int_val = int(value)
        if value == float(int_val):
            return [int_val]
        return []

    if isinstance(value, str):
        try:
            # Must be whole number representation
            if "." in value:
                f = float(value)
                if f == int(f):
                    return [int(f)]
                return []
            return [int(value)]
        except ValueError:
            return []

    return []


@FunctionRegistry.register("convertsToInteger")
def fn_converts_to_integer(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Returns true if the input can be converted to an integer."""
    result = fn_to_integer(ctx, collection)
    return [len(result) > 0]


@FunctionRegistry.register("toDecimal")
def fn_to_decimal(ctx: EvaluationContext, collection: list[Any]) -> list[float]:
    """Converts the input to a decimal."""
    if not collection:
        return []

    value = collection[0]

    if isinstance(value, bool):
        return [1.0 if value else 0.0]

    if isinstance(value, (int, float)):
        return [float(value)]

    if isinstance(value, str):
        try:
            return [float(value)]
        except ValueError:
            return []

    return []


@FunctionRegistry.register("convertsToDecimal")
def fn_converts_to_decimal(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Returns true if the input can be converted to a decimal."""
    result = fn_to_decimal(ctx, collection)
    return [len(result) > 0]


@FunctionRegistry.register("toString")
def fn_to_string(ctx: EvaluationContext, collection: list[Any]) -> list[str]:
    """Converts the input to a string."""
    if not collection:
        return []

    value = collection[0]

    if isinstance(value, bool):
        return ["true" if value else "false"]

    if isinstance(value, (int, float)):
        return [str(value)]

    if isinstance(value, str):
        return [value]

    return []


@FunctionRegistry.register("convertsToString")
def fn_converts_to_string(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Returns true if the input can be converted to a string."""
    result = fn_to_string(ctx, collection)
    return [len(result) > 0]


@FunctionRegistry.register("toDate")
def fn_to_date(ctx: EvaluationContext, collection: list[Any]) -> list[str]:
    """Converts the input to a date."""
    if not collection:
        return []

    value = collection[0]

    if isinstance(value, str):
        # Basic date validation - YYYY-MM-DD format
        import re

        if re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", value):
            return [value]
        # Handle datetime by extracting date part
        if "T" in value:
            date_part = value.split("T")[0]
            if re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", date_part):
                return [date_part]
    return []


@FunctionRegistry.register("convertsToDate")
def fn_converts_to_date(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Returns true if the input can be converted to a date."""
    result = fn_to_date(ctx, collection)
    return [len(result) > 0]


@FunctionRegistry.register("toDateTime")
def fn_to_datetime(ctx: EvaluationContext, collection: list[Any]) -> list[str]:
    """Converts the input to a datetime."""
    if not collection:
        return []

    value = collection[0]

    if isinstance(value, str):
        import re

        # Full datetime or date-only (which implicitly becomes datetime)
        if re.match(r"^\d{4}(-\d{2}(-\d{2}(T\d{2}(:\d{2}(:\d{2}(\.\d+)?)?)?([Z+-]\d{2}:\d{2})?)?)?)?$", value):
            return [value]
    return []


@FunctionRegistry.register("convertsToDateTime")
def fn_converts_to_datetime(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Returns true if the input can be converted to a datetime."""
    result = fn_to_datetime(ctx, collection)
    return [len(result) > 0]


@FunctionRegistry.register("toTime")
def fn_to_time(ctx: EvaluationContext, collection: list[Any]) -> list[str]:
    """Converts the input to a time."""
    if not collection:
        return []

    value = collection[0]

    if isinstance(value, str):
        import re

        # Time format HH:MM:SS.fff
        if re.match(r"^\d{2}(:\d{2}(:\d{2}(\.\d+)?)?)?$", value):
            return [value]
        # Handle T prefix
        if value.startswith("T") and re.match(r"^T\d{2}(:\d{2}(:\d{2}(\.\d+)?)?)?$", value):
            return [value[1:]]
    return []


@FunctionRegistry.register("convertsToTime")
def fn_converts_to_time(ctx: EvaluationContext, collection: list[Any]) -> list[bool]:
    """Returns true if the input can be converted to a time."""
    result = fn_to_time(ctx, collection)
    return [len(result) > 0]


@FunctionRegistry.register("toQuantity")
def fn_to_quantity(ctx: EvaluationContext, collection: list[Any], unit: str | None = None) -> list[Any]:
    """Converts the input to a quantity."""
    from decimal import Decimal

    from ...types import Quantity

    if not collection:
        return []

    value = collection[0]

    if isinstance(value, Quantity):
        return [value]

    if isinstance(value, (int, float)):
        return [Quantity(value=Decimal(str(value)), unit=unit or "1")]

    if isinstance(value, bool):
        return [Quantity(value=Decimal(1 if value else 0), unit=unit or "1")]

    if isinstance(value, str):
        import re

        # Parse "number unit" format
        match = re.match(r"^([+-]?\d+\.?\d*)\s*(.*)$", value.strip())
        if match:
            num_str, unit_str = match.groups()
            try:
                return [Quantity(value=Decimal(num_str), unit=unit_str.strip() or unit or "1")]
            except (ValueError, ArithmeticError):
                pass
    return []


@FunctionRegistry.register("convertsToQuantity")
def fn_converts_to_quantity(ctx: EvaluationContext, collection: list[Any], unit: str | None = None) -> list[bool]:
    """Returns true if the input can be converted to a quantity."""
    result = fn_to_quantity(ctx, collection, unit)
    return [len(result) > 0]
