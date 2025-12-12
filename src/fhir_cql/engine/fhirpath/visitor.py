"""FHIRPath ANTLR visitor for expression evaluation."""

import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from antlr4 import ParserRuleContext

# Add generated directory to path
_gen_path = str(Path(__file__).parent.parent.parent.parent.parent / "generated" / "fhirpath")
if _gen_path not in sys.path:
    sys.path.insert(0, _gen_path)

from fhirpathParser import fhirpathParser  # noqa: E402
from fhirpathVisitor import fhirpathVisitor  # noqa: E402

from ..context import EvaluationContext  # noqa: E402
from ..functions import FunctionRegistry  # noqa: E402
from ..types import FHIRDate, FHIRDateTime, FHIRTime, Quantity  # noqa: E402


class FHIRPathEvaluatorVisitor(fhirpathVisitor):
    """
    Visitor that evaluates FHIRPath expressions.

    All expressions return a list (collection) as per FHIRPath semantics.
    """

    def __init__(self, ctx: EvaluationContext, input_collection: list[Any]):
        """
        Initialize the visitor.

        Args:
            ctx: Evaluation context with resource and environment
            input_collection: Initial collection to evaluate against
        """
        self.ctx = ctx
        self.input_collection = input_collection

    def evaluate(self, tree: ParserRuleContext) -> list[Any]:
        """Evaluate the parse tree and return the result collection."""
        result = self.visit(tree)
        if result is None:
            return []
        if not isinstance(result, list):
            return [result]
        return result

    # ===== Expression visitors =====

    def visitTermExpression(self, ctx: fhirpathParser.TermExpressionContext) -> list[Any]:
        """Visit terminal expression (literal, invocation, etc.)."""
        return self.visit(ctx.term())

    def visitInvocationExpression(self, ctx: fhirpathParser.InvocationExpressionContext) -> list[Any]:
        """Visit invocation expression (expr.member or expr.function())."""
        # Evaluate the left expression first
        left = self.visit(ctx.expression())
        if left is None:
            left = []

        # Now evaluate the invocation on the result
        return self._evaluate_invocation(left, ctx.invocation())

    def visitIndexerExpression(self, ctx: fhirpathParser.IndexerExpressionContext) -> list[Any]:
        """Visit indexer expression (expr[index])."""
        collection = self.visit(ctx.expression(0))
        if not collection:
            return []

        index_result = self.visit(ctx.expression(1))
        if not index_result:
            return []

        index = int(index_result[0])
        if 0 <= index < len(collection):
            return [collection[index]]
        return []

    def visitPolarityExpression(self, ctx: fhirpathParser.PolarityExpressionContext) -> list[Any]:
        """Visit polarity expression (+expr or -expr)."""
        result = self.visit(ctx.expression())
        if not result:
            return []

        value = result[0]
        if ctx.getChild(0).getText() == "-":
            if isinstance(value, (int, float, Decimal)):
                return [-value]
        return result

    def visitMultiplicativeExpression(self, ctx: fhirpathParser.MultiplicativeExpressionContext) -> list[Any]:
        """Visit multiplicative expression (*, /, div, mod)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        if not left or not right:
            return []

        left_val = left[0]
        right_val = right[0]

        if not isinstance(left_val, (int, float, Decimal)) or not isinstance(right_val, (int, float, Decimal)):
            return []

        # Convert to Decimal for consistent arithmetic
        left_dec = Decimal(str(left_val))
        right_dec = Decimal(str(right_val))

        op = ctx.getChild(1).getText()
        try:
            if op == "*":
                return [left_dec * right_dec]
            elif op == "/":
                if right_dec == 0:
                    return []
                return [left_dec / right_dec]
            elif op == "div":
                if right_dec == 0:
                    return []
                return [int(left_dec // right_dec)]
            elif op == "mod":
                if right_dec == 0:
                    return []
                return [left_dec % right_dec]
        except (ZeroDivisionError, ArithmeticError):
            return []

        return []

    def visitAdditiveExpression(self, ctx: fhirpathParser.AdditiveExpressionContext) -> list[Any]:
        """Visit additive expression (+, -, &)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        op = ctx.getChild(1).getText()

        # String concatenation with &
        if op == "&":
            left_str = str(left[0]) if left else ""
            right_str = str(right[0]) if right else ""
            return [left_str + right_str]

        if not left or not right:
            return []

        left_val = left[0]
        right_val = right[0]

        # Handle Quantity arithmetic
        if isinstance(left_val, Quantity) and isinstance(right_val, Quantity):
            if left_val.unit == right_val.unit:
                if op == "+":
                    return [Quantity(value=left_val.value + right_val.value, unit=left_val.unit)]
                elif op == "-":
                    return [Quantity(value=left_val.value - right_val.value, unit=left_val.unit)]
            return []

        # Handle date/datetime arithmetic with Quantity
        if isinstance(left_val, (FHIRDate, FHIRDateTime)) and isinstance(right_val, Quantity):
            result = self._date_add(left_val, right_val, op)
            return [result] if result else []

        if not isinstance(left_val, (int, float, Decimal)) or not isinstance(right_val, (int, float, Decimal)):
            return []

        # Convert to Decimal for consistent arithmetic
        left_dec = Decimal(str(left_val))
        right_dec = Decimal(str(right_val))

        if op == "+":
            return [left_dec + right_dec]
        elif op == "-":
            return [left_dec - right_dec]

        return []

    def _date_add(
        self, date_val: FHIRDate | FHIRDateTime, quantity: Quantity, op: str
    ) -> FHIRDate | FHIRDateTime | None:
        """Add or subtract a duration from a date/datetime."""
        unit = quantity.unit.lower().rstrip("s")  # Normalize: years -> year
        amount = int(quantity.value)
        if op == "-":
            amount = -amount

        # Map common duration units
        unit_map = {
            "year": "year",
            "month": "month",
            "day": "day",
            "week": "week",
            "hour": "hour",
            "minute": "minute",
            "second": "second",
            "millisecond": "millisecond",
            "a": "year",
            "mo": "month",
            "d": "day",
            "wk": "week",
            "h": "hour",
            "min": "minute",
            "s": "second",
            "ms": "millisecond",
        }

        normalized_unit = unit_map.get(unit)
        if not normalized_unit:
            return None

        if isinstance(date_val, FHIRDate):
            return self._add_to_date(date_val, amount, normalized_unit)
        else:
            return self._add_to_datetime(date_val, amount, normalized_unit)

    def _add_to_date(self, date_val: FHIRDate, amount: int, unit: str) -> FHIRDate | None:
        """Add a duration to a FHIRDate."""
        year = date_val.year
        month = date_val.month
        day = date_val.day

        if unit == "year":
            year += amount
        elif unit == "month":
            if month is not None:
                month += amount
                while month > 12:
                    month -= 12
                    year += 1
                while month < 1:
                    month += 12
                    year -= 1
            else:
                return None
        elif unit == "week":
            if day is not None and month is not None:
                from datetime import date as py_date
                from datetime import timedelta

                d = py_date(year, month, day)
                d += timedelta(weeks=amount)
                return FHIRDate(year=d.year, month=d.month, day=d.day)
            return None
        elif unit == "day":
            if day is not None and month is not None:
                from datetime import date as py_date
                from datetime import timedelta

                d = py_date(year, month, day)
                d += timedelta(days=amount)
                return FHIRDate(year=d.year, month=d.month, day=d.day)
            return None
        else:
            return None  # Time units not applicable to Date

        return FHIRDate(year=year, month=month, day=day)

    def _add_to_datetime(self, dt_val: FHIRDateTime, amount: int, unit: str) -> FHIRDateTime | None:
        """Add a duration to a FHIRDateTime."""
        from datetime import timedelta

        year = dt_val.year
        month = dt_val.month
        day = dt_val.day
        hour = dt_val.hour
        minute = dt_val.minute
        second = dt_val.second
        millisecond = dt_val.millisecond

        if unit == "year":
            year += amount
        elif unit == "month":
            if month is not None:
                month += amount
                while month > 12:
                    month -= 12
                    year += 1
                while month < 1:
                    month += 12
                    year -= 1
            else:
                return None
        elif unit in ("week", "day", "hour", "minute", "second", "millisecond"):
            if month is None or day is None:
                return None
            py_dt = dt_val.to_datetime()
            if py_dt is None:
                return None

            if unit == "week":
                py_dt += timedelta(weeks=amount)
            elif unit == "day":
                py_dt += timedelta(days=amount)
            elif unit == "hour":
                py_dt += timedelta(hours=amount)
            elif unit == "minute":
                py_dt += timedelta(minutes=amount)
            elif unit == "second":
                py_dt += timedelta(seconds=amount)
            elif unit == "millisecond":
                py_dt += timedelta(milliseconds=amount)

            return FHIRDateTime(
                year=py_dt.year,
                month=py_dt.month,
                day=py_dt.day,
                hour=py_dt.hour if dt_val.hour is not None else None,
                minute=py_dt.minute if dt_val.minute is not None else None,
                second=py_dt.second if dt_val.second is not None else None,
                millisecond=py_dt.microsecond // 1000 if dt_val.millisecond is not None else None,
                tz_offset=dt_val.tz_offset,
            )
        else:
            return None

        return FHIRDateTime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            millisecond=millisecond,
            tz_offset=dt_val.tz_offset,
        )

    def visitUnionExpression(self, ctx: fhirpathParser.UnionExpressionContext) -> list[Any]:
        """Visit union expression (expr | expr)."""
        left = self.visit(ctx.expression(0)) or []
        right = self.visit(ctx.expression(1)) or []

        # Union combines and removes duplicates
        result = list(left)
        for item in right:
            if item not in result:
                result.append(item)
        return result

    def visitInequalityExpression(self, ctx: fhirpathParser.InequalityExpressionContext) -> list[Any]:
        """Visit inequality expression (<, >, <=, >=)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        if not left or not right:
            return []

        op = ctx.getChild(1).getText()
        return FunctionRegistry.call(op, self.ctx, left, right)

    def visitEqualityExpression(self, ctx: fhirpathParser.EqualityExpressionContext) -> list[Any]:
        """Visit equality expression (=, !=, ~, !~)."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        op = ctx.getChild(1).getText()
        return FunctionRegistry.call(op, self.ctx, left or [], right or [])

    def visitMembershipExpression(self, ctx: fhirpathParser.MembershipExpressionContext) -> list[Any]:
        """Visit membership expression (in, contains)."""
        left = self.visit(ctx.expression(0)) or []
        right = self.visit(ctx.expression(1)) or []

        op = ctx.getChild(1).getText()

        if op == "in":
            # left in right: true if all elements of left are in right
            if not left:
                return [True]
            for item in left:
                if item not in right:
                    return [False]
            return [True]
        elif op == "contains":
            # left contains right: true if all elements of right are in left
            if not right:
                return [True]
            for item in right:
                if item not in left:
                    return [False]
            return [True]

        return []

    def visitAndExpression(self, ctx: fhirpathParser.AndExpressionContext) -> list[Any]:
        """Visit and expression."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        left_bool = self._to_boolean(left)
        right_bool = self._to_boolean(right)

        # FHIRPath three-valued logic
        if left_bool is False or right_bool is False:
            return [False]
        if left_bool is None or right_bool is None:
            return []
        return [True]

    def visitOrExpression(self, ctx: fhirpathParser.OrExpressionContext) -> list[Any]:
        """Visit or/xor expression."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        op = ctx.getChild(1).getText()

        left_bool = self._to_boolean(left)
        right_bool = self._to_boolean(right)

        if op == "or":
            if left_bool is True or right_bool is True:
                return [True]
            if left_bool is None or right_bool is None:
                return []
            return [False]
        elif op == "xor":
            if left_bool is None or right_bool is None:
                return []
            return [left_bool != right_bool]

        return []

    def visitImpliesExpression(self, ctx: fhirpathParser.ImpliesExpressionContext) -> list[Any]:
        """Visit implies expression."""
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))

        left_bool = self._to_boolean(left)
        right_bool = self._to_boolean(right)

        # p implies q = not p or q
        # Truth table: F->? = T, ?->T = T, T->F = F, else empty
        if left_bool is False:
            return [True]
        if right_bool is True:
            return [True]
        # At this point: left is True or None, right is False or None
        if left_bool is None or right_bool is None:
            return []
        # left is True and right is False
        return [False]

    def visitTypeExpression(self, ctx: fhirpathParser.TypeExpressionContext) -> list[Any]:
        """Visit type expression (is, as)."""
        left = self.visit(ctx.expression())
        type_spec = ctx.typeSpecifier().getText()

        op = ctx.getChild(1).getText()

        if op == "is":
            if not left:
                return [False]
            return [self._is_type(left[0], type_spec)]
        elif op == "as":
            if not left:
                return []
            if self._is_type(left[0], type_spec):
                return left
            return []

        return []

    # ===== Term visitors =====

    def visitInvocationTerm(self, ctx: fhirpathParser.InvocationTermContext) -> list[Any]:
        """Visit invocation term (initial member or function)."""
        return self._evaluate_invocation(self.input_collection, ctx.invocation())

    def visitLiteralTerm(self, ctx: fhirpathParser.LiteralTermContext) -> list[Any]:
        """Visit literal term."""
        return self.visit(ctx.literal())

    def visitExternalConstantTerm(self, ctx: fhirpathParser.ExternalConstantTermContext) -> list[Any]:
        """Visit external constant term (%name)."""
        return self.visit(ctx.externalConstant())

    def visitParenthesizedTerm(self, ctx: fhirpathParser.ParenthesizedTermContext) -> list[Any]:
        """Visit parenthesized expression."""
        return self.visit(ctx.expression())

    # ===== Literal visitors =====

    def visitNullLiteral(self, ctx: fhirpathParser.NullLiteralContext) -> list[Any]:
        """Visit null literal ({})."""
        return []

    def visitBooleanLiteral(self, ctx: fhirpathParser.BooleanLiteralContext) -> list[Any]:
        """Visit boolean literal."""
        return [ctx.getText() == "true"]

    def visitStringLiteral(self, ctx: fhirpathParser.StringLiteralContext) -> list[Any]:
        """Visit string literal."""
        text = ctx.getText()[1:-1]  # Remove quotes
        # Handle escape sequences
        text = self._unescape_string(text)
        return [text]

    def visitNumberLiteral(self, ctx: fhirpathParser.NumberLiteralContext) -> list[Any]:
        """Visit number literal."""
        text = ctx.getText()
        if "." in text:
            return [Decimal(text)]
        return [int(text)]

    def visitDateLiteral(self, ctx: fhirpathParser.DateLiteralContext) -> list[Any]:
        """Visit date literal (@YYYY-MM-DD)."""
        text = ctx.getText()[1:]  # Remove @
        parsed = FHIRDate.parse(text)
        return [parsed] if parsed else [text]

    def visitDateTimeLiteral(self, ctx: fhirpathParser.DateTimeLiteralContext) -> list[Any]:
        """Visit datetime literal (@YYYY-MM-DDThh:mm:ss)."""
        text = ctx.getText()[1:]  # Remove @
        parsed = FHIRDateTime.parse(text)
        return [parsed] if parsed else [text]

    def visitTimeLiteral(self, ctx: fhirpathParser.TimeLiteralContext) -> list[Any]:
        """Visit time literal (@Thh:mm:ss)."""
        text = ctx.getText()[1:]  # Remove @
        parsed = FHIRTime.parse(text)
        return [parsed] if parsed else [text]

    def visitQuantityLiteral(self, ctx: fhirpathParser.QuantityLiteralContext) -> list[Any]:
        """Visit quantity literal."""
        return self.visit(ctx.quantity())

    def visitQuantity(self, ctx: fhirpathParser.QuantityContext) -> list[Any]:
        """Visit quantity."""
        number = ctx.NUMBER().getText()
        value = Decimal(number) if "." in number else int(number)

        unit = ""
        if ctx.unit():
            unit = ctx.unit().getText()
            if unit.startswith("'") and unit.endswith("'"):
                unit = unit[1:-1]

        return [Quantity(value=Decimal(str(value)), unit=unit)]

    def visitExternalConstant(self, ctx: fhirpathParser.ExternalConstantContext) -> list[Any]:
        """Visit external constant (%name)."""
        if ctx.identifier():
            name = ctx.identifier().getText()
        else:
            name = ctx.STRING().getText()[1:-1]

        value = self.ctx.get_constant(name)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    # ===== Invocation visitors =====

    def visitMemberInvocation(self, ctx: fhirpathParser.MemberInvocationContext) -> list[Any]:
        """Visit member invocation - handled via _evaluate_invocation."""
        # This should not be called directly
        return self.visitChildren(ctx)

    def visitFunctionInvocation(self, ctx: fhirpathParser.FunctionInvocationContext) -> list[Any]:
        """Visit function invocation - handled via _evaluate_invocation."""
        # This should not be called directly
        return self.visitChildren(ctx)

    def visitThisInvocation(self, ctx: fhirpathParser.ThisInvocationContext) -> list[Any]:
        """Visit $this invocation."""
        value = self.ctx.this
        if value is None:
            return []
        return [value] if not isinstance(value, list) else value

    def visitIndexInvocation(self, ctx: fhirpathParser.IndexInvocationContext) -> list[Any]:
        """Visit $index invocation."""
        index = self.ctx.index
        if index is None:
            return []
        return [index]

    def visitTotalInvocation(self, ctx: fhirpathParser.TotalInvocationContext) -> list[Any]:
        """Visit $total invocation."""
        total = self.ctx.total
        if total is None:
            return []
        return [total] if not isinstance(total, list) else total

    # ===== Helper methods =====

    def _evaluate_invocation(self, input_collection: list[Any], invocation_ctx: ParserRuleContext) -> list[Any]:
        """Evaluate an invocation on a collection."""
        if isinstance(invocation_ctx, fhirpathParser.MemberInvocationContext):
            return self._evaluate_member(input_collection, invocation_ctx.identifier().getText())
        elif isinstance(invocation_ctx, fhirpathParser.FunctionInvocationContext):
            return self._evaluate_function(input_collection, invocation_ctx.function())
        elif isinstance(invocation_ctx, fhirpathParser.ThisInvocationContext):
            value = self.ctx.this
            return [value] if value is not None else []
        elif isinstance(invocation_ctx, fhirpathParser.IndexInvocationContext):
            index = self.ctx.index
            return [index] if index is not None else []
        elif isinstance(invocation_ctx, fhirpathParser.TotalInvocationContext):
            total = self.ctx.total
            return [total] if total is not None else []

        return []

    def _evaluate_member(self, collection: list[Any], member_name: str) -> list[Any]:
        """Navigate to a member on each item in the collection."""
        result = []
        for item in collection:
            if isinstance(item, dict):
                # Check if member_name matches resourceType (type filter)
                # This handles expressions like "Patient.name" where Patient is the type
                resource_type = item.get("resourceType")
                if resource_type == member_name:
                    result.append(item)
                    continue

                # Standard property access
                value = item.get(member_name)
                if value is not None:
                    if isinstance(value, list):
                        result.extend(value)
                    else:
                        result.append(value)
        return result

    # Functions that need full collection arguments (not just first element)
    _COLLECTION_ARG_FUNCTIONS = frozenset(["union", "intersect", "exclude", "combine", "subsetOf", "supersetOf"])

    def _evaluate_function(
        self, input_collection: list[Any], function_ctx: fhirpathParser.FunctionContext
    ) -> list[Any]:
        """Evaluate a function call."""
        func_name = function_ctx.identifier().getText()

        # Get arguments
        param_list = function_ctx.paramList()
        args = []
        if param_list:
            for expr in param_list.expression():
                args.append(expr)  # Pass AST node, not evaluated result

        # Handle special functions that need AST evaluation
        if func_name in ("where", "select", "repeat", "all", "exists"):
            return self._evaluate_special_function(func_name, input_collection, args)

        # Check if function needs full collection arguments
        needs_collection = func_name in self._COLLECTION_ARG_FUNCTIONS

        # For regular functions, evaluate arguments first
        evaluated_args: list[Any] = []
        for arg in args:
            # Create a sub-visitor with the input collection
            result = self.visit(arg)
            if result is None:
                result = []
            elif not isinstance(result, list):
                result = [result]

            if needs_collection:
                # Pass the full collection
                evaluated_args.append(result)
            else:
                # For most functions, we pass single values not lists
                if result:
                    evaluated_args.append(result[0])
                else:
                    evaluated_args.append(None)

        # Call the registered function
        return FunctionRegistry.call(func_name, self.ctx, input_collection, *evaluated_args)

    def _evaluate_special_function(self, func_name: str, collection: list[Any], args: list) -> list[Any]:
        """Evaluate functions that need special AST-based evaluation."""
        if func_name == "where":
            if not args:
                return collection
            return self._evaluate_where(collection, args[0])
        elif func_name == "select":
            if not args:
                return collection
            return self._evaluate_select(collection, args[0])
        elif func_name == "repeat":
            if not args:
                return collection
            return self._evaluate_repeat(collection, args[0])
        elif func_name == "all":
            if not args:
                return [True] if not collection else [all(bool(x) for x in collection)]
            return self._evaluate_all(collection, args[0])
        elif func_name == "exists":
            if not args:
                return [len(collection) > 0]
            return self._evaluate_exists(collection, args[0])
        return []

    def _evaluate_where(self, collection: list[Any], criteria_ctx: ParserRuleContext) -> list[Any]:
        """Evaluate where() with criteria."""
        result = []
        for i, item in enumerate(collection):
            self.ctx.push_this(item)
            self.ctx.push_index(i)
            try:
                # Create visitor with item as single-element collection
                sub_visitor = FHIRPathEvaluatorVisitor(self.ctx, [item])
                criteria_result = sub_visitor.visit(criteria_ctx)
                if self._to_boolean(criteria_result) is True:
                    result.append(item)
            finally:
                self.ctx.pop_this()
                self.ctx.pop_index()
        return result

    def _evaluate_select(self, collection: list[Any], projection_ctx: ParserRuleContext) -> list[Any]:
        """Evaluate select() with projection."""
        result = []
        for i, item in enumerate(collection):
            self.ctx.push_this(item)
            self.ctx.push_index(i)
            try:
                sub_visitor = FHIRPathEvaluatorVisitor(self.ctx, [item])
                projection_result = sub_visitor.visit(projection_ctx)
                if projection_result:
                    result.extend(projection_result if isinstance(projection_result, list) else [projection_result])
            finally:
                self.ctx.pop_this()
                self.ctx.pop_index()
        return result

    def _evaluate_repeat(self, collection: list[Any], expr_ctx: ParserRuleContext) -> list[Any]:
        """Evaluate repeat() - recursively apply expression until no new items."""
        result = []
        seen = set()
        work_list = list(collection)

        while work_list:
            item = work_list.pop(0)
            item_id = id(item) if isinstance(item, dict) else hash(str(item))

            if item_id in seen:
                continue
            seen.add(item_id)
            result.append(item)

            self.ctx.push_this(item)
            try:
                sub_visitor = FHIRPathEvaluatorVisitor(self.ctx, [item])
                new_items = sub_visitor.visit(expr_ctx)
                if new_items:
                    work_list.extend(new_items if isinstance(new_items, list) else [new_items])
            finally:
                self.ctx.pop_this()

        return result

    def _evaluate_all(self, collection: list[Any], criteria_ctx: ParserRuleContext) -> list[Any]:
        """Evaluate all() with criteria."""
        if not collection:
            return [True]

        for i, item in enumerate(collection):
            self.ctx.push_this(item)
            self.ctx.push_index(i)
            try:
                sub_visitor = FHIRPathEvaluatorVisitor(self.ctx, [item])
                criteria_result = sub_visitor.visit(criteria_ctx)
                if self._to_boolean(criteria_result) is not True:
                    return [False]
            finally:
                self.ctx.pop_this()
                self.ctx.pop_index()
        return [True]

    def _evaluate_exists(self, collection: list[Any], criteria_ctx: ParserRuleContext) -> list[Any]:
        """Evaluate exists() with criteria."""
        for i, item in enumerate(collection):
            self.ctx.push_this(item)
            self.ctx.push_index(i)
            try:
                sub_visitor = FHIRPathEvaluatorVisitor(self.ctx, [item])
                criteria_result = sub_visitor.visit(criteria_ctx)
                if self._to_boolean(criteria_result) is True:
                    return [True]
            finally:
                self.ctx.pop_this()
                self.ctx.pop_index()
        return [False]

    def _to_boolean(self, collection: list[Any] | None) -> bool | None:
        """Convert a collection to a boolean using FHIRPath rules."""
        if collection is None or len(collection) == 0:
            return None
        if len(collection) == 1:
            val = collection[0]
            if isinstance(val, bool):
                return val
            return True  # Single non-boolean value is truthy
        # Multiple items - error in strict mode, but we'll return True
        return True

    def _is_type(self, value: Any, type_name: str) -> bool:
        """Check if a value is of the specified type."""
        if isinstance(value, dict):
            if "resourceType" in value:
                return value["resourceType"] == type_name
            # For elements, check type info if available
            return True  # Relaxed check for elements

        type_map: dict[str, type | tuple[type, ...]] = {
            "Boolean": bool,
            "String": str,
            "Integer": int,
            "Decimal": (float, Decimal),
            "Quantity": Quantity,
        }

        if type_name in type_map:
            if type_name == "Integer":
                return isinstance(value, int) and not isinstance(value, bool)
            return isinstance(value, type_map[type_name])

        return False

    def _unescape_string(self, s: str) -> str:
        """Unescape a FHIRPath string literal."""
        result = []
        i = 0
        while i < len(s):
            if s[i] == "\\" and i + 1 < len(s):
                next_char = s[i + 1]
                if next_char == "n":
                    result.append("\n")
                elif next_char == "r":
                    result.append("\r")
                elif next_char == "t":
                    result.append("\t")
                elif next_char == "f":
                    result.append("\f")
                elif next_char == "\\":
                    result.append("\\")
                elif next_char == "'":
                    result.append("'")
                elif next_char == "/":
                    result.append("/")
                elif next_char == "`":
                    result.append("`")
                elif next_char == "u" and i + 5 < len(s):
                    # Unicode escape
                    hex_str = s[i + 2 : i + 6]
                    try:
                        result.append(chr(int(hex_str, 16)))
                        i += 4
                    except ValueError:
                        result.append(s[i : i + 2])
                else:
                    result.append(s[i : i + 2])
                i += 2
            else:
                result.append(s[i])
                i += 1
        return "".join(result)
