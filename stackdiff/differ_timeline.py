"""differ_timeline.py – build a chronological diff timeline from a sequence of configs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from stackdiff.differ import DiffResult, diff_configs


class TimelineError(Exception):
    """Raised when timeline construction fails."""


@dataclass
class TimelineEntry:
    label: str
    diff: DiffResult

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "added": self.diff.added,
            "removed": self.diff.removed,
            "changed": self.diff.changed,
            "unchanged": list(self.diff.unchanged),
        }


@dataclass
class DiffTimeline:
    entries: list[TimelineEntry] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"entries": [e.as_dict() for e in self.entries]}

    def summary(self) -> dict[str, Any]:
        total_added = sum(len(e.diff.added) for e in self.entries)
        total_removed = sum(len(e.diff.removed) for e in self.entries)
        total_changed = sum(len(e.diff.changed) for e in self.entries)
        most_active = max(
            self.entries,
            key=lambda e: len(e.diff.added) + len(e.diff.removed) + len(e.diff.changed),
            default=None,
        )
        return {
            "steps": len(self.entries),
            "total_added": total_added,
            "total_removed": total_removed,
            "total_changed": total_changed,
            "most_active_step": most_active.label if most_active else None,
        }


def build_timeline(
    configs: list[dict[str, Any]],
    labels: list[str] | None = None,
) -> DiffTimeline:
    """Diff consecutive config pairs and return a DiffTimeline.

    Args:
        configs: Ordered list of config dicts (oldest → newest).
        labels:  Optional labels for each transition, e.g. ["v1→v2", "v2→v3"].
                 Must have len(configs) - 1 elements when provided.
    """
    if len(configs) < 2:
        raise TimelineError("At least two configs are required to build a timeline.")

    n_steps = len(configs) - 1
    if labels is None:
        labels = [f"step-{i + 1}" for i in range(n_steps)]
    if len(labels) != n_steps:
        raise TimelineError(
            f"Expected {n_steps} labels for {n_steps} transitions, got {len(labels)}."
        )

    entries: list[TimelineEntry] = []
    for i, (a, b) in enumerate(zip(configs, configs[1:])):
        result = diff_configs(a, b)
        entries.append(TimelineEntry(label=labels[i], diff=result))

    return DiffTimeline(entries=entries)
