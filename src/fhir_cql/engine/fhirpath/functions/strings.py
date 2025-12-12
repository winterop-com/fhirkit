"""String functions."""

import re
from typing import Any

from ...context import EvaluationContext
from ...functions import FunctionRegistry


@FunctionRegistry.register("startsWith")
def fn_starts_with(ctx: EvaluationContext, collection: list[Any], prefix: str) -> list[bool]:
    """Returns true if string starts with the given prefix."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [value.startswith(prefix)]


@FunctionRegistry.register("endsWith")
def fn_ends_with(ctx: EvaluationContext, collection: list[Any], suffix: str) -> list[bool]:
    """Returns true if string ends with the given suffix."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [value.endswith(suffix)]


@FunctionRegistry.register("contains")
def fn_contains(ctx: EvaluationContext, collection: list[Any], substring: str) -> list[bool]:
    """Returns true if string contains the given substring."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [substring in value]


@FunctionRegistry.register("matches")
def fn_matches(ctx: EvaluationContext, collection: list[Any], pattern: str) -> list[bool]:
    """Returns true if string matches the regex pattern."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    try:
        return [bool(re.search(pattern, value))]
    except re.error:
        return [False]


@FunctionRegistry.register("replace")
def fn_replace(ctx: EvaluationContext, collection: list[Any], pattern: str, substitution: str) -> list[str]:
    """Replaces all occurrences of pattern with substitution (simple string replacement)."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [value.replace(pattern, substitution)]


@FunctionRegistry.register("replaceMatches")
def fn_replace_matches(ctx: EvaluationContext, collection: list[Any], regex: str, substitution: str) -> list[str]:
    """Replaces all matches of regex pattern with substitution."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    try:
        return [re.sub(regex, substitution, value)]
    except re.error:
        return [value]


@FunctionRegistry.register("length")
def fn_length(ctx: EvaluationContext, collection: list[Any]) -> list[int]:
    """Returns the length of the string."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [len(value)]


@FunctionRegistry.register("substring")
def fn_substring(ctx: EvaluationContext, collection: list[Any], start: int, length: int | None = None) -> list[str]:
    """Returns a substring starting at start index."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    start = int(start)
    if length is not None:
        length = int(length)
        return [value[start : start + length]]
    return [value[start:]]


@FunctionRegistry.register("upper")
def fn_upper(ctx: EvaluationContext, collection: list[Any]) -> list[str]:
    """Returns the string in uppercase."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [value.upper()]


@FunctionRegistry.register("lower")
def fn_lower(ctx: EvaluationContext, collection: list[Any]) -> list[str]:
    """Returns the string in lowercase."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [value.lower()]


@FunctionRegistry.register("trim")
def fn_trim(ctx: EvaluationContext, collection: list[Any]) -> list[str]:
    """Returns the string with whitespace trimmed."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [value.strip()]


@FunctionRegistry.register("split")
def fn_split(ctx: EvaluationContext, collection: list[Any], separator: str) -> list[str]:
    """Splits the string by separator."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return value.split(separator)


@FunctionRegistry.register("join")
def fn_join(ctx: EvaluationContext, collection: list[Any], separator: str = "") -> list[str]:
    """Joins collection elements with separator."""
    if not collection:
        return []
    strings = [str(item) for item in collection if item is not None]
    return [separator.join(strings)]


@FunctionRegistry.register("indexOf")
def fn_index_of(ctx: EvaluationContext, collection: list[Any], substring: str) -> list[int]:
    """Returns the index of substring, or -1 if not found."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return [value.find(substring)]


@FunctionRegistry.register("toChars")
def fn_to_chars(ctx: EvaluationContext, collection: list[Any]) -> list[str]:
    """Converts string to list of characters."""
    if not collection:
        return []
    value = collection[0]
    if not isinstance(value, str):
        return []
    return list(value)
