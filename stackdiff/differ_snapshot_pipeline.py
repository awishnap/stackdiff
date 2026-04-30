"""High-level pipeline helpers that combine snapshot diffing with masking and reporting."""
from __future__ import annotations

from typing import Dict, Any, List, Optional

from stackdiff.differ_snapshot import diff_against_snapshot, SnapshotDiffResult
from stackdiff.masker import mask_config
from stackdiff.reporter import format_report
from stackdiff.snapshot import list_snapshots


def masked_snapshot_diff(
    snapshot_name: str,
    live_config: Dict[str, Any],
    patterns: Optional[List[str]] = None,
    snap_dir: Optional[str] = None,
) -> SnapshotDiffResult:
    """Mask sensitive keys in both configs before diffing against snapshot."""
    kwargs: Dict[str, Any] = {}
    if snap_dir is not None:
        kwargs["snap_dir"] = snap_dir

    result = diff_against_snapshot(snapshot_name, live_config, **kwargs)

    masked_snap = mask_config(result.snapshot_config, patterns=patterns)
    masked_live = mask_config(live_config, patterns=patterns)

    from stackdiff.differ import diff_configs
    masked_diff = diff_configs(masked_snap, masked_live)

    return SnapshotDiffResult(
        snapshot_name=snapshot_name,
        snapshot_config=masked_snap,
        live_config=masked_live,
        diff=masked_diff,
        label_a=result.label_a,
        label_b=result.label_b,
    )


def snapshot_drift_report(
    snapshot_name: str,
    live_config: Dict[str, Any],
    snap_dir: Optional[str] = None,
) -> str:
    """Return a formatted human-readable drift report for a snapshot comparison."""
    kwargs: Dict[str, Any] = {}
    if snap_dir is not None:
        kwargs["snap_dir"] = snap_dir
    result = diff_against_snapshot(snapshot_name, live_config, **kwargs)
    return format_report(result.diff)


def batch_snapshot_drift(
    live_config: Dict[str, Any],
    snap_dir: Optional[str] = None,
) -> List[SnapshotDiffResult]:
    """Diff *live_config* against every available snapshot and return results."""
    kwargs: Dict[str, Any] = {}
    if snap_dir is not None:
        kwargs["snap_dir"] = snap_dir
    names = list_snapshots(**kwargs)
    results: List[SnapshotDiffResult] = []
    for name in names:
        results.append(
            diff_against_snapshot(name, live_config, **kwargs)
        )
    return results
