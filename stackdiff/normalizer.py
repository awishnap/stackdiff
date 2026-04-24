"""Normalize config values for consistent comparison (trim whitespace, unify booleans, etc.)."""

from __future__ import annotations

from typing import Any

_TRUE_STRINGS = {"true", "yes", "1", "on"}
_FALSE_STRINGS = {"false", "no", "0", "off"}


class NormalizerError(Exception):
    """Raised when normalization fails."""


def normalize_value(value: Any, *, coerce_booleans: bool = True, strip_strings: bool = True) -> Any:
    """Normalize a single config value.

    - Strips leading/trailing whitespace from strings (when strip_strings=True).
    - Coerces common boolean-like strings to actual booleans (when coerce_booleans=True).
    - Returns all other types unchanged.
    """
    if isinstance(value, str):
        if strip_strings:
            value = value.strip()
        if coerce_booleans:
            lower = value.lower()
            if lower in _TRUE_STRINGS:
                return True
            if lower in _FALSE_STRINGS:
                return False
    return value


def normalize_config(
    config: dict[str, Any],
    *,
    coerce_booleans: bool = True,
    strip_strings: bool = True,
    keys: list[str] | None = None,
) -> dict[str, Any]:
    """Return a new config dict with normalized values.

    Args:
        config: Source configuration mapping.
        coerce_booleans: Convert boolean-like strings to bool.
        strip_strings: Strip whitespace from string values.
        keys: If provided, only normalize these keys; others are copied as-is.

    Returns:
        New dict with normalized values.

    Raises:
        NormalizerError: If *config* is not a dict.
    """
    if not isinstance(config, dict):
        raise NormalizerError(f"Expected a dict, got {type(config).__name__}")

    result: dict[str, Any] = {}
    for k, v in config.items():
        if keys is None or k in keys:
            result[k] = normalize_value(v, coerce_booleans=coerce_booleans, strip_strings=strip_strings)
        else:
            result[k] = v
    return result
