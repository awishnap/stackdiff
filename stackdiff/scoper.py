"""scoper.py — restrict config diffs to a named scope (prefix namespace)."""
from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional


class ScopeError(Exception):
    """Raised when scoping operations fail."""


def _validate_scope(scope: str) -> None:
    if not scope or not scope.strip():
        raise ScopeError("Scope name must be a non-empty string.")


def scope_config(
    config: dict,
    scope: str,
    *,
    separator: str = ".",
    strip_prefix: bool = True,
) -> dict:
    """Return only keys that belong to *scope* (prefix match).

    Args:
        config: Flat key/value config dict.
        scope: Prefix to filter by (e.g. ``"db"``).
        separator: Character separating prefix from the rest of the key.
        strip_prefix: When True the scope prefix is removed from returned keys.

    Returns:
        Dict of matching keys, optionally with prefix stripped.
    """
    if not isinstance(config, dict):
        raise ScopeError("config must be a dict.")
    _validate_scope(scope)
    prefix = scope.rstrip(separator) + separator
    result: dict = {}
    for key, value in config.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):] if strip_prefix else key
            result[new_key] = value
    return result


def list_scopes(config: dict, *, separator: str = ".") -> List[str]:
    """Return sorted unique top-level scope names found in *config* keys."""
    if not isinstance(config, dict):
        raise ScopeError("config must be a dict.")
    scopes: set = set()
    for key in config:
        if separator in key:
            scopes.add(key.split(separator, 1)[0])
    return sorted(scopes)


def scope_summary(scoped: dict, scope: str) -> str:
    """Return a human-readable summary line for a scoped config."""
    count = len(scoped)
    noun = "key" if count == 1 else "keys"
    return f"Scope '{scope}': {count} {noun}"
