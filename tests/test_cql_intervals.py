"""Tests for CQL interval operations.

Tests cover:
- Basic interval creation and properties
- Timing relationships (before, after, meets, overlaps, starts, ends, during, includes)
- Compound timing (overlaps before, overlaps after)
- Collapse and expand operations
- Edge cases with open/closed bounds
"""

import pytest

from fhirkit.engine.cql import CQLEvaluator


@pytest.fixture
def evaluator():
    """Create a CQL evaluator."""
    return CQLEvaluator()


class TestIntervalCreation:
    """Test interval literal creation."""

    def test_closed_interval(self, evaluator):
        result = evaluator.evaluate_expression("Interval[1, 10]")
        assert result is not None
        assert result.low == 1
        assert result.high == 10
        assert result.low_closed is True
        assert result.high_closed is True

    def test_open_interval(self, evaluator):
        result = evaluator.evaluate_expression("Interval(1, 10)")
        assert result is not None
        assert result.low == 1
        assert result.high == 10
        assert result.low_closed is False
        assert result.high_closed is False

    def test_half_open_interval(self, evaluator):
        result = evaluator.evaluate_expression("Interval[1, 10)")
        assert result is not None
        assert result.low_closed is True
        assert result.high_closed is False

    def test_half_open_interval_reversed(self, evaluator):
        result = evaluator.evaluate_expression("Interval(1, 10]")
        assert result is not None
        assert result.low_closed is False
        assert result.high_closed is True


class TestIntervalContains:
    """Test interval contains/in operations."""

    def test_contains_point_in_closed(self, evaluator):
        assert evaluator.evaluate_expression("5 in Interval[1, 10]") is True

    def test_contains_point_at_boundary_closed(self, evaluator):
        assert evaluator.evaluate_expression("1 in Interval[1, 10]") is True
        assert evaluator.evaluate_expression("10 in Interval[1, 10]") is True

    def test_contains_point_at_boundary_open(self, evaluator):
        assert evaluator.evaluate_expression("1 in Interval(1, 10)") is False
        assert evaluator.evaluate_expression("10 in Interval(1, 10)") is False

    def test_contains_point_outside(self, evaluator):
        assert evaluator.evaluate_expression("0 in Interval[1, 10]") is False
        assert evaluator.evaluate_expression("11 in Interval[1, 10]") is False


class TestIntervalBefore:
    """Test interval before operator."""

    def test_before_simple(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 5] before Interval[10, 15]") is True

    def test_before_adjacent(self, evaluator):
        # Adjacent but not overlapping - still before
        assert evaluator.evaluate_expression("Interval[1, 5] before Interval[6, 10]") is True

    def test_before_touching(self, evaluator):
        # Touching at point 5 - not before (meets)
        assert evaluator.evaluate_expression("Interval[1, 5] before Interval[5, 10]") is False

    def test_before_overlapping(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 7] before Interval[5, 10]") is False

    def test_after_simple(self, evaluator):
        assert evaluator.evaluate_expression("Interval[10, 15] after Interval[1, 5]") is True


class TestIntervalMeets:
    """Test interval meets operator."""

    def test_meets_before(self, evaluator):
        # With closed bounds, [1,5] meets [5,10] at point 5
        assert evaluator.evaluate_expression("Interval[1, 5] meets Interval[5, 10]") is True

    def test_meets_after(self, evaluator):
        assert evaluator.evaluate_expression("Interval[5, 10] meets Interval[1, 5]") is True

    def test_meets_gap(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 5] meets Interval[6, 10]") is False


class TestIntervalOverlaps:
    """Test interval overlaps operators."""

    def test_overlaps_simple(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 6] overlaps Interval[5, 10]") is True

    def test_overlaps_no_overlap(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 4] overlaps Interval[6, 10]") is False

    def test_overlaps_before(self, evaluator):
        # [1,6] overlaps [5,10] AND starts before [5,10]
        assert evaluator.evaluate_expression("Interval[1, 6] overlaps before Interval[5, 10]") is True

    def test_overlaps_before_false(self, evaluator):
        # [5,10] overlaps [1,6] but does NOT start before [1,6]
        assert evaluator.evaluate_expression("Interval[5, 10] overlaps before Interval[1, 6]") is False

    def test_overlaps_after(self, evaluator):
        # [5,10] overlaps [1,6] AND ends after [1,6]
        assert evaluator.evaluate_expression("Interval[5, 10] overlaps after Interval[1, 6]") is True

    def test_overlaps_after_false(self, evaluator):
        # [1,6] overlaps [5,10] but does NOT end after [5,10]
        assert evaluator.evaluate_expression("Interval[1, 6] overlaps after Interval[5, 10]") is False


class TestIntervalStarts:
    """Test interval starts operator."""

    def test_starts_true(self, evaluator):
        # [1,5] starts [1,10] - same start, [1,5] is contained
        assert evaluator.evaluate_expression("Interval[1, 5] starts Interval[1, 10]") is True

    def test_starts_equal(self, evaluator):
        # Equal intervals - one starts the other
        assert evaluator.evaluate_expression("Interval[1, 10] starts Interval[1, 10]") is True

    def test_starts_false_longer(self, evaluator):
        # [1,10] does NOT start [1,5] - [1,10] extends beyond [1,5]
        assert evaluator.evaluate_expression("Interval[1, 10] starts Interval[1, 5]") is False

    def test_starts_false_different(self, evaluator):
        # Different start points
        assert evaluator.evaluate_expression("Interval[2, 5] starts Interval[1, 10]") is False


class TestIntervalEnds:
    """Test interval ends operator."""

    def test_ends_true(self, evaluator):
        # [5,10] ends [1,10] - same end, [5,10] is contained
        assert evaluator.evaluate_expression("Interval[5, 10] ends Interval[1, 10]") is True

    def test_ends_equal(self, evaluator):
        # Equal intervals - one ends the other
        assert evaluator.evaluate_expression("Interval[1, 10] ends Interval[1, 10]") is True

    def test_ends_false_longer(self, evaluator):
        # [1,10] does NOT end [5,10] - [1,10] extends before [5,10]
        assert evaluator.evaluate_expression("Interval[1, 10] ends Interval[5, 10]") is False

    def test_ends_false_different(self, evaluator):
        # Different end points
        assert evaluator.evaluate_expression("Interval[1, 8] ends Interval[1, 10]") is False


class TestIntervalDuring:
    """Test interval during/included in operators."""

    def test_during_true(self, evaluator):
        assert evaluator.evaluate_expression("Interval[3, 7] during Interval[1, 10]") is True

    def test_during_equal(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 10] during Interval[1, 10]") is True

    def test_during_false(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 10] during Interval[3, 7]") is False

    def test_included_in(self, evaluator):
        assert evaluator.evaluate_expression("Interval[3, 7] included in Interval[1, 10]") is True


class TestIntervalIncludes:
    """Test interval includes operator."""

    def test_includes_interval(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 10] includes Interval[3, 7]") is True

    def test_includes_point(self, evaluator):
        assert evaluator.evaluate_expression("Interval[1, 10] includes 5") is True


class TestCollapse:
    """Test collapse function for merging intervals."""

    def test_collapse_overlapping(self, evaluator):
        result = evaluator.evaluate_expression("collapse { Interval[1, 5], Interval[3, 8] }")
        assert len(result) == 1
        assert result[0].low == 1
        assert result[0].high == 8

    def test_collapse_separate(self, evaluator):
        result = evaluator.evaluate_expression("collapse { Interval[1, 5], Interval[10, 15] }")
        assert len(result) == 2

    def test_collapse_multiple(self, evaluator):
        result = evaluator.evaluate_expression("collapse { Interval[1, 5], Interval[3, 8], Interval[10, 15] }")
        assert len(result) == 2
        assert result[0].low == 1
        assert result[0].high == 8
        assert result[1].low == 10
        assert result[1].high == 15

    def test_collapse_adjacent(self, evaluator):
        # Adjacent intervals should merge
        result = evaluator.evaluate_expression("collapse { Interval[1, 5], Interval[5, 10] }")
        assert len(result) == 1
        assert result[0].low == 1
        assert result[0].high == 10


class TestExpand:
    """Test expand function for interval expansion."""

    def test_expand_integer(self, evaluator):
        result = evaluator.evaluate_expression("expand Interval[1, 5]")
        assert result == [1, 2, 3, 4, 5]

    def test_expand_integer_open(self, evaluator):
        result = evaluator.evaluate_expression("expand Interval(1, 5)")
        assert result == [2, 3, 4]

    def test_expand_half_open(self, evaluator):
        result = evaluator.evaluate_expression("expand Interval[1, 5)")
        assert result == [1, 2, 3, 4]


class TestIntervalWidth:
    """Test interval width calculation."""

    def test_width_integer(self, evaluator):
        assert evaluator.evaluate_expression("width of Interval[1, 10]") == 9

    def test_width_decimal(self, evaluator):
        result = evaluator.evaluate_expression("width of Interval[1.0, 5.5]")
        assert result == pytest.approx(4.5)


class TestIntervalStartEnd:
    """Test interval start/end accessors."""

    def test_start_of(self, evaluator):
        assert evaluator.evaluate_expression("start of Interval[1, 10]") == 1

    def test_end_of(self, evaluator):
        assert evaluator.evaluate_expression("end of Interval[1, 10]") == 10


class TestIntervalPointFrom:
    """Test point from unit interval."""

    def test_point_from_unit(self, evaluator):
        assert evaluator.evaluate_expression("point from Interval[5, 5]") == 5

    def test_point_from_non_unit_raises(self, evaluator):
        with pytest.raises(Exception):
            evaluator.evaluate_expression("point from Interval[1, 5]")


class TestIntervalMeetsBefore:
    """Test interval meets before operator."""

    def test_meets_before_true(self, evaluator):
        # [1,5] meets before [5,10] at point 5 (half-open/half-closed)
        result = evaluator.evaluate_expression("Interval[1, 5) meets before Interval[5, 10]")
        assert result is True

    def test_meets_before_false(self, evaluator):
        # [5,10] does not meet before [1,5]
        result = evaluator.evaluate_expression("Interval[5, 10] meets before Interval[1, 5]")
        assert result is False


class TestIntervalMeetsAfter:
    """Test interval meets after operator."""

    def test_meets_after_true(self, evaluator):
        # [5,10] meets after [1,5)
        result = evaluator.evaluate_expression("Interval[5, 10] meets after Interval[1, 5)")
        assert result is True

    def test_meets_after_false(self, evaluator):
        # [1,5) does not meet after [5,10]
        result = evaluator.evaluate_expression("Interval[1, 5) meets after Interval[5, 10]")
        assert result is False


class TestIntervalUnion:
    """Test interval union as list operation."""

    def test_union_overlapping(self, evaluator):
        # Union returns a list containing both intervals
        result = evaluator.evaluate_expression("{ Interval[1, 5] } union { Interval[3, 8] }")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_union_removes_duplicates(self, evaluator):
        # Union of same interval returns single item
        result = evaluator.evaluate_expression("{ Interval[1, 5] } union { Interval[1, 5] }")
        assert len(result) == 1


class TestIntervalIntersect:
    """Test interval intersect as list operation."""

    def test_intersect_common(self, evaluator):
        # Intersect returns items in both lists
        result = evaluator.evaluate_expression("{ Interval[1, 5] } intersect { Interval[1, 5] }")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_intersect_different(self, evaluator):
        result = evaluator.evaluate_expression("{ Interval[1, 5] } intersect { Interval[10, 15] }")
        assert result == []


class TestIntervalExcept:
    """Test interval except as list operation."""

    def test_except_removes_matching(self, evaluator):
        # Except removes items from first list that are in second
        result = evaluator.evaluate_expression("{ Interval[1, 5], Interval[10, 15] } except { Interval[10, 15] }")
        assert len(result) == 1
        assert result[0].low == 1


class TestCollapseDateIntervals:
    """Test collapse with date intervals."""

    def test_collapse_date_overlapping(self, evaluator):
        result = evaluator.evaluate_expression(
            "collapse { Interval[@2024-01-01, @2024-01-15], Interval[@2024-01-10, @2024-01-25] }"
        )
        assert len(result) == 1


class TestExpandWithPer:
    """Test expand with per quantity."""

    def test_expand_per_2(self, evaluator):
        # Expand with step of 2
        result = evaluator.evaluate_expression("expand Interval[1, 6] per 2")
        # Should create intervals of width 2
        assert len(result) >= 1
