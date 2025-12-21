"""Comparison functions and operators."""

from decimal import Decimal
from typing import Any

from ...context import EvaluationContext
from ...functions import FunctionRegistry
from ...types import FHIRDate, FHIRDateTime, FHIRTime, Quantity


def _normalize_for_comparison(value: Any) -> Any:
    """Normalize a value for comparison.

    Converts date strings to FHIRDate/FHIRDateTime for proper comparison.
    Also unwraps _PrimitiveWithExtension wrappers.
    Converts FHIR Quantity dicts to Quantity objects.
    """
    # Import here to avoid circular imports
    from ..visitor import _PrimitiveWithExtension

    # Unwrap primitive wrappers
    if isinstance(value, _PrimitiveWithExtension):
        value = value.value

    # Convert FHIR Quantity dict to Quantity object
    if isinstance(value, dict) and "value" in value and ("unit" in value or "code" in value):
        qty_value = value.get("value")
        # Prefer 'code' (UCUM code) over 'unit' (human-readable)
        qty_unit = value.get("code") or value.get("unit") or "1"
        if qty_value is not None:
            return Quantity(value=Decimal(str(qty_value)), unit=qty_unit)

    if isinstance(value, str):
        # Try to parse as date or datetime
        if "T" in value or len(value) > 10:
            # Might be a datetime
            try:
                result = FHIRDateTime.parse(value)
                if result is not None:
                    return result
            except (ValueError, AttributeError):
                pass
        # Try as date (only if looks like a date pattern: YYYY or YYYY-MM or YYYY-MM-DD)
        if len(value) >= 4 and value[:4].isdigit():
            try:
                date_result = FHIRDate.parse(value)
                if date_result is not None:
                    return date_result
            except (ValueError, AttributeError):
                pass
    return value


def equals(left: Any, right: Any) -> bool | None:
    """
    FHIRPath equality comparison.

    Returns None if either operand is empty/null.
    Collections must be singletons for comparison - different sizes = False.
    """
    if left is None or right is None:
        return None

    # Handle lists
    if isinstance(left, list):
        if not left:
            return None
        if len(left) > 1:
            # Multi-element collection on left side
            if isinstance(right, list):
                if not right:
                    return None
                if len(right) != len(left):
                    return False
                # Compare element by element
                for l_item, r_item in zip(left, right):
                    result = _equals_single(l_item, r_item)
                    if result is None:
                        return None  # Incomparable items
                    if not result:
                        return False
                return True
            return False  # Can't compare multi-element with singleton
        left = left[0]

    if isinstance(right, list):
        if not right:
            return None
        if len(right) > 1:
            return False  # Can't compare singleton with multi-element
        right = right[0]

    return _equals_single(left, right)


def _equals_single(left: Any, right: Any) -> bool | None:
    """Compare two single values for equality.

    Returns:
        True if equal, False if not equal, None if incomparable (different precision).
    """
    # Normalize date strings to FHIRDate/FHIRDateTime
    left = _normalize_for_comparison(left)
    right = _normalize_for_comparison(right)

    # Handle date/datetime cross-comparison with precision check
    if isinstance(left, FHIRDate) and isinstance(right, FHIRDateTime):
        # Date has precision only to day, datetime may have time components
        # If datetime has time components, they have different precision → None
        if right.hour is not None:
            return None  # Incomparable precision
        # Compare date parts only
        return left.year == right.year and left.month == right.month and left.day == right.day

    if isinstance(left, FHIRDateTime) and isinstance(right, FHIRDate):
        # Same as above, reversed
        if left.hour is not None:
            return None  # Incomparable precision
        return left.year == right.year and left.month == right.month and left.day == right.day

    # Type-specific comparison
    if type(left) is not type(right):
        # Different types are not equal (with some exceptions)
        # int, float, and Decimal can be compared
        if isinstance(left, (int, float, Decimal)) and isinstance(right, (int, float, Decimal)):
            return float(left) == float(right)
        return False

    # Special handling for FHIRDateTime with timezone - compare in UTC
    if isinstance(left, FHIRDateTime) and isinstance(right, FHIRDateTime):
        # If both have timezones, compare normalized UTC tuples
        if left.tz_offset is not None and right.tz_offset is not None:
            return left._to_utc_tuple() == right._to_utc_tuple()

    # Special handling for Quantity - incompatible units return None (incomparable)
    if isinstance(left, Quantity) and isinstance(right, Quantity):
        result = left._convert_for_comparison(right)
        if result is None:
            return None  # Incomparable units
        return result[0] == result[1]

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

    # Handle date/datetime cross-comparison with precision check
    if isinstance(left, FHIRDate) and isinstance(right, FHIRDateTime):
        # If datetime has time components AND dates are equal, precision matters
        if right.hour is not None:
            # Only return None if date parts are equal (time would determine result)
            if left.year == right.year and left.month == right.month and left.day == right.day:
                return None  # Incomparable precision (same date, different time precision)
            # Otherwise, compare date parts only
            if left.year < right.year:
                return -1
            if left.year > right.year:
                return 1
            if left.month is not None and right.month is not None:
                if left.month < right.month:
                    return -1
                if left.month > right.month:
                    return 1
            if left.day is not None and right.day is not None:
                if left.day < right.day:
                    return -1
                if left.day > right.day:
                    return 1
            return 0
    elif isinstance(left, FHIRDateTime) and isinstance(right, FHIRDate):
        if left.hour is not None:
            # Only return None if date parts are equal
            if left.year == right.year and left.month == right.month and left.day == right.day:
                return None  # Incomparable precision
            # Otherwise, compare date parts only
            if left.year < right.year:
                return -1
            if left.year > right.year:
                return 1
            if left.month is not None and right.month is not None:
                if left.month < right.month:
                    return -1
                if left.month > right.month:
                    return 1
            if left.day is not None and right.day is not None:
                if left.day < right.day:
                    return -1
                if left.day > right.day:
                    return 1
            return 0

    # Handle FHIRDateTime precision differences
    if isinstance(left, FHIRDateTime) and isinstance(right, FHIRDateTime):
        # Check if precisions differ
        left_precision = _get_datetime_precision(left)
        right_precision = _get_datetime_precision(right)

        if left_precision != right_precision:
            # Compare up to the less precise level
            # The more precise value is truncated to match the less precise one
            min_precision = min(left_precision, right_precision)
            cmp_result = _compare_datetime_to_precision(left, right, min_precision)
            if cmp_result == 0:
                # Equal up to less precise level - incomparable for ordering
                return None
            return cmp_result

    # Handle FHIRTime precision differences
    if isinstance(left, FHIRTime) and isinstance(right, FHIRTime):
        left_precision = _get_time_precision(left)
        right_precision = _get_time_precision(right)

        if left_precision != right_precision:
            min_precision = min(left_precision, right_precision)
            cmp_result = _compare_time_to_precision(left, right, min_precision)
            if cmp_result == 0:
                # Equal up to less precise level - incomparable for ordering
                return None
            return cmp_result

    # After handling cross-type comparisons, remaining comparisons should be same-type
    try:
        if left < right:  # type: ignore[operator]
            return -1
        elif left > right:  # type: ignore[operator]
            return 1
        else:
            return 0
    except TypeError:
        return None


def _get_datetime_precision(dt: FHIRDateTime) -> int:
    """Get the precision level of a FHIRDateTime.

    Returns:
        1: year only
        2: year-month
        3: year-month-day
        4: year-month-day hour
        5: year-month-day hour:minute
        6: year-month-day hour:minute:second
        7: year-month-day hour:minute:second.millisecond
    """
    if dt.millisecond is not None:
        return 7
    if dt.second is not None:
        return 6
    if dt.minute is not None:
        return 5
    if dt.hour is not None:
        return 4
    if dt.day is not None:
        return 3
    if dt.month is not None:
        return 2
    return 1


def _compare_datetime_to_precision(left: FHIRDateTime, right: FHIRDateTime, precision: int) -> int:
    """Compare two FHIRDateTimes up to the specified precision level."""
    # Year
    if left.year < right.year:
        return -1
    if left.year > right.year:
        return 1
    if precision == 1:
        return 0

    # Month
    l_month = left.month or 1
    r_month = right.month or 1
    if l_month < r_month:
        return -1
    if l_month > r_month:
        return 1
    if precision == 2:
        return 0

    # Day
    l_day = left.day or 1
    r_day = right.day or 1
    if l_day < r_day:
        return -1
    if l_day > r_day:
        return 1
    if precision == 3:
        return 0

    # Hour
    l_hour = left.hour or 0
    r_hour = right.hour or 0
    if l_hour < r_hour:
        return -1
    if l_hour > r_hour:
        return 1
    if precision == 4:
        return 0

    # Minute
    l_min = left.minute or 0
    r_min = right.minute or 0
    if l_min < r_min:
        return -1
    if l_min > r_min:
        return 1
    if precision == 5:
        return 0

    # Second
    l_sec = left.second or 0
    r_sec = right.second or 0
    if l_sec < r_sec:
        return -1
    if l_sec > r_sec:
        return 1
    if precision == 6:
        return 0

    # Millisecond
    l_ms = left.millisecond or 0
    r_ms = right.millisecond or 0
    if l_ms < r_ms:
        return -1
    if l_ms > r_ms:
        return 1
    return 0


def _get_time_precision(t: FHIRTime) -> int:
    """Get the precision level of a FHIRTime.

    Returns:
        1: hour only
        2: hour:minute
        3: hour:minute:second
        4: hour:minute:second.millisecond
    """
    if t.millisecond is not None:
        return 4
    if t.second is not None:
        return 3
    if t.minute is not None:
        return 2
    return 1


def _compare_time_to_precision(left: FHIRTime, right: FHIRTime, precision: int) -> int:
    """Compare two FHIRTimes up to the specified precision level."""
    # Hour
    if left.hour < right.hour:
        return -1
    if left.hour > right.hour:
        return 1
    if precision == 1:
        return 0

    # Minute
    l_min = left.minute or 0
    r_min = right.minute or 0
    if l_min < r_min:
        return -1
    if l_min > r_min:
        return 1
    if precision == 2:
        return 0

    # Second
    l_sec = left.second or 0
    r_sec = right.second or 0
    if l_sec < r_sec:
        return -1
    if l_sec > r_sec:
        return 1
    if precision == 3:
        return 0

    # Millisecond
    l_ms = left.millisecond or 0
    r_ms = right.millisecond or 0
    if l_ms < r_ms:
        return -1
    if l_ms > r_ms:
        return 1
    return 0


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


@FunctionRegistry.register("comparable")
def fn_comparable(ctx: EvaluationContext, collection: list[Any], other: Any) -> list[bool]:
    """
    Returns true if the quantities are comparable (have compatible units).

    This function checks if two Quantity values can be compared by determining
    if their units can be converted to a common unit.
    """
    if not collection:
        return []

    left = collection[0]
    if not isinstance(left, Quantity):
        return []

    # Handle list argument
    if isinstance(other, list):
        if not other:
            return []
        other = other[0]

    if not isinstance(other, Quantity):
        return []

    # Check if the quantities can be converted for comparison
    result = left._convert_for_comparison(other)
    return [result is not None]
