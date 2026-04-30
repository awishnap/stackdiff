"""Heatmap: rank keys by how frequently they change across multiple diff results."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from stackdiff.differ import DiffResult


class HeatmapError(Exception):
    """Raised when heatmap computation fails."""


@dataclass
class HeatmapEntry:
    key: str
    change_count: int
    total_diffs: int

    @property
    def frequency(self) -> float:
        if self.total_diffs == 0:
            return 0.0
        return self.change_count / self.total_diffs

    def as_dict(self) -> Dict:
        return {
            "key": self.key,
            "change_count": self.change_count,
            "total_diffs": self.total_diffs,
            "frequency": round(self.frequency, 4),
        }


@dataclass
class Heatmap:
    entries: List[HeatmapEntry] = field(default_factory=list)
    total_diffs: int = 0

    def as_dict(self) -> Dict:
        return {
            "total_diffs": self.total_diffs,
            "entries": [e.as_dict() for e in self.entries],
        }

    def top(self, n: int = 10) -> List[HeatmapEntry]:
        return self.entries[:n]

    def filter_by_min_frequency(self, min_frequency: float) -> List[HeatmapEntry]:
        """Return entries whose change frequency is at or above *min_frequency*.

        Args:
            min_frequency: A value between 0.0 and 1.0 (inclusive).

        Returns:
            A filtered list of :class:`HeatmapEntry` objects, preserving the
            existing descending-frequency order.
        """
        if not 0.0 <= min_frequency <= 1.0:
            raise HeatmapError(
                f"min_frequency must be between 0.0 and 1.0, got {min_frequency!r}."
            )
        return [e for e in self.entries if e.frequency >= min_frequency]


def build_heatmap(
    results: Sequence[DiffResult],
    top_n: int | None = None,
) -> Heatmap:
    """Build a heatmap from a sequence of DiffResult objects.

    A key is counted as 'changed' if it appears in added, removed, or changed.
    """
    if not results:
        raise HeatmapError("At least one DiffResult is required to build a heatmap.")

    total = len(results)
    counter: Counter = Counter()

    for result in results:
        changed_keys = (
            set(result.added)
            | set(result.removed)
            | set(result.changed)
        )
        for key in changed_keys:
            counter[key] += 1

    entries = [
        HeatmapEntry(key=key, change_count=count, total_diffs=total)
        for key, count in counter.most_common()
    ]

    if top_n is not None:
        entries = entries[:top_n]

    return Heatmap(entries=entries, total_diffs=total)


def heatmap_summary(heatmap: Heatmap, top_n: int = 5) -> str:
    """Return a human-readable summary of the hottest keys."""
    lines = [f"Heatmap over {heatmap.total_diffs} diff(s):"]
    for entry in heatmap.top(top_n):
        pct = round(entry.frequency * 100, 1)
        lines.append(f"  {entry.key}: {entry.change_count} change(s) ({pct}%)")
    if not heatmap.entries:
        lines.append("  (no changes detected)")
    return "\n".join(lines)
