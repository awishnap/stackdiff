"""Build a dependency/relationship graph from multiple config diffs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from stackdiff.differ import diff_configs


class GraphError(Exception):
    """Raised when graph construction fails."""


@dataclass
class GraphEdge:
    source: str
    target: str
    shared_keys: List[str]
    diff_count: int

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "shared_keys": self.shared_keys,
            "diff_count": self.diff_count,
        }


@dataclass
class DiffGraph:
    nodes: List[str]
    edges: List[GraphEdge]

    def as_dict(self) -> dict:
        return {
            "nodes": self.nodes,
            "edges": [e.as_dict() for e in self.edges],
        }

    def summary(self) -> str:
        total_diffs = sum(e.diff_count for e in self.edges)
        return (
            f"{len(self.nodes)} nodes, {len(self.edges)} edges, "
            f"{total_diffs} total diffs"
        )

    def most_connected(self) -> str:
        if not self.edges:
            return ""
        counts: Dict[str, int] = {}
        for e in self.edges:
            counts[e.source] = counts.get(e.source, 0) + 1
            counts[e.target] = counts.get(e.target, 0) + 1
        return max(counts, key=lambda k: counts[k])


def build_graph(
    configs: Dict[str, dict],
    *,
    min_shared_keys: int = 1,
) -> DiffGraph:
    """Build a graph where each pair of configs sharing keys forms an edge."""
    if not isinstance(configs, dict) or len(configs) < 2:
        raise GraphError("At least two named configs are required.")

    labels = list(configs.keys())
    nodes = labels[:]
    edges: List[GraphEdge] = []

    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a_label, b_label = labels[i], labels[j]
            a_cfg, b_cfg = configs[a_label], configs[b_label]
            shared: List[str] = sorted(
                set(a_cfg.keys()) & set(b_cfg.keys())
            )
            if len(shared) < min_shared_keys:
                continue
            result = diff_configs(a_cfg, b_cfg)
            diff_count = (
                len(result.added)
                + len(result.removed)
                + len(result.changed)
            )
            edges.append(
                GraphEdge(
                    source=a_label,
                    target=b_label,
                    shared_keys=shared,
                    diff_count=diff_count,
                )
            )

    return DiffGraph(nodes=nodes, edges=edges)
