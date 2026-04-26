"""scorer.py — compute a numeric similarity score between two configs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from stackdiff.differ import diff_configs, DiffResult


class ScorerError(Exception):
    """Raised when scoring cannot be completed."""


@dataclass
class SimilarityScore:
    total_keys: int
    matched_keys: int
    score: float          # 0.0 – 1.0
    grade: str            # A / B / C / D / F

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total_keys": self.total_keys,
            "matched_keys": self.matched_keys,
            "score": self.score,
            "grade": self.grade,
        }


def _grade(score: float) -> str:
    if score >= 0.90:
        return "A"
    if score >= 0.75:
        return "B"
    if score >= 0.60:
        return "C"
    if score >= 0.40:
        return "D"
    return "F"


def score_configs(
    local: Dict[str, Any],
    remote: Dict[str, Any],
) -> SimilarityScore:
    """Return a SimilarityScore comparing *local* against *remote*.

    A key counts as "matched" when it exists in both configs **and** has the
    same value.  Keys that are only added, only removed, or changed all count
    against the score.
    """
    if not isinstance(local, dict) or not isinstance(remote, dict):
        raise ScorerError("Both configs must be dicts")

    result: DiffResult = diff_configs(local, remote)

    total = (
        len(result.added)
        + len(result.removed)
        + len(result.changed)
        + len(result.unchanged)
    )

    if total == 0:
        return SimilarityScore(
            total_keys=0, matched_keys=0, score=1.0, grade="A"
        )

    matched = len(result.unchanged)
    raw = matched / total
    return SimilarityScore(
        total_keys=total,
        matched_keys=matched,
        score=round(raw, 4),
        grade=_grade(raw),
    )
