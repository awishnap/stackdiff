"""scoper_pipeline.py — combine scoping with diffing for namespace-aware comparisons."""
from __future__ import annotations

from typing import Dict, List, Optional

from stackdiff.differ import DiffResult, diff_configs
from stackdiff.scoper import ScopeError, list_scopes, scope_config


def diff_scope(
    config_a: dict,
    config_b: dict,
    scope: str,
    *,
    separator: str = ".",
    strip_prefix: bool = True,
) -> DiffResult:
    """Diff two configs restricted to a single *scope*.

    Both configs are filtered to the given scope before diffing so that
    unrelated keys are excluded from the result.
    """
    scoped_a = scope_config(config_a, scope, separator=separator, strip_prefix=strip_prefix)
    scoped_b = scope_config(config_b, scope, separator=separator, strip_prefix=strip_prefix)
    return diff_configs(scoped_a, scoped_b)


def diff_all_scopes(
    config_a: dict,
    config_b: dict,
    *,
    separator: str = ".",
    strip_prefix: bool = True,
) -> Dict[str, DiffResult]:
    """Diff every scope found in the union of both configs.

    Returns a mapping of scope name -> :class:`DiffResult`.
    """
    scopes_a = set(list_scopes(config_a, separator=separator))
    scopes_b = set(list_scopes(config_b, separator=separator))
    all_scopes = sorted(scopes_a | scopes_b)

    results: Dict[str, DiffResult] = {}
    for scope in all_scopes:
        results[scope] = diff_scope(
            config_a,
            config_b,
            scope,
            separator=separator,
            strip_prefix=strip_prefix,
        )
    return results


def scoped_diff_summary(results: Dict[str, DiffResult]) -> str:
    """Return a compact multi-line summary of per-scope diff results."""
    if not results:
        return "No scopes to compare."
    lines: List[str] = []
    for scope, result in sorted(results.items()):
        total = (
            len(result.added)
            + len(result.removed)
            + len(result.changed)
        )
        status = "clean" if total == 0 else f"{total} change(s)"
        lines.append(f"  {scope}: {status}")
    return "Scope diff summary:\n" + "\n".join(lines)
