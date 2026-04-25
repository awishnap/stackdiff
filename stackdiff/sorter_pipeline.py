"""Pipeline integration helpers for the sorter module."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from stackdiff.sorter import apply_sort, sort_keys_explicit, SorterError


def sorted_diff_input(
    config: Dict[str, Any],
    strategy: str = "alpha",
    reverse: bool = False,
    order: Optional[List[str]] = None,
    drop_missing: bool = False,
) -> Dict[str, Any]:
    """Return *config* with keys sorted, ready for deterministic diffing.

    When *order* is provided the explicit ordering is applied instead of
    the named *strategy*.

    Raises :class:`SorterError` on invalid input.
    """
    if order:
        return sort_keys_explicit(config, order=order, drop_missing=drop_missing)
    return apply_sort(config, strategy=strategy, reverse=reverse)


def sort_both(
    local: Dict[str, Any],
    remote: Dict[str, Any],
    strategy: str = "alpha",
    reverse: bool = False,
    order: Optional[List[str]] = None,
    drop_missing: bool = False,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Sort *local* and *remote* configs with identical settings.

    Returns a ``(sorted_local, sorted_remote)`` tuple so that downstream
    diff operations produce stable, human-readable output.
    """
    kwargs: Dict[str, Any] = {
        "strategy": strategy,
        "reverse": reverse,
        "order": order,
        "drop_missing": drop_missing,
    }
    return (
        sorted_diff_input(local, **kwargs),
        sorted_diff_input(remote, **kwargs),
    )


def normalize_key_order(configs: List[Dict[str, Any]], strategy: str = "alpha") -> List[Dict[str, Any]]:
    """Apply *strategy* to every config in *configs* and return the sorted list.

    Useful when merging multiple environment configs before comparison.
    """
    if not configs:
        raise SorterError("configs list must not be empty")
    return [apply_sort(cfg, strategy=strategy) for cfg in configs]
