"""Key sorting utilities for config dicts."""

from __future__ import annotations

from typing import Dict, Any, List


class SorterError(Exception):
    """Raised when sorting fails."""


def sort_keys_alpha(config: Dict[str, Any], reverse: bool = False) -> Dict[str, Any]:
    """Return a new dict with keys sorted alphabetically."""
    if not isinstance(config, dict):
        raise SorterError(f"Expected dict, got {type(config).__name__}")
    return dict(sorted(config.items(), key=lambda kv: kv[0].lower(), reverse=reverse))


def sort_keys_by_value(config: Dict[str, Any], reverse: bool = False) -> Dict[str, Any]:
    """Return a new dict sorted by string representation of values."""
    if not isinstance(config, dict):
        raise SorterError(f"Expected dict, got {type(config).__name__}")
    try:
        return dict(sorted(config.items(), key=lambda kv: str(kv[1]), reverse=reverse))
    except TypeError as exc:
        raise SorterError(f"Cannot compare values for sorting: {exc}") from exc


def sort_keys_by_length(config: Dict[str, Any], reverse: bool = False) -> Dict[str, Any]:
    """Return a new dict with keys sorted by key length."""
    if not isinstance(config, dict):
        raise SorterError(f"Expected dict, got {type(config).__name__}")
    return dict(sorted(config.items(), key=lambda kv: len(kv[0]), reverse=reverse))


def sort_keys_explicit(config: Dict[str, Any], order: List[str], drop_missing: bool = False) -> Dict[str, Any]:
    """Return a new dict ordered by *order*; keys not in *order* are appended alphabetically.

    If *drop_missing* is True, keys not in *order* are omitted.
    """
    if not isinstance(config, dict):
        raise SorterError(f"Expected dict, got {type(config).__name__}")
    if not order:
        raise SorterError("Explicit order list must not be empty")

    seen = set()
    result: Dict[str, Any] = {}
    for key in order:
        if key in config:
            result[key] = config[key]
            seen.add(key)

    if not drop_missing:
        for key in sorted(config.keys()):
            if key not in seen:
                result[key] = config[key]

    return result


_STRATEGIES = {
    "alpha": sort_keys_alpha,
    "value": sort_keys_by_value,
    "length": sort_keys_by_length,
}


def apply_sort(config: Dict[str, Any], strategy: str = "alpha", reverse: bool = False) -> Dict[str, Any]:
    """Apply a named sorting strategy to *config*."""
    if strategy not in _STRATEGIES:
        raise SorterError(f"Unknown sort strategy '{strategy}'. Choose from: {sorted(_STRATEGIES)}.")
    return _STRATEGIES[strategy](config, reverse=reverse)
