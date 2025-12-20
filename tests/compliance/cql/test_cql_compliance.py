"""
CQL Compliance Tests - Official HL7 CQL Test Suite.

This module runs the official HL7 CQL test suite against the FHIRKit CQL evaluator.
Tests are parametrized from the XML test files.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from tests.compliance.test_runner import (
    TestCase,
    get_test_statistics,
    load_cql_test_suites,
)

# Path to test data
DATA_DIR = Path(__file__).parent.parent / "cql" / "data"


def get_all_cql_tests() -> list[TestCase]:
    """Load all CQL test cases."""
    suites = load_cql_test_suites(DATA_DIR)
    tests = []
    for suite in suites:
        tests.extend(suite.all_tests)
    return tests


# Load tests at module level for parametrization
ALL_CQL_TESTS = get_all_cql_tests()


def evaluate_cql_expression(expression: str) -> Any:
    """Evaluate a CQL expression and return the result."""
    # Import here to avoid import errors if CQL module not available
    try:
        from fhirkit.engine.cql.evaluator import CQLEvaluator
    except ImportError:
        from fhir_cql.cql_evaluator import CQLEvaluator

    evaluator = CQLEvaluator()

    # Wrap expression in a library definition
    library_code = f"""
library ComplianceTest version '1.0.0'

define TestResult: {expression}
"""
    try:
        evaluator.compile(library_code)
        result = evaluator.evaluate_definition("TestResult")
        return result
    except Exception:
        raise


def normalize_result(result: Any) -> Any:
    """Normalize a CQL result for comparison."""
    if result is None:
        return None

    # Handle lists
    if isinstance(result, (list, tuple)):
        if len(result) == 0:
            return []
        if len(result) == 1:
            return normalize_result(result[0])
        return [normalize_result(r) for r in result]

    # Handle Decimal
    if isinstance(result, Decimal):
        return result

    # Handle FHIRDateTime - convert to normalized string format
    if hasattr(result, "year") and hasattr(result, "month") and hasattr(result, "hour"):
        # FHIRDateTime - format with full precision for comparison
        parts = [f"{result.year:04d}"]
        if result.month is not None:
            parts.append(f"-{result.month:02d}")
            if result.day is not None:
                parts.append(f"-{result.day:02d}")
                # Include time components - let comparison handle precision
                h = result.hour if result.hour is not None else 0
                m = result.minute if result.minute is not None else 0
                s = result.second if result.second is not None else 0
                ms = result.millisecond if result.millisecond is not None else 0
                parts.append(f"T{h:02d}:{m:02d}:{s:02d}.{ms:03d}")
        return "@" + "".join(parts)

    # Handle FHIRDate
    if hasattr(result, "year") and hasattr(result, "month") and not hasattr(result, "hour"):
        parts = [f"{result.year:04d}"]
        if result.month is not None:
            parts.append(f"-{result.month:02d}")
            if result.day is not None:
                parts.append(f"-{result.day:02d}")
        return "@" + "".join(parts)

    # Handle FHIRTime
    if hasattr(result, "hour") and hasattr(result, "minute") and not hasattr(result, "year"):
        parts = [f"{result.hour:02d}"]
        if result.minute is not None:
            parts.append(f":{result.minute:02d}")
            if result.second is not None:
                parts.append(f":{result.second:02d}")
                if result.millisecond is not None and result.millisecond != 0:
                    parts.append(f".{result.millisecond:03d}")
        return "@T" + "".join(parts)

    # Handle CQLInterval - convert to string format
    if hasattr(result, "low") and hasattr(result, "high") and hasattr(result, "low_closed"):
        low = normalize_result(result.low)
        high = normalize_result(result.high)
        low_bracket = "[" if result.low_closed else "("
        high_bracket = "]" if result.high_closed else ")"
        return f"Interval {low_bracket} {low}, {high} {high_bracket}"

    # Handle Quantity-like objects
    if hasattr(result, "value") and hasattr(result, "unit"):
        return {"value": Decimal(str(result.value)), "unit": result.unit}

    # Handle dicts (tuples, quantities, etc.)
    if isinstance(result, dict):
        if "value" in result and "unit" in result:
            return {"value": Decimal(str(result["value"])), "unit": result["unit"]}
        return result

    # Handle floats (convert to Decimal for precision)
    if isinstance(result, float):
        return Decimal(str(result))

    return result


def parse_interval_string(s: str) -> tuple[str, str, bool, bool] | None:
    """Parse an interval string like 'Interval [ 1, 10 ]' or 'Interval ( 1, 10 )'."""
    import re

    # Pattern: Interval [/( low, high ]/)]
    pattern = r"Interval\s*([\[\(])\s*(.+?)\s*,\s*(.+?)\s*([\]\)])"
    match = re.match(pattern, s.strip())
    if match:
        low_closed = match.group(1) == "["
        high_closed = match.group(4) == "]"
        return match.group(2).strip(), match.group(3).strip(), low_closed, high_closed
    return None


def compare_interval_strings(actual: str, expected: str) -> bool:
    """Compare two interval strings."""
    actual_parts = parse_interval_string(actual)
    expected_parts = parse_interval_string(expected)

    if not actual_parts or not expected_parts:
        return actual == expected

    actual_low, actual_high, actual_low_closed, actual_high_closed = actual_parts
    expected_low, expected_high, expected_low_closed, expected_high_closed = expected_parts

    # Compare closure
    if actual_low_closed != expected_low_closed or actual_high_closed != expected_high_closed:
        return False

    # Compare bounds (handle datetime, decimal, integer)
    return compare_interval_bounds(actual_low, expected_low) and compare_interval_bounds(actual_high, expected_high)


def compare_interval_bounds(actual: str, expected: str) -> bool:
    """Compare interval bound values."""
    # Handle datetime bounds
    if actual.startswith("@") and expected.startswith("@"):
        return compare_datetime_strings(actual, expected)

    # Handle decimal bounds
    try:
        actual_num = Decimal(actual)
        expected_num = Decimal(expected)
        return actual_num == expected_num
    except Exception:
        pass

    # String comparison
    return actual == expected


def compare_interval_list(actual: Any, expected: str) -> bool:
    """Compare a list of intervals against expected string format.

    Expected format: {Interval [ 1, 10 ], Interval [ 12, 19 ]}
    """
    import re

    # Parse expected intervals from string
    # Remove outer braces and split by 'Interval'
    inner = expected.strip()[1:-1].strip()  # Remove { }
    if not inner:
        return not actual or actual == []

    # Find all Interval[...] patterns
    interval_pattern = r"Interval\s*[\[\(][^\]\)]+[\]\)]"
    expected_intervals = re.findall(interval_pattern, inner)

    # Handle actual - should be a list
    if not isinstance(actual, list):
        actual = [actual] if actual else []

    if len(actual) != len(expected_intervals):
        return False

    # Compare each interval
    for act, exp in zip(actual, expected_intervals):
        if isinstance(act, str):
            if not compare_interval_strings(act, exp):
                return False
        else:
            return False

    return True


def parse_cql_list(expected: str) -> list[Any]:
    """Parse a CQL list literal like {'a', 'b'} or {1, 2, 3}."""
    import re

    inner = expected.strip()[1:-1].strip()  # Remove { }
    if not inner:
        return []

    # Handle string elements (quoted)
    if "'" in inner:
        # Find all quoted strings
        pattern = r"'([^']*)'|\"([^\"]*)\""
        matches = re.findall(pattern, inner)
        # Each match is a tuple (single_quoted, double_quoted)
        return [m[0] if m[0] else m[1] for m in matches]

    # Handle numeric elements
    elements = [e.strip() for e in inner.split(",")]
    result = []
    for elem in elements:
        try:
            if "." in elem:
                result.append(Decimal(elem))
            else:
                result.append(int(elem))
        except ValueError:
            result.append(elem)
    return result


def compare_cql_list(actual: Any, expected: str) -> bool:
    """Compare actual result against CQL list format {element, element}."""
    expected_list = parse_cql_list(expected)

    # Handle actual - should be a list
    if not isinstance(actual, list):
        actual = [actual] if actual else []

    if len(actual) != len(expected_list):
        return False

    return all(compare_results(a, e) for a, e in zip(actual, expected_list))


def compare_datetime_strings(actual: str, expected: str) -> bool:
    """Compare datetime strings with precision awareness.

    The expected string determines the precision level for comparison.
    E.g., @2016-06-11T00 means hour precision, @2016-06-11 means day precision.
    """
    import re

    # Strip @ prefix if present
    actual = actual.lstrip("@")
    expected = expected.lstrip("@")

    # Parse both into components
    # Pattern: YYYY[-MM[-DD[Thh[:mm[:ss[.fff]]][tz]]]]
    dt_pattern = r"^(\d{4})(?:-(\d{2})(?:-(\d{2})(?:T(\d{2})(?::(\d{2})(?::(\d{2})(?:\.(\d+))?)?)?([Z+-].*)?)?)?)?$"

    actual_match = re.match(dt_pattern, actual)
    expected_match = re.match(dt_pattern, expected)

    if not actual_match or not expected_match:
        return actual == expected

    # Compare only up to the precision of expected
    for i in range(1, 8):  # Groups 1-7: year, month, day, hour, minute, second, millisecond
        exp_val = expected_match.group(i)
        act_val = actual_match.group(i)

        if exp_val is None:
            # Expected doesn't have this component, stop comparing
            break

        if act_val is None:
            # Actual doesn't have component but expected does
            return False

        if exp_val != act_val:
            return False

    return True


def compare_results(actual: Any, expected: Any) -> bool:
    """Compare actual and expected results with type coercion."""
    actual = normalize_result(actual)

    if actual is None and expected is None:
        return True

    if actual is None or expected is None:
        return False

    # Handle quantity comparison
    if isinstance(expected, dict) and "value" in expected and "unit" in expected:
        if isinstance(actual, dict) and "value" in actual:
            return (
                Decimal(str(actual.get("value", 0))) == expected["value"]
                and actual.get("unit", "1") == expected["unit"]
            )
        return False

    # Handle Decimal comparison
    if isinstance(expected, Decimal):
        if isinstance(actual, (int, float, Decimal)):
            return Decimal(str(actual)) == expected
        return False

    # Handle integer comparison
    if isinstance(expected, int):
        if isinstance(actual, (int, float, Decimal)):
            return int(actual) == expected
        return False

    # Handle boolean comparison
    if isinstance(expected, bool):
        return actual == expected

    # Handle string comparison
    if isinstance(expected, str):
        # Handle quoted string literals from CQL tests (e.g., 'abc' should match abc)
        if expected.startswith("'") and expected.endswith("'"):
            expected_unquoted = expected[1:-1]
            return str(actual) == expected_unquoted
        # Handle interval list format: {Interval [...], Interval [...]}
        if expected.startswith("{") and "Interval" in expected:
            return compare_interval_list(actual, expected)
        # Handle general CQL list format: {'a', 'b'} or {1, 2}
        if expected.startswith("{") and expected.endswith("}"):
            return compare_cql_list(actual, expected)
        # Handle single interval format: Interval [...]
        if expected.startswith("Interval"):
            if isinstance(actual, str) and actual.startswith("Interval"):
                return compare_interval_strings(actual, expected)
            return False
        actual_str = str(actual)
        # Handle datetime string comparisons with precision awareness
        if expected.startswith("@") and actual_str.startswith("@"):
            return compare_datetime_strings(actual_str, expected)
        return actual_str == expected

    # Handle list comparison
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False
        if len(actual) != len(expected):
            return False
        return all(compare_results(a, e) for a, e in zip(actual, expected))

    # Default comparison
    return actual == expected


@pytest.mark.parametrize(
    "test_case",
    ALL_CQL_TESTS,
    ids=lambda tc: tc.test_id,
)
def test_cql_compliance(test_case: TestCase) -> None:
    """Run a single CQL compliance test."""
    if test_case.expects_error:
        if test_case.expects_semantic_error:
            with pytest.raises(Exception):
                evaluate_cql_expression(test_case.expression)
        else:
            # Runtime errors - expression should parse but fail at runtime
            with pytest.raises(Exception):
                evaluate_cql_expression(test_case.expression)
        return

    # Normal test - evaluate and compare
    try:
        result = evaluate_cql_expression(test_case.expression)
    except Exception as e:
        pytest.fail(f"Expression failed to evaluate: {e}\nExpression: {test_case.expression}")

    # Compare with expected outputs
    if not test_case.outputs:
        # No expected output means empty result
        assert result is None or result == [] or result == "", f"Expected empty result, got: {result}"
        return

    if len(test_case.outputs) == 1:
        expected = test_case.outputs[0].parse_value()
        assert compare_results(result, expected), (
            f"Result mismatch:\n"
            f"  Expression: {test_case.expression}\n"
            f"  Expected: {expected} ({type(expected).__name__})\n"
            f"  Actual: {result} ({type(result).__name__})"
        )
    else:
        # Multiple outputs - result should be a list
        expected_values = [out.parse_value() for out in test_case.outputs]
        if not isinstance(result, list):
            result = [result]
        assert len(result) == len(expected_values), (
            f"Result count mismatch:\n"
            f"  Expression: {test_case.expression}\n"
            f"  Expected {len(expected_values)} values: {expected_values}\n"
            f"  Actual {len(result)} values: {result}"
        )
        for i, (actual, expected) in enumerate(zip(result, expected_values)):
            assert compare_results(actual, expected), (
                f"Result mismatch at index {i}:\n"
                f"  Expression: {test_case.expression}\n"
                f"  Expected: {expected}\n"
                f"  Actual: {actual}"
            )


def test_cql_test_suite_loaded() -> None:
    """Verify that CQL test suites were loaded successfully."""
    suites = load_cql_test_suites(DATA_DIR)
    stats = get_test_statistics(suites)

    print("\nCQL Test Suite Statistics:")
    print(f"  Total suites: {stats['total_suites']}")
    print(f"  Total groups: {stats['total_groups']}")
    print(f"  Total tests: {stats['total_tests']}")
    print("  By suite:")
    for suite_name, count in stats["by_suite"].items():
        print(f"    {suite_name}: {count}")

    assert stats["total_suites"] > 0, "No CQL test suites found"
    assert stats["total_tests"] > 0, "No CQL tests found"
