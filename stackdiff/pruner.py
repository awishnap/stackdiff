"""pruner.py — remove keys from a config by pattern, value, or type."""

from __future__ import annotations

import fnmatch
from typing import Any, Iterable


class PrunerError(Exception):
    """Raised when pruning cannot be completed."""


def _match_any(key: str, patterns: Iterable[str]) -> bool:
    key_lower = key.lower()
    return any(fnmatch.fnmatch(key_lower, p.lower()) for p in patterns)


def prune_by_pattern(config: dict, patterns: Iterable[str]) -> dict:
    """Return a copy of *config* with keys matching any glob *patterns* removed."""
    if not isinstance(config, dict):
        raise PrunerError("config must be a dict")
    pats = list(patterns)
    if not pats:
        raise PrunerError("at least one pattern is required")
    return {k: v for k, v in config.items() if not _match_any(k, pats)}


def prune_by_value(config: dict, values: Iterable[Any]) -> dict:
    """Return a copy of *config* with keys whose value is in *values* removed."""
    if not isinstance(config, dict):
        raise PrunerError("config must be a dict")
    drop = set()
    sentinel = object()
    for v in values:
        for k, cv in config.items():
            try:
                if cv == v and type(cv) is type(v):
                    drop.add(k)
            except Exception:
                pass
    return {k: v for k, v in config.items() if k not in drop}


def prune_by_type(config: dict, types: Iterable[type]) -> dict:
    """Return a copy of *config* removing keys whose value is an instance of any of *types*."""
    if not isinstance(config, dict):
        raise PrunerError("config must be a dict")
    type_tuple = tuple(types)
    if not type_tuple:
        raise PrunerError("at least one type is required")
    return {k: v for k, v in config.items() if not isinstance(v, type_tuple)}


def prune_summary(original: dict, pruned: dict) -> dict:
    """Return a summary dict describing what was removed."""
    removed = [k for k in original if k not in pruned]
    return {
        "original_count": len(original),
        "pruned_count": len(pruned),
        "removed_count": len(removed),
        "removed_keys": removed,
    }
