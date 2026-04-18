"""Snapshot: save and load config snapshots to disk for later comparison."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

DEFAULT_SNAPSHOT_DIR = ".stackdiff_snapshots"


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def snapshot_path(name: str, snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> str:
    """Return the file path for a named snapshot."""
    return os.path.join(snapshot_dir, f"{name}.json")


def save_snapshot(
    name: str,
    config: dict[str, Any],
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
) -> str:
    """Persist *config* as a named snapshot. Returns the file path written."""
    _ensure_dir(snapshot_dir)
    path = snapshot_path(name, snapshot_dir)
    payload = {
        "name": name,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "config": config,
    }
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
    except OSError as exc:
        raise SnapshotError(f"Could not write snapshot '{name}': {exc}") from exc
    return path


def load_snapshot(
    name: str,
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
) -> dict[str, Any]:
    """Load and return the config dict stored in a named snapshot."""
    path = snapshot_path(name, snapshot_dir)
    if not os.path.exists(path):
        raise SnapshotError(f"Snapshot '{name}' not found at {path}")
    try:
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Could not read snapshot '{name}': {exc}") from exc
    return payload["config"]


def list_snapshots(snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> list[str]:
    """Return sorted names of all saved snapshots."""
    if not os.path.isdir(snapshot_dir):
        return []
    return sorted(
        f[:-5] for f in os.listdir(snapshot_dir) if f.endswith(".json")
    )
