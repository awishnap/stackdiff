"""Snapshot-based diff: compare a saved snapshot against a live config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from stackdiff.differ import DiffResult, diff_configs
from stackdiff.snapshot import load_snapshot, SnapshotError


class SnapshotDiffError(Exception):
    """Raised when a snapshot-based diff cannot be completed."""


@dataclass
class SnapshotDiffResult:
    snapshot_name: str
    snapshot_config: Dict[str, Any]
    live_config: Dict[str, Any]
    diff: DiffResult
    label_a: str = "snapshot"
    label_b: str = "live"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_name": self.snapshot_name,
            "label_a": self.label_a,
            "label_b": self.label_b,
            "added": self.diff.added,
            "removed": self.diff.removed,
            "changed": self.diff.changed,
            "unchanged": self.diff.unchanged,
        }

    def has_drift(self) -> bool:
        return bool(self.diff.added or self.diff.removed or self.diff.changed)

    def summary(self) -> str:
        d = self.diff
        parts = []
        if d.added:
            parts.append(f"+{len(d.added)} added")
        if d.removed:
            parts.append(f"-{len(d.removed)} removed")
        if d.changed:
            parts.append(f"~{len(d.changed)} changed")
        if not parts:
            return f"No drift from snapshot '{self.snapshot_name}'."
        return f"Drift from snapshot '{self.snapshot_name}': " + ", ".join(parts) + "."


def diff_against_snapshot(
    snapshot_name: str,
    live_config: Dict[str, Any],
    snap_dir: Optional[str] = None,
    label_a: str = "snapshot",
    label_b: str = "live",
) -> SnapshotDiffResult:
    """Load *snapshot_name* and diff it against *live_config*."""
    kwargs: Dict[str, Any] = {}
    if snap_dir is not None:
        kwargs["snap_dir"] = snap_dir
    try:
        snap_cfg = load_snapshot(snapshot_name, **kwargs)
    except SnapshotError as exc:
        raise SnapshotDiffError(str(exc)) from exc

    if not isinstance(live_config, dict):
        raise SnapshotDiffError("live_config must be a dict.")

    result = diff_configs(snap_cfg, live_config)
    return SnapshotDiffResult(
        snapshot_name=snapshot_name,
        snapshot_config=snap_cfg,
        live_config=live_config,
        diff=result,
        label_a=label_a,
        label_b=label_b,
    )
