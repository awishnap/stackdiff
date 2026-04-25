"""Pipeline helpers combining grouper with differ and reporter."""
from __future__ import annotations

from typing import Dict, List, Optional

from stackdiff.grouper import group_by_prefix, group_by_glob, GrouperError
from stackdiff.differ import diff_configs, DiffResult


def diff_groups(
    local: dict,
    remote: dict,
    prefixes: List[str],
    separator: str = "_",
    default_group: Optional[str] = "other",
) -> Dict[str, DiffResult]:
    """Split both configs by prefix then diff each group independently."""
    local_groups = group_by_prefix(local, prefixes, separator=separator, default_group=default_group)
    remote_groups = group_by_prefix(remote, prefixes, separator=separator, default_group=default_group)

    all_groups = set(local_groups) | set(remote_groups)
    results: Dict[str, DiffResult] = {}
    for group in sorted(all_groups):
        l = local_groups.get(group, {})
        r = remote_groups.get(group, {})
        results[group] = diff_configs(l, r)
    return results


def diff_groups_by_glob(
    local: dict,
    remote: dict,
    patterns: Dict[str, str],
    default_group: Optional[str] = "other",
) -> Dict[str, DiffResult]:
    """Split both configs by glob patterns then diff each group independently."""
    local_groups = group_by_glob(local, patterns, default_group=default_group)
    remote_groups = group_by_glob(remote, patterns, default_group=default_group)

    all_groups = set(local_groups) | set(remote_groups)
    results: Dict[str, DiffResult] = {}
    for group in sorted(all_groups):
        l = local_groups.get(group, {})
        r = remote_groups.get(group, {})
        results[group] = diff_configs(l, r)
    return results


def group_diff_summary(group_results: Dict[str, DiffResult]) -> Dict[str, dict]:
    """Return a summary dict for each group showing change counts."""
    summary: Dict[str, dict] = {}
    for group, result in group_results.items():
        summary[group] = {
            "added": len(result.added),
            "removed": len(result.removed),
            "changed": len(result.changed),
            "unchanged": len(result.unchanged),
            "has_diff": bool(result.added or result.removed or result.changed),
        }
    return summary
