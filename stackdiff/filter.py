"""Key-based filtering for config dicts."""
from __future__ import annotations

import fnmatch
from typing import Iterable


class FilterError(Exception):
    """Raised when filter configuration is invalid."""


def _match(key: str, patterns: Iterable[str]) -> bool:
    """Return True if *key* matches any glob pattern."""
    return any(fnmatch.fnmatch(key, p) for p in patterns)


def include_keys(config: dict, patterns: list[str]) -> dict:
    """Return a new dict containing only keys that match *patterns*.

    Args:
        config: Source config dictionary.
        patterns: List of glob patterns to include.

    Returns:
        Filtered dictionary.

    Raises:
        FilterError: If *patterns* is empty.
    """
    if not patterns:
        raise FilterError("include_keys requires at least one pattern")
    return {k: v for k, v in config.items() if _match(k, patterns)}


def exclude_keys(config: dict, patterns: list[str]) -> dict:
    """Return a new dict with keys matching *patterns* removed.

    Args:
        config: Source config dictionary.
        patterns: List of glob patterns to exclude.

    Returns:
        Filtered dictionary.

    Raises:
        FilterError: If *patterns* is empty.
    """
    if not patterns:
        raise FilterError("exclude_keys requires at least one pattern")
    return {k: v for k, v in config.items() if not _match(k, patterns)}


def apply_filters(
    config: dict,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> dict:
    """Apply optional include and exclude filters to *config*.

    Include is applied before exclude. If neither is provided the
    original dict is returned unchanged.
    """
    result = config
    if include:
        result = include_keys(result, include)
    if exclude:
        result = exclude_keys(result, exclude)
    return result
