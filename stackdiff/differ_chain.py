"""differ_chain: run a sequence of diffs across an ordered list of configs.

Useful for tracking how a config evolves across multiple environments
(e.g. dev -> staging -> prod).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from stackdiff.differ import DiffResult, diff_configs


class ChainError(Exception):
    """Raised when the diff chain cannot be built."""


@dataclass
class ChainLink:
    """A single step in the diff chain."""
    left_label: str
    right_label: str
    result: DiffResult

    def as_dict(self) -> dict:
        return {
            "left": self.left_label,
            "right": self.right_label,
            "added": self.result.added,
            "removed": self.result.removed,
            "changed": self.result.changed,
            "unchanged": list(self.result.unchanged),
        }


@dataclass
class DiffChain:
    """Ordered collection of ChainLinks."""
    links: List[ChainLink] = field(default_factory=list)

    def as_dict(self) -> List[dict]:
        return [link.as_dict() for link in self.links]

    def total_changes(self) -> int:
        total = 0
        for link in self.links:
            total += (
                len(link.result.added)
                + len(link.result.removed)
                + len(link.result.changed)
            )
        return total


def build_chain(
    configs: Sequence[Dict[str, object]],
    labels: Sequence[str] | None = None,
) -> DiffChain:
    """Build a DiffChain by diffing each consecutive pair.

    Args:
        configs: Ordered sequence of config dicts (at least 2).
        labels:  Optional display names; defaults to "config_0", "config_1", …

    Returns:
        DiffChain with len(configs) - 1 links.

    Raises:
        ChainError: If fewer than 2 configs are provided or labels length mismatch.
    """
    if len(configs) < 2:
        raise ChainError("At least two configs are required to build a chain.")

    if labels is None:
        labels = [f"config_{i}" for i in range(len(configs))]

    if len(labels) != len(configs):
        raise ChainError(
            f"labels length ({len(labels)}) must match configs length ({len(configs)})."
        )

    chain = DiffChain()
    for i in range(len(configs) - 1):
        result = diff_configs(configs[i], configs[i + 1])
        chain.links.append(ChainLink(
            left_label=labels[i],
            right_label=labels[i + 1],
            result=result,
        ))
    return chain


def chain_summary(chain: DiffChain) -> str:
    """Return a human-readable summary of all chain links."""
    lines: List[str] = []
    for link in chain.links:
        r = link.result
        lines.append(
            f"{link.left_label} -> {link.right_label}: "
            f"+{len(r.added)} -{len(r.removed)} ~{len(r.changed)} ={len(r.unchanged)}"
        )
    if not lines:
        return "(empty chain)"
    return "\n".join(lines)
