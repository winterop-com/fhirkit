"""FHIRPath evaluator."""

# Import functions to register them
from . import functions  # noqa: F401  # pyright: ignore[reportUnusedImport]
from .evaluator import FHIRPathEvaluator, evaluate

__all__ = ["FHIRPathEvaluator", "evaluate"]
