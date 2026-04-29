"""Overlap analysis between two configs: shared keys, exclusive keys, and value agreement."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from stackdiff.differ import diff_configs


class OverlapError(Exception):
    """Raised when overlap analysis fails."""


@dataclass
class OverlapResult:
    shared_keys: list[str] = field(default_factory=list)
    only_in_a: list[str] = field(default_factory=list)
    only_in_b: list[str] = field(default_factory=list)
    agreed_keys: list[str] = field(default_factory=list)
    disagreed_keys: list[str] = field(default_factory=list)

    @property
    def overlap_ratio(self) -> float:
        """Fraction of all keys that appear in both configs."""
        total = len(self.shared_keys) + len(self.only_in_a) + len(self.only_in_b)
        if total == 0:
            return 1.0
        return len(self.shared_keys) / total

    @property
    def agreement_ratio(self) -> float:
        """Fraction of shared keys whose values agree."""
        if not self.shared_keys:
            return 1.0
        return len(self.agreed_keys) / len(self.shared_keys)

    def as_dict(self) -> dict[str, Any]:
        return {
            "shared_keys": self.shared_keys,
            "only_in_a": self.only_in_a,
            "only_in_b": self.only_in_b,
            "agreed_keys": self.agreed_keys,
            "disagreed_keys": self.disagreed_keys,
            "overlap_ratio": round(self.overlap_ratio, 4),
            "agreement_ratio": round(self.agreement_ratio, 4),
        }


def analyze_overlap(config_a: dict, config_b: dict) -> OverlapResult:
    """Return an OverlapResult describing how two configs relate."""
    if not isinstance(config_a, dict) or not isinstance(config_b, dict):
        raise OverlapError("Both configs must be dicts.")

    keys_a = set(config_a)
    keys_b = set(config_b)

    shared = sorted(keys_a & keys_b)
    only_a = sorted(keys_a - keys_b)
    only_b = sorted(keys_b - keys_a)

    result = diff_configs(config_a, config_b)
    changed = set(result.changed)

    agreed = [k for k in shared if k not in changed]
    disagreed = [k for k in shared if k in changed]

    return OverlapResult(
        shared_keys=shared,
        only_in_a=only_a,
        only_in_b=only_b,
        agreed_keys=agreed,
        disagreed_keys=disagreed,
    )


def overlap_summary(result: OverlapResult) -> str:
    """Return a human-readable one-line summary of the overlap."""
    return (
        f"shared={len(result.shared_keys)} "
        f"only_a={len(result.only_in_a)} "
        f"only_b={len(result.only_in_b)} "
        f"agreed={len(result.agreed_keys)} "
        f"disagreed={len(result.disagreed_keys)} "
        f"overlap={result.overlap_ratio:.0%} "
        f"agreement={result.agreement_ratio:.0%}"
    )
