"""Key selector: pick a subset of config keys by explicit list or glob patterns."""

from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional


class SelectorError(Exception):
    """Raised when selection cannot be performed."""


def select_keys(
    config: dict,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> dict:
    """Return a new dict containing only the chosen keys.

    Args:
        config:   Source configuration dictionary.
        keys:     Exact key names to keep.
        patterns: Glob patterns (e.g. ``"DB_*"``) to match against keys.

    At least one of *keys* or *patterns* must be supplied.
    """
    if not isinstance(config, dict):
        raise SelectorError("config must be a dict")
    if not keys and not patterns:
        raise SelectorError("Provide at least one of 'keys' or 'patterns'")

    selected: dict = {}

    if keys:
        for k in keys:
            if k in config:
                selected[k] = config[k]

    if patterns:
        for k, v in config.items():
            if any(fnmatch.fnmatch(k, pat) for pat in patterns):
                selected.setdefault(k, v)

    return selected


def deselect_keys(
    config: dict,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> dict:
    """Return a new dict with the chosen keys removed."""
    if not isinstance(config, dict):
        raise SelectorError("config must be a dict")
    if not keys and not patterns:
        raise SelectorError("Provide at least one of 'keys' or 'patterns'")

    drop: set = set(keys or [])
    for k in list(config):
        if patterns and any(fnmatch.fnmatch(k, pat) for pat in patterns):
            drop.add(k)

    return {k: v for k, v in config.items() if k not in drop}


def selection_summary(original: dict, selected: dict) -> Dict[str, int]:
    """Return a brief summary of how many keys were kept / dropped."""
    total = len(original)
    kept = len(selected)
    return {"total": total, "kept": kept, "dropped": total - kept}
