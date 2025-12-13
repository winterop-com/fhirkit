"""CQL expression evaluator.

This module provides the main CQLEvaluator class for evaluating
CQL expressions and libraries against FHIR data.
"""

import sys
from pathlib import Path
from typing import Any

from antlr4 import CommonTokenStream, InputStream

# Add generated directory to path
_gen_path = str(Path(__file__).parent.parent.parent.parent.parent / "generated" / "cql")
if _gen_path not in sys.path:
    sys.path.insert(0, _gen_path)

from cqlLexer import cqlLexer  # noqa: E402
from cqlParser import cqlParser  # noqa: E402

from ..exceptions import CQLError  # noqa: E402
from .context import CQLContext, DataSource  # noqa: E402
from .library import CQLLibrary, LibraryManager  # noqa: E402
from .visitor import CQLEvaluatorVisitor  # noqa: E402

# Import ELM serializer (lazy import to avoid circular dependency)
ELMSerializer = None
ELMLibrary = None


class CQLErrorListener:
    """ANTLR error listener that raises CQLError."""

    def syntaxError(
        self,
        recognizer: Any,
        offendingSymbol: Any,
        line: int,
        column: int,
        msg: str,
        e: Any,
    ) -> None:
        raise CQLError(f"Syntax error at line {line}:{column}: {msg}")

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


class CQLEvaluator:
    """Main CQL evaluation engine.

    This class provides methods for:
    - Parsing and compiling CQL libraries
    - Evaluating CQL expressions
    - Evaluating named definitions within libraries
    - Managing library dependencies

    Example:
        evaluator = CQLEvaluator()

        # Load a library
        library = evaluator.compile('''
            library Example version '1.0'
            using FHIR version '4.0.1'
            define Sum: 1 + 2 + 3
        ''')

        # Evaluate a definition
        result = evaluator.evaluate_definition("Sum")
        # Returns: 6

        # Evaluate an inline expression
        result = evaluator.evaluate_expression("1 + 2 * 3")
        # Returns: 7
    """

    def __init__(
        self,
        data_source: DataSource | None = None,
        library_manager: LibraryManager | None = None,
    ):
        """Initialize the CQL evaluator.

        Args:
            data_source: Optional data source for retrieve operations
            library_manager: Optional library manager for dependencies
        """
        self._library_manager = library_manager or LibraryManager()
        self._data_source = data_source
        self._current_library: CQLLibrary | None = None
        self._expression_cache: dict[str, cqlParser.ExpressionContext] = {}

    @property
    def library_manager(self) -> LibraryManager:
        """Get the library manager."""
        return self._library_manager

    @property
    def current_library(self) -> CQLLibrary | None:
        """Get the currently loaded library."""
        return self._current_library

    def compile(self, source: str) -> CQLLibrary:
        """Compile CQL source code into a library.

        Args:
            source: CQL source code

        Returns:
            Compiled CQLLibrary

        Raises:
            CQLError: If compilation fails
        """
        tree = self._parse_library(source)
        context = CQLContext(
            library_manager=self._library_manager,
            data_source=self._data_source,
        )
        visitor = CQLEvaluatorVisitor(context)

        library = visitor.visit(tree)
        if not isinstance(library, CQLLibrary):
            raise CQLError("Failed to compile library")

        library.source = source
        self._library_manager.add_library(library)
        self._current_library = library

        return library

    def load_library(self, name: str, version: str | None = None) -> CQLLibrary | None:
        """Load a library by name.

        Args:
            name: Library name
            version: Optional library version

        Returns:
            CQLLibrary or None if not found
        """
        library = self._library_manager.get_library(name, version)
        if library:
            self._current_library = library
        return library

    def evaluate_definition(
        self,
        definition_name: str,
        resource: dict[str, Any] | None = None,
        parameters: dict[str, Any] | None = None,
        library: CQLLibrary | None = None,
    ) -> Any:
        """Evaluate a named definition within a library.

        Args:
            definition_name: Name of the definition to evaluate
            resource: Optional context resource (e.g., Patient)
            parameters: Optional parameter values
            library: Optional library (uses current library if not specified)

        Returns:
            Evaluation result

        Raises:
            CQLError: If definition not found or evaluation fails
        """
        lib = library or self._current_library
        if not lib:
            raise CQLError("No library loaded")

        definition = lib.get_definition(definition_name)
        if not definition:
            raise CQLError(f"Definition not found: {definition_name}")

        if not definition.expression_tree:
            raise CQLError(f"Definition has no expression: {definition_name}")

        # Create context
        context = CQLContext(
            resource=resource,
            library=lib,
            library_manager=self._library_manager,
            data_source=self._data_source,
        )

        # Set parameters
        if parameters:
            for name, value in parameters.items():
                context.set_parameter(name, value)

        # Evaluate
        visitor = CQLEvaluatorVisitor(context)
        visitor._library = lib

        return visitor.visit(definition.expression_tree)

    def evaluate_expression(
        self,
        expression: str,
        resource: dict[str, Any] | None = None,
        parameters: dict[str, Any] | None = None,
        library: CQLLibrary | None = None,
    ) -> Any:
        """Evaluate a CQL expression.

        Args:
            expression: CQL expression to evaluate
            resource: Optional context resource
            parameters: Optional parameter values
            library: Optional library context for definition resolution

        Returns:
            Evaluation result

        Raises:
            CQLError: If evaluation fails
        """
        tree = self._parse_expression(expression)

        lib = library or self._current_library
        context = CQLContext(
            resource=resource,
            library=lib,
            library_manager=self._library_manager,
            data_source=self._data_source,
        )

        # Set parameters
        if parameters:
            for name, value in parameters.items():
                context.set_parameter(name, value)

        visitor = CQLEvaluatorVisitor(context)
        if lib:
            visitor._library = lib

        return visitor.visit(tree)

    def evaluate_all_definitions(
        self,
        resource: dict[str, Any] | None = None,
        parameters: dict[str, Any] | None = None,
        library: CQLLibrary | None = None,
    ) -> dict[str, Any]:
        """Evaluate all definitions in a library.

        Args:
            resource: Optional context resource
            parameters: Optional parameter values
            library: Optional library (uses current library if not specified)

        Returns:
            Dictionary mapping definition names to their values

        Raises:
            CQLError: If no library loaded
        """
        lib = library or self._current_library
        if not lib:
            raise CQLError("No library loaded")

        results: dict[str, Any] = {}

        # Create context
        context = CQLContext(
            resource=resource,
            library=lib,
            library_manager=self._library_manager,
            data_source=self._data_source,
        )

        # Set parameters
        if parameters:
            for name, value in parameters.items():
                context.set_parameter(name, value)

        visitor = CQLEvaluatorVisitor(context)
        visitor._library = lib

        for name, definition in lib.definitions.items():
            if definition.expression_tree:
                try:
                    results[name] = visitor.visit(definition.expression_tree)
                except Exception as e:
                    results[name] = CQLError(f"Error evaluating {name}: {e}")

        return results

    def get_definitions(self, library: CQLLibrary | None = None) -> list[str]:
        """Get list of definition names in a library.

        Args:
            library: Optional library (uses current library if not specified)

        Returns:
            List of definition names
        """
        lib = library or self._current_library
        if not lib:
            return []
        return list(lib.definitions.keys())

    def get_parameters(self, library: CQLLibrary | None = None) -> dict[str, Any]:
        """Get parameter definitions from a library.

        Args:
            library: Optional library (uses current library if not specified)

        Returns:
            Dictionary mapping parameter names to their default values
        """
        lib = library or self._current_library
        if not lib:
            return {}
        return {name: param.default_value for name, param in lib.parameters.items()}

    def to_elm(self, source: str | None = None) -> Any:
        """Convert CQL source to ELM (Expression Logical Model).

        Args:
            source: CQL source code. If not provided, uses the source
                from the current library.

        Returns:
            ELMLibrary model instance.

        Raises:
            CQLError: If no source is available or conversion fails.

        Example:
            evaluator = CQLEvaluator()
            evaluator.compile("library Test define Sum: 1 + 2")
            elm = evaluator.to_elm()
        """
        global ELMSerializer, ELMLibrary
        if ELMSerializer is None:
            from ..elm.models.library import ELMLibrary as _ELMLibrary
            from ..elm.serializer import ELMSerializer as _ELMSerializer

            ELMSerializer = _ELMSerializer
            ELMLibrary = _ELMLibrary

        # Get source
        if source is None:
            if self._current_library and self._current_library.source:
                source = self._current_library.source
            else:
                raise CQLError("No CQL source available. Provide source or compile a library first.")

        try:
            serializer = ELMSerializer()
            return serializer.serialize_to_model(source)
        except Exception as e:
            raise CQLError(f"Failed to convert to ELM: {e}") from e

    def to_elm_json(self, source: str | None = None, indent: int = 2) -> str:
        """Convert CQL source to ELM JSON string.

        Args:
            source: CQL source code. If not provided, uses the source
                from the current library.
            indent: JSON indentation level (default 2).

        Returns:
            ELM library as JSON string.

        Raises:
            CQLError: If no source is available or conversion fails.

        Example:
            evaluator = CQLEvaluator()
            evaluator.compile("library Test define Sum: 1 + 2")
            elm_json = evaluator.to_elm_json()
            print(elm_json)
        """
        global ELMSerializer
        if ELMSerializer is None:
            from ..elm.serializer import ELMSerializer as _ELMSerializer

            ELMSerializer = _ELMSerializer

        # Get source
        if source is None:
            if self._current_library and self._current_library.source:
                source = self._current_library.source
            else:
                raise CQLError("No CQL source available. Provide source or compile a library first.")

        try:
            serializer = ELMSerializer()
            return serializer.serialize_library_json(source, indent)
        except Exception as e:
            raise CQLError(f"Failed to convert to ELM JSON: {e}") from e

    def to_elm_dict(self, source: str | None = None) -> dict[str, Any]:
        """Convert CQL source to ELM dictionary.

        Args:
            source: CQL source code. If not provided, uses the source
                from the current library.

        Returns:
            ELM library as dictionary.

        Raises:
            CQLError: If no source is available or conversion fails.
        """
        global ELMSerializer
        if ELMSerializer is None:
            from ..elm.serializer import ELMSerializer as _ELMSerializer

            ELMSerializer = _ELMSerializer

        # Get source
        if source is None:
            if self._current_library and self._current_library.source:
                source = self._current_library.source
            else:
                raise CQLError("No CQL source available. Provide source or compile a library first.")

        try:
            serializer = ELMSerializer()
            return serializer.serialize_library(source)
        except Exception as e:
            raise CQLError(f"Failed to convert to ELM dict: {e}") from e

    def _parse_library(self, source: str) -> cqlParser.LibraryContext:
        """Parse CQL library source code."""
        try:
            input_stream = InputStream(source)
            lexer = cqlLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = cqlParser(token_stream)

            parser.removeErrorListeners()
            parser.addErrorListener(CQLErrorListener())

            return parser.library()

        except CQLError:
            raise
        except Exception as e:
            raise CQLError(f"Failed to parse library: {e}") from e

    def _parse_expression(self, expression: str) -> cqlParser.ExpressionContext:
        """Parse a single CQL expression."""
        if expression in self._expression_cache:
            return self._expression_cache[expression]

        try:
            input_stream = InputStream(expression)
            lexer = cqlLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = cqlParser(token_stream)

            parser.removeErrorListeners()
            parser.addErrorListener(CQLErrorListener())

            tree = parser.expression()
            self._expression_cache[expression] = tree
            return tree

        except CQLError:
            raise
        except Exception as e:
            raise CQLError(f"Failed to parse expression: {expression}") from e

    def clear_cache(self) -> None:
        """Clear expression parse cache."""
        self._expression_cache.clear()


def compile_library(source: str) -> CQLLibrary:
    """Convenience function to compile a CQL library.

    Args:
        source: CQL source code

    Returns:
        Compiled CQLLibrary
    """
    evaluator = CQLEvaluator()
    return evaluator.compile(source)


def evaluate(expression: str, resource: dict[str, Any] | None = None) -> Any:
    """Convenience function to evaluate a CQL expression.

    Args:
        expression: CQL expression
        resource: Optional context resource

    Returns:
        Evaluation result
    """
    evaluator = CQLEvaluator()
    return evaluator.evaluate_expression(expression, resource)
