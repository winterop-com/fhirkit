"""FHIRPath expression evaluator."""

import sys
from pathlib import Path
from typing import Any

from antlr4 import CommonTokenStream, InputStream

# Add generated directory to path
_gen_path = str(Path(__file__).parent.parent.parent.parent.parent / "generated" / "fhirpath")
if _gen_path not in sys.path:
    sys.path.insert(0, _gen_path)

from fhirpathLexer import fhirpathLexer  # noqa: E402
from fhirpathParser import fhirpathParser  # noqa: E402

from ..context import EvaluationContext  # noqa: E402
from ..exceptions import FHIRPathError  # noqa: E402
from .visitor import FHIRPathEvaluatorVisitor  # noqa: E402


class FHIRPathEvaluator:
    """
    Evaluates FHIRPath expressions against FHIR resources.

    This evaluator can be extended by CQL to support additional
    operations while reusing FHIRPath functionality.

    Example:
        evaluator = FHIRPathEvaluator()
        result = evaluator.evaluate("Patient.name.given", patient_resource)
        # Returns: ["John", "William"]
    """

    def __init__(self, context: EvaluationContext | None = None):
        """
        Initialize the evaluator.

        Args:
            context: Optional evaluation context. If not provided,
                    a new context will be created for each evaluation.
        """
        self._context = context
        self._cache: dict[str, fhirpathParser.ExpressionContext] = {}

    def evaluate(
        self,
        expression: str,
        resource: dict[str, Any] | list[Any] | None = None,
        context: EvaluationContext | None = None,
    ) -> list[Any]:
        """
        Evaluate a FHIRPath expression against a resource.

        Args:
            expression: FHIRPath expression to evaluate
            resource: FHIR resource (dict) or collection to evaluate against
            context: Optional evaluation context (overrides instance context)

        Returns:
            Collection (list) of results

        Raises:
            FHIRPathError: If expression parsing or evaluation fails
        """
        # Parse expression
        tree = self._parse(expression)

        # Build context
        ctx = context or self._context
        if ctx is None:
            if isinstance(resource, dict):
                ctx = EvaluationContext(resource=resource)
            else:
                ctx = EvaluationContext()

        # Build input collection
        if resource is None:
            input_collection = []
        elif isinstance(resource, list):
            input_collection = resource
        else:
            input_collection = [resource]

        # Evaluate
        visitor = FHIRPathEvaluatorVisitor(ctx, input_collection)
        return visitor.evaluate(tree)

    def evaluate_boolean(
        self,
        expression: str,
        resource: dict[str, Any] | list[Any] | None = None,
        context: EvaluationContext | None = None,
    ) -> bool | None:
        """
        Evaluate a FHIRPath expression and return a boolean result.

        Args:
            expression: FHIRPath expression to evaluate
            resource: FHIR resource or collection
            context: Optional evaluation context

        Returns:
            True, False, or None (empty result)
        """
        result = self.evaluate(expression, resource, context)

        if not result:
            return None
        if len(result) == 1:
            val = result[0]
            if isinstance(val, bool):
                return val
            return True  # Non-empty, non-boolean is truthy
        # Multiple values - could be error in strict mode
        return True

    def evaluate_single(
        self,
        expression: str,
        resource: dict[str, Any] | list[Any] | None = None,
        context: EvaluationContext | None = None,
    ) -> Any | None:
        """
        Evaluate a FHIRPath expression expecting a single result.

        Args:
            expression: FHIRPath expression to evaluate
            resource: FHIR resource or collection
            context: Optional evaluation context

        Returns:
            Single value or None

        Raises:
            FHIRPathError: If result has more than one element
        """
        result = self.evaluate(expression, resource, context)

        if not result:
            return None
        if len(result) == 1:
            return result[0]
        raise FHIRPathError(f"Expected single result, got {len(result)} elements")

    def check(
        self,
        expression: str,
        resource: dict[str, Any] | list[Any] | None = None,
        context: EvaluationContext | None = None,
    ) -> bool:
        """
        Check if a FHIRPath expression returns a truthy result.

        Convenience method for constraint checking.

        Args:
            expression: FHIRPath expression to evaluate
            resource: FHIR resource or collection
            context: Optional evaluation context

        Returns:
            True if result is truthy, False otherwise
        """
        result = self.evaluate_boolean(expression, resource, context)
        return result is True

    def _parse(self, expression: str) -> fhirpathParser.ExpressionContext:
        """Parse a FHIRPath expression, using cache if available."""
        if expression in self._cache:
            return self._cache[expression]

        try:
            input_stream = InputStream(expression)
            lexer = fhirpathLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = fhirpathParser(token_stream)

            # Add error listener
            parser.removeErrorListeners()
            parser.addErrorListener(FHIRPathErrorListener())

            tree = parser.expression()

            # Cache successful parse
            self._cache[expression] = tree
            return tree

        except Exception as e:
            raise FHIRPathError(f"Failed to parse expression: {expression}") from e

    def clear_cache(self) -> None:
        """Clear the expression parse cache."""
        self._cache.clear()


class FHIRPathErrorListener:
    """ANTLR error listener that raises FHIRPathError."""

    def syntaxError(
        self,
        recognizer: Any,
        offendingSymbol: Any,
        line: int,
        column: int,
        msg: str,
        e: Any,
    ) -> None:
        raise FHIRPathError(f"Syntax error at line {line}:{column}: {msg}")

    def reportAmbiguity(
        self,
        recognizer: Any,
        dfa: Any,
        startIndex: int,
        stopIndex: int,
        exact: bool,
        ambigAlts: Any,
        configs: Any,
    ) -> None:
        pass

    def reportAttemptingFullContext(
        self,
        recognizer: Any,
        dfa: Any,
        startIndex: int,
        stopIndex: int,
        conflictingAlts: Any,
        configs: Any,
    ) -> None:
        pass

    def reportContextSensitivity(
        self,
        recognizer: Any,
        dfa: Any,
        startIndex: int,
        stopIndex: int,
        prediction: int,
        configs: Any,
    ) -> None:
        pass


def evaluate(expression: str, resource: dict[str, Any] | list[Any] | None = None) -> list[Any]:
    """
    Convenience function to evaluate a FHIRPath expression.

    Args:
        expression: FHIRPath expression
        resource: FHIR resource or collection

    Returns:
        Collection of results
    """
    evaluator = FHIRPathEvaluator()
    return evaluator.evaluate(expression, resource)
