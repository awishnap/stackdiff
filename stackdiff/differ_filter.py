"""Combine differ and filter to produce filtered diff results."""

from typing import List, Optional

from stackdiff.differ import DiffResult, diff_configs
from stackdiff.filter import FilterError, apply_filters


class FilteredDiffError(Exception):
    """Raised when a filtered diff operation fails."""


def filtered_diff(
    local: dict,
    remote: dict,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> DiffResult:
    """Diff two configs after applying include/exclude key filters.

    Parameters
    ----------
    local:
        Local configuration dictionary.
    remote:
        Remote/deployed configuration dictionary.
    include:
        Optional list of glob patterns; only matching keys are kept.
    exclude:
        Optional list of glob patterns; matching keys are removed.

    Returns
    -------
    DiffResult
        Diff result computed on the filtered configs.

    Raises
    ------
    FilteredDiffError
        If the filter step fails (e.g. empty pattern list).
    """
    try:
        filtered_local = apply_filters(local, include=include, exclude=exclude)
        filtered_remote = apply_filters(remote, include=include, exclude=exclude)
    except FilterError as exc:
        raise FilteredDiffError(str(exc)) from exc

    return diff_configs(filtered_local, filtered_remote)


def filtered_diff_summary(
    local: dict,
    remote: dict,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> str:
    """Return a human-readable summary of the filtered diff."""
    result = filtered_diff(local, remote, include=include, exclude=exclude)
    parts = []
    if result.added:
        parts.append(f"added={len(result.added)}")
    if result.removed:
        parts.append(f"removed={len(result.removed)}")
    if result.changed:
        parts.append(f"changed={len(result.changed)}")
    if not parts:
        return "No differences found."
    return "Differences: " + ", ".join(parts) + "."
