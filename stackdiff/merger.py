"""merger.py — merge multiple config dicts with precedence rules."""

from __future__ import annotations

from typing import Any


class MergeError(Exception):
    """Raised when configs cannot be merged."""


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge *override* into *base*, returning a new dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def merge_configs(
    *configs: dict[str, Any],
    strategy: str = "last_wins",
) -> dict[str, Any]:
    """Merge two or more config dicts.

    Parameters
    ----------
    *configs:
        One or more config dicts.  Later entries take precedence.
    strategy:
        ``"last_wins"`` (default) — later values overwrite earlier ones.
        ``"first_wins"`` — earlier values are preserved.
        ``"deep"`` — recursively merge nested dicts (last wins for scalars).

    Returns
    -------
    dict
        The merged configuration.

    Raises
    ------
    MergeError
        If fewer than one config is supplied or an unknown strategy is given.
    """
    if not configs:
        raise MergeError("merge_configs requires at least one config dict")

    valid_strategies = {"last_wins", "first_wins", "deep"}
    if strategy not in valid_strategies:
        raise MergeError(
            f"Unknown merge strategy {strategy!r}. Choose from {valid_strategies}."
        )

    if strategy == "first_wins":
        # Reverse so that the first dict ends up winning in a simple update pass
        ordered = list(reversed(configs))
    else:
        ordered = list(configs)

    result: dict[str, Any] = {}
    for cfg in ordered:
        if not isinstance(cfg, dict):
            raise MergeError(f"Expected dict, got {type(cfg).__name__}")
        if strategy == "deep":
            result = _deep_merge(result, cfg)
        else:
            result.update(cfg)

    return result
