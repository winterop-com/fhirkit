"""CQL Interval Timing Functions.

Implements interval comparison operations for CQL timing relationships:
- before/after
- meets before/after
- overlaps before/after
- starts/ends
- during/included in/includes
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..types import CQLInterval


def interval_timing(left: "CQLInterval[Any]", right: "CQLInterval[Any]", op: str) -> bool | None:
    """Handle interval-to-interval timing comparisons.

    CQL interval timing operators:
    - before/after: intervals don't overlap and one is entirely before/after the other
    - meets before/after: intervals touch at exactly one point
    - overlaps before: left overlaps right AND left starts before right
    - overlaps after: left overlaps right AND left ends after right
    - starts: left and right have same start AND left ends before or at right's end
    - ends: left and right have same end AND left starts at or after right's start
    - during/included in: left is entirely within right
    - includes: right is entirely within left
    """
    # Handle compound 'overlaps before/after' first (before 'before'/'after' checks)
    if "overlaps" in op:
        if "before" in op:
            # overlaps before: left overlaps right AND left starts before right starts
            if left.low is None or right.low is None:
                return None
            return left.overlaps(right) and left.low < right.low
        elif "after" in op:
            # overlaps after: left overlaps right AND left ends after right ends
            if left.high is None or right.high is None:
                return None
            return left.overlaps(right) and left.high > right.high
        else:
            # Simple overlaps
            return left.overlaps(right)

    # Handle compound 'meets before/after'
    if "meets" in op:
        if "before" in op:
            return left.high == right.low
        elif "after" in op:
            return left.low == right.high
        else:
            return left.high == right.low or left.low == right.high

    # Handle simple before/after (intervals don't overlap)
    if "before" in op:
        if left.high is None or right.low is None:
            return None
        return left.high < right.low
    elif "after" in op:
        if left.low is None or right.high is None:
            return None
        return left.low > right.high

    # Handle 'starts': same start AND left is contained within or equal to right
    elif "starts" in op:
        if left.low is None or right.low is None:
            return None
        if left.low != right.low:
            return False
        # Also check low_closed matches
        if left.low_closed != right.low_closed:
            return False
        # left must end before or at right's end
        if left.high is None and right.high is None:
            return True
        if left.high is None or right.high is None:
            return left.high is None  # left unbounded ends after right
        return left.high <= right.high

    # Handle 'ends': same end AND left is contained within or equal to right
    elif "ends" in op:
        if left.high is None or right.high is None:
            return None
        if left.high != right.high:
            return False
        # Also check high_closed matches
        if left.high_closed != right.high_closed:
            return False
        # left must start at or after right's start
        if left.low is None and right.low is None:
            return True
        if left.low is None or right.low is None:
            return right.low is None  # right unbounded starts before left
        return left.low >= right.low

    elif "during" in op or "included in" in op:
        return right.includes(left)
    elif "includes" in op:
        return left.includes(right)
    elif "same" in op:
        return left == right
    return None


def interval_point_timing(interval: "CQLInterval[Any]", point: Any, op: str) -> bool | None:
    """Handle interval-to-point timing comparisons."""
    if "before" in op:
        return interval.high is not None and interval.high < point
    elif "after" in op:
        return interval.low is not None and interval.low > point
    elif "contains" in op or "includes" in op:
        return interval.contains(point)
    return None


def point_interval_timing(point: Any, interval: "CQLInterval[Any]", op: str) -> bool | None:
    """Handle point-to-interval timing comparisons."""
    if "before" in op:
        return interval.low is not None and point < interval.low
    elif "after" in op:
        return interval.high is not None and point > interval.high
    elif "during" in op or "in" in op or "included in" in op:
        return interval.contains(point)
    return None


def collapse_intervals(
    intervals: list["CQLInterval[Any]"],
    interval_class: type,
) -> list["CQLInterval[Any]"]:
    """Collapse overlapping/adjacent intervals into merged intervals.

    Args:
        intervals: List of intervals to collapse
        interval_class: The CQLInterval class to use for creating new intervals
    """
    if not intervals:
        return []

    # Sort by low bound - we filter to only intervals with non-None low
    filtered = [i for i in intervals if i.low is not None]
    sorted_intervals = sorted(filtered, key=lambda x: x.low)  # type: ignore[arg-type,return-value]

    if not sorted_intervals:
        return []

    result = [sorted_intervals[0]]
    for current in sorted_intervals[1:]:
        last = result[-1]
        # Check if intervals overlap or are adjacent
        if last.high is not None and current.low is not None:
            if last.high >= current.low or (last.high == current.low and (last.high_closed or current.low_closed)):
                # Merge intervals
                new_high = max(last.high, current.high) if current.high is not None else current.high
                result[-1] = interval_class(
                    low=last.low,
                    high=new_high,
                    low_closed=last.low_closed,
                    high_closed=current.high_closed if new_high == current.high else last.high_closed,
                )
            else:
                result.append(current)
        else:
            result.append(current)

    return result
