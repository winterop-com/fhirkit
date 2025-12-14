"""Tests for ELM type casting (As expression)."""

from decimal import Decimal

import pytest

from fhirkit.engine.cql.context import CQLContext
from fhirkit.engine.elm.exceptions import ELMExecutionError
from fhirkit.engine.elm.visitor import ELMExpressionVisitor
from fhirkit.engine.types import FHIRDate, FHIRDateTime


class TestAsExpression:
    """Test As (type cast) expression."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = CQLContext()
        self.visitor = ELMExpressionVisitor(self.context)

    def test_cast_integer_to_integer(self):
        """Test casting integer to integer (identity)."""
        node = {
            "type": "As",
            "asType": "Integer",
            "operand": {"type": "Literal", "valueType": "Integer", "value": "42"},
        }
        result = self.visitor.evaluate(node)
        assert result == 42

    def test_cast_decimal_to_integer(self):
        """Test casting decimal to integer."""
        node = {
            "type": "As",
            "asType": "Integer",
            "operand": {"type": "Literal", "valueType": "Decimal", "value": "3.7"},
        }
        result = self.visitor.evaluate(node)
        assert result == 3

    def test_cast_string_to_integer(self):
        """Test casting string to integer."""
        node = {
            "type": "As",
            "asType": "Integer",
            "operand": {"type": "Literal", "valueType": "String", "value": "123"},
        }
        result = self.visitor.evaluate(node)
        assert result == 123

    def test_cast_invalid_string_to_integer(self):
        """Test casting invalid string to integer returns null."""
        node = {
            "type": "As",
            "asType": "Integer",
            "operand": {"type": "Literal", "valueType": "String", "value": "abc"},
        }
        result = self.visitor.evaluate(node)
        assert result is None

    def test_cast_to_decimal(self):
        """Test casting integer to decimal."""
        node = {
            "type": "As",
            "asType": "Decimal",
            "operand": {"type": "Literal", "valueType": "Integer", "value": "42"},
        }
        result = self.visitor.evaluate(node)
        assert result == Decimal("42")

    def test_cast_integer_to_string(self):
        """Test casting integer to string."""
        node = {
            "type": "As",
            "asType": "String",
            "operand": {"type": "Literal", "valueType": "Integer", "value": "42"},
        }
        result = self.visitor.evaluate(node)
        assert result == "42"

    def test_cast_boolean_to_string(self):
        """Test casting boolean to string."""
        node = {
            "type": "As",
            "asType": "String",
            "operand": {"type": "Literal", "valueType": "Boolean", "value": "true"},
        }
        result = self.visitor.evaluate(node)
        assert result == "true"

    def test_cast_string_to_boolean_true(self):
        """Test casting string to boolean (true)."""
        for val in ["true", "t", "yes", "y", "1"]:
            node = {
                "type": "As",
                "asType": "Boolean",
                "operand": {"type": "Literal", "valueType": "String", "value": val},
            }
            result = self.visitor.evaluate(node)
            assert result is True, f"Expected True for '{val}'"

    def test_cast_string_to_boolean_false(self):
        """Test casting string to boolean (false)."""
        for val in ["false", "f", "no", "n", "0"]:
            node = {
                "type": "As",
                "asType": "Boolean",
                "operand": {"type": "Literal", "valueType": "String", "value": val},
            }
            result = self.visitor.evaluate(node)
            assert result is False, f"Expected False for '{val}'"

    def test_cast_integer_to_boolean(self):
        """Test casting integer to boolean."""
        node_true = {
            "type": "As",
            "asType": "Boolean",
            "operand": {"type": "Literal", "valueType": "Integer", "value": "1"},
        }
        assert self.visitor.evaluate(node_true) is True

        node_false = {
            "type": "As",
            "asType": "Boolean",
            "operand": {"type": "Literal", "valueType": "Integer", "value": "0"},
        }
        assert self.visitor.evaluate(node_false) is False

    def test_cast_datetime_to_date(self):
        """Test casting datetime to date."""
        node = {
            "type": "As",
            "asType": "Date",
            "operand": {
                "type": "DateTime",
                "year": 2024,
                "month": 6,
                "day": 15,
                "hour": 10,
                "minute": 30,
            },
        }
        result = self.visitor.evaluate(node)
        assert isinstance(result, FHIRDate)
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15

    def test_cast_date_to_datetime(self):
        """Test casting date to datetime."""
        node = {
            "type": "As",
            "asType": "DateTime",
            "operand": {"type": "Date", "year": 2024, "month": 6, "day": 15},
        }
        result = self.visitor.evaluate(node)
        assert isinstance(result, FHIRDateTime)
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15

    def test_cast_null_returns_null(self):
        """Test casting null returns null."""
        node = {
            "type": "As",
            "asType": "Integer",
            "operand": {"type": "Null"},
        }
        result = self.visitor.evaluate(node)
        assert result is None

    def test_cast_strict_mode_error(self):
        """Test strict mode raises error on invalid cast."""
        node = {
            "type": "As",
            "asType": "Integer",
            "strict": True,
            "operand": {"type": "Literal", "valueType": "String", "value": "invalid"},
        }
        with pytest.raises(ELMExecutionError):
            self.visitor.evaluate(node)

    def test_cast_with_type_specifier(self):
        """Test casting using asTypeSpecifier instead of asType."""
        node = {
            "type": "As",
            "asTypeSpecifier": {"type": "NamedTypeSpecifier", "name": "Integer"},
            "operand": {"type": "Literal", "valueType": "String", "value": "42"},
        }
        result = self.visitor.evaluate(node)
        assert result == 42

    def test_cast_with_namespace_prefix(self):
        """Test casting with namespace prefix in type name."""
        node = {
            "type": "As",
            "asType": "{urn:hl7-org:elm-types:r1}Integer",
            "operand": {"type": "Literal", "valueType": "Decimal", "value": "3.14"},
        }
        result = self.visitor.evaluate(node)
        assert result == 3

    def test_cast_to_list(self):
        """Test casting singleton to list (singleton promotion)."""
        node = {
            "type": "As",
            "asType": "List<Integer>",
            "operand": {"type": "Literal", "valueType": "Integer", "value": "42"},
        }
        result = self.visitor.evaluate(node)
        assert result == [42]

    def test_cast_resource_type(self):
        """Test casting FHIR resource types."""
        patient = {"resourceType": "Patient", "id": "123"}
        self.context.set_alias("$this", patient)

        node = {
            "type": "As",
            "asType": "patient",
            "operand": {
                "type": "AliasRef",
                "name": "$this",
            },
        }
        result = self.visitor.evaluate(node)
        assert result == patient
