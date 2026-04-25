"""Flatten and unflatten nested config dicts using a separator."""

from __future__ import annotations

from typing import Any


class FlattenerError(Exception):
    """Raised when flattening or unflattening fails."""


def flatten(
    config: dict[str, Any],
    sep: str = ".",
    prefix: str = "",
) -> dict[str, Any]:
    """Recursively flatten a nested dict into dot-separated keys.

    Args:
        config: The dict to flatten.
        sep:    Key separator (default ``"."``).
        prefix: Internal prefix used during recursion.

    Returns:
        A single-level dict with compound keys.

    Raises:
        FlattenerError: If *config* is not a dict.
    """
    if not isinstance(config, dict):
        raise FlattenerError(f"Expected a dict, got {type(config).__name__}")

    result: dict[str, Any] = {}
    for key, value in config.items():
        full_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict) and value:
            nested = flatten(value, sep=sep, prefix=full_key)
            result.update(nested)
        else:
            result[full_key] = value
    return result


def unflatten(
    config: dict[str, Any],
    sep: str = ".",
) -> dict[str, Any]:
    """Reconstruct a nested dict from dot-separated keys.

    Args:
        config: Flat dict produced by :func:`flatten`.
        sep:    Key separator used when the dict was flattened.

    Returns:
        A nested dict.

    Raises:
        FlattenerError: If *config* is not a dict.
    """
    if not isinstance(config, dict):
        raise FlattenerError(f"Expected a dict, got {type(config).__name__}")

    result: dict[str, Any] = {}
    for compound_key, value in config.items():
        parts = compound_key.split(sep)
        node = result
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return result
