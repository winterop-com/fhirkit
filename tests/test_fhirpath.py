"""Tests for FHIRPath parser."""

import sys
from pathlib import Path

# Add generated directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "generated" / "fhirpath"))

from antlr4 import CommonTokenStream, InputStream
from fhirpathLexer import fhirpathLexer
from fhirpathParser import fhirpathParser


def parse_fhirpath(expression: str) -> fhirpathParser.ExpressionContext:
    """Parse a FHIRPath expression and return the parse tree."""
    input_stream = InputStream(expression)
    lexer = fhirpathLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = fhirpathParser(token_stream)
    return parser.expression()


class TestFHIRPathParser:
    def test_simple_path(self):
        tree = parse_fhirpath("Patient.name")
        assert tree is not None

    def test_function_call(self):
        tree = parse_fhirpath("Patient.name.given.first()")
        assert tree is not None

    def test_where_clause(self):
        tree = parse_fhirpath("Patient.name.where(use = 'official')")
        assert tree is not None

    def test_boolean_expression(self):
        tree = parse_fhirpath("Patient.active = true")
        assert tree is not None

    def test_arithmetic(self):
        tree = parse_fhirpath("1 + 2 * 3")
        assert tree is not None

    def test_date_literal(self):
        tree = parse_fhirpath("@2024-01-01")
        assert tree is not None

    def test_datetime_literal(self):
        tree = parse_fhirpath("@2024-01-01T10:30:00Z")
        assert tree is not None

    def test_exists(self):
        tree = parse_fhirpath("Patient.name.exists()")
        assert tree is not None

    def test_union(self):
        tree = parse_fhirpath("Patient.name | Patient.address")
        assert tree is not None

    def test_membership(self):
        tree = parse_fhirpath("'A' in Patient.name.given")
        assert tree is not None
