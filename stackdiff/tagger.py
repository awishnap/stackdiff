"""Tag configs with arbitrary metadata labels for grouping and filtering."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

TAGS_FILENAME = "tags.json"


class TaggerError(Exception):
    """Raised when a tagging operation fails."""


def _tags_path(tags_dir: str) -> Path:
    return Path(tags_dir) / TAGS_FILENAME


def _load_raw(tags_dir: str) -> Dict[str, List[str]]:
    path = _tags_path(tags_dir)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_raw(tags_dir: str, data: Dict[str, List[str]]) -> None:
    path = _tags_path(tags_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def add_tag(tags_dir: str, name: str, tag: str) -> None:
    """Add *tag* to the entry identified by *name*."""
    data = _load_raw(tags_dir)
    tags = data.setdefault(name, [])
    if tag not in tags:
        tags.append(tag)
    _save_raw(tags_dir, data)


def remove_tag(tags_dir: str, name: str, tag: str) -> None:
    """Remove *tag* from *name*. Raises TaggerError if tag not found."""
    data = _load_raw(tags_dir)
    tags = data.get(name, [])
    if tag not in tags:
        raise TaggerError(f"Tag '{tag}' not found on '{name}'.")
    tags.remove(tag)
    if not tags:
        data.pop(name, None)
    else:
        data[name] = tags
    _save_raw(tags_dir, data)


def list_tags(tags_dir: str, name: str) -> List[str]:
    """Return all tags for *name*, or an empty list."""
    return _load_raw(tags_dir).get(name, [])


def find_by_tag(tags_dir: str, tag: str) -> List[str]:
    """Return all names that carry *tag*."""
    return [name for name, tags in _load_raw(tags_dir).items() if tag in tags]


def clear_tags(tags_dir: str, name: str) -> None:
    """Remove all tags for *name*."""
    data = _load_raw(tags_dir)
    data.pop(name, None)
    _save_raw(tags_dir, data)


def rename_tag(tags_dir: str, old_tag: str, new_tag: str) -> int:
    """Rename *old_tag* to *new_tag* across all entries.

    Returns the number of entries that were updated.
    Raises TaggerError if *old_tag* does not exist on any entry.
    """
    data = _load_raw(tags_dir)
    updated = 0
    for name, tags in data.items():
        if old_tag in tags:
            tags[tags.index(old_tag)] = new_tag
            updated += 1
    if updated == 0:
        raise TaggerError(f"Tag '{old_tag}' not found on any entry.")
    _save_raw(tags_dir, data)
    return updated
