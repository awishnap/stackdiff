"""archiver.py – save and retrieve named diff archives (frozen exports)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from stackdiff.differ import DiffResult


class ArchiverError(Exception):
    """Raised when an archive operation fails."""


def _archive_dir(base_dir: str) -> Path:
    p = Path(base_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _archive_path(base_dir: str, name: str) -> Path:
    return _archive_dir(base_dir) / f"{name}.json"


def save_archive(base_dir: str, name: str, result: DiffResult, meta: dict[str, Any] | None = None) -> str:
    """Persist *result* as a named archive entry.  Returns the file path."""
    if not name or "/" in name:
        raise ArchiverError(f"Invalid archive name: {name!r}")
    payload = {
        "name": name,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "meta": meta or {},
        "added": result.added,
        "removed": result.removed,
        "changed": result.changed,
        "unchanged": result.unchanged,
    }
    path = _archive_path(base_dir, name)
    path.write_text(json.dumps(payload, indent=2))
    return str(path)


def load_archive(base_dir: str, name: str) -> dict[str, Any]:
    """Load a previously saved archive by name."""
    path = _archive_path(base_dir, name)
    if not path.exists():
        raise ArchiverError(f"Archive not found: {name!r}")
    return json.loads(path.read_text())


def list_archives(base_dir: str) -> list[str]:
    """Return sorted archive names (without extension) in *base_dir*."""
    d = Path(base_dir)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.json"))


def delete_archive(base_dir: str, name: str) -> None:
    """Remove the named archive.  Raises ArchiverError if absent."""
    path = _archive_path(base_dir, name)
    if not path.exists():
        raise ArchiverError(f"Archive not found: {name!r}")
    path.unlink()
