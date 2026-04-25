"""splitter.py — split a flat config dict into named groups by key prefix or pattern."""
from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional


class SplitterError(Exception):
    """Raised when splitting fails."""


def split_by_prefix(
    config: dict,
    prefixes: List[str],
    *,
    strip_prefix: bool = False,
    default_group: Optional[str] = "__other__",
) -> Dict[str, dict]:
    """Partition *config* keys into groups by prefix.

    Keys are matched against *prefixes* in order; the first match wins.
    Keys that match no prefix land in *default_group* (or are dropped when
    *default_group* is ``None``).
    """
    if not isinstance(config, dict):
        raise SplitterError("config must be a dict")
    if not prefixes:
        raise SplitterError("prefixes list must not be empty")

    groups: Dict[str, dict] = {p: {} for p in prefixes}
    if default_group is not None:
        groups.setdefault(default_group, {})

    for key, value in config.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                out_key = key[len(prefix):] if strip_prefix else key
                groups[prefix][out_key] = value
                matched = True
                break
        if not matched and default_group is not None:
            groups[default_group][key] = value

    return groups


def split_by_glob(
    config: dict,
    patterns: Dict[str, str],
    *,
    default_group: Optional[str] = "__other__",
) -> Dict[str, dict]:
    """Partition *config* keys using glob *patterns* mapping name -> pattern.

    ``patterns`` is an ordered dict of ``{group_name: glob_pattern}``.
    First matching group wins.
    """
    if not isinstance(config, dict):
        raise SplitterError("config must be a dict")
    if not patterns:
        raise SplitterError("patterns mapping must not be empty")

    groups: Dict[str, dict] = {name: {} for name in patterns}
    if default_group is not None:
        groups.setdefault(default_group, {})

    for key, value in config.items():
        matched = False
        for group_name, pattern in patterns.items():
            if fnmatch.fnmatch(key, pattern):
                groups[group_name][key] = value
                matched = True
                break
        if not matched and default_group is not None:
            groups[default_group][key] = value

    return groups


def merge_groups(groups: Dict[str, dict]) -> dict:
    """Flatten a groups dict back into a single config dict (last-wins on collision)."""
    merged: dict = {}
    for group in groups.values():
        merged.update(group)
    return merged
