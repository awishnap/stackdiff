"""Rank configs by how much they differ from a reference config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from stackdiff.differ import diff_configs


class RankError(Exception):
    """Raised when ranking fails."""


@dataclass
class RankEntry:
    label: str
    added: int
    removed: int
    changed: int
    total_diff: int
    rank: int = 0

    def as_dict(self) -> dict:
        return {
            "rank": self.rank,
            "label": self.label,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "total_diff": self.total_diff,
        }


@dataclass
class RankResult:
    reference_label: str
    entries: List[RankEntry] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "reference_label": self.reference_label,
            "entries": [e.as_dict() for e in self.entries],
        }


def rank_configs(
    reference: dict,
    candidates: Dict[str, dict],
    *,
    reference_label: str = "reference",
) -> RankResult:
    """Rank each candidate config by total diff count against *reference*.

    Args:
        reference: The baseline config to compare against.
        candidates: Mapping of label -> config dict.
        reference_label: Display name for the reference config.

    Returns:
        A :class:`RankResult` with entries sorted from most to least divergent.

    Raises:
        RankError: If *candidates* is empty or any value is not a dict.
    """
    if not candidates:
        raise RankError("candidates must not be empty")

    entries: List[RankEntry] = []
    for label, cfg in candidates.items():
        if not isinstance(cfg, dict):
            raise RankError(f"candidate '{label}' is not a dict")
        result = diff_configs(reference, cfg)
        total = len(result.added) + len(result.removed) + len(result.changed)
        entries.append(
            RankEntry(
                label=label,
                added=len(result.added),
                removed=len(result.removed),
                changed=len(result.changed),
                total_diff=total,
            )
        )

    entries.sort(key=lambda e: e.total_diff, reverse=True)
    for i, entry in enumerate(entries, start=1):
        entry.rank = i

    return RankResult(reference_label=reference_label, entries=entries)
