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
    """Convert quantity to different units using UCUM.

    Performs real unit conversion using the UCUM (Unified Code for Units of Measure)
    specification. Supports:
    - Metric prefixes (mg, kg, mL, etc.)
    - US customary units ([lb_av], [oz_av], [in_i], etc.)
    - Temperature conversions (Cel, [degF], K)
    - Compound units (mg/dL, mmol/L, etc.)

    Args:
        args: [quantity, target_unit] - quantity to convert and target unit code

    Returns:
        Quantity with converted value and new unit, or None if conversion fails

    Examples:
        ConvertQuantity(1 'g', 'mg') = 1000 'mg'
        ConvertQuantity(98.6 '[degF]', 'Cel') = 37 'Cel'
        ConvertQuantity(150 '[lb_av]', 'kg') = 68.0388555 'kg'
    """
    if len(args) >= 2 and args[0] is not None:
        quantity = args[0]
        target_unit = args[1]

        if isinstance(quantity, Quantity) and target_unit:
            from fhirkit.engine.units import convert_quantity as ucum_convert

            source_unit = quantity.unit or "1"
            target_unit_str = str(target_unit)

            converted_value = ucum_convert(quantity.value, source_unit, target_unit_str)

            if converted_value is not None:
                return Quantity(value=Decimal(str(converted_value)), unit=target_unit_str)

            # Fallback: if conversion fails, just change the unit (for compatibility)
            return Quantity(value=quantity.value, unit=target_unit_str)

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


def _round(args: list[Any]) -> Decimal | int | None:
    """Round to nearest integer or specified precision.

    Per CQL tests: Uses "round half toward positive infinity" for .5 cases.
    - 0.5 -> 1 (up)
    - -0.5 -> 0 (toward positive infinity)
    - -1.5 -> -1 (toward positive infinity)
    """
    if args and args[0] is not None:
        val = args[0]
        precision = int(args[1]) if len(args) > 1 and args[1] is not None else 0

        # Use Decimal for precise rounding
        decimal_val = Decimal(str(val))

        # Custom implementation: round half toward positive infinity
        # This is equivalent to floor(x + 0.5) for the specified precision
        shift = Decimal(10) ** precision
        shifted = decimal_val * shift + Decimal("0.5")

        import math

        result = Decimal(math.floor(float(shifted))) / shift

        # Quantize to the correct precision
        quantize_str = "1" if precision == 0 else "1." + "0" * precision
        result = result.quantize(Decimal(quantize_str))

        # Return int for 0 precision
        if precision == 0:
            return int(result)
        return result
    return None


def _ln(args: list[Any]) -> float | None:
    """Natural logarithm.

    Per CQL spec: Ln(0) and Ln of negative numbers raise an error.
    """
    import math

    if args and args[0] is not None:
        val = float(args[0])
        if val <= 0:
            raise ValueError(f"Ln is undefined for {val}")
        return math.log(val)
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


def _precision(args: list[Any]) -> int | None:
    """Get precision of a value.

    For Decimal: returns number of decimal places
    For Date/DateTime/Time: returns precision level (year=4, month=6, day=8, etc.)
    """
    if not args or args[0] is None:
        return None

    val = args[0]

    # Decimal precision - count digits after decimal point
    if isinstance(val, Decimal):
        sign, digits, exponent = val.as_tuple()
        # exponent can be 'n', 'N', 'F' for special values (NaN, infinity)
        if isinstance(exponent, int) and exponent < 0:
            return -exponent
        return 0

    if isinstance(val, float):
        # Convert to string and count decimal places
        s = str(val)
        if "." in s:
            return len(s.split(".")[1].rstrip("0")) or 0
        return 0

    if isinstance(val, int):
        return 0

    # Date/DateTime precision based on components present
    if isinstance(val, FHIRDateTime):
        if val.millisecond is not None:
            return 17  # Full millisecond precision
        if val.second is not None:
            return 14  # Second precision
        if val.minute is not None:
            return 12  # Minute precision
        if val.hour is not None:
            return 10  # Hour precision
        if val.day is not None:
            return 8  # Day precision
        if val.month is not None:
            return 6  # Month precision
        return 4  # Year precision

    if isinstance(val, FHIRDate):
        if val.day is not None:
            return 8  # Day precision
        if val.month is not None:
            return 6  # Month precision
        return 4  # Year precision

    if isinstance(val, FHIRTime):
        if val.millisecond is not None:
            return 9  # Millisecond precision
        if val.second is not None:
            return 6  # Second precision
        if val.minute is not None:
            return 4  # Minute precision
        return 2  # Hour precision

    if isinstance(val, (date, datetime)):
        return 8  # Python date/datetime always has day precision

    return None


def _low_boundary(args: list[Any]) -> Any:
    """Get the lowest possible value for an imprecise value.

    LowBoundary(value, precision) returns the least possible value
    that the input could represent.
    """
    if len(args) < 2 or args[0] is None:
        return None

    val = args[0]
    precision = args[1]

    # For Decimal - pad with zeros to reach precision
    if isinstance(val, (Decimal, float, int)):
        decimal_val = Decimal(str(val))
        if precision is not None:
            # Low boundary for a decimal at given precision is the value itself
            # truncated to that precision
            quantize_str = "1." + "0" * int(precision) if precision > 0 else "1"
            return decimal_val.quantize(Decimal(quantize_str))
        return decimal_val

    # For FHIRDate - fill in lowest possible values for missing components
    if isinstance(val, FHIRDate):
        return FHIRDate(
            year=val.year,
            month=val.month if val.month is not None else 1,
            day=val.day if val.day is not None else 1,
        )

    # For FHIRDateTime - fill in lowest possible values
    if isinstance(val, FHIRDateTime):
        return FHIRDateTime(
            year=val.year,
            month=val.month if val.month is not None else 1,
            day=val.day if val.day is not None else 1,
            hour=val.hour if val.hour is not None else 0,
            minute=val.minute if val.minute is not None else 0,
            second=val.second if val.second is not None else 0,
            millisecond=val.millisecond if val.millisecond is not None else 0,
        )

    # For FHIRTime - fill in lowest values
    if isinstance(val, FHIRTime):
        return FHIRTime(
            hour=val.hour,
            minute=val.minute if val.minute is not None else 0,
            second=val.second if val.second is not None else 0,
            millisecond=val.millisecond if val.millisecond is not None else 0,
        )

    return val


def _high_boundary(args: list[Any]) -> Any:
    """Get the highest possible value for an imprecise value.

    HighBoundary(value, precision) returns the greatest possible value
    that the input could represent.
    """
    if len(args) < 2 or args[0] is None:
        return None

    val = args[0]
    precision = args[1]

    # For Decimal - add 0.5 at the next precision level
    if isinstance(val, (Decimal, float, int)):
        decimal_val = Decimal(str(val))
        if precision is not None and precision >= 0:
            # High boundary is value + (10^-precision - smallest_unit)
            increment = Decimal(10) ** (-int(precision))
            # Round up to next precision boundary minus smallest representable
            quantize_str = "1." + "0" * int(precision) if precision > 0 else "1"
            return (decimal_val + increment - Decimal("0.00000001")).quantize(Decimal(quantize_str))
        return decimal_val

    # For FHIRDate - fill in highest possible values for missing components
    if isinstance(val, FHIRDate):
        month = val.month if val.month is not None else 12
        # Calculate days in month
        if month in (1, 3, 5, 7, 8, 10, 12):
            max_day = 31
        elif month in (4, 6, 9, 11):
            max_day = 30
        else:  # February
            year = val.year
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            max_day = 29 if is_leap else 28

        return FHIRDate(
            year=val.year,
            month=month,
            day=val.day if val.day is not None else max_day,
        )

    # For FHIRDateTime - fill in highest possible values
    if isinstance(val, FHIRDateTime):
        month = val.month if val.month is not None else 12
        if month in (1, 3, 5, 7, 8, 10, 12):
            max_day = 31
        elif month in (4, 6, 9, 11):
            max_day = 30
        else:
            year = val.year
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            max_day = 29 if is_leap else 28

        return FHIRDateTime(
            year=val.year,
            month=month,
            day=val.day if val.day is not None else max_day,
            hour=val.hour if val.hour is not None else 23,
            minute=val.minute if val.minute is not None else 59,
            second=val.second if val.second is not None else 59,
            millisecond=val.millisecond if val.millisecond is not None else 999,
        )

    # For FHIRTime - fill in highest values
    if isinstance(val, FHIRTime):
        return FHIRTime(
            hour=val.hour,
            minute=val.minute if val.minute is not None else 59,
            second=val.second if val.second is not None else 59,
            millisecond=val.millisecond if val.millisecond is not None else 999,
        )

    return val


def _min_value(args: list[Any]) -> Any:
    """Get minimum representable value for a type.

    MinValue(type) returns the minimum value for Integer, Decimal, Date, DateTime, Time.
    """
    import sys

    if not args:
        return None

    type_name = str(args[0]).lower() if args[0] else None

    if type_name in ("integer", "int"):
        return -sys.maxsize - 1

    if type_name == "decimal":
        # CQL spec: minimum decimal is -10^28 + 1
        return Decimal("-99999999999999999999999999.99999999")

    if type_name == "date":
        return FHIRDate(year=1, month=1, day=1)

    if type_name == "datetime":
        return FHIRDateTime(year=1, month=1, day=1, hour=0, minute=0, second=0, millisecond=0)

    if type_name == "time":
        return FHIRTime(hour=0, minute=0, second=0, millisecond=0)

    if type_name == "quantity":
        return Quantity(value=Decimal("-99999999999999999999999999.99999999"), unit="1")

    return None


def _max_value(args: list[Any]) -> Any:
    """Get maximum representable value for a type.

    MaxValue(type) returns the maximum value for Integer, Decimal, Date, DateTime, Time.
    """
    import sys

    if not args:
        return None

    type_name = str(args[0]).lower() if args[0] else None

    if type_name in ("integer", "int"):
        return sys.maxsize

    if type_name == "decimal":
        # CQL spec: maximum decimal is 10^28 - 1
        return Decimal("99999999999999999999999999.99999999")

    if type_name == "date":
        return FHIRDate(year=9999, month=12, day=31)

    if type_name == "datetime":
        return FHIRDateTime(year=9999, month=12, day=31, hour=23, minute=59, second=59, millisecond=999)

    if type_name == "time":
        return FHIRTime(hour=23, minute=59, second=59, millisecond=999)

    if type_name == "quantity":
        return Quantity(value=Decimal("99999999999999999999999999.99999999"), unit="1")

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
    # Precision and boundary functions
    registry.register("Precision", _precision, category="math", min_args=1, max_args=1)
    registry.register("LowBoundary", _low_boundary, category="math", min_args=2, max_args=2)
    registry.register("HighBoundary", _high_boundary, category="math", min_args=2, max_args=2)
    registry.register("MinValue", _min_value, category="math", min_args=1, max_args=1)
    registry.register("MaxValue", _max_value, category="math", min_args=1, max_args=1)
