"""Combine scoring and diffing into a single scored comparison result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any

from stackdiff.differ import diff_configs, DiffResult
from stackdiff.scorer import score_configs, SimilarityScore


class ScoredDiffError(Exception):
    """Raised when a scored diff cannot be produced."""


@dataclass
class ScoredDiffResult:
    """Holds both a structural diff and a similarity score."""

    diff: DiffResult
    score: SimilarityScore
    label_a: str = "a"
    label_b: str = "b"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "score": self.score.as_dict(),
            "diff": {
                "added": self.diff.added,
                "removed": self.diff.removed,
                "changed": self.diff.changed,
                "unchanged": self.diff.unchanged,
            },
        }

    def summary(self) -> str:
        s = self.score
        d = self.diff
        return (
            f"[{self.label_a} vs {self.label_b}] "
            f"score={s.score:.2f} grade={s.grade} "
            f"added={len(d.added)} removed={len(d.removed)} "
            f"changed={len(d.changed)} unchanged={len(d.unchanged)}"
        )


def scored_diff(
    config_a: Dict[str, Any],
    config_b: Dict[str, Any],
    label_a: str = "a",
    label_b: str = "b",
) -> ScoredDiffResult:
    """Run a diff and a similarity score together and return a combined result."""
    if not isinstance(config_a, dict) or not isinstance(config_b, dict):
        raise ScoredDiffError("Both configs must be dicts.")

    diff = diff_configs(config_a, config_b)
    score = score_configs(config_a, config_b)
    return ScoredDiffResult(diff=diff, score=score, label_a=label_a, label_b=label_b)
