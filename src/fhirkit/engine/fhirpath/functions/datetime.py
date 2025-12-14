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
