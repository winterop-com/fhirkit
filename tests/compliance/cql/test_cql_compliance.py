"""
CQL Compliance Tests - Official HL7 CQL Test Suite.

This module runs the official HL7 CQL test suite against the FHIRKit CQL evaluator.
Tests are parametrized from the XML test files.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from tests.compliance.test_runner import (
    TestCase,
    TestOutput,
    load_cql_test_suites,
    get_test_statistics,
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
        library = evaluator.compile(library_code)
        result = evaluator.evaluate_definition("TestResult")
        return result
    except Exception as e:
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
        return str(actual) == expected

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
        assert result is None or result == [] or result == "", (
            f"Expected empty result, got: {result}"
        )
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

    print(f"\nCQL Test Suite Statistics:")
    print(f"  Total suites: {stats['total_suites']}")
    print(f"  Total groups: {stats['total_groups']}")
    print(f"  Total tests: {stats['total_tests']}")
    print(f"  By suite:")
    for suite_name, count in stats["by_suite"].items():
        print(f"    {suite_name}: {count}")

    assert stats["total_suites"] > 0, "No CQL test suites found"
    assert stats["total_tests"] > 0, "No CQL tests found"
