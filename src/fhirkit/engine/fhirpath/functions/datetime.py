"""Date/Time functions: today, now, timeOfDay, and component extraction."""

from datetime import datetime, timezone
from typing import Any

from ...context import EvaluationContext
from ...functions import FunctionRegistry
from ...types import FHIRDate, FHIRDateTime, FHIRTime


@FunctionRegistry.register("today")
def fn_today(ctx: EvaluationContext, collection: list[Any]) -> list[FHIRDate]:
    """Returns the current date."""
    now = ctx.now or datetime.now(timezone.utc)
    return [FHIRDate(year=now.year, month=now.month, day=now.day)]


@FunctionRegistry.register("now")
def fn_now(ctx: EvaluationContext, collection: list[Any]) -> list[FHIRDateTime]:
    """Returns the current date and time, including timezone offset."""
    now = ctx.now or datetime.now(timezone.utc)
    tz_offset = "Z"
    if now.tzinfo is not None:
        offset = now.utcoffset()
        if offset is not None:
            total_seconds = int(offset.total_seconds())
            if total_seconds == 0:
                tz_offset = "Z"
            else:
                sign = "+" if total_seconds >= 0 else "-"
                hours, remainder = divmod(abs(total_seconds), 3600)
                minutes = remainder // 60
                tz_offset = f"{sign}{hours:02d}:{minutes:02d}"

    return [
        FHIRDateTime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            second=now.second,
            millisecond=now.microsecond // 1000,
            tz_offset=tz_offset,
        )
    ]


@FunctionRegistry.register("timeOfDay")
def fn_time_of_day(ctx: EvaluationContext, collection: list[Any]) -> list[FHIRTime]:
    """Returns the current time."""
    now = ctx.now or datetime.now(timezone.utc)
    return [
        FHIRTime(
            hour=now.hour,
            minute=now.minute,
            second=now.second,
            millisecond=now.microsecond // 1000,
        )
    ]


# Date/Time component extraction functions


def _extract_date_value(collection: list[Any]) -> FHIRDate | FHIRDateTime | None:
    """Extract a date or datetime value from a collection."""
    if not collection:
        return None
    value = collection[0]
    if isinstance(value, (FHIRDate, FHIRDateTime)):
        return value
    # Try to parse string values
    if isinstance(value, str):
        parsed = FHIRDateTime.parse(value)
        if parsed:
            return parsed
        parsed_date = FHIRDate.parse(value)
        if parsed_date:
            return parsed_date
    return None


def _extract_time_value(collection: list[Any]) -> FHIRTime | FHIRDateTime | None:
    """Extract a time or datetime value from a collection."""
    if not collection:
        return None
    value = collection[0]
    if isinstance(value, (FHIRTime, FHIRDateTime)):
        return value
    # Try to parse string values
    if isinstance(value, str):
        parsed = FHIRDateTime.parse(value)
        if parsed:
            return parsed
        parsed_time = FHIRTime.parse(value)
        if parsed_time:
            return parsed_time
    return None


@FunctionRegistry.register("year")
def fn_year(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the year component of a Date or DateTime.

    If the input is empty or not a date/datetime, returns empty.
    """
    value = _extract_date_value(collection)
    if value is None:
        return []
    return [value.year]


@FunctionRegistry.register("month")
def fn_month(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the month component of a Date or DateTime.

    If the input is empty, not a date/datetime, or doesn't have month precision,
    returns empty.
    """
    value = _extract_date_value(collection)
    if value is None or value.month is None:
        return []
    return [value.month]


@FunctionRegistry.register("day")
def fn_day(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the day component of a Date or DateTime.

    If the input is empty, not a date/datetime, or doesn't have day precision,
    returns empty.
    """
    value = _extract_date_value(collection)
    if value is None or value.day is None:
        return []
    return [value.day]


@FunctionRegistry.register("hour")
def fn_hour(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the hour component of a DateTime or Time.

    If the input is empty, not a datetime/time, or doesn't have hour precision,
    returns empty.
    """
    value = _extract_time_value(collection)
    if value is None:
        return []
    if isinstance(value, FHIRTime):
        return [value.hour]
    if isinstance(value, FHIRDateTime):
        if value.hour is None:
            return []
        return [value.hour]
    return []


@FunctionRegistry.register("minute")
def fn_minute(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the minute component of a DateTime or Time.

    If the input is empty, not a datetime/time, or doesn't have minute precision,
    returns empty.
    """
    value = _extract_time_value(collection)
    if value is None:
        return []
    if isinstance(value, FHIRTime):
        if value.minute is None:
            return []
        return [value.minute]
    if isinstance(value, FHIRDateTime):
        if value.minute is None:
            return []
        return [value.minute]
    return []


@FunctionRegistry.register("second")
def fn_second(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the second component of a DateTime or Time.

    If the input is empty, not a datetime/time, or doesn't have second precision,
    returns empty.
    """
    value = _extract_time_value(collection)
    if value is None:
        return []
    if isinstance(value, FHIRTime):
        if value.second is None:
            return []
        return [value.second]
    if isinstance(value, FHIRDateTime):
        if value.second is None:
            return []
        return [value.second]
    return []


@FunctionRegistry.register("millisecond")
def fn_millisecond(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the millisecond component of a DateTime or Time.

    If the input is empty, not a datetime/time, or doesn't have millisecond precision,
    returns empty.
    """
    value = _extract_time_value(collection)
    if value is None:
        return []
    if isinstance(value, FHIRTime):
        if value.millisecond is None:
            return []
        return [value.millisecond]
    if isinstance(value, FHIRDateTime):
        if value.millisecond is None:
            return []
        return [value.millisecond]
    return []
