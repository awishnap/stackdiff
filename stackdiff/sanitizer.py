"""sanitizer.py – strip, normalize, and clean config values before comparison."""

from __future__ import annotations

import re
from typing import Any


class SanitizerError(Exception):
    """Raised when sanitization fails."""


_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")


def strip_whitespace(value: Any) -> Any:
    """Strip leading/trailing whitespace from string values."""
    if isinstance(value, str):
        return value.strip()
    return value


def remove_control_chars(value: Any) -> Any:
    """Remove ASCII control characters from string values."""
    if isinstance(value, str):
        return _CONTROL_CHAR_RE.sub("", value)
    return value


def collapse_whitespace(value: Any) -> Any:
    """Collapse runs of internal whitespace to a single space."""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value)
    return value


def normalize_newlines(value: Any) -> Any:
    """Replace \\r\\n and \\r with \\n."""
    if isinstance(value, str):
        return value.replace("\r\n", "\n").replace("\r", "\n")
    return value


_PIPELINE = [
    remove_control_chars,
    normalize_newlines,
    strip_whitespace,
]


def sanitize_value(
    value: Any,
    *,
    collapse: bool = False,
) -> Any:
    """Apply the default sanitization pipeline to a single value.

    Args:
        value: The value to sanitize.
        collapse: If True, also collapse internal whitespace runs.

    Returns:
        The sanitized value (unchanged if not a string).
    """
    result = value
    for fn in _PIPELINE:
        result = fn(result)
    if collapse:
        result = collapse_whitespace(result)
    return result


def sanitize_config(
    config: dict[str, Any],
    *,
    collapse: bool = False,
) -> dict[str, Any]:
    """Sanitize all values in a config dict.

    Args:
        config: Flat or nested config mapping.
        collapse: Passed through to :func:`sanitize_value`.

    Returns:
        New dict with sanitized values; keys are unchanged.

    Raises:
        SanitizerError: If *config* is not a dict.
    """
    if not isinstance(config, dict):
        raise SanitizerError(f"Expected dict, got {type(config).__name__}")
    return {
        k: sanitize_value(v, collapse=collapse)
        for k, v in config.items()
    }
