"""Compute statistical metrics over a collection of DiffResults."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from stackdiff.differ import DiffResult


class StatsError(Exception):
    """Raised when stats computation fails."""


@dataclass
class DiffStats:
    total_keys: int = 0
    added_count: int = 0
    removed_count: int = 0
    changed_count: int = 0
    unchanged_count: int = 0
    change_rate: float = 0.0
    most_volatile_keys: List[str] = field(default_factory=list)


def _key_change_frequency(results: List[DiffResult]) -> Dict[str, int]:
    """Count how many results each key appears as changed/added/removed."""
    freq: Dict[str, int] = {}
    for r in results:
        for k in list(r.added) + list(r.removed) + list(r.changed):
            freq[k] = freq.get(k, 0) + 1
    return freq


def compute_stats(results: List[DiffResult], top_n: int = 5) -> DiffStats:
    """Aggregate diff statistics across multiple DiffResult objects.

    Args:
        results: List of DiffResult instances to analyse.
        top_n: Number of most-volatile keys to include.

    Returns:
        A DiffStats dataclass with aggregated metrics.

    Raises:
        StatsError: If *results* is empty or *top_n* is not positive.
    """
    if not results:
        raise StatsError("results list must not be empty")
    if top_n < 1:
        raise StatsError("top_n must be a positive integer")

    added = sum(len(r.added) for r in results)
    removed = sum(len(r.removed) for r in results)
    changed = sum(len(r.changed) for r in results)
    unchanged = sum(len(r.unchanged) for r in results)
    total = added + removed + changed + unchanged

    change_rate = (added + removed + changed) / total if total > 0 else 0.0

    freq = _key_change_frequency(results)
    volatile = sorted(freq, key=lambda k: freq[k], reverse=True)[:top_n]

    return DiffStats(
        total_keys=total,
        added_count=added,
        removed_count=removed,
        changed_count=changed,
        unchanged_count=unchanged,
        change_rate=round(change_rate, 4),
        most_volatile_keys=volatile,
    )
