"""compressor.py — strip unchanged keys from a diff to produce a compact view."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List

from stackdiff.differ import DiffResult


class CompressorError(Exception):
    """Raised when compression cannot be performed."""


@dataclass
class CompressedDiff:
    """A diff with unchanged keys omitted (or summarised)."""

    added: Dict[str, Any] = field(default_factory=dict)
    removed: Dict[str, Any] = field(default_factory=dict)
    changed: Dict[str, Any] = field(default_factory=dict)
    unchanged_count: int = 0
    unchanged_keys: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "unchanged_count": self.unchanged_count,
            "unchanged_keys": self.unchanged_keys,
        }


def compress(result: DiffResult, *, keep_unchanged_keys: bool = False) -> CompressedDiff:
    """Return a *CompressedDiff* that drops unchanged entries.

    Parameters
    ----------
    result:
        A :class:`~stackdiff.differ.DiffResult` produced by ``diff_configs``.
    keep_unchanged_keys:
        When *True* the list of unchanged key names is preserved in
        ``CompressedDiff.unchanged_keys``; otherwise it is left empty to
        save memory.
    """
    if not isinstance(result, DiffResult):
        raise CompressorError("compress() requires a DiffResult instance")

    unchanged_keys: List[str] = list(result.unchanged.keys()) if keep_unchanged_keys else []

    return CompressedDiff(
        added=dict(result.added),
        removed=dict(result.removed),
        changed=dict(result.changed),
        unchanged_count=len(result.unchanged),
        unchanged_keys=unchanged_keys,
    )


def compression_ratio(result: DiffResult) -> float:
    """Return the fraction of keys that are unchanged (0.0 – 1.0)."""
    if not isinstance(result, DiffResult):
        raise CompressorError("compression_ratio() requires a DiffResult instance")

    total = (
        len(result.added)
        + len(result.removed)
        + len(result.changed)
        + len(result.unchanged)
    )
    if total == 0:
        return 1.0
    return len(result.unchanged) / total
