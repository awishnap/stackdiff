"""Apply a diff result as a patch to a config dict, producing a new config."""

from __future__ import annotations

from typing import Any

from stackdiff.differ import DiffResult


class PatchError(Exception):
    """Raised when a patch cannot be applied."""


def apply_patch(
    base: dict[str, Any],
    diff: DiffResult,
    *,
    strategy: str = "forward",
) -> dict[str, Any]:
    """Return a new config produced by applying *diff* to *base*.

    Parameters
    ----------
    base:
        The config dict to patch.
    diff:
        A :class:`~stackdiff.differ.DiffResult` describing the changes.
    strategy:
        ``"forward"`` applies the diff (base → changed).
        ``"reverse"`` reverts the diff (changed → base).
    """
    if strategy not in ("forward", "reverse"):
        raise PatchError(f"Unknown patch strategy: {strategy!r}")

    result = dict(base)

    if strategy == "forward":
        for key in diff.removed:
            result.pop(key, None)
        for key, value in diff.added.items():
            result[key] = value
        for key, (_, new_val) in diff.changed.items():
            result[key] = new_val
    else:  # reverse
        for key, value in diff.added.items():
            result.pop(key, None)
        for key in diff.removed:
            if key not in base:
                raise PatchError(
                    f"Cannot reverse-patch: key {key!r} missing from base config"
                )
            result[key] = base[key]
        for key, (old_val, _) in diff.changed.items():
            result[key] = old_val

    return result


def patch_summary(diff: DiffResult, strategy: str = "forward") -> str:
    """Return a one-line human-readable summary of what the patch will do."""
    direction = "applying" if strategy == "forward" else "reverting"
    parts = []
    if diff.added:
        parts.append(f"+{len(diff.added)} added")
    if diff.removed:
        parts.append(f"-{len(diff.removed)} removed")
    if diff.changed:
        parts.append(f"~{len(diff.changed)} changed")
    changes = ", ".join(parts) if parts else "no changes"
    return f"Patch ({direction}): {changes}"
