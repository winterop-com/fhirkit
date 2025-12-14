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
