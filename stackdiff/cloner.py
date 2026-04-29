"""cloner.py — deep-copy and remap config dicts with optional key transforms."""
from __future__ import annotations

import copy
from typing import Callable, Dict, Optional


class ClonerError(Exception):
    """Raised when cloning fails."""


def clone_config(
    config: dict,
    *,
    key_transform: Optional[Callable[[str], str]] = None,
    value_transform: Optional[Callable[[object], object]] = None,
) -> dict:
    """Return a deep copy of *config*, optionally transforming keys and/or values.

    Args:
        config: Source configuration dictionary.
        key_transform: Optional callable applied to every key.
        value_transform: Optional callable applied to every leaf value.

    Returns:
        A new dictionary that is a transformed deep copy of *config*.

    Raises:
        ClonerError: If *config* is not a dict.
    """
    if not isinstance(config, dict):
        raise ClonerError(f"Expected dict, got {type(config).__name__}")

    result: Dict[str, object] = {}
    for key, value in config.items():
        new_key = key_transform(key) if key_transform is not None else key
        if not isinstance(new_key, str):
            raise ClonerError(
                f"key_transform must return str; got {type(new_key).__name__} for key {key!r}"
            )
        new_value = copy.deepcopy(value)
        if value_transform is not None:
            new_value = value_transform(new_value)
        result[new_key] = new_value
    return result


def clone_subset(config: dict, keys: list) -> dict:
    """Return a deep copy containing only *keys* from *config*.

    Missing keys are silently ignored.

    Raises:
        ClonerError: If *config* is not a dict.
    """
    if not isinstance(config, dict):
        raise ClonerError(f"Expected dict, got {type(config).__name__}")
    return {k: copy.deepcopy(config[k]) for k in keys if k in config}


def clone_summary(original: dict, cloned: dict) -> str:
    """Return a human-readable summary of a clone operation."""
    added = set(cloned) - set(original)
    removed = set(original) - set(cloned)
    kept = set(original) & set(cloned)
    lines = [
        f"keys kept   : {len(kept)}",
        f"keys added  : {len(added)}",
        f"keys removed: {len(removed)}",
    ]
    return "\n".join(lines)
