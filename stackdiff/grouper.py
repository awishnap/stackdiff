"""Group config keys by prefix, pattern, or custom mapping."""
from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional


class GrouperError(Exception):
    """Raised when grouping fails."""


def group_by_prefix(
    config: dict,
    prefixes: List[str],
    separator: str = "_",
    default_group: Optional[str] = "other",
) -> Dict[str, dict]:
    """Group keys by matching prefix (case-insensitive)."""
    if not isinstance(config, dict):
        raise GrouperError("config must be a dict")
    if not prefixes:
        raise GrouperError("prefixes list must not be empty")

    groups: Dict[str, dict] = {p: {} for p in prefixes}
    if default_group is not None:
        groups[default_group] = {}

    for key, value in config.items():
        matched = False
        for prefix in prefixes:
            if key.lower().startswith(prefix.lower() + separator) or key.lower() == prefix.lower():
                groups[prefix][key] = value
                matched = True
                break
        if not matched and default_group is not None:
            groups[default_group][key] = value

    return {k: v for k, v in groups.items() if v or k in prefixes}


def group_by_glob(
    config: dict,
    patterns: Dict[str, str],
    default_group: Optional[str] = "other",
) -> Dict[str, dict]:
    """Group keys by glob pattern. patterns maps group_name -> glob."""
    if not isinstance(config, dict):
        raise GrouperError("config must be a dict")
    if not patterns:
        raise GrouperError("patterns dict must not be empty")

    groups: Dict[str, dict] = {name: {} for name in patterns}
    if default_group is not None:
        groups.setdefault(default_group, {})

    for key, value in config.items():
        matched = False
        for group_name, glob in patterns.items():
            if fnmatch.fnmatch(key, glob):
                groups[group_name][key] = value
                matched = True
                break
        if not matched and default_group is not None:
            groups[default_group][key] = value

    return groups


def merge_groups(groups: Dict[str, dict]) -> dict:
    """Flatten grouped config back into a single dict (last group wins on collision)."""
    merged: dict = {}
    for group_dict in groups.values():
        merged.update(group_dict)
    return merged
