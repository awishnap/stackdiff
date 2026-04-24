"""Drift detection: compare a live config against a saved baseline and flag drift."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.baseline import BaselineError, load_baseline
from stackdiff.differ import DiffResult, diff_configs


class DriftError(Exception):
    """Raised when drift detection encounters an unrecoverable problem."""


@dataclass
class DriftReport:
    baseline_name: str
    drifted: bool
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)
    message: str = ""

    def summary(self) -> str:
        if not self.drifted:
            return f"No drift detected against baseline '{self.baseline_name}'."
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        detail = ", ".join(parts)
        return f"Drift detected against baseline '{self.baseline_name}': {detail}."


def detect_drift(
    baseline_name: str,
    live_config: Dict[str, str],
    baselines_dir: Optional[str] = None,
) -> DriftReport:
    """Compare *live_config* against the named baseline and return a DriftReport.

    Parameters
    ----------
    baseline_name:
        Name of the previously saved baseline to compare against.
    live_config:
        The current (live) configuration dictionary.
    baselines_dir:
        Optional directory override passed through to :func:`load_baseline`.
    """
    kwargs = {"baselines_dir": baselines_dir} if baselines_dir is not None else {}
    try:
        baseline_config = load_baseline(baseline_name, **kwargs)
    except BaselineError as exc:
        raise DriftError(f"Could not load baseline '{baseline_name}': {exc}") from exc

    result: DiffResult = diff_configs(baseline_config, live_config)

    drifted = bool(result.added or result.removed or result.changed)
    report = DriftReport(
        baseline_name=baseline_name,
        drifted=drifted,
        added=result.added,
        removed=result.removed,
        changed=result.changed,
    )
    report.message = report.summary()
    return report
