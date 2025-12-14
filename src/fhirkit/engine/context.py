"""Evaluation context for FHIRPath and CQL."""

from datetime import datetime
from typing import Any, Callable, Protocol


class ModelProvider(Protocol):
    """Protocol for FHIR model information (needed by CQL)."""

    def get_type_info(self, type_name: str) -> dict[str, Any]:
        """Get type information for a FHIR type."""
        ...

    def get_property_type(self, type_name: str, property_name: str) -> str | None:
        """Get the type of a property on a FHIR type."""
        ...


class EvaluationContext:
    """
    Context for FHIRPath/CQL expression evaluation.

    This context is designed to be extended by CQL for additional
    functionality like library management, retrieve operations, etc.
    """

    def __init__(
        self,
        resource: dict[str, Any] | None = None,
        root_resource: dict[str, Any] | None = None,
        model: ModelProvider | None = None,
        now: datetime | None = None,
        reference_resolver: Callable[[str], dict[str, Any] | None] | None = None,
    ):
        """
        Initialize evaluation context.

        Args:
            resource: Current resource (%resource)
            root_resource: Root resource for nested evaluations (%rootResource)
            model: FHIR model provider for type information
            now: Fixed datetime for today()/now() functions (useful for testing)
            reference_resolver: Callback to resolve FHIR references
        """
        self.resource = resource
        self.root_resource = root_resource or resource
        self.model = model
        self.now = now
        self.reference_resolver = reference_resolver

        # Variable stack for $this, $index, $total
        self._this_stack: list[Any] = []
        self._index_stack: list[int] = []
        self._total_stack: list[Any] = []

        # External constants (%name)
        self._constants: dict[str, Any] = {}

        # Custom function overrides
        self._function_overrides: dict[str, Callable[..., Any]] = {}

    @property
    def this(self) -> Any:
        """Get current $this value."""
        return self._this_stack[-1] if self._this_stack else None

    @property
    def index(self) -> int | None:
        """Get current $index value."""
        return self._index_stack[-1] if self._index_stack else None

    @property
    def total(self) -> Any:
        """Get current $total value (for aggregate)."""
        return self._total_stack[-1] if self._total_stack else None

    def push_this(self, value: Any) -> None:
        """Push a new $this value onto the stack."""
        self._this_stack.append(value)

    def pop_this(self) -> Any:
        """Pop $this value from the stack."""
        return self._this_stack.pop() if self._this_stack else None

    def push_index(self, value: int) -> None:
        """Push a new $index value onto the stack."""
        self._index_stack.append(value)

    def pop_index(self) -> int | None:
        """Pop $index value from the stack."""
        return self._index_stack.pop() if self._index_stack else None

    def push_total(self, value: Any) -> None:
        """Push a new $total value onto the stack."""
        self._total_stack.append(value)

    def pop_total(self) -> Any:
        """Pop $total value from the stack."""
        return self._total_stack.pop() if self._total_stack else None

    def set_constant(self, name: str, value: Any) -> None:
        """Set an external constant (%name)."""
        self._constants[name] = value

    def get_constant(self, name: str) -> Any:
        """Get an external constant (%name)."""
        if name == "resource":
            return self.resource
        if name == "rootResource":
            return self.root_resource
        if name == "context":
            return self.resource  # Default context is resource
        return self._constants.get(name)

    def register_function(self, name: str, fn: Callable[..., Any]) -> None:
        """Register a custom function override."""
        self._function_overrides[name] = fn

    def get_function_override(self, name: str) -> Callable[..., Any] | None:
        """Get a custom function override if registered."""
        return self._function_overrides.get(name)

    def child(self, resource: dict[str, Any] | None = None) -> "EvaluationContext":
        """
        Create a child context, optionally with a new resource.

        Useful for nested evaluations while preserving parent context.
        """
        child_ctx = EvaluationContext(
            resource=resource or self.resource,
            root_resource=self.root_resource,
            model=self.model,
            now=self.now,
            reference_resolver=self.reference_resolver,
        )
        child_ctx._constants = self._constants.copy()
        child_ctx._function_overrides = self._function_overrides.copy()
        return child_ctx
