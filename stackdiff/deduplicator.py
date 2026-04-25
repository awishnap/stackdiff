"""Deduplicator: detect and remove duplicate values across config dicts."""

from __future__ import annotations

from typing import Any


class DeduplicatorError(Exception):
    """Raised when deduplication fails."""


def find_duplicate_values(config: dict[str, Any]) -> dict[Any, list[str]]:
    """Return a mapping of value -> [keys] for values that appear more than once."""
    if not isinstance(config, dict):
        raise DeduplicatorError("config must be a dict")

    seen: dict[Any, list[str]] = {}
    for key, value in config.items():
        try:
            hash(value)  # only hashable values can be duplicates
        except TypeError:
            continue
        seen.setdefault(value, []).append(key)

    return {v: keys for v, keys in seen.items() if len(keys) > 1}


def has_duplicates(config: dict[str, Any]) -> bool:
    """Return True if any values are duplicated."""
    return bool(find_duplicate_values(config))


def drop_duplicate_keys(
    config: dict[str, Any],
    keep: str = "first",
) -> dict[str, Any]:
    """Return a new config with duplicate-value keys removed.

    Args:
        config: Source config dict.
        keep: ``'first'`` keeps the first occurrence (dict insertion order),
              ``'last'`` keeps the last occurrence.
    """
    if keep not in ("first", "last"):
        raise DeduplicatorError("keep must be 'first' or 'last'")

    duplicates = find_duplicate_values(config)
    keys_to_drop: set[str] = set()
    for keys in duplicates.values():
        if keep == "first":
            keys_to_drop.update(keys[1:])
        else:
            keys_to_drop.update(keys[:-1])

    return {k: v for k, v in config.items() if k not in keys_to_drop}


def dedup_summary(config: dict[str, Any]) -> str:
    """Return a human-readable summary of duplicate values found."""
    dupes = find_duplicate_values(config)
    if not dupes:
        return "No duplicate values found."
    lines = [f"Found {len(dupes)} duplicate value(s):"]
    for value, keys in dupes.items():
        lines.append(f"  {value!r}: {', '.join(keys)}")
    return "\n".join(lines)
