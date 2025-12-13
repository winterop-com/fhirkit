"""CQL Evaluator Visitor.

This module implements the ANTLR visitor pattern for CQL evaluation.
It walks the parse tree and evaluates expressions.
"""

import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from antlr4 import ParseTreeVisitor

# Add generated directory to path
_gen_path = str(Path(__file__).parent.parent.parent.parent.parent / "generated" / "cql")
if _gen_path not in sys.path:
    sys.path.insert(0, _gen_path)

from cqlParser import cqlParser  # noqa: E402
from cqlVisitor import cqlVisitor  # noqa: E402

from ..exceptions import CQLError  # noqa: E402
from ..types import FHIRDate, FHIRDateTime, FHIRTime, Quantity  # noqa: E402
from .context import CQLContext  # noqa: E402
from .library import (  # noqa: E402
    CodeDefinition,
    CodeSystemDefinition,
    ConceptDefinition,
    CQLLibrary,
    ExpressionDefinition,
    FunctionDefinition,
    IncludeDefinition,
    ParameterDefinition,
    UsingDefinition,
    ValueSetDefinition,
)
from .types import CQLCode, CQLConcept, CQLInterval, CQLRatio, CQLTuple  # noqa: E402


class CQLEvaluatorVisitor(cqlVisitor):
    """Visitor that evaluates CQL expressions.

    This visitor implements the evaluation logic for CQL by walking
    the ANTLR parse tree and computing values.
    """

    def __init__(self, context: CQLContext | None = None):
        """Initialize the visitor.

        Args:
            context: CQL evaluation context
        """
        self.context = context or CQLContext()
        self._library: CQLLibrary | None = None

    @property
    def library(self) -> CQLLibrary | None:
        """Get the current library."""
        return self._library

    def evaluate(self, tree: Any) -> Any:
        """Evaluate a parse tree and return the result."""
        return self.visit(tree)

    # =========================================================================
    # Library Structure
    # =========================================================================

    def visitLibrary(self, ctx: cqlParser.LibraryContext) -> CQLLibrary:
        """Visit a library and build CQLLibrary structure."""
        # Get library definition
        lib_def = ctx.libraryDefinition()
        if lib_def:
            name, version = self.visit(lib_def)
        else:
            name, version = "Anonymous", None

        self._library = CQLLibrary(name=name, version=version)

        # Process all definitions in the library
        for child in ctx.children or []:
            if isinstance(child, cqlParser.LibraryDefinitionContext):
                continue  # Already processed
            result = self.visit(child)
            if result is not None:
                self._process_library_element(result)

        return self._library

    def _process_library_element(self, element: Any) -> None:
        """Process a library element and add it to the library."""
        if self._library is None:
            return

        if isinstance(element, UsingDefinition):
            self._library.using.append(element)
        elif isinstance(element, IncludeDefinition):
            self._library.includes.append(element)
        elif isinstance(element, CodeSystemDefinition):
            self._library.codesystems[element.name] = element
        elif isinstance(element, ValueSetDefinition):
            self._library.valuesets[element.name] = element
        elif isinstance(element, CodeDefinition):
            self._library.codes[element.name] = element
        elif isinstance(element, ConceptDefinition):
            self._library.concepts[element.name] = element
        elif isinstance(element, ParameterDefinition):
            self._library.parameters[element.name] = element
        elif isinstance(element, ExpressionDefinition):
            self._library.definitions[element.name] = element
        elif isinstance(element, FunctionDefinition):
            self._library.add_function(element)
        elif isinstance(element, str) and element.startswith("context:"):
            # Context definition
            ctx_name = element[8:]
            if ctx_name not in self._library.contexts:
                self._library.contexts.append(ctx_name)
            self._library.current_context = ctx_name

    def visitLibraryDefinition(self, ctx: cqlParser.LibraryDefinitionContext) -> tuple[str, str | None]:
        """Visit library definition and extract name and version."""
        name_ctx = ctx.qualifiedIdentifier()
        name = self._get_identifier_text(name_ctx)

        version = None
        version_ctx = ctx.versionSpecifier()
        if version_ctx:
            version = self._unquote_string(version_ctx.getText())

        return name, version

    def visitUsingDefinition(self, ctx: cqlParser.UsingDefinitionContext) -> UsingDefinition:
        """Visit using definition."""
        # UsingDefinition uses qualifiedIdentifier for the model name
        model_id = ctx.qualifiedIdentifier()
        model = self._get_identifier_text(model_id)

        version = None
        version_ctx = ctx.versionSpecifier()
        if version_ctx:
            version = self._unquote_string(version_ctx.getText())

        return UsingDefinition(model=model, version=version)

    def visitIncludeDefinition(self, ctx: cqlParser.IncludeDefinitionContext) -> IncludeDefinition:
        """Visit include definition."""
        lib_id = ctx.qualifiedIdentifier()
        library = self._get_identifier_text(lib_id)

        version = None
        version_ctx = ctx.versionSpecifier()
        if version_ctx:
            version = self._unquote_string(version_ctx.getText())

        alias = None
        local_id = ctx.localIdentifier()
        if local_id:
            alias = self._get_identifier_text(local_id)

        return IncludeDefinition(library=library, version=version, alias=alias)

    def visitParameterDefinition(self, ctx: cqlParser.ParameterDefinitionContext) -> ParameterDefinition:
        """Visit parameter definition."""
        name = self._get_identifier_text(ctx.identifier())

        type_spec = None
        type_ctx = ctx.typeSpecifier()
        if type_ctx:
            type_spec = type_ctx.getText()

        default_value = None
        expr = ctx.expression()
        if expr:
            default_value = self.visit(expr)

        return ParameterDefinition(name=name, type_specifier=type_spec, default_value=default_value)

    def visitCodesystemDefinition(self, ctx: cqlParser.CodesystemDefinitionContext) -> CodeSystemDefinition:
        """Visit codesystem definition."""
        name = self._get_identifier_text(ctx.identifier())
        cs_id = self._unquote_string(ctx.codesystemId().getText())

        version = None
        version_ctx = ctx.versionSpecifier()
        if version_ctx:
            version = self._unquote_string(version_ctx.getText())

        return CodeSystemDefinition(name=name, id=cs_id, version=version)

    def visitValuesetDefinition(self, ctx: cqlParser.ValuesetDefinitionContext) -> ValueSetDefinition:
        """Visit valueset definition."""
        name = self._get_identifier_text(ctx.identifier())
        vs_id = self._unquote_string(ctx.valuesetId().getText())

        version = None
        version_ctx = ctx.versionSpecifier()
        if version_ctx:
            version = self._unquote_string(version_ctx.getText())

        codesystems: list[str] = []
        cs_ctx = ctx.codesystems()
        if cs_ctx:
            for cs_id in cs_ctx.codesystemIdentifier():
                codesystems.append(self._get_identifier_text(cs_id))

        return ValueSetDefinition(name=name, id=vs_id, version=version, codesystems=codesystems)

    def visitCodeDefinition(self, ctx: cqlParser.CodeDefinitionContext) -> CodeDefinition:
        """Visit code definition."""
        name = self._get_identifier_text(ctx.identifier())
        code = self._unquote_string(ctx.codeId().getText())
        codesystem = self._get_identifier_text(ctx.codesystemIdentifier())

        display = None
        display_ctx = ctx.displayClause() if hasattr(ctx, "displayClause") else None
        if display_ctx:
            display = self._unquote_string(display_ctx.STRING().getText())

        return CodeDefinition(name=name, code=code, codesystem=codesystem, display=display)

    def visitConceptDefinition(self, ctx: cqlParser.ConceptDefinitionContext) -> ConceptDefinition:
        """Visit concept definition."""
        name = self._get_identifier_text(ctx.identifier())

        codes = []
        for code_id in ctx.codeIdentifier():
            codes.append(self._get_identifier_text(code_id))

        display = None
        display_ctx = ctx.displayClause() if hasattr(ctx, "displayClause") else None
        if display_ctx:
            display = self._unquote_string(display_ctx.STRING().getText())

        return ConceptDefinition(name=name, codes=codes, display=display)

    def visitContextDefinition(self, ctx: cqlParser.ContextDefinitionContext) -> str:
        """Visit context definition."""
        context_name = self._get_identifier_text(ctx.identifier())
        return f"context:{context_name}"

    def visitExpressionDefinition(self, ctx: cqlParser.ExpressionDefinitionContext) -> ExpressionDefinition:
        """Visit expression definition (define statement)."""
        name = self._get_identifier_text(ctx.identifier())

        access_modifier = None
        access_ctx = ctx.accessModifier()
        if access_ctx:
            access_modifier = access_ctx.getText()

        # Store the expression tree for later evaluation
        expr = ctx.expression()

        return ExpressionDefinition(
            name=name,
            access_modifier=access_modifier,
            expression_tree=expr,
            context=self._library.current_context if self._library else None,
        )

    def visitFunctionDefinition(self, ctx: cqlParser.FunctionDefinitionContext) -> FunctionDefinition:
        """Visit function definition."""
        name = self._get_identifier_text(ctx.identifierOrFunctionIdentifier())

        parameters = []
        for operand in ctx.operandDefinition():
            param_name = self._get_identifier_text(operand.referentialIdentifier())
            param_type = operand.typeSpecifier().getText() if operand.typeSpecifier() else "Any"
            parameters.append((param_name, param_type))

        return_type = None
        return_ctx = ctx.typeSpecifier()
        if return_ctx:
            return_type = return_ctx.getText()

        fluent = ctx.fluentModifier() is not None
        external = ctx.functionBody() is None or "external" in ctx.getText()

        body = ctx.functionBody()
        body_tree = body.expression() if body else None

        return FunctionDefinition(
            name=name,
            parameters=parameters,
            return_type=return_type,
            body_tree=body_tree,
            fluent=fluent,
            external=external,
        )

    # =========================================================================
    # Literals
    # =========================================================================

    def visitLiteralTerm(self, ctx: cqlParser.LiteralTermContext) -> Any:
        """Visit a literal term."""
        return self.visit(ctx.literal())

    def visitBooleanLiteral(self, ctx: cqlParser.BooleanLiteralContext) -> bool:
        """Visit a boolean literal."""
        return ctx.getText().lower() == "true"

    def visitNullLiteral(self, ctx: cqlParser.NullLiteralContext) -> None:
        """Visit a null literal."""
        return None

    def visitStringLiteral(self, ctx: cqlParser.StringLiteralContext) -> str:
        """Visit a string literal."""
        return self._unquote_string(ctx.getText())

    def visitNumberLiteral(self, ctx: cqlParser.NumberLiteralContext) -> int | Decimal:
        """Visit a number literal."""
        text = ctx.getText()
        if "." in text:
            return Decimal(text)
        return int(text)

    def visitLongNumberLiteral(self, ctx: cqlParser.LongNumberLiteralContext) -> int:
        """Visit a long number literal."""
        text = ctx.getText()
        # Remove 'L' suffix if present
        if text.endswith("L"):
            text = text[:-1]
        return int(text)

    def visitDateTimeLiteral(self, ctx: cqlParser.DateTimeLiteralContext) -> FHIRDateTime | None:
        """Visit a datetime literal (@YYYY-MM-DDThh:mm:ss)."""
        text = ctx.getText()
        return FHIRDateTime.parse(text)

    def visitDateLiteral(self, ctx: cqlParser.DateLiteralContext) -> FHIRDate | None:
        """Visit a date literal (@YYYY-MM-DD)."""
        text = ctx.getText()
        # Remove @ prefix
        if text.startswith("@"):
            text = text[1:]
        return FHIRDate.parse(text)

    def visitTimeLiteral(self, ctx: cqlParser.TimeLiteralContext) -> FHIRTime | None:
        """Visit a time literal (@Thh:mm:ss)."""
        text = ctx.getText()
        # Remove @T prefix
        if text.startswith("@T"):
            text = text[2:]
        elif text.startswith("@"):
            text = text[1:]
        return FHIRTime.parse(text)

    def visitQuantityLiteral(self, ctx: cqlParser.QuantityLiteralContext) -> Quantity:
        """Visit a quantity literal (e.g., 10 'mg')."""
        quantity_ctx = ctx.quantity()
        return self.visitQuantity(quantity_ctx)

    def visitQuantity(self, ctx: cqlParser.QuantityContext) -> Quantity:
        """Visit a quantity value."""
        number_text = ctx.NUMBER().getText()
        value = Decimal(number_text) if "." in number_text else Decimal(int(number_text))

        unit = "1"  # Default unit
        unit_ctx = ctx.unit()
        if unit_ctx:
            unit = self._unquote_string(unit_ctx.getText())

        return Quantity(value=value, unit=unit)

    def visitRatioLiteral(self, ctx: cqlParser.RatioLiteralContext) -> CQLRatio:
        """Visit a ratio literal (e.g., 1:10)."""
        ratio_ctx = ctx.ratio()
        return self.visitRatio(ratio_ctx)

    def visitRatio(self, ctx: cqlParser.RatioContext) -> CQLRatio:
        """Visit a ratio value."""
        quantities = ctx.quantity()
        numerator = self.visitQuantity(quantities[0])
        denominator = self.visitQuantity(quantities[1])
        return CQLRatio(numerator=numerator, denominator=denominator)

    # =========================================================================
    # Selectors (Constructors)
    # =========================================================================

    def visitIntervalSelectorTerm(self, ctx: cqlParser.IntervalSelectorTermContext) -> CQLInterval[Any]:
        """Visit interval selector term."""
        return self.visit(ctx.intervalSelector())

    def visitIntervalSelector(self, ctx: cqlParser.IntervalSelectorContext) -> CQLInterval[Any]:
        """Visit interval selector (Interval[low, high])."""
        # Determine if bounds are open or closed
        text = ctx.getText()
        low_closed = text.startswith("Interval[")
        high_closed = text.endswith("]")

        # Get the expressions
        expressions = ctx.expression()
        low = self.visit(expressions[0]) if len(expressions) > 0 else None
        high = self.visit(expressions[1]) if len(expressions) > 1 else None

        return CQLInterval(low=low, high=high, low_closed=low_closed, high_closed=high_closed)

    def visitListSelectorTerm(self, ctx: cqlParser.ListSelectorTermContext) -> list[Any]:
        """Visit list selector term."""
        return self.visit(ctx.listSelector())

    def visitListSelector(self, ctx: cqlParser.ListSelectorContext) -> list[Any]:
        """Visit list selector ({ item1, item2, ... })."""
        result = []
        for expr in ctx.expression():
            result.append(self.visit(expr))
        return result

    def visitTupleSelectorTerm(self, ctx: cqlParser.TupleSelectorTermContext) -> CQLTuple:
        """Visit tuple selector term."""
        return self.visit(ctx.tupleSelector())

    def visitTupleSelector(self, ctx: cqlParser.TupleSelectorContext) -> CQLTuple:
        """Visit tuple selector (Tuple { element1: value1, ... })."""
        elements: dict[str, Any] = {}
        for element in ctx.tupleElementSelector():
            name = self._get_identifier_text(element.referentialIdentifier())
            value = self.visit(element.expression())
            elements[name] = value
        return CQLTuple(elements=elements)

    def visitCodeSelectorTerm(self, ctx: cqlParser.CodeSelectorTermContext) -> CQLCode:
        """Visit code selector term."""
        return self.visit(ctx.codeSelector())

    def visitCodeSelector(self, ctx: cqlParser.CodeSelectorContext) -> CQLCode:
        """Visit code selector (Code 'code' from "system")."""
        code = self._unquote_string(ctx.STRING().getText())
        system_ctx = ctx.codesystemIdentifier()

        # Resolve codesystem
        if self._library and system_ctx:
            cs_name = self._get_identifier_text(system_ctx)
            cs_def = self._library.codesystems.get(cs_name)
            if cs_def:
                system = cs_def.id
            else:
                system = cs_name
        else:
            system = ""

        display = None
        display_ctx = ctx.displayClause() if hasattr(ctx, "displayClause") else None
        if display_ctx:
            display = self._unquote_string(display_ctx.STRING().getText())

        return CQLCode(code=code, system=system, display=display)

    def visitConceptSelectorTerm(self, ctx: cqlParser.ConceptSelectorTermContext) -> CQLConcept:
        """Visit concept selector term."""
        return self.visit(ctx.conceptSelector())

    def visitConceptSelector(self, ctx: cqlParser.ConceptSelectorContext) -> CQLConcept:
        """Visit concept selector (Concept { code1, code2 })."""
        codes = []
        for code_selector in ctx.codeSelector():
            codes.append(self.visit(code_selector))

        display = None
        display_ctx = ctx.displayClause() if hasattr(ctx, "displayClause") else None
        if display_ctx:
            display = self._unquote_string(display_ctx.STRING().getText())

        return CQLConcept(codes=tuple(codes), display=display)

    # =========================================================================
    # Expression Terms
    # =========================================================================

    def visitTermExpression(self, ctx: cqlParser.TermExpressionContext) -> Any:
        """Visit a term expression."""
        return self.visit(ctx.expressionTerm())

    def visitTermExpressionTerm(self, ctx: cqlParser.TermExpressionTermContext) -> Any:
        """Visit a term expression term."""
        return self.visit(ctx.term())

    def visitParenthesizedTerm(self, ctx: cqlParser.ParenthesizedTermContext) -> Any:
        """Visit a parenthesized term."""
        return self.visit(ctx.expression())

    def visitExternalConstantTerm(self, ctx: cqlParser.ExternalConstantTermContext) -> Any:
        """Visit external constant (%name)."""
        return self.visit(ctx.externalConstant())

    def visitExternalConstant(self, ctx: cqlParser.ExternalConstantContext) -> Any:
        """Visit external constant."""
        name = ctx.getText()[1:]  # Remove % prefix
        return self.context.get_constant(name)

    # =========================================================================
    # Arithmetic Operations
    # =========================================================================

    def visitAdditionExpressionTerm(self, ctx: cqlParser.AdditionExpressionTermContext) -> Any:
        """Visit addition/subtraction expression."""
        left = self.visit(ctx.expressionTerm(0))
        right = self.visit(ctx.expressionTerm(1))
        op = ctx.getChild(1).getText()

        # String concatenation handles null specially
        if op == "&":
            # In CQL, null is treated as empty string in string concatenation
            left_str = str(left) if left is not None else ""
            right_str = str(right) if right is not None else ""
            return left_str + right_str

        if left is None or right is None:
            return None

        if op == "+":
            return self._add(left, right)
        elif op == "-":
            return self._subtract(left, right)

        return None

    def visitMultiplicationExpressionTerm(self, ctx: cqlParser.MultiplicationExpressionTermContext) -> Any:
        """Visit multiplication/division expression."""
        left = self.visit(ctx.expressionTerm(0))
        right = self.visit(ctx.expressionTerm(1))
        op = ctx.getChild(1).getText()

        if left is None or right is None:
            return None

        if op == "*":
            return self._multiply(left, right)
        elif op == "/":
            return self._divide(left, right)
        elif op == "div":
            return self._truncated_divide(left, right)
        elif op == "mod":
            return self._modulo(left, right)

        return None

    def visitPowerExpressionTerm(self, ctx: cqlParser.PowerExpressionTermContext) -> Any:
        """Visit power expression (x ^ y)."""
        base = self.visit(ctx.expressionTerm(0))
        exponent = self.visit(ctx.expressionTerm(1))

        if base is None or exponent is None:
            return None

        return Decimal(base) ** Decimal(exponent)

    def visitPolarityExpressionTerm(self, ctx: cqlParser.PolarityExpressionTermContext) -> Any:
        """Visit polarity expression (+x or -x)."""
        value = self.visit(ctx.expressionTerm())
        op = ctx.getChild(0).getText()

        if value is None:
            return None

        if op == "-":
            if isinstance(value, Quantity):
                return Quantity(value=-value.value, unit=value.unit)
            return -value
        return value

    # =========================================================================
    # Boolean Operations
    # =========================================================================

    def visitAndExpression(self, ctx: cqlParser.AndExpressionContext) -> bool | None:
        """Visit AND expression with three-valued logic."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return self._three_valued_and(left, right)

    def visitOrExpression(self, ctx: cqlParser.OrExpressionContext) -> bool | None:
        """Visit OR/XOR expression with three-valued logic."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        op = ctx.getChild(1).getText().lower()

        if op == "or":
            return self._three_valued_or(left, right)
        elif op == "xor":
            return self._three_valued_xor(left, right)

        return None

    def visitNotExpression(self, ctx: cqlParser.NotExpressionContext) -> bool | None:
        """Visit NOT expression."""
        value = self.visit(ctx.expression())
        if value is None:
            return None
        return not value

    def visitImpliesExpression(self, ctx: cqlParser.ImpliesExpressionContext) -> bool | None:
        """Visit IMPLIES expression."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return self._three_valued_implies(left, right)

    def visitBooleanExpression(self, ctx: cqlParser.BooleanExpressionContext) -> bool | None:
        """Visit boolean IS/IS NOT expression."""
        value = self.visit(ctx.expression())
        text = ctx.getText().lower()

        # Check IS NOT patterns first (longer match)
        if "isnotnull" in text:
            return value is not None
        elif "isnull" in text:
            return value is None
        elif "isnottrue" in text:
            return value is not True
        elif "istrue" in text:
            return value is True
        elif "isnotfalse" in text:
            return value is not False
        elif "isfalse" in text:
            return value is False

        return None

    # =========================================================================
    # Comparison Operations
    # =========================================================================

    def visitEqualityExpression(self, ctx: cqlParser.EqualityExpressionContext) -> bool | None:
        """Visit equality expression (= or !=)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        op = ctx.getChild(1).getText()

        if left is None or right is None:
            return None

        if op == "=" or op == "~":
            return self._equals(left, right)
        elif op == "!=" or op == "!~":
            result = self._equals(left, right)
            return not result if result is not None else None

        return None

    def visitInequalityExpression(self, ctx: cqlParser.InequalityExpressionContext) -> bool | None:
        """Visit inequality expression (<, <=, >, >=)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        op = ctx.getChild(1).getText()

        if left is None or right is None:
            return None

        if op == "<":
            return left < right
        elif op == "<=":
            return left <= right
        elif op == ">":
            return left > right
        elif op == ">=":
            return left >= right

        return None

    # =========================================================================
    # Conditional Expressions
    # =========================================================================

    def visitIfThenElseExpressionTerm(self, ctx: cqlParser.IfThenElseExpressionTermContext) -> Any:
        """Visit if-then-else expression."""
        condition = self.visit(ctx.expression(0))

        if condition is True:
            return self.visit(ctx.expression(1))
        else:
            return self.visit(ctx.expression(2))

    def visitCaseExpressionTerm(self, ctx: cqlParser.CaseExpressionTermContext) -> Any:
        """Visit case expression."""
        # Check if this is a simple case (with comparand) or searched case
        comparand = None
        if ctx.expression():
            comparand = self.visit(ctx.expression())

        for item in ctx.caseExpressionItem():
            when_expr = item.expression(0)
            then_expr = item.expression(1)

            when_value = self.visit(when_expr)

            if comparand is not None:
                # Simple case: compare with comparand
                if self._equals(comparand, when_value):
                    return self.visit(then_expr)
            else:
                # Searched case: when_value should be boolean
                if when_value is True:
                    return self.visit(then_expr)

        # Return else clause if present
        else_expr = ctx.expression()
        if else_expr and ctx.getChildCount() > 0:
            # Find the else expression (last expression in context)
            expressions = [child for child in ctx.children if hasattr(child, "expression")]
            if expressions:
                return self.visit(expressions[-1])

        return None

    # =========================================================================
    # Invocations
    # =========================================================================

    def visitInvocationTerm(self, ctx: cqlParser.InvocationTermContext) -> Any:
        """Visit an invocation term."""
        return self.visit(ctx.invocation())

    def visitMemberInvocation(self, ctx: cqlParser.MemberInvocationContext) -> Any:
        """Visit member invocation (identifier access)."""
        name = self._get_identifier_text(ctx.referentialIdentifier())

        # Check if it's a query alias
        if self.context.has_alias(name):
            return self.context.get_alias(name)

        # Check if it's a parameter
        if self.context.has_parameter(name):
            return self.context.get_parameter(name)

        # Check if it's a definition
        if self._library and name in self._library.definitions:
            return self._evaluate_definition(name)

        # Check if it's a code reference
        if self._library and name in self._library.codes:
            return self._library.resolve_code(name)

        # Check if it's a concept reference
        if self._library and name in self._library.concepts:
            return self._library.resolve_concept(name)

        return None

    def visitFunctionInvocation(self, ctx: cqlParser.FunctionInvocationContext) -> Any:
        """Visit function invocation."""
        func_ctx = ctx.function()
        name = self._get_identifier_text(func_ctx.referentialIdentifier())

        # Evaluate arguments
        args = []
        param_list = func_ctx.paramList()
        if param_list:
            for expr in param_list.expression():
                args.append(self.visit(expr))

        return self._call_function(name, args)

    def visitInvocationExpressionTerm(self, ctx: cqlParser.InvocationExpressionTermContext) -> Any:
        """Visit invocation expression (method chaining)."""
        target = self.visit(ctx.expressionTerm())
        invocation = ctx.qualifiedInvocation()

        if isinstance(invocation, cqlParser.QualifiedMemberInvocationContext):
            # Property access on target
            name = self._get_identifier_text(invocation.referentialIdentifier())
            if isinstance(target, dict):
                return target.get(name)
            elif isinstance(target, CQLTuple):
                return target.elements.get(name)
            elif isinstance(target, list):
                # Flatten property access on list
                return [item.get(name) if isinstance(item, dict) else getattr(item, name, None) for item in target]
        elif isinstance(invocation, cqlParser.QualifiedFunctionInvocationContext):
            # Method call on target
            func_ctx = invocation.qualifiedFunction()
            name = self._get_identifier_text(func_ctx.identifierOrFunctionIdentifier())

            args = [target]
            param_list = func_ctx.paramList()
            if param_list:
                for expr in param_list.expression():
                    args.append(self.visit(expr))

            return self._call_function(name, args)

        return target

    def visitThisInvocation(self, ctx: cqlParser.ThisInvocationContext) -> Any:
        """Visit $this invocation."""
        return self.context.this

    def visitIndexInvocation(self, ctx: cqlParser.IndexInvocationContext) -> int | None:
        """Visit $index invocation."""
        return self.context.index

    def visitTotalInvocation(self, ctx: cqlParser.TotalInvocationContext) -> Any:
        """Visit $total invocation."""
        return self.context.total

    # =========================================================================
    # Existence/Membership
    # =========================================================================

    def visitExistenceExpression(self, ctx: cqlParser.ExistenceExpressionContext) -> bool:
        """Visit exists expression."""
        value = self.visit(ctx.expression())
        if isinstance(value, list):
            return len(value) > 0
        return value is not None

    def visitMembershipExpression(self, ctx: cqlParser.MembershipExpressionContext) -> bool | None:
        """Visit membership expression (in, contains)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        op = ctx.getChild(1).getText().lower()

        if op == "in":
            if isinstance(right, list):
                return left in right
            elif isinstance(right, CQLInterval):
                return right.contains(left)
        elif op == "contains":
            if isinstance(left, list):
                return right in left
            elif isinstance(left, CQLInterval):
                return left.contains(right)

        return None

    def visitBetweenExpression(self, ctx: cqlParser.BetweenExpressionContext) -> bool | None:
        """Visit between expression (x between y and z)."""
        value = self.visit(ctx.expression())
        expressions = ctx.expressionTerm()
        low = self.visit(expressions[0])
        high = self.visit(expressions[1])

        if value is None or low is None or high is None:
            return None

        return low <= value <= high

    # =========================================================================
    # Type Operations
    # =========================================================================

    def visitTypeExpression(self, ctx: cqlParser.TypeExpressionContext) -> Any:
        """Visit type expression (is, as)."""
        value = self.visit(ctx.expression())
        type_name = ctx.typeSpecifier().getText()
        op = ctx.getChild(1).getText().lower()

        if op == "is":
            return self._check_type(value, type_name)
        elif op == "as":
            return self._cast_type(value, type_name)

        return value

    def visitCastExpression(self, ctx: cqlParser.CastExpressionContext) -> Any:
        """Visit cast expression."""
        value = self.visit(ctx.expression())
        type_name = ctx.typeSpecifier().getText()
        return self._cast_type(value, type_name)

    # =========================================================================
    # Query Expressions
    # =========================================================================

    def visitQueryExpression(self, ctx: cqlParser.QueryExpressionContext) -> list[Any]:
        """Visit query expression."""
        return self.visit(ctx.query())

    def visitQuery(self, ctx: cqlParser.QueryContext) -> list[Any]:
        """Visit a query and execute it."""
        # Get source clause
        source_clause = ctx.sourceClause()
        results = self._process_query_sources(source_clause)

        # Apply let clauses
        let_clause = ctx.letClause()
        if let_clause:
            results = self._apply_let_clause(results, let_clause)

        # Apply query inclusion clauses (with/without)
        inclusion_clauses = ctx.queryInclusionClause()
        if inclusion_clauses:
            for inclusion in inclusion_clauses:
                results = self._apply_inclusion_clause(results, inclusion)

        # Apply where clause
        where_clause = ctx.whereClause()
        if where_clause:
            results = self._apply_where_clause(results, where_clause)

        # Apply aggregate clause OR return clause (mutually exclusive)
        aggregate_clause = ctx.aggregateClause()
        return_clause = ctx.returnClause()

        if aggregate_clause:
            return self._apply_aggregate_clause(results, aggregate_clause)
        elif return_clause:
            results = self._apply_return_clause(results, return_clause)

        # Apply sort clause
        sort_clause = ctx.sortClause()
        if sort_clause:
            results = self._apply_sort_clause(results, sort_clause)

        return results

    def _process_query_sources(self, ctx: cqlParser.SourceClauseContext) -> list[Any]:
        """Process query source clause and return initial result set."""
        results: list[dict[str, Any]] = []

        for alias_def in ctx.aliasedQuerySource():
            source = alias_def.querySource()
            alias = self._get_identifier_text(alias_def.alias().identifier())

            # Evaluate the source expression
            source_value = self._evaluate_query_source(source)

            # Convert to list if necessary
            if not isinstance(source_value, list):
                source_value = [source_value] if source_value is not None else []

            # Initialize result set with source
            if not results:
                results = [{alias: item} for item in source_value]
            else:
                # Cross join with additional source
                new_results = []
                for existing in results:
                    for item in source_value:
                        combined = dict(existing)
                        combined[alias] = item
                        new_results.append(combined)
                results = new_results

        return results

    def _evaluate_query_source(self, ctx: cqlParser.QuerySourceContext) -> Any:
        """Evaluate a query source."""
        # Check if it's a retrieve
        retrieve = ctx.retrieve()
        if retrieve:
            return self.visit(retrieve)

        # Check if it's an expression
        expr = ctx.expression()
        if expr:
            return self.visit(expr)

        # Check if it's a qualified identifier expression (reference to definition)
        qual_id = ctx.qualifiedIdentifierExpression()
        if qual_id:
            name = self._get_identifier_text(qual_id)
            if self._library and name in self._library.definitions:
                return self._evaluate_definition(name)
            return self.context.get_alias(name)

        return None

    def _apply_let_clause(self, results: list[dict[str, Any]], ctx: cqlParser.LetClauseContext) -> list[dict[str, Any]]:
        """Apply let clause to bind additional variables."""
        for let_item in ctx.letClauseItem():
            identifier = self._get_identifier_text(let_item.identifier())
            expr = let_item.expression()

            new_results = []
            for row in results:
                # Create context with current row aliases
                self.context.push_scope()
                for alias, value in row.items():
                    self.context.set_alias(alias, value)

                try:
                    let_value = self.visit(expr)
                    new_row = dict(row)
                    new_row[identifier] = let_value
                    new_results.append(new_row)
                finally:
                    self.context.pop_scope()

            results = new_results

        return results

    def _apply_where_clause(
        self, results: list[dict[str, Any]], ctx: cqlParser.WhereClauseContext
    ) -> list[dict[str, Any]]:
        """Apply where clause filter."""
        expr = ctx.expression()
        filtered = []

        for row in results:
            # Create context with current row aliases
            self.context.push_scope()
            for alias, value in row.items():
                self.context.set_alias(alias, value)

            try:
                condition = self.visit(expr)
                if condition is True:
                    filtered.append(row)
            finally:
                self.context.pop_scope()

        return filtered

    def _apply_return_clause(self, results: list[dict[str, Any]], ctx: cqlParser.ReturnClauseContext) -> list[Any]:
        """Apply return clause to shape output."""
        expr = ctx.expression()
        distinct = ctx.getText().lower().startswith("return distinct") or ctx.getText().lower().startswith("return all")
        is_all = "all" in ctx.getText().lower()

        returned = []
        for row in results:
            # Create context with current row aliases
            self.context.push_scope()
            for alias, value in row.items():
                self.context.set_alias(alias, value)

            try:
                value = self.visit(expr)
                returned.append(value)
            finally:
                self.context.pop_scope()

        # Apply distinct if specified
        if distinct and not is_all:
            seen: list[Any] = []
            for item in returned:
                if item not in seen:
                    seen.append(item)
            return seen

        return returned

    def _apply_sort_clause(self, results: list[Any], ctx: cqlParser.SortClauseContext) -> list[Any]:
        """Apply sort clause to order results."""
        sort_items = ctx.sortByItem()

        # Check for simple sort direction (sort asc / sort desc)
        if not sort_items:
            direction = ctx.sortDirection()
            if direction:
                dir_text = direction.getText().lower()
                reverse = dir_text in ("desc", "descending")
                try:
                    # Filter out None values for sorting, then sort
                    non_none = [r for r in results if r is not None]
                    none_count = len(results) - len(non_none)
                    sorted_results = sorted(non_none, reverse=reverse)
                    # Add None values at the end
                    return sorted_results + [None] * none_count
                except TypeError:
                    pass  # Keep original order if not sortable
            return results

        # Complex sort with sortByItem
        for sort_item in reversed(sort_items):  # Apply in reverse order
            direction = sort_item.sortDirection()
            dir_text = direction.getText().lower() if direction else "asc"
            reverse = dir_text in ("desc", "descending")

            expr = sort_item.expressionTerm()
            if expr:
                # Sort by expression
                def sort_key(item: Any) -> Any:
                    self.context.push_scope()
                    self.context.set_alias("$this", item)
                    try:
                        key = self.visit(expr)
                        return (key is None, key)  # None values sort last
                    finally:
                        self.context.pop_scope()

                try:
                    results = sorted(results, key=sort_key, reverse=reverse)
                except TypeError:
                    pass  # Keep original order if not sortable
            else:
                # Sort by natural order
                try:
                    results = sorted(results, reverse=reverse)
                except TypeError:
                    pass

        return results

    def _apply_inclusion_clause(
        self, results: list[dict[str, Any]], ctx: cqlParser.QueryInclusionClauseContext
    ) -> list[dict[str, Any]]:
        """Apply with/without clause to filter results based on related data."""
        # Check if it's a with or without clause
        with_clause = ctx.withClause()
        without_clause = ctx.withoutClause()

        if with_clause:
            return self._apply_with_clause(results, with_clause)
        elif without_clause:
            return self._apply_without_clause(results, without_clause)

        return results

    def _apply_with_clause(
        self, results: list[dict[str, Any]], ctx: cqlParser.WithClauseContext
    ) -> list[dict[str, Any]]:
        """Apply with clause - include rows that have matching related data."""
        # Get the aliased query source
        aliased_source = ctx.aliasedQuerySource()
        source = aliased_source.querySource()
        alias = self._get_identifier_text(aliased_source.alias().identifier())

        # Get the 'such that' condition expression
        condition = ctx.expression()

        # Evaluate the source
        source_value = self._evaluate_query_source(source)
        if not isinstance(source_value, list):
            source_value = [source_value] if source_value is not None else []

        # Filter results based on whether any related item matches the condition
        filtered = []
        for row in results:
            has_match = False
            for related_item in source_value:
                # Create context with current row aliases and the related item
                self.context.push_scope()
                for row_alias, value in row.items():
                    self.context.set_alias(row_alias, value)
                self.context.set_alias(alias, related_item)

                try:
                    result = self.visit(condition)
                    if result is True:
                        has_match = True
                        break
                finally:
                    self.context.pop_scope()

            if has_match:
                filtered.append(row)

        return filtered

    def _apply_without_clause(
        self, results: list[dict[str, Any]], ctx: cqlParser.WithoutClauseContext
    ) -> list[dict[str, Any]]:
        """Apply without clause - include rows that have NO matching related data."""
        # Get the aliased query source
        aliased_source = ctx.aliasedQuerySource()
        source = aliased_source.querySource()
        alias = self._get_identifier_text(aliased_source.alias().identifier())

        # Get the 'such that' condition expression
        condition = ctx.expression()

        # Evaluate the source
        source_value = self._evaluate_query_source(source)
        if not isinstance(source_value, list):
            source_value = [source_value] if source_value is not None else []

        # Filter results based on whether NO related item matches the condition
        filtered = []
        for row in results:
            has_match = False
            for related_item in source_value:
                # Create context with current row aliases and the related item
                self.context.push_scope()
                for row_alias, value in row.items():
                    self.context.set_alias(row_alias, value)
                self.context.set_alias(alias, related_item)

                try:
                    result = self.visit(condition)
                    if result is True:
                        has_match = True
                        break
                finally:
                    self.context.pop_scope()

            if not has_match:
                filtered.append(row)

        return filtered

    def _apply_aggregate_clause(self, results: list[dict[str, Any]], ctx: cqlParser.AggregateClauseContext) -> Any:
        """Apply aggregate clause to accumulate a value across results.

        Syntax: aggregate [all|distinct] identifier [starting value] : expression
        """
        # Get the accumulator identifier
        identifier = self._get_identifier_text(ctx.identifier())

        # Check for distinct modifier
        is_distinct = "distinct" in ctx.getText().lower().split("aggregate")[1].split(identifier)[0]

        # Get starting value
        starting_clause = ctx.startingClause()
        if starting_clause:
            # Check for different starting value formats
            simple_literal = starting_clause.simpleLiteral()
            quantity = starting_clause.quantity()
            paren_expr = starting_clause.expression()

            if simple_literal:
                accumulator = self.visit(simple_literal)
            elif quantity:
                accumulator = self.visit(quantity)
            elif paren_expr:
                accumulator = self.visit(paren_expr)
            else:
                accumulator = None
        else:
            accumulator = None

        # Get the aggregation expression
        agg_expression = ctx.expression()

        # Apply distinct if specified
        if is_distinct:
            seen: list[Any] = []
            unique_results = []
            for row in results:
                # Get a hashable representation
                row_key = tuple(sorted(row.items())) if isinstance(row, dict) else row
                if row_key not in seen:
                    seen.append(row_key)
                    unique_results.append(row)
            results = unique_results

        # Iterate through results, accumulating value
        for row in results:
            self.context.push_scope()

            # Set row aliases
            for row_alias, value in row.items():
                self.context.set_alias(row_alias, value)

            # Set the accumulator
            self.context.set_alias(identifier, accumulator)

            try:
                accumulator = self.visit(agg_expression)
            finally:
                self.context.pop_scope()

        return accumulator

    def visitRetrieve(self, ctx: cqlParser.RetrieveContext) -> list[Any]:
        """Visit retrieve expression [ResourceType: property in ValueSet].

        CQL retrieve syntax:
            [ResourceType]
            [ResourceType: codePath in valueset]
            [ResourceType: codePath ~ code]
        """
        # Get resource type
        named_type = ctx.namedTypeSpecifier()
        if named_type:
            resource_type = self._get_identifier_text(named_type)
        else:
            # Parse from text: [Condition] -> "Condition"
            text = ctx.getText()
            resource_type = text.strip("[]").split(":")[0].strip()

        # Initialize retrieve parameters
        code_path: str | None = None
        codes: list[Any] | None = None
        valueset: str | None = None

        # Get code path if present
        code_path_ctx = ctx.codePath() if hasattr(ctx, "codePath") else None
        if code_path_ctx:
            code_path = self._get_identifier_text(code_path_ctx)
        else:
            # Use default code paths for common resource types
            default_code_paths = {
                "Condition": "code",
                "Observation": "code",
                "Procedure": "code",
                "MedicationRequest": "medication.concept",
                "MedicationStatement": "medication.concept",
                "AllergyIntolerance": "code",
                "DiagnosticReport": "code",
                "Immunization": "vaccineCode",
                "CarePlan": "category",
            }
            code_path = default_code_paths.get(resource_type)

        # Get terminology filter if present
        terminology = ctx.terminology() if hasattr(ctx, "terminology") else None
        if terminology:
            # Parse terminology reference (valueset or code)
            term_expr = terminology.qualifiedIdentifierExpression()
            if term_expr:
                term_name = self._get_identifier_text(term_expr)
                if self._library:
                    if term_name in self._library.valuesets:
                        valueset = self._library.valuesets[term_name].id
                    elif term_name in self._library.codes:
                        code = self._library.resolve_code(term_name)
                        if code:
                            codes = [code]
                    elif term_name in self._library.concepts:
                        concept = self._library.concepts[term_name]
                        codes = list(concept.codes)
            else:
                # Direct code expression
                code_expr = terminology.expression() if hasattr(terminology, "expression") else None
                if code_expr:
                    code_value = self.visit(code_expr)
                    if code_value:
                        if isinstance(code_value, list):
                            codes = code_value
                        else:
                            codes = [code_value]

        # Use data source if available
        if self.context.data_source:
            return self.context.data_source.retrieve(
                resource_type=resource_type,
                context=self.context,
                code_path=code_path,
                codes=codes,
                valueset=valueset,
            )

        return []

    # =========================================================================
    # Set Operations
    # =========================================================================

    def visitInFixSetExpression(self, ctx: cqlParser.InFixSetExpressionContext) -> list[Any]:
        """Visit infix set expression (union, intersect, except)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        op = ctx.getChild(1).getText().lower()

        if not isinstance(left, list):
            left = [left] if left is not None else []
        if not isinstance(right, list):
            right = [right] if right is not None else []

        if op == "union":
            # Union removes duplicates
            result = list(left)
            for item in right:
                if item not in result:
                    result.append(item)
            return result
        elif op == "intersect":
            return [item for item in left if item in right]
        elif op == "except":
            return [item for item in left if item not in right]

        return left

    # =========================================================================
    # Interval Operations
    # =========================================================================

    def visitTimingExpression(self, ctx: cqlParser.TimingExpressionContext) -> bool | None:
        """Visit timing expression (before, after, during, etc.)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        # Get the operator
        op_text = ""
        for i in range(1, ctx.getChildCount() - 1):
            child = ctx.getChild(i)
            if hasattr(child, "getText"):
                op_text += child.getText().lower() + " "
        op_text = op_text.strip()

        if left is None or right is None:
            return None

        # Handle interval timing
        if isinstance(left, CQLInterval) and isinstance(right, CQLInterval):
            return self._interval_timing(left, right, op_text)
        elif isinstance(left, CQLInterval):
            return self._interval_point_timing(left, right, op_text)
        elif isinstance(right, CQLInterval):
            return self._point_interval_timing(left, right, op_text)

        # Handle point comparisons
        if "before" in op_text:
            return left < right
        elif "after" in op_text:
            return left > right

        return None

    def _interval_timing(self, left: CQLInterval[Any], right: CQLInterval[Any], op: str) -> bool | None:
        """Handle interval-to-interval timing comparisons."""
        if "before" in op:
            if left.high is None or right.low is None:
                return None
            return left.high < right.low
        elif "after" in op:
            if left.low is None or right.high is None:
                return None
            return left.low > right.high
        elif "meets" in op:
            if "before" in op:
                return left.high == right.low
            elif "after" in op:
                return left.low == right.high
            else:
                return left.high == right.low or left.low == right.high
        elif "overlaps" in op:
            return left.overlaps(right)
        elif "starts" in op:
            return left.low == right.low
        elif "ends" in op:
            return left.high == right.high
        elif "during" in op or "included in" in op:
            return right.includes(left)
        elif "includes" in op:
            return left.includes(right)
        elif "same" in op:
            return left == right
        return None

    def _interval_point_timing(self, interval: CQLInterval[Any], point: Any, op: str) -> bool | None:
        """Handle interval-to-point timing comparisons."""
        if "before" in op:
            return interval.high is not None and interval.high < point
        elif "after" in op:
            return interval.low is not None and interval.low > point
        elif "contains" in op or "includes" in op:
            return interval.contains(point)
        return None

    def _point_interval_timing(self, point: Any, interval: CQLInterval[Any], op: str) -> bool | None:
        """Handle point-to-interval timing comparisons."""
        if "before" in op:
            return interval.low is not None and point < interval.low
        elif "after" in op:
            return interval.high is not None and point > interval.high
        elif "during" in op or "in" in op or "included in" in op:
            return interval.contains(point)
        return None

    # =========================================================================
    # Duration and Difference Expressions
    # =========================================================================

    def visitDurationBetweenExpression(self, ctx: cqlParser.DurationBetweenExpressionContext) -> int | None:
        """Visit duration between expression (years/months/days between X and Y)."""
        # Get the precision (years, months, days, etc.)
        precision_ctx = ctx.pluralDateTimePrecision()
        precision = precision_ctx.getText().lower() if precision_ctx else "days"

        # Get the two expression terms
        terms = ctx.expressionTerm()
        if len(terms) < 2:
            return None

        start = self.visit(terms[0])
        end = self.visit(terms[1])

        if start is None or end is None:
            return None

        return self._date_diff(start, end, precision)

    def visitDifferenceBetweenExpression(self, ctx: cqlParser.DifferenceBetweenExpressionContext) -> int | None:
        """Visit difference between expression (difference in years between X and Y)."""
        # Get the precision (years, months, days, etc.)
        precision_ctx = ctx.pluralDateTimePrecision()
        precision = precision_ctx.getText().lower() if precision_ctx else "days"

        # Get the two expression terms
        terms = ctx.expressionTerm()
        if len(terms) < 2:
            return None

        start = self.visit(terms[0])
        end = self.visit(terms[1])

        if start is None or end is None:
            return None

        return self._date_diff(start, end, precision)

    def visitTimeUnitExpressionTerm(self, ctx: cqlParser.TimeUnitExpressionTermContext) -> int | None:
        """Visit time unit expression (year from X, month from X, etc.)."""
        expr = ctx.expressionTerm()
        value = self.visit(expr)

        if value is None:
            return None

        # Get the time unit (year, month, day, hour, minute, second)
        unit_ctx = ctx.dateTimeComponent()
        if unit_ctx is None:
            return None

        unit = unit_ctx.getText().lower()

        # Extract the component
        if unit in ("year", "years"):
            return self._call_builtin_function("year", [value])
        elif unit in ("month", "months"):
            return self._call_builtin_function("month", [value])
        elif unit in ("day", "days"):
            return self._call_builtin_function("day", [value])
        elif unit in ("hour", "hours"):
            return self._call_builtin_function("hour", [value])
        elif unit in ("minute", "minutes"):
            return self._call_builtin_function("minute", [value])
        elif unit in ("second", "seconds"):
            return self._call_builtin_function("second", [value])
        elif unit in ("millisecond", "milliseconds"):
            # Handle millisecond extraction
            if isinstance(value, FHIRDateTime):
                return value.millisecond if hasattr(value, "millisecond") else 0
            if isinstance(value, datetime):
                return value.microsecond // 1000
        elif unit in ("timezone", "timezoneoffset"):
            return self._call_builtin_function("timezone", [value])

        return None

    def visitWidthExpressionTerm(self, ctx: cqlParser.WidthExpressionTermContext) -> Any:
        """Visit width of expression (width of Interval)."""
        expr = ctx.expressionTerm()
        interval = self.visit(expr)

        if isinstance(interval, CQLInterval):
            return interval.width()
        return None

    def visitTimeBoundaryExpressionTerm(self, ctx: cqlParser.TimeBoundaryExpressionTermContext) -> Any:
        """Visit time boundary expression (start of / end of Interval)."""
        # Get the boundary type (first token: 'start' or 'end')
        boundary = ctx.getChild(0).getText().lower()
        # Get the expression (the interval)
        expr = ctx.expressionTerm()
        value = self.visit(expr)

        if value is None:
            return None

        if isinstance(value, CQLInterval):
            if boundary == "start":
                return value.low
            elif boundary == "end":
                return value.high

        return None

    def visitSetAggregateExpressionTerm(self, ctx: cqlParser.SetAggregateExpressionTermContext) -> Any:
        """Visit set aggregate expression (expand / collapse)."""
        # Get the operation (first token: 'expand' or 'collapse')
        op = ctx.getChild(0).getText().lower()
        # Get the expressions
        expressions = ctx.expression()

        if op == "collapse":
            if expressions:
                value = self.visit(expressions[0])
                if isinstance(value, list):
                    intervals = [i for i in value if isinstance(i, CQLInterval)]
                    return self._collapse_intervals(intervals)
            return []

        elif op == "expand":
            if expressions:
                value = self.visit(expressions[0])
                if isinstance(value, CQLInterval):
                    per = None
                    if len(expressions) > 1:
                        per = self.visit(expressions[1])
                    return self._expand_interval(value, per)
            return []

        return None

    # =========================================================================
    # Indexing
    # =========================================================================

    def visitIndexedExpressionTerm(self, ctx: cqlParser.IndexedExpressionTermContext) -> Any:
        """Visit indexed expression (list[index])."""
        collection = self.visit(ctx.expressionTerm())
        index = self.visit(ctx.expression())

        if collection is None or index is None:
            return None

        if isinstance(collection, list):
            if isinstance(index, int) and 0 <= index < len(collection):
                return collection[index]
        elif isinstance(collection, str):
            if isinstance(index, int) and 0 <= index < len(collection):
                return collection[index]

        return None

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_identifier_text(self, ctx: Any) -> str:
        """Extract identifier text from various context types."""
        if ctx is None:
            return ""

        text = ctx.getText()

        # Handle quoted identifiers
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        if text.startswith("`") and text.endswith("`"):
            return text[1:-1]

        return text

    def _unquote_string(self, text: str) -> str:
        """Remove quotes from a string literal."""
        if len(text) >= 2:
            if (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')):
                text = text[1:-1]
                # Handle escape sequences
                text = text.replace("\\'", "'")
                text = text.replace('\\"', '"')
                text = text.replace("\\\\", "\\")
                text = text.replace("\\n", "\n")
                text = text.replace("\\r", "\r")
                text = text.replace("\\t", "\t")
        return text

    def _evaluate_definition(self, name: str) -> Any:
        """Evaluate a named definition."""
        if not self._library:
            return None

        # Check cache
        found, cached = self.context.get_cached_definition(name)
        if found:
            return cached

        # Check for recursion
        if not self.context.start_evaluation(name):
            raise CQLError(f"Recursive definition detected: {name}")

        try:
            definition = self._library.definitions.get(name)
            if not definition or not definition.expression_tree:
                return None

            result = self.visit(definition.expression_tree)
            self.context.cache_definition(name, result)
            return result
        finally:
            self.context.end_evaluation(name)

    def _call_function(self, name: str, args: list[Any]) -> Any:
        """Call a function by name with arguments."""
        # Check for user-defined functions
        if self._library:
            func = self._library.get_function(name, len(args))
            if func and func.body_tree:
                return self._call_user_function(func, args)

        # Built-in functions - delegate to function registry
        # This will be implemented later with the function modules
        return self._call_builtin_function(name, args)

    def _call_user_function(self, func: FunctionDefinition, args: list[Any]) -> Any:
        """Call a user-defined function."""
        # Create new context with parameters bound
        child_ctx = self.context.child()
        for (param_name, _), arg_value in zip(func.parameters, args):
            child_ctx.set_alias(param_name, arg_value)

        # Save current context and switch
        old_ctx = self.context
        self.context = child_ctx

        try:
            result = self.visit(func.body_tree)
            return result
        finally:
            self.context = old_ctx

    def _call_builtin_function(self, name: str, args: list[Any]) -> Any:
        """Call a built-in function."""
        # Basic built-in functions for Phase 1
        name_lower = name.lower()

        if name_lower == "count":
            if args and isinstance(args[0], list):
                return len(args[0])
            return 0

        if name_lower == "exists":
            if args:
                val = args[0]
                if isinstance(val, list):
                    return len(val) > 0
                return val is not None
            return False

        if name_lower == "first":
            if args and isinstance(args[0], list) and len(args[0]) > 0:
                return args[0][0]
            return None

        if name_lower == "last":
            if args and isinstance(args[0], list) and len(args[0]) > 0:
                return args[0][-1]
            return None

        if name_lower == "length":
            if args:
                val = args[0]
                if isinstance(val, str):
                    return len(val)
                if isinstance(val, list):
                    return len(val)
            return None

        if name_lower == "tostring":
            if args and args[0] is not None:
                return str(args[0])
            return None

        if name_lower == "tointeger":
            if args and args[0] is not None:
                try:
                    return int(args[0])
                except (ValueError, TypeError):
                    return None
            return None

        if name_lower == "todecimal":
            if args and args[0] is not None:
                try:
                    return Decimal(str(args[0]))
                except (ValueError, TypeError):
                    return None
            return None

        if name_lower == "toboolean":
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, bool):
                    return val
                if isinstance(val, str):
                    return val.lower() in ("true", "t", "yes", "y", "1")
            return None

        if name_lower == "coalesce":
            for arg in args:
                if arg is not None:
                    if isinstance(arg, list):
                        if len(arg) > 0:
                            return arg
                    else:
                        return arg
            return None

        if name_lower == "isnull":
            return args[0] is None if args else True

        if name_lower in ("sum", "avg", "min", "max"):
            if args and isinstance(args[0], list):
                values = [v for v in args[0] if v is not None and isinstance(v, (int, float, Decimal))]
                if not values:
                    return None
                if name_lower == "sum":
                    return sum(values)
                if name_lower == "avg":
                    return sum(values) / len(values)
                if name_lower == "min":
                    return min(values)
                if name_lower == "max":
                    return max(values)
            return None

        # Phase 2: List functions
        if name_lower == "tail":
            if args and isinstance(args[0], list) and len(args[0]) > 0:
                return args[0][1:]
            return []

        if name_lower == "take":
            if len(args) >= 2 and isinstance(args[0], list):
                n = args[1]
                if n is None or n < 0:
                    return []
                return args[0][:n]
            return []

        if name_lower == "skip":
            if len(args) >= 2 and isinstance(args[0], list):
                n = args[1]
                if n is None or n < 0:
                    return args[0]
                return args[0][n:]
            return []

        if name_lower == "flatten":
            if args and isinstance(args[0], list):
                result = []
                for item in args[0]:
                    if isinstance(item, list):
                        result.extend(item)
                    else:
                        result.append(item)
                return result
            return []

        if name_lower == "distinct":
            if args and isinstance(args[0], list):
                seen: list[Any] = []
                for item in args[0]:
                    if item not in seen:
                        seen.append(item)
                return seen
            return []

        if name_lower == "sort":
            if args and isinstance(args[0], list):
                items = [i for i in args[0] if i is not None]
                try:
                    return sorted(items)
                except TypeError:
                    return items
            return []

        if name_lower == "indexof":
            if len(args) >= 2:
                # List IndexOf - find element in list
                if isinstance(args[0], list):
                    try:
                        return args[0].index(args[1])
                    except ValueError:
                        return -1
                # String IndexOf - find substring in string
                if isinstance(args[0], str) and isinstance(args[1], str):
                    return args[0].find(args[1])
            return -1

        if name_lower == "singleton":
            if args and isinstance(args[0], list):
                if len(args[0]) == 1:
                    return args[0][0]
                elif len(args[0]) == 0:
                    return None
                else:
                    raise CQLError("Expected single element but found multiple")
            return args[0] if args else None

        if name_lower == "alltrue":
            if args and isinstance(args[0], list):
                for item in args[0]:
                    if item is not True:
                        return False
                return True
            return True

        if name_lower == "anytrue":
            if args and isinstance(args[0], list):
                for item in args[0]:
                    if item is True:
                        return True
                return False
            return False

        if name_lower == "allfalse":
            if args and isinstance(args[0], list):
                for item in args[0]:
                    if item is not False:
                        return False
                return True
            return True

        if name_lower == "anyfalse":
            if args and isinstance(args[0], list):
                for item in args[0]:
                    if item is False:
                        return True
                return False
            return False

        if name_lower == "reverse":
            if args and isinstance(args[0], list):
                return list(reversed(args[0]))
            return []

        if name_lower == "slice":
            if len(args) >= 3 and isinstance(args[0], list):
                start = args[1] if args[1] is not None else 0
                length = args[2] if args[2] is not None else len(args[0])
                return args[0][start : start + length]
            return []

        if name_lower == "singletonFrom":
            return self._call_builtin_function("singleton", args)

        if name_lower == "combine":
            if len(args) >= 2 and isinstance(args[0], list) and isinstance(args[1], list):
                # Combine two lists (list concatenation)
                return args[0] + args[1]
            elif len(args) >= 1 and isinstance(args[0], list):
                # Combine list of strings with optional separator (string join)
                strings = args[0]
                separator = args[1] if len(args) > 1 and args[1] is not None else ""
                if isinstance(separator, str):
                    return separator.join(str(s) for s in strings if s is not None)
            return []

        if name_lower == "union":
            if len(args) >= 2 and isinstance(args[0], list) and isinstance(args[1], list):
                result = list(args[0])
                for item in args[1]:
                    if item not in result:
                        result.append(item)
                return result
            return []

        if name_lower == "intersect":
            if len(args) >= 2 and isinstance(args[0], list) and isinstance(args[1], list):
                return [item for item in args[0] if item in args[1]]
            return []

        if name_lower == "except":
            if len(args) >= 2 and isinstance(args[0], list) and isinstance(args[1], list):
                return [item for item in args[0] if item not in args[1]]
            return []

        # Aggregate functions with context
        if name_lower == "populationvariance":
            if args and isinstance(args[0], list):
                values = [Decimal(str(v)) for v in args[0] if v is not None and isinstance(v, (int, float, Decimal))]
                if len(values) < 1:
                    return None
                mean = sum(values) / Decimal(len(values))
                return sum((v - mean) ** 2 for v in values) / Decimal(len(values))
            return None

        if name_lower == "variance":
            if args and isinstance(args[0], list):
                values = [Decimal(str(v)) for v in args[0] if v is not None and isinstance(v, (int, float, Decimal))]
                if len(values) < 2:
                    return None
                mean = sum(values) / Decimal(len(values))
                return sum((v - mean) ** 2 for v in values) / Decimal(len(values) - 1)
            return None

        if name_lower == "populationstddev":
            if args and isinstance(args[0], list):
                variance = self._call_builtin_function("populationvariance", args)
                if variance is not None:
                    return Decimal(variance).sqrt()
            return None

        if name_lower == "stddev":
            if args and isinstance(args[0], list):
                variance = self._call_builtin_function("variance", args)
                if variance is not None:
                    return Decimal(variance).sqrt()
            return None

        if name_lower == "median":
            if args and isinstance(args[0], list):
                values = sorted(
                    Decimal(str(v)) for v in args[0] if v is not None and isinstance(v, (int, float, Decimal))
                )
                if not values:
                    return None
                n = len(values)
                if n % 2 == 1:
                    return values[n // 2]
                else:
                    return (values[n // 2 - 1] + values[n // 2]) / 2
            return None

        if name_lower == "mode":
            if args and isinstance(args[0], list):
                values = [v for v in args[0] if v is not None]
                if not values:
                    return None
                # Count occurrences
                counts: dict[Any, int] = {}
                for v in values:
                    counts[v] = counts.get(v, 0) + 1
                max_count = max(counts.values())
                return [k for k, v in counts.items() if v == max_count][0]
            return None

        if name_lower == "product":
            if args and isinstance(args[0], list):
                values = [v for v in args[0] if v is not None and isinstance(v, (int, float, Decimal))]
                if not values:
                    return None
                product_result = Decimal(1)
                for v in values:
                    product_result *= Decimal(str(v))
                return product_result
            return None

        if name_lower == "geometricmean":
            if args and isinstance(args[0], list):
                values = [v for v in args[0] if v is not None and isinstance(v, (int, float, Decimal))]
                if not values or any(v <= 0 for v in values):
                    return None
                product = self._call_builtin_function("product", args)
                if product is not None:
                    return Decimal(product) ** (Decimal(1) / Decimal(len(values)))
            return None

        # =====================================================================
        # Phase 3: Date/Time and Interval Functions
        # =====================================================================

        # Date/Time constructors
        if name_lower == "today":
            d = self.context.now.date() if self.context.now else datetime.now().date()
            return FHIRDate(year=d.year, month=d.month, day=d.day)

        if name_lower == "now":
            now = self.context.now or datetime.now()
            return FHIRDateTime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=now.hour,
                minute=now.minute,
                second=now.second,
                millisecond=now.microsecond // 1000,
            )

        if name_lower == "timeofday":
            now = self.context.now or datetime.now()
            t = now.time()
            return FHIRTime(hour=t.hour, minute=t.minute, second=t.second, millisecond=t.microsecond // 1000)

        if name_lower == "date":
            # Date(year, month, day)
            if len(args) >= 1:
                year = args[0]
                month = args[1] if len(args) > 1 else 1
                day = args[2] if len(args) > 2 else 1
                if year is not None:
                    return FHIRDate(year=int(year), month=int(month or 1), day=int(day or 1))
            return None

        if name_lower == "datetime":
            # DateTime(year, month, day, hour, minute, second, millisecond, timezone)
            if len(args) >= 1 and args[0] is not None:
                year = int(args[0])
                month = int(args[1]) if len(args) > 1 and args[1] is not None else 1
                day = int(args[2]) if len(args) > 2 and args[2] is not None else 1
                hour = int(args[3]) if len(args) > 3 and args[3] is not None else 0
                minute = int(args[4]) if len(args) > 4 and args[4] is not None else 0
                second = int(args[5]) if len(args) > 5 and args[5] is not None else 0
                return FHIRDateTime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
            return None

        if name_lower == "time":
            # Time(hour, minute, second, millisecond)
            if len(args) >= 1 and args[0] is not None:
                hour = int(args[0])
                minute = int(args[1]) if len(args) > 1 and args[1] is not None else 0
                second = int(args[2]) if len(args) > 2 and args[2] is not None else 0
                return FHIRTime(hour=hour, minute=minute, second=second)
            return None

        # Interval functions
        if name_lower in ("start", "startof"):
            if args and isinstance(args[0], CQLInterval):
                return args[0].low
            return None

        if name_lower in ("end", "endof"):
            if args and isinstance(args[0], CQLInterval):
                return args[0].high
            return None

        if name_lower in ("width", "widthof"):
            if args and isinstance(args[0], CQLInterval):
                return args[0].width()
            return None

        if name_lower in ("size", "sizeof"):
            if args and isinstance(args[0], CQLInterval):
                interval = args[0]
                if interval.low is None or interval.high is None:
                    return None
                # Size includes boundaries for closed intervals
                width = interval.high - interval.low
                if isinstance(width, int):
                    width += 1 if interval.low_closed and interval.high_closed else 0
                return width
            return None

        if name_lower == "pointfrom":
            if args and isinstance(args[0], CQLInterval):
                interval = args[0]
                if interval.low == interval.high and interval.low_closed and interval.high_closed:
                    return interval.low
                raise CQLError("pointFrom requires a unit interval")
            return args[0] if args else None

        if name_lower == "collapse":
            if args and isinstance(args[0], list):
                intervals = [i for i in args[0] if isinstance(i, CQLInterval)]
                return self._collapse_intervals(intervals)
            return []

        if name_lower == "expand":
            if args and isinstance(args[0], CQLInterval):
                interval = args[0]
                per = args[1] if len(args) > 1 else None
                return self._expand_interval(interval, per)
            return []

        # Component extraction
        if name_lower in ("year", "yearfrom"):
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDate):
                    return val.year
                if isinstance(val, FHIRDateTime):
                    return val.year
                if isinstance(val, date):
                    return val.year
                if isinstance(val, datetime):
                    return val.year
            return None

        if name_lower in ("month", "monthfrom"):
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDate):
                    return val.month
                if isinstance(val, FHIRDateTime):
                    return val.month
                if isinstance(val, date):
                    return val.month
                if isinstance(val, datetime):
                    return val.month
            return None

        if name_lower in ("day", "dayfrom"):
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDate):
                    return val.day
                if isinstance(val, FHIRDateTime):
                    return val.day
                if isinstance(val, date):
                    return val.day
                if isinstance(val, datetime):
                    return val.day
            return None

        if name_lower in ("hour", "hourfrom"):
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDateTime):
                    return val.hour
                if isinstance(val, FHIRTime):
                    return val.hour
                if isinstance(val, datetime):
                    return val.hour
                if isinstance(val, time):
                    return val.hour
            return None

        if name_lower in ("minute", "minutefrom"):
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDateTime):
                    return val.minute
                if isinstance(val, FHIRTime):
                    return val.minute
                if isinstance(val, datetime):
                    return val.minute
                if isinstance(val, time):
                    return val.minute
            return None

        if name_lower in ("second", "secondfrom"):
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDateTime):
                    return val.second
                if isinstance(val, FHIRTime):
                    return val.second
                if isinstance(val, datetime):
                    return val.second
                if isinstance(val, time):
                    return val.second
            return None

        if name_lower in ("timezone", "timezonefrom", "timezoneoffsetfrom"):
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDateTime) and val.tz_offset is not None:
                    return val.tz_offset
                if isinstance(val, datetime) and val.tzinfo is not None:
                    offset = val.utcoffset()
                    if offset is not None:
                        return offset.total_seconds() / 3600
            return None

        if name_lower == "datediff":
            # Calculate difference in days
            if len(args) >= 2:
                return self._date_diff(args[0], args[1], "day")
            return None

        # Clinical age functions
        if name_lower == "ageinyears":
            birthdate = self._get_patient_birthdate()
            if birthdate:
                return self._calculate_age_in_years(birthdate, self.context.now or datetime.now())
            return None

        if name_lower == "ageinmonths":
            birthdate = self._get_patient_birthdate()
            if birthdate:
                return self._calculate_age_in_months(birthdate, self.context.now or datetime.now())
            return None

        if name_lower == "ageinweeks":
            birthdate = self._get_patient_birthdate()
            if birthdate:
                return self._calculate_age_in_weeks(birthdate, self.context.now or datetime.now())
            return None

        if name_lower == "ageindays":
            birthdate = self._get_patient_birthdate()
            if birthdate:
                return self._calculate_age_in_days(birthdate, self.context.now or datetime.now())
            return None

        if name_lower == "ageinyearsat":
            if args:
                birthdate = self._get_patient_birthdate()
                as_of = args[0]
                if birthdate and as_of:
                    return self._calculate_age_in_years(birthdate, as_of)
            return None

        if name_lower == "ageinmonthsat":
            if args:
                birthdate = self._get_patient_birthdate()
                as_of = args[0]
                if birthdate and as_of:
                    return self._calculate_age_in_months(birthdate, as_of)
            return None

        if name_lower == "calculateageinyears":
            if len(args) >= 2:
                return self._calculate_age_in_years(args[0], args[1])
            return None

        if name_lower == "calculateageinmonths":
            if len(args) >= 2:
                return self._calculate_age_in_months(args[0], args[1])
            return None

        if name_lower == "calculateageinweeks":
            if len(args) >= 2:
                return self._calculate_age_in_weeks(args[0], args[1])
            return None

        if name_lower == "calculateageindays":
            if len(args) >= 2:
                return self._calculate_age_in_days(args[0], args[1])
            return None

        # =====================================================================
        # Phase 4: String Functions
        # =====================================================================

        if name_lower == "concat":
            # Concatenate all string arguments
            concat_result = ""
            for arg in args:
                if arg is not None:
                    concat_result += str(arg)
            return concat_result

        if name_lower == "split":
            # Split string by separator
            if len(args) >= 2 and args[0] is not None and args[1] is not None:
                return str(args[0]).split(str(args[1]))
            return None

        if name_lower == "upper":
            if args and args[0] is not None:
                return str(args[0]).upper()
            return None

        if name_lower == "lower":
            if args and args[0] is not None:
                return str(args[0]).lower()
            return None

        if name_lower == "substring":
            # Substring(string, startIndex[, length])
            if args and args[0] is not None:
                s = str(args[0])
                start = int(args[1]) if len(args) > 1 and args[1] is not None else 0
                if len(args) > 2 and args[2] is not None:
                    length = int(args[2])
                    return s[start : start + length]
                return s[start:]
            return None

        if name_lower == "startswith":
            if len(args) >= 2 and args[0] is not None and args[1] is not None:
                return str(args[0]).startswith(str(args[1]))
            return None

        if name_lower == "endswith":
            if len(args) >= 2 and args[0] is not None and args[1] is not None:
                return str(args[0]).endswith(str(args[1]))
            return None

        if name_lower == "matches":
            # Regex match
            import re

            if len(args) >= 2 and args[0] is not None and args[1] is not None:
                try:
                    return bool(re.search(str(args[1]), str(args[0])))
                except re.error:
                    return None
            return None

        if name_lower == "replacematches":
            # Regex replace
            import re

            if len(args) >= 3 and args[0] is not None:
                try:
                    return re.sub(str(args[1]), str(args[2]), str(args[0]))
                except re.error:
                    return None
            return None

        if name_lower == "replace":
            # Simple string replace
            if len(args) >= 3 and args[0] is not None:
                return str(args[0]).replace(str(args[1] or ""), str(args[2] or ""))
            return None

        if name_lower == "indexof":
            # IndexOf(string, substring) - find substring in string
            if len(args) >= 2 and args[0] is not None and args[1] is not None:
                try:
                    return str(args[0]).find(str(args[1]))
                except ValueError:
                    return -1
            return None

        if name_lower == "lastpositionof":
            if len(args) >= 2 and args[0] is not None and args[1] is not None:
                try:
                    return str(args[1]).rindex(str(args[0]))
                except ValueError:
                    return -1
            return None

        if name_lower == "positionof":
            if len(args) >= 2 and args[0] is not None and args[1] is not None:
                try:
                    return str(args[1]).index(str(args[0]))
                except ValueError:
                    return -1
            return None

        if name_lower == "trim":
            if args and args[0] is not None:
                return str(args[0]).strip()
            return None

        if name_lower == "length":
            if args and args[0] is not None:
                if isinstance(args[0], str):
                    return len(args[0])
                if isinstance(args[0], list):
                    return len(args[0])
            return None

        # =====================================================================
        # Phase 4: Type Conversion Functions
        # =====================================================================

        if name_lower in ("tostring", "convert"):
            if args and args[0] is not None:
                return str(args[0])
            return None

        if name_lower == "tointeger":
            if args and args[0] is not None:
                try:
                    return int(args[0])
                except (ValueError, TypeError):
                    return None
            return None

        if name_lower == "todecimal":
            if args and args[0] is not None:
                try:
                    return Decimal(str(args[0]))
                except Exception:
                    return None
            return None

        if name_lower == "toboolean":
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, bool):
                    return val
                if isinstance(val, str):
                    lower = val.lower()
                    if lower in ("true", "t", "yes", "y", "1"):
                        return True
                    if lower in ("false", "f", "no", "n", "0"):
                        return False
                return None
            return None

        if name_lower == "todate":
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDate):
                    return val
                if isinstance(val, FHIRDateTime):
                    return FHIRDate(year=val.year, month=val.month, day=val.day)
                if isinstance(val, str):
                    return FHIRDate.parse(val)
            return None

        if name_lower == "todatetime":
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRDateTime):
                    return val
                if isinstance(val, FHIRDate):
                    return FHIRDateTime(year=val.year, month=val.month, day=val.day)
                if isinstance(val, str):
                    return FHIRDateTime.parse(val)
            return None

        if name_lower == "totime":
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, FHIRTime):
                    return val
                if isinstance(val, str):
                    return FHIRTime.parse(val)
            return None

        if name_lower == "toquantity":
            if args:
                if len(args) >= 2:
                    return Quantity(value=Decimal(str(args[0])), unit=str(args[1]))
                if isinstance(args[0], Quantity):
                    return args[0]
            return None

        # =====================================================================
        # Phase 4: Utility Functions
        # =====================================================================

        if name_lower == "coalesce":
            # Return first non-null argument
            for arg in args:
                if arg is not None:
                    return arg
            return None

        if name_lower == "isnull":
            return args[0] is None if args else True

        if name_lower == "isnotnull":
            return args[0] is not None if args else False

        if name_lower == "istrue":
            return args[0] is True if args else False

        if name_lower == "isfalse":
            return args[0] is False if args else False

        if name_lower == "abs":
            if args and args[0] is not None:
                val = args[0]
                if isinstance(val, Quantity):
                    return Quantity(value=abs(val.value), unit=val.unit)
                return abs(val)
            return None

        if name_lower == "ceiling":
            import math

            if args and args[0] is not None:
                return math.ceil(float(args[0]))
            return None

        if name_lower == "floor":
            import math

            if args and args[0] is not None:
                return math.floor(float(args[0]))
            return None

        if name_lower == "truncate":
            if args and args[0] is not None:
                return int(float(args[0]))
            return None

        if name_lower == "round":
            if args and args[0] is not None:
                precision = int(args[1]) if len(args) > 1 and args[1] is not None else 0
                return round(float(args[0]), precision)
            return None

        if name_lower == "ln":
            import math

            if args and args[0] is not None:
                try:
                    return math.log(float(args[0]))
                except (ValueError, TypeError):
                    return None
            return None

        if name_lower == "log":
            import math

            if args and args[0] is not None:
                base = float(args[1]) if len(args) > 1 and args[1] is not None else 10
                try:
                    return math.log(float(args[0]), base)
                except (ValueError, TypeError):
                    return None
            return None

        if name_lower == "exp":
            import math

            if args and args[0] is not None:
                try:
                    return math.exp(float(args[0]))
                except (ValueError, TypeError):
                    return None
            return None

        if name_lower == "power":
            if len(args) >= 2 and args[0] is not None and args[1] is not None:
                return float(args[0]) ** float(args[1])
            return None

        if name_lower == "sqrt":
            import math

            if args and args[0] is not None:
                try:
                    return math.sqrt(float(args[0]))
                except (ValueError, TypeError):
                    return None
            return None

        # =====================================================================
        # Phase 4: Code/Terminology Functions
        # =====================================================================

        if name_lower == "tocode":
            # Convert string to Code
            if args and args[0] is not None:
                if isinstance(args[0], CQLCode):
                    return args[0]
                if isinstance(args[0], str):
                    # Simple string to code (no system)
                    return CQLCode(code=args[0], system="")
            return None

        if name_lower == "toconcept":
            # Convert code(s) to Concept
            if args:
                if isinstance(args[0], CQLConcept):
                    return args[0]
                if isinstance(args[0], CQLCode):
                    return CQLConcept(codes=(args[0],))
                if isinstance(args[0], list):
                    codes = tuple(c for c in args[0] if isinstance(c, CQLCode))
                    if codes:
                        return CQLConcept(codes=codes)
            return None

        if name_lower == "code":
            # Create a Code from system and code
            if len(args) >= 2:
                return CQLCode(
                    code=str(args[0]),
                    system=str(args[1]),
                    display=str(args[2]) if len(args) > 2 and args[2] else None,
                )
            return None

        # Function not found - try user-defined function
        return self._call_user_defined_function(name, args)

    def _call_user_defined_function(self, name: str, args: list[Any]) -> Any:
        """Call a user-defined function from the current library."""
        if not self._library:
            return None

        # Look up function in library
        func_def = self._library.get_function(name)
        if not func_def:
            return None

        # Check argument count (all parameters are required - no defaults)
        if len(args) < len(func_def.parameters):
            return None

        # Create child context for function execution
        func_context = self.context.child()

        # Bind parameters - parameters are (name, type) tuples
        for i, (param_name, _param_type) in enumerate(func_def.parameters):
            if i < len(args):
                func_context.set_alias(param_name, args[i])

        # Create a new visitor with the function context
        func_visitor = CQLEvaluatorVisitor(func_context)
        func_visitor._library = self._library

        # Evaluate function body
        if func_def.body_tree:
            return func_visitor.visit(func_def.body_tree)

        return None

    # Arithmetic helpers
    def _add(self, left: Any, right: Any) -> Any:
        """Add two values."""
        # Quantity + Quantity
        if isinstance(left, Quantity) and isinstance(right, Quantity):
            if left.unit == right.unit:
                return Quantity(value=left.value + right.value, unit=left.unit)
            return None

        # Date/DateTime + Quantity (duration)
        if isinstance(left, (FHIRDate, FHIRDateTime, date, datetime)) and isinstance(right, Quantity):
            return self._add_duration(left, int(right.value), right.unit)

        # Quantity + Date/DateTime
        if isinstance(right, (FHIRDate, FHIRDateTime, date, datetime)) and isinstance(left, Quantity):
            return self._add_duration(right, int(left.value), left.unit)

        return left + right  # type: ignore[operator]

    def _subtract(self, left: Any, right: Any) -> Any:
        """Subtract two values."""
        # Quantity - Quantity
        if isinstance(left, Quantity) and isinstance(right, Quantity):
            if left.unit == right.unit:
                return Quantity(value=left.value - right.value, unit=left.unit)
            return None

        # Date/DateTime - Quantity (duration)
        if isinstance(left, (FHIRDate, FHIRDateTime, date, datetime)) and isinstance(right, Quantity):
            return self._add_duration(left, -int(right.value), right.unit)

        # Date/DateTime - Date/DateTime (calculate days between)
        if isinstance(left, (FHIRDate, FHIRDateTime, date, datetime)) and isinstance(
            right, (FHIRDate, FHIRDateTime, date, datetime)
        ):
            left_date = self._to_date(left)
            right_date = self._to_date(right)
            if left_date and right_date:
                delta = left_date - right_date
                return delta.days

        return left - right  # type: ignore[operator]

    def _multiply(self, left: Any, right: Any) -> Any:
        """Multiply two values."""
        if isinstance(left, Quantity) and isinstance(right, (int, float, Decimal)):
            return Quantity(value=left.value * Decimal(str(right)), unit=left.unit)
        if isinstance(right, Quantity) and isinstance(left, (int, float, Decimal)):
            return Quantity(value=right.value * Decimal(str(left)), unit=right.unit)
        return left * right  # type: ignore[operator]

    def _divide(self, left: Any, right: Any) -> Any:
        """Divide two values."""
        if right == 0:
            return None
        if isinstance(left, Quantity) and isinstance(right, (int, float, Decimal)):
            return Quantity(value=left.value / Decimal(str(right)), unit=left.unit)
        if isinstance(left, int) and isinstance(right, int):
            return Decimal(left) / Decimal(right)
        return left / right

    def _truncated_divide(self, left: Any, right: Any) -> int | None:
        """Truncated division (div)."""
        if right == 0:
            return None
        return int(left // right)

    def _modulo(self, left: Any, right: Any) -> Any:
        """Modulo operation."""
        if right == 0:
            return None
        return left % right

    # Three-valued logic helpers
    def _three_valued_and(self, left: Any, right: Any) -> bool | None:
        """Three-valued AND logic."""
        if left is False or right is False:
            return False
        if left is None or right is None:
            return None
        return bool(left) and bool(right)

    def _three_valued_or(self, left: Any, right: Any) -> bool | None:
        """Three-valued OR logic."""
        if left is True or right is True:
            return True
        if left is None or right is None:
            return None
        return bool(left) or bool(right)

    def _three_valued_xor(self, left: Any, right: Any) -> bool | None:
        """Three-valued XOR logic."""
        if left is None or right is None:
            return None
        return bool(left) != bool(right)

    def _three_valued_implies(self, left: Any, right: Any) -> bool | None:
        """Three-valued IMPLIES logic (left implies right)."""
        if left is False:
            return True
        if left is True and right is True:
            return True
        if left is True and right is False:
            return False
        return None

    # Equality helpers
    def _equals(self, left: Any, right: Any) -> bool | None:
        """Check equality with CQL semantics."""
        if left is None or right is None:
            return None

        # Handle lists
        if isinstance(left, list) and isinstance(right, list):
            if len(left) != len(right):
                return False
            return all(self._equals(left_item, right_item) for left_item, right_item in zip(left, right))

        # Handle Quantity
        if isinstance(left, Quantity) and isinstance(right, Quantity):
            if left.unit != right.unit:
                return None  # Incompatible units
            return left.value == right.value

        # Handle Interval
        if isinstance(left, CQLInterval) and isinstance(right, CQLInterval):
            return left == right

        # Handle Code
        if isinstance(left, CQLCode) and isinstance(right, CQLCode):
            return left.equivalent(right)

        return left == right

    # Type checking helpers
    def _check_type(self, value: Any, type_name: str) -> bool:
        """Check if value is of the given type."""
        type_lower = type_name.lower()

        if value is None:
            return False

        if type_lower in ("boolean", "system.boolean"):
            return isinstance(value, bool)
        if type_lower in ("integer", "system.integer"):
            return isinstance(value, int) and not isinstance(value, bool)
        if type_lower in ("decimal", "system.decimal"):
            return isinstance(value, Decimal | float)
        if type_lower in ("string", "system.string"):
            return isinstance(value, str)
        if type_lower in ("date", "system.date"):
            return isinstance(value, FHIRDate)
        if type_lower in ("datetime", "system.datetime"):
            return isinstance(value, FHIRDateTime)
        if type_lower in ("time", "system.time"):
            return isinstance(value, FHIRTime)
        if type_lower in ("quantity", "system.quantity"):
            return isinstance(value, Quantity)
        if type_lower in ("code", "system.code"):
            return isinstance(value, CQLCode)
        if type_lower in ("concept", "system.concept"):
            return isinstance(value, CQLConcept)

        return False

    def _cast_type(self, value: Any, type_name: str) -> Any:
        """Cast value to the given type."""
        if value is None:
            return None

        type_lower = type_name.lower()

        if type_lower in ("string", "system.string"):
            return str(value)
        if type_lower in ("integer", "system.integer"):
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        if type_lower in ("decimal", "system.decimal"):
            try:
                return Decimal(str(value))
            except (ValueError, TypeError):
                return None
        if type_lower in ("boolean", "system.boolean"):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "t", "yes", "y", "1")
            return None

        return value

    # =========================================================================
    # Phase 3: Date/Time Helpers
    # =========================================================================

    def _to_date(self, value: Any) -> date | None:
        """Convert a value to a Python date."""
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, FHIRDate):
            return value.to_date()
        if isinstance(value, FHIRDateTime):
            dt = value.to_datetime()
            return dt.date() if dt else None
        return None

    def _to_datetime(self, value: Any) -> datetime | None:
        """Convert a value to a Python datetime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, time(0, 0, 0))
        if isinstance(value, FHIRDateTime):
            return value.to_datetime()
        if isinstance(value, FHIRDate):
            d = value.to_date()
            return datetime.combine(d, time(0, 0, 0)) if d else None
        return None

    def _get_patient_birthdate(self) -> date | None:
        """Get the patient's birthdate from context."""
        resource = self.context.resource
        if resource:
            birthdate = resource.get("birthDate")
            if birthdate:
                if isinstance(birthdate, str):
                    try:
                        return date.fromisoformat(birthdate[:10])
                    except ValueError:
                        return None
                if isinstance(birthdate, date):
                    return birthdate
                if isinstance(birthdate, FHIRDate):
                    return birthdate.to_date()
        return None

    def _calculate_age_in_years(self, birthdate: Any, as_of: Any) -> int | None:
        """Calculate age in years."""
        birth = self._to_date(birthdate)
        ref = self._to_date(as_of) if not isinstance(as_of, datetime) else as_of.date()
        if birth is None or ref is None:
            return None

        age = ref.year - birth.year
        if (ref.month, ref.day) < (birth.month, birth.day):
            age -= 1
        return age

    def _calculate_age_in_months(self, birthdate: Any, as_of: Any) -> int | None:
        """Calculate age in months."""
        birth = self._to_date(birthdate)
        ref = self._to_date(as_of) if not isinstance(as_of, datetime) else as_of.date()
        if birth is None or ref is None:
            return None

        months = (ref.year - birth.year) * 12 + (ref.month - birth.month)
        if ref.day < birth.day:
            months -= 1
        return months

    def _calculate_age_in_weeks(self, birthdate: Any, as_of: Any) -> int | None:
        """Calculate age in weeks."""
        birth = self._to_date(birthdate)
        ref = self._to_date(as_of) if not isinstance(as_of, datetime) else as_of.date()
        if birth is None or ref is None:
            return None

        delta = ref - birth
        return delta.days // 7

    def _calculate_age_in_days(self, birthdate: Any, as_of: Any) -> int | None:
        """Calculate age in days."""
        birth = self._to_date(birthdate)
        ref = self._to_date(as_of) if not isinstance(as_of, datetime) else as_of.date()
        if birth is None or ref is None:
            return None

        delta = ref - birth
        return delta.days

    def _date_diff(self, start: Any, end: Any, unit: str) -> int | None:
        """Calculate difference between two dates in the given unit."""
        start_date = self._to_date(start)
        end_date = self._to_date(end)
        if start_date is None or end_date is None:
            return None

        unit_lower = unit.lower()
        if unit_lower in ("year", "years"):
            return self._calculate_age_in_years(start_date, end_date)
        elif unit_lower in ("month", "months"):
            return self._calculate_age_in_months(start_date, end_date)
        elif unit_lower in ("week", "weeks"):
            delta = end_date - start_date
            return delta.days // 7
        elif unit_lower in ("day", "days"):
            delta = end_date - start_date
            return delta.days
        return None

    def _add_duration(self, dt: Any, value: int, unit: str) -> Any:
        """Add a duration to a date or datetime."""
        unit_lower = unit.lower().rstrip("s")  # Remove trailing 's' for plural

        if isinstance(dt, FHIRDate):
            d = dt.to_date()
            if d is None:
                return None
            result = self._add_to_date(d, value, unit_lower)
            if result:
                return FHIRDate(year=result.year, month=result.month, day=result.day)
            return None

        if isinstance(dt, FHIRDateTime):
            d = dt.to_datetime()
            if d is None:
                return None
            result = self._add_to_datetime(d, value, unit_lower)
            if result:
                return FHIRDateTime(
                    year=result.year,
                    month=result.month,
                    day=result.day,
                    hour=result.hour,
                    minute=result.minute,
                    second=result.second,
                    millisecond=result.microsecond // 1000,
                )
            return None

        if isinstance(dt, date) and not isinstance(dt, datetime):
            return self._add_to_date(dt, value, unit_lower)

        if isinstance(dt, datetime):
            return self._add_to_datetime(dt, value, unit_lower)

        return None

    def _add_to_date(self, d: date, value: int, unit: str) -> date | None:
        """Add duration to a date."""
        if unit == "year":
            try:
                return d.replace(year=d.year + value)
            except ValueError:
                # Handle Feb 29 -> Feb 28 for non-leap years
                return d.replace(year=d.year + value, day=28)
        elif unit == "month":
            month = d.month + value
            year = d.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            try:
                return d.replace(year=year, month=month)
            except ValueError:
                # Handle day overflow (e.g., Jan 31 + 1 month)
                import calendar

                max_day = calendar.monthrange(year, month)[1]
                return d.replace(year=year, month=month, day=min(d.day, max_day))
        elif unit == "week":
            return d + timedelta(weeks=value)
        elif unit == "day":
            return d + timedelta(days=value)
        return None

    def _add_to_datetime(self, dt: datetime, value: int, unit: str) -> datetime | None:
        """Add duration to a datetime."""
        if unit in ("year", "month", "week", "day"):
            result_date = self._add_to_date(dt.date(), value, unit)
            if result_date:
                return datetime.combine(result_date, dt.time())
            return None
        elif unit == "hour":
            return dt + timedelta(hours=value)
        elif unit == "minute":
            return dt + timedelta(minutes=value)
        elif unit == "second":
            return dt + timedelta(seconds=value)
        elif unit == "millisecond":
            return dt + timedelta(milliseconds=value)
        return None

    def _collapse_intervals(self, intervals: list[CQLInterval[Any]]) -> list[CQLInterval[Any]]:
        """Collapse overlapping/adjacent intervals into merged intervals."""
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
                    result[-1] = CQLInterval(
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

    # =========================================================================
    # Missing Expression Terms (Phase 8)
    # =========================================================================

    def visitAggregateExpressionTerm(self, ctx: cqlParser.AggregateExpressionTermContext) -> Any:
        """Visit aggregate expression term (distinct/flatten as expression)."""
        # Get the operation (first token: 'distinct' or 'flatten')
        op = ctx.getChild(0).getText().lower()
        expr = ctx.expression()
        value = self.visit(expr)

        if op == "distinct":
            if isinstance(value, list):
                seen: list[Any] = []
                for item in value:
                    if item not in seen:
                        seen.append(item)
                return seen
            return value

        elif op == "flatten":
            if isinstance(value, list):
                result: list[Any] = []
                for item in value:
                    if isinstance(item, list):
                        result.extend(item)
                    else:
                        result.append(item)
                return result
            return value

        return value

    def visitElementExtractorExpressionTerm(self, ctx: cqlParser.ElementExtractorExpressionTermContext) -> Any:
        """Visit element extractor expression (singleton from X)."""
        expr = ctx.expressionTerm()
        value = self.visit(expr)

        if isinstance(value, list):
            if len(value) == 0:
                return None
            elif len(value) == 1:
                return value[0]
            else:
                raise CQLError("singleton from requires a list with at most one element")
        return value

    def visitPointExtractorExpressionTerm(self, ctx: cqlParser.PointExtractorExpressionTermContext) -> Any:
        """Visit point extractor expression (point from Interval)."""
        expr = ctx.expressionTerm()
        value = self.visit(expr)

        if isinstance(value, CQLInterval):
            # point from requires a unit interval (low == high)
            if value.low is not None and value.high is not None and value.low == value.high:
                if value.low_closed and value.high_closed:
                    return value.low
            raise CQLError("point from requires a unit interval (low = high, both closed)")
        return None

    def visitSuccessorExpressionTerm(self, ctx: cqlParser.SuccessorExpressionTermContext) -> Any:
        """Visit successor expression (successor of X)."""
        expr = ctx.expressionTerm()
        value = self.visit(expr)

        if value is None:
            return None

        # Integer successor
        if isinstance(value, int):
            return value + 1

        # Decimal successor (add minimum precision)
        if isinstance(value, Decimal):
            # Get the scale and add the smallest increment
            sign, digits, exp = value.as_tuple()
            if exp < 0:
                increment = Decimal(10) ** exp
            else:
                increment = Decimal(1)
            return value + increment

        # Date successor (next day)
        if isinstance(value, (date, FHIRDate)):
            d = self._to_date(value)
            if d:
                next_day = d + timedelta(days=1)
                return FHIRDate(year=next_day.year, month=next_day.month, day=next_day.day)

        # DateTime successor (next millisecond)
        if isinstance(value, (datetime, FHIRDateTime)):
            dt = self._to_datetime(value)
            if dt:
                next_ms = dt + timedelta(milliseconds=1)
                return FHIRDateTime(
                    year=next_ms.year,
                    month=next_ms.month,
                    day=next_ms.day,
                    hour=next_ms.hour,
                    minute=next_ms.minute,
                    second=next_ms.second,
                    microsecond=next_ms.microsecond,
                )

        # Time successor
        if isinstance(value, (time, FHIRTime)):
            t = self._to_time(value)
            if t:
                # Add 1 millisecond
                total_ms = (t.hour * 3600 + t.minute * 60 + t.second) * 1000 + t.microsecond // 1000 + 1
                if total_ms >= 24 * 3600 * 1000:
                    total_ms = 0  # Wrap around
                h = (total_ms // 3600000) % 24
                m = (total_ms // 60000) % 60
                s = (total_ms // 1000) % 60
                ms = total_ms % 1000
                return FHIRTime(hour=h, minute=m, second=s, millisecond=ms)

        return None

    def visitPredecessorExpressionTerm(self, ctx: cqlParser.PredecessorExpressionTermContext) -> Any:
        """Visit predecessor expression (predecessor of X)."""
        expr = ctx.expressionTerm()
        value = self.visit(expr)

        if value is None:
            return None

        # Integer predecessor
        if isinstance(value, int):
            return value - 1

        # Decimal predecessor
        if isinstance(value, Decimal):
            sign, digits, exp = value.as_tuple()
            if exp < 0:
                decrement = Decimal(10) ** exp
            else:
                decrement = Decimal(1)
            return value - decrement

        # Date predecessor (previous day)
        if isinstance(value, (date, FHIRDate)):
            d = self._to_date(value)
            if d:
                prev_day = d - timedelta(days=1)
                return FHIRDate(year=prev_day.year, month=prev_day.month, day=prev_day.day)

        # DateTime predecessor
        if isinstance(value, (datetime, FHIRDateTime)):
            dt = self._to_datetime(value)
            if dt:
                prev_ms = dt - timedelta(milliseconds=1)
                return FHIRDateTime(
                    year=prev_ms.year,
                    month=prev_ms.month,
                    day=prev_ms.day,
                    hour=prev_ms.hour,
                    minute=prev_ms.minute,
                    second=prev_ms.second,
                    microsecond=prev_ms.microsecond,
                )

        # Time predecessor
        if isinstance(value, (time, FHIRTime)):
            t = self._to_time(value)
            if t:
                total_ms = (t.hour * 3600 + t.minute * 60 + t.second) * 1000 + t.microsecond // 1000 - 1
                if total_ms < 0:
                    total_ms = 24 * 3600 * 1000 - 1  # Wrap around
                h = (total_ms // 3600000) % 24
                m = (total_ms // 60000) % 60
                s = (total_ms // 1000) % 60
                ms = total_ms % 1000
                return FHIRTime(hour=h, minute=m, second=s, millisecond=ms)

        return None

    def visitConversionExpressionTerm(self, ctx: cqlParser.ConversionExpressionTermContext) -> Any:
        """Visit conversion expression (convert X to Y)."""
        expr = ctx.expression()
        value = self.visit(expr)

        if value is None:
            return None

        # Check if converting to a type specifier or unit
        type_spec = ctx.typeSpecifier()
        unit = ctx.unit()

        if type_spec:
            # Type conversion
            type_name = type_spec.getText()
            return self._convert_to_type(value, type_name)

        if unit:
            # Unit conversion for quantities
            unit_text = self._unquote_string(unit.getText())
            if isinstance(value, Quantity):
                # For now, just change the unit (proper conversion would need unit tables)
                return Quantity(value=value.value, unit=unit_text)
            elif isinstance(value, (int, float, Decimal)):
                return Quantity(value=Decimal(str(value)), unit=unit_text)

        return value

    def _convert_to_type(self, value: Any, type_name: str) -> Any:
        """Convert a value to the specified type."""
        type_lower = type_name.lower()

        if type_lower == "string":
            return str(value) if value is not None else None

        if type_lower == "integer":
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        if type_lower == "decimal":
            try:
                return Decimal(str(value))
            except (ValueError, TypeError):
                return None

        if type_lower == "boolean":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "t", "yes", "y", "1")
            return None

        if type_lower == "date":
            return self._to_fhir_date(value)

        if type_lower == "datetime":
            return self._to_fhir_datetime(value)

        if type_lower == "quantity":
            if isinstance(value, Quantity):
                return value
            if isinstance(value, (int, float, Decimal)):
                return Quantity(value=Decimal(str(value)), unit="1")
            return None

        return value

    def _to_fhir_date(self, value: Any) -> FHIRDate | None:
        """Convert value to FHIRDate."""
        if isinstance(value, FHIRDate):
            return value
        if isinstance(value, date):
            return FHIRDate(year=value.year, month=value.month, day=value.day)
        if isinstance(value, str):
            try:
                d = date.fromisoformat(value[:10])
                return FHIRDate(year=d.year, month=d.month, day=d.day)
            except ValueError:
                return None
        return None

    def _to_fhir_datetime(self, value: Any) -> FHIRDateTime | None:
        """Convert value to FHIRDateTime."""
        if isinstance(value, FHIRDateTime):
            return value
        if isinstance(value, datetime):
            return FHIRDateTime(
                year=value.year,
                month=value.month,
                day=value.day,
                hour=value.hour,
                minute=value.minute,
                second=value.second,
                microsecond=value.microsecond,
            )
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return FHIRDateTime(
                    year=dt.year,
                    month=dt.month,
                    day=dt.day,
                    hour=dt.hour,
                    minute=dt.minute,
                    second=dt.second,
                    microsecond=dt.microsecond,
                )
            except ValueError:
                return None
        return None

    def visitDurationExpressionTerm(self, ctx: cqlParser.DurationExpressionTermContext) -> Any:
        """Visit duration expression (duration in X of Interval)."""
        # Get the precision (pluralDateTimePrecision)
        precision = ctx.pluralDateTimePrecision().getText().lower()
        expr = ctx.expressionTerm()
        interval = self.visit(expr)

        if not isinstance(interval, CQLInterval):
            return None

        if interval.low is None or interval.high is None:
            return None

        return self._calculate_duration(interval.low, interval.high, precision)

    def visitDifferenceExpressionTerm(self, ctx: cqlParser.DifferenceExpressionTermContext) -> Any:
        """Visit difference expression (difference in X of Interval)."""
        # Get the precision
        precision = ctx.pluralDateTimePrecision().getText().lower()
        expr = ctx.expressionTerm()
        interval = self.visit(expr)

        if not isinstance(interval, CQLInterval):
            return None

        if interval.low is None or interval.high is None:
            return None

        # Difference uses calendar-based calculation (same as duration for most cases)
        return self._calculate_duration(interval.low, interval.high, precision)

    def _calculate_duration(self, low: Any, high: Any, precision: str) -> int | None:
        """Calculate duration between two values at given precision."""
        # Handle dates
        if isinstance(low, (date, FHIRDate)) and isinstance(high, (date, FHIRDate)):
            d1 = self._to_date(low)
            d2 = self._to_date(high)
            if d1 is None or d2 is None:
                return None

            if precision in ("years", "year"):
                return d2.year - d1.year - (1 if (d2.month, d2.day) < (d1.month, d1.day) else 0)
            elif precision in ("months", "month"):
                return (d2.year - d1.year) * 12 + d2.month - d1.month - (1 if d2.day < d1.day else 0)
            elif precision in ("weeks", "week"):
                return (d2 - d1).days // 7
            elif precision in ("days", "day"):
                return (d2 - d1).days

        # Handle datetimes
        if isinstance(low, (datetime, FHIRDateTime)) and isinstance(high, (datetime, FHIRDateTime)):
            dt1 = self._to_datetime(low)
            dt2 = self._to_datetime(high)
            if dt1 is None or dt2 is None:
                return None

            delta = dt2 - dt1

            if precision in ("years", "year"):
                return dt2.year - dt1.year - (1 if (dt2.month, dt2.day) < (dt1.month, dt1.day) else 0)
            elif precision in ("months", "month"):
                return (dt2.year - dt1.year) * 12 + dt2.month - dt1.month - (1 if dt2.day < dt1.day else 0)
            elif precision in ("weeks", "week"):
                return delta.days // 7
            elif precision in ("days", "day"):
                return delta.days
            elif precision in ("hours", "hour"):
                return int(delta.total_seconds() // 3600)
            elif precision in ("minutes", "minute"):
                return int(delta.total_seconds() // 60)
            elif precision in ("seconds", "second"):
                return int(delta.total_seconds())
            elif precision in ("milliseconds", "millisecond"):
                return int(delta.total_seconds() * 1000)

        # Handle times
        if isinstance(low, (time, FHIRTime)) and isinstance(high, (time, FHIRTime)):
            t1 = self._to_time(low)
            t2 = self._to_time(high)
            if t1 is None or t2 is None:
                return None

            secs1 = t1.hour * 3600 + t1.minute * 60 + t1.second + t1.microsecond / 1_000_000
            secs2 = t2.hour * 3600 + t2.minute * 60 + t2.second + t2.microsecond / 1_000_000
            delta_secs = secs2 - secs1

            if precision in ("hours", "hour"):
                return int(delta_secs // 3600)
            elif precision in ("minutes", "minute"):
                return int(delta_secs // 60)
            elif precision in ("seconds", "second"):
                return int(delta_secs)
            elif precision in ("milliseconds", "millisecond"):
                return int(delta_secs * 1000)

        return None

    def visitTypeExtentExpressionTerm(self, ctx: cqlParser.TypeExtentExpressionTermContext) -> Any:
        """Visit type extent expression (minimum/maximum Type)."""
        # Get the extent (minimum or maximum)
        extent = ctx.getChild(0).getText().lower()
        type_spec = ctx.namedTypeSpecifier()
        type_name = type_spec.getText().lower() if type_spec else ""

        if extent == "minimum":
            return self._get_type_minimum(type_name)
        elif extent == "maximum":
            return self._get_type_maximum(type_name)

        return None

    def _get_type_minimum(self, type_name: str) -> Any:
        """Get the minimum value for a type."""
        if type_name == "integer":
            return -(2**31)  # CQL Integer is 32-bit
        elif type_name == "decimal":
            return Decimal("-99999999999999999999.99999999")
        elif type_name == "date":
            return FHIRDate(year=1, month=1, day=1)
        elif type_name == "datetime":
            return FHIRDateTime(year=1, month=1, day=1, hour=0, minute=0, second=0)
        elif type_name == "time":
            return FHIRTime(hour=0, minute=0, second=0, millisecond=0)
        elif type_name == "quantity":
            return Quantity(value=Decimal("-99999999999999999999.99999999"), unit="1")
        return None

    def _get_type_maximum(self, type_name: str) -> Any:
        """Get the maximum value for a type."""
        if type_name == "integer":
            return 2**31 - 1  # CQL Integer is 32-bit
        elif type_name == "decimal":
            return Decimal("99999999999999999999.99999999")
        elif type_name == "date":
            return FHIRDate(year=9999, month=12, day=31)
        elif type_name == "datetime":
            return FHIRDateTime(year=9999, month=12, day=31, hour=23, minute=59, second=59)
        elif type_name == "time":
            return FHIRTime(hour=23, minute=59, second=59, millisecond=999)
        elif type_name == "quantity":
            return Quantity(value=Decimal("99999999999999999999.99999999"), unit="1")
        return None

    def _expand_interval(self, interval: CQLInterval[Any], per: Any = None) -> list[Any]:
        """Expand an interval into a list of points."""
        if interval.low is None or interval.high is None:
            return []

        # For integer intervals, expand to individual values
        if isinstance(interval.low, int) and isinstance(interval.high, int):
            start = interval.low if interval.low_closed else interval.low + 1
            end = interval.high if interval.high_closed else interval.high - 1
            return list(range(start, end + 1))

        # For date intervals with a per quantity
        if isinstance(interval.low, (date, FHIRDate)) and per is not None:
            return self._expand_date_interval(interval, per)

        return []

    def _expand_date_interval(self, interval: CQLInterval[Any], per: Any) -> list[Any]:
        """Expand a date interval by a given period."""
        low = self._to_date(interval.low)
        high = self._to_date(interval.high)
        if low is None or high is None:
            return []

        # Determine the unit from per (could be Quantity or string)
        if isinstance(per, Quantity):
            unit = per.unit
            step = int(per.value)
        elif isinstance(per, str):
            unit = per
            step = 1
        else:
            return []

        result = []
        current = low if interval.low_closed else self._add_to_date(low, 1, unit.rstrip("s"))

        while current and current <= high:
            if current < high or interval.high_closed:
                result.append(FHIRDate(year=current.year, month=current.month, day=current.day))
            next_date = self._add_to_date(current, step, unit.rstrip("s"))
            if next_date is None or next_date <= current:
                break
            current = next_date

        return result


del ParseTreeVisitor  # Clean up namespace
