"""aliaser.py – manage key aliases (alternate names) for config keys.

Allows users to define aliases so that 'DB_HOST' and 'DATABASE_HOST'
are treated as the same key during comparison.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class AliasError(Exception):
    """Raised when an alias operation fails."""


def _alias_path(store_dir: str, group: str) -> Path:
    return Path(store_dir) / f"{group}.aliases.json"


def _load_raw(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_raw(path: Path, data: Dict[str, List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def add_alias(store_dir: str, group: str, canonical: str, alias: str) -> None:
    """Register *alias* as an alternate name for *canonical* in *group*."""
    if not canonical or not alias:
        raise AliasError("canonical and alias must be non-empty strings")
    path = _alias_path(store_dir, group)
    data = _load_raw(path)
    aliases = data.setdefault(canonical, [])
    if alias not in aliases:
        aliases.append(alias)
    _save_raw(path, data)


def remove_alias(store_dir: str, group: str, canonical: str, alias: str) -> None:
    """Remove *alias* from *canonical* in *group*."""
    path = _alias_path(store_dir, group)
    data = _load_raw(path)
    if canonical not in data or alias not in data[canonical]:
        raise AliasError(f"alias '{alias}' not found for '{canonical}' in group '{group}'")
    data[canonical].remove(alias)
    if not data[canonical]:
        del data[canonical]
    _save_raw(path, data)


def list_aliases(store_dir: str, group: str) -> Dict[str, List[str]]:
    """Return all canonical -> [aliases] mappings for *group*."""
    return _load_raw(_alias_path(store_dir, group))


def resolve_aliases(config: Dict[str, str], store_dir: str, group: str) -> Dict[str, str]:
    """Return a copy of *config* where alias keys are renamed to their canonical name.

    If both the alias and the canonical key exist, the canonical value wins.
    """
    aliases = list_aliases(store_dir, group)
    # build alias -> canonical lookup
    alias_to_canonical: Dict[str, str] = {}
    for canonical, alias_list in aliases.items():
        for a in alias_list:
            alias_to_canonical[a] = canonical

    result: Dict[str, str] = {}
    for key, value in config.items():
        resolved_key = alias_to_canonical.get(key, key)
        if resolved_key not in result:
            result[resolved_key] = value
    return result
