"""Cluster multiple configs by similarity using diff-based distance."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from stackdiff.differ import diff_configs
from stackdiff.scorer import score_configs


class ClusterError(Exception):
    """Raised when clustering fails."""


@dataclass
class ClusterResult:
    """Result of grouping configs into similarity clusters."""

    clusters: Dict[str, List[str]]  # centroid label -> member labels
    centroid_scores: Dict[str, float]  # centroid label -> avg similarity to members

    def as_dict(self) -> dict:
        return {
            "clusters": self.clusters,
            "centroid_scores": self.centroid_scores,
        }

    def summary(self) -> str:
        lines = []
        for centroid, members in self.clusters.items():
            score = self.centroid_scores.get(centroid, 0.0)
            lines.append(
                f"  [{centroid}] avg_similarity={score:.2f} members={members}"
            )
        return "Clusters:\n" + "\n".join(lines)


def _pairwise_similarity(
    configs: Dict[str, dict]
) -> Dict[Tuple[str, str], float]:
    """Compute similarity score for every unique pair of configs."""
    labels = list(configs.keys())
    scores: Dict[Tuple[str, str], float] = {}
    for i, a in enumerate(labels):
        for b in labels[i + 1 :]:
            s = score_configs(configs[a], configs[b])
            scores[(a, b)] = s.score
            scores[(b, a)] = s.score
    return scores


def cluster_configs(
    configs: Dict[str, dict],
    threshold: float = 0.7,
) -> ClusterResult:
    """Group configs into clusters where members exceed *threshold* similarity.

    Uses a greedy approach: the first unseen config becomes a centroid; any
    remaining config whose similarity to that centroid meets the threshold is
    added to the cluster.

    Args:
        configs: Mapping of label -> config dict.
        threshold: Minimum similarity score (0-1) to join a cluster.

    Returns:
        ClusterResult with cluster membership and per-centroid average scores.

    Raises:
        ClusterError: If fewer than two configs are provided.
    """
    if len(configs) < 2:
        raise ClusterError("At least two configs are required for clustering.")
    if not (0.0 <= threshold <= 1.0):
        raise ClusterError("threshold must be between 0.0 and 1.0.")

    sims = _pairwise_similarity(configs)
    labels = list(configs.keys())
    assigned: set = set()
    clusters: Dict[str, List[str]] = {}
    centroid_scores: Dict[str, float] = {}

    for label in labels:
        if label in assigned:
            continue
        centroid = label
        members: List[str] = []
        for other in labels:
            if other == centroid or other in assigned:
                continue
            if sims.get((centroid, other), 0.0) >= threshold:
                members.append(other)
                assigned.add(other)
        assigned.add(centroid)
        clusters[centroid] = [centroid] + members
        if members:
            avg = sum(sims[(centroid, m)] for m in members) / len(members)
        else:
            avg = 1.0
        centroid_scores[centroid] = round(avg, 4)

    return ClusterResult(clusters=clusters, centroid_scores=centroid_scores)
