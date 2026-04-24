"""summarizer.py – produce human-readable summary statistics from a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from stackdiff.differ import DiffResult


class SummarizerError(Exception):
    """Raised when summarization fails."""


@dataclass
class DiffSummary:
    total_keys: int
    added: int
    removed: int
    changed: int
    unchanged: int
    change_rate: float  # fraction of total_keys that changed (added+removed+changed)
    top_changed: List[str]  # up to N keys with changes, sorted alphabetically

    def as_dict(self) -> Dict[str, object]:
        return {
            "total_keys": self.total_keys,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "unchanged": self.unchanged,
            "change_rate": round(self.change_rate, 4),
            "top_changed": self.top_changed,
        }


def summarize(result: DiffResult, top_n: int = 10) -> DiffSummary:
    """Build a :class:`DiffSummary` from a :class:`DiffResult`.

    Parameters
    ----------
    result:
        The diff result to summarise.
    top_n:
        Maximum number of changed key names to include in *top_changed*.

    Raises
    ------
    SummarizerError
        If *result* is not a valid :class:`DiffResult` instance.
    """
    if not isinstance(result, DiffResult):
        raise SummarizerError(f"Expected DiffResult, got {type(result).__name__}")
    if top_n < 0:
        raise SummarizerError("top_n must be >= 0")

    added = len(result.added)
    removed = len(result.removed)
    changed = len(result.changed)
    unchanged = len(result.unchanged)
    total = added + removed + changed + unchanged

    change_rate = (added + removed + changed) / total if total > 0 else 0.0

    all_changed_keys = sorted(
        list(result.added.keys())
        + list(result.removed.keys())
        + list(result.changed.keys())
    )
    top_changed = all_changed_keys[:top_n]

    return DiffSummary(
        total_keys=total,
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
        change_rate=change_rate,
        top_changed=top_changed,
    )


def format_summary(summary: DiffSummary) -> str:
    """Return a compact, human-readable string for *summary*."""
    lines = [
        f"Total keys : {summary.total_keys}",
        f"Added      : {summary.added}",
        f"Removed    : {summary.removed}",
        f"Changed    : {summary.changed}",
        f"Unchanged  : {summary.unchanged}",
        f"Change rate: {summary.change_rate:.1%}",
    ]
    if summary.top_changed:
        lines.append("Top changed: " + ", ".join(summary.top_changed))
    return "\n".join(lines)
