"""differ_pivot: pivot a diff result into a key-centric view.

Instead of separate added/removed/changed/unchanged buckets, produce a
flat list of records – one per key – each carrying its status and both
the 'before' and 'after' values.  Useful for tabular exports and
spreadsheet-style reviews.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from stackdiff.differ import DiffResult


class PivotError(Exception):
    """Raised when pivoting fails."""


@dataclass
class PivotRow:
    key: str
    status: str          # 'added' | 'removed' | 'changed' | 'unchanged'
    before: Optional[Any] = None
    after: Optional[Any] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "status": self.status,
            "before": self.before,
            "after": self.after,
        }


@dataclass
class PivotTable:
    rows: List[PivotRow] = field(default_factory=list)

    def as_dict(self) -> List[Dict[str, Any]]:
        return [r.as_dict() for r in self.rows]

    def filter_status(self, *statuses: str) -> "PivotTable":
        return PivotTable([r for r in self.rows if r.status in statuses])

    def keys_with_status(self, status: str) -> List[str]:
        return [r.key for r in self.rows if r.status == status]


def pivot_diff(result: DiffResult, *, include_unchanged: bool = False) -> PivotTable:
    """Convert a DiffResult into a PivotTable.

    Parameters
    ----------
    result:
        A :class:`~stackdiff.differ.DiffResult` produced by ``diff_configs``.
    include_unchanged:
        When *True*, unchanged keys are included in the table.  Defaults
        to *False* to keep the output concise.
    """
    if not isinstance(result, DiffResult):
        raise PivotError(f"Expected DiffResult, got {type(result).__name__}")

    rows: List[PivotRow] = []

    for key, after_val in sorted(result.added.items()):
        rows.append(PivotRow(key=key, status="added", before=None, after=after_val))

    for key, before_val in sorted(result.removed.items()):
        rows.append(PivotRow(key=key, status="removed", before=before_val, after=None))

    for key, (before_val, after_val) in sorted(result.changed.items()):
        rows.append(PivotRow(key=key, status="changed", before=before_val, after=after_val))

    if include_unchanged:
        for key, val in sorted(result.unchanged.items()):
            rows.append(PivotRow(key=key, status="unchanged", before=val, after=val))

    return PivotTable(rows)
