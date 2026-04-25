"""High-level helpers that combine loading, diffing, and patching."""

from __future__ import annotations

from typing import Any

from stackdiff.config_loader import load_config
from stackdiff.differ import DiffResult, diff_configs
from stackdiff.patcher import PatchError, apply_patch


def load_and_patch(
    base_path: str,
    target_path: str,
    *,
    strategy: str = "forward",
) -> dict[str, Any]:
    """Load two config files, compute their diff, and return the patched result.

    Parameters
    ----------
    base_path:
        Path to the base config file.
    target_path:
        Path to the target config file.
    strategy:
        Patch direction – ``"forward"`` (base → target) or
        ``"reverse"`` (target → base).

    Returns
    -------
    dict
        The patched config dictionary.

    Raises
    ------
    ConfigLoadError
        If either config file cannot be loaded.
    PatchError
        If the patch cannot be applied with the given strategy.
    """
    base = load_config(base_path)
    target = load_config(target_path)
    diff = diff_configs(base, target)
    return apply_patch(base, diff, strategy=strategy)


def patch_and_diff(
    base_path: str,
    target_path: str,
    *,
    strategy: str = "forward",
) -> tuple[dict[str, Any], DiffResult]:
    """Return both the patched config *and* the diff used to produce it.

    Useful when callers need the diff for reporting as well as the patched
    output for further processing.
    """
    base = load_config(base_path)
    target = load_config(target_path)
    diff = diff_configs(base, target)
    patched = apply_patch(base, diff, strategy=strategy)
    return patched, diff
