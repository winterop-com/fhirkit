"""CQL Type Conversion Functions.

Implements: ToString, ToInteger, ToDecimal, ToBoolean, ToDate, ToDateTime, ToTime,
ToQuantity, Coalesce, IsNull, IsTrue, IsFalse, ToList, ToChars
"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any

from ...types import FHIRDate, FHIRDateTime, FHIRTime, Quantity

if TYPE_CHECKING:
    from .registry import FunctionRegistry


def _to_string(args: list[Any]) -> str | None:
    """Convert value to string."""
    if args and args[0] is not None:
        return str(args[0])
    return None


def _to_integer(args: list[Any]) -> int | None:
    """Convert value to integer."""
    if args and args[0] is not None:
        try:
            val = args[0]
            if isinstance(val, bool):
                return 1 if val else 0
            return int(val)
        except (ValueError, TypeError):
            return None
    return None


def _to_decimal(args: list[Any]) -> Decimal | None:
    """Convert value to decimal."""
    if args and args[0] is not None:
        try:
            return Decimal(str(args[0]))
        except (ValueError, InvalidOperation):
            return None
    return None


def _to_boolean(args: list[Any]) -> bool | None:
    """Convert value to boolean."""
    if args and args[0] is not None:
        val = args[0]
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            lower = val.lower()
            if lower in ("true", "t", "yes", "y", "1"):
                return True
            if lower in ("false", "f", "no", "n", "0"):
                return False
        if isinstance(val, (int, float)):
            return val != 0
    return None


def _to_date(args: list[Any]) -> FHIRDate | None:
    """Convert value to Date."""
    if args and args[0] is not None:
        val = args[0]
        if isinstance(val, FHIRDate):
            return val
        if isinstance(val, FHIRDateTime):
            return FHIRDate(year=val.year, month=val.month, day=val.day)
        if isinstance(val, datetime):
            return FHIRDate(year=val.year, month=val.month, day=val.day)
        if isinstance(val, date):
            return FHIRDate(year=val.year, month=val.month, day=val.day)
        if isinstance(val, str):
            return FHIRDate.parse(val)
    return None


def _to_datetime(args: list[Any]) -> FHIRDateTime | None:
    """Convert value to DateTime."""
    if args and args[0] is not None:
        val = args[0]
        if isinstance(val, FHIRDateTime):
            return val
        if isinstance(val, FHIRDate):
            return FHIRDateTime(year=val.year, month=val.month, day=val.day)
        if isinstance(val, datetime):
            return FHIRDateTime(
                year=val.year,
                month=val.month,
                day=val.day,
                hour=val.hour,
                minute=val.minute,
                second=val.second,
                millisecond=val.microsecond // 1000,
            )
        if isinstance(val, date):
            return FHIRDateTime(year=val.year, month=val.month, day=val.day)
        if isinstance(val, str):
            return FHIRDateTime.parse(val)
    return None


def _to_time(args: list[Any]) -> FHIRTime | None:
    """Convert value to Time."""
    if args and args[0] is not None:
        val = args[0]
        if isinstance(val, FHIRTime):
            return val
        if isinstance(val, str):
            return FHIRTime.parse(val)
    return None


def _to_quantity(args: list[Any]) -> Quantity | None:
    """Convert value to Quantity."""
    if not args:
        return None
    val = args[0]
    unit = args[1] if len(args) > 1 else "1"
    if val is not None:
        try:
            return Quantity(value=Decimal(str(val)), unit=str(unit))
        except (ValueError, InvalidOperation):
            return None
    return None


def _coalesce(args: list[Any]) -> Any:
    """Return first non-null argument."""
    for arg in args:
        if arg is not None:
            if isinstance(arg, list):
                # For lists, return first non-empty list
                if arg:
                    return arg
            else:
                return arg
    return None


def _is_null(args: list[Any]) -> bool:
    """Check if value is null."""
    if not args:
        return True
    val = args[0]
    if isinstance(val, list):
        return len(val) == 0
    return val is None


def _is_not_null(args: list[Any]) -> bool:
    """Check if value is not null."""
    if not args:
        return False
    val = args[0]
    if isinstance(val, list):
        return len(val) > 0
    return val is not None


def _is_true(args: list[Any]) -> bool:
    """Check if value is true."""
    if args and args[0] is True:
        return True
    return False


def _is_false(args: list[Any]) -> bool:
    """Check if value is false."""
    if args and args[0] is False:
        return True
    return False


def _to_list(args: list[Any]) -> list[Any]:
    """Convert value to a list."""
    if not args:
        return []
    val = args[0]
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def _to_chars(args: list[Any]) -> list[str] | None:
    """Convert string to list of characters."""
    if args and args[0] is not None:
        return list(str(args[0]))
    return None


def _convert_quantity(args: list[Any]) -> Quantity | None:
    """Convert quantity to different units."""
    if len(args) >= 2 and args[0] is not None:
        quantity = args[0]
        target_unit = args[1]
        if isinstance(quantity, Quantity) and target_unit:
            # Simple conversion - just change the unit
            # A real implementation would handle unit conversion
            return Quantity(value=quantity.value, unit=str(target_unit))
    return None


def _abs(args: list[Any]) -> Any:
    """Absolute value."""
    if args and args[0] is not None:
        val = args[0]
        if isinstance(val, (int, float, Decimal)):
            return abs(val)
        if isinstance(val, Quantity):
            return Quantity(value=abs(val.value), unit=val.unit)
    return None


def _ceiling(args: list[Any]) -> int | None:
    """Ceiling (round up)."""
    import math

    if args and args[0] is not None:
        return math.ceil(float(args[0]))
    return None


def _floor(args: list[Any]) -> int | None:
    """Floor (round down)."""
    import math

    if args and args[0] is not None:
        return math.floor(float(args[0]))
    return None


def _truncate(args: list[Any]) -> int | None:
    """Truncate (toward zero)."""
    import math

    if args and args[0] is not None:
        return math.trunc(float(args[0]))
    return None


def _round(args: list[Any]) -> float | int | None:
    """Round to nearest integer or specified precision."""
    if args and args[0] is not None:
        val = args[0]
        precision = int(args[1]) if len(args) > 1 and args[1] is not None else 0
        # Always convert to float for consistency
        result = round(float(val), precision)
        # Return int if precision is 0
        if precision == 0:
            return int(result)
        return result
    return None


def _ln(args: list[Any]) -> float | None:
    """Natural logarithm."""
    import math

    if args and args[0] is not None and args[0] > 0:
        return math.log(float(args[0]))
    return None


def _log(args: list[Any]) -> float | None:
    """Logarithm with specified base."""
    import math

    if len(args) >= 2 and args[0] is not None and args[1] is not None:
        if args[0] > 0 and args[1] > 0:
            return math.log(float(args[0]), float(args[1]))
    return None


def _exp(args: list[Any]) -> float | None:
    """Exponential (e^x)."""
    import math

    if args and args[0] is not None:
        return math.exp(float(args[0]))
    return None


def _power(args: list[Any]) -> Any:
    """Raise to a power."""
    if len(args) >= 2 and args[0] is not None and args[1] is not None:
        return args[0] ** args[1]
    return None


def _sqrt(args: list[Any]) -> float | None:
    """Square root."""
    import math

    if args and args[0] is not None and float(args[0]) >= 0:
        return math.sqrt(float(args[0]))
    return None


def register(registry: "FunctionRegistry") -> None:
    """Register all conversion functions."""
    registry.register("ToString", _to_string, category="conversion", min_args=1, max_args=1)
    registry.register("ToInteger", _to_integer, category="conversion", min_args=1, max_args=1)
    registry.register("ToDecimal", _to_decimal, category="conversion", min_args=1, max_args=1)
    registry.register("ToBoolean", _to_boolean, category="conversion", min_args=1, max_args=1)
    registry.register("ToDate", _to_date, category="conversion", min_args=1, max_args=1)
    registry.register("ToDateTime", _to_datetime, category="conversion", min_args=1, max_args=1)
    registry.register("ToTime", _to_time, category="conversion", min_args=1, max_args=1)
    registry.register("ToQuantity", _to_quantity, category="conversion", min_args=1, max_args=2)
    registry.register("Coalesce", _coalesce, category="conversion", min_args=1)
    registry.register("IsNull", _is_null, category="conversion", min_args=1, max_args=1)
    registry.register("IsNotNull", _is_not_null, category="conversion", min_args=1, max_args=1)
    registry.register("IsTrue", _is_true, category="conversion", min_args=1, max_args=1)
    registry.register("IsFalse", _is_false, category="conversion", min_args=1, max_args=1)
    registry.register("ToList", _to_list, category="conversion", min_args=1, max_args=1)
    registry.register("ToChars", _to_chars, category="conversion", min_args=1, max_args=1)
    registry.register("ConvertQuantity", _convert_quantity, category="conversion", min_args=2, max_args=2)
    registry.register("Abs", _abs, category="math", min_args=1, max_args=1)
    registry.register("Ceiling", _ceiling, category="math", min_args=1, max_args=1)
    registry.register("Floor", _floor, category="math", min_args=1, max_args=1)
    registry.register("Truncate", _truncate, category="math", min_args=1, max_args=1)
    registry.register("Round", _round, category="math", min_args=1, max_args=2)
    registry.register("Ln", _ln, category="math", min_args=1, max_args=1)
    registry.register("Log", _log, category="math", min_args=2, max_args=2)
    registry.register("Exp", _exp, category="math", min_args=1, max_args=1)
    registry.register("Power", _power, category="math", min_args=2, max_args=2)
    registry.register("Sqrt", _sqrt, category="math", min_args=1, max_args=1)
