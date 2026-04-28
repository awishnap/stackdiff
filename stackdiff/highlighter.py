"""highlighter.py — highlight changed keys between two configs with context lines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.differ import DiffResult, diff_configs


class HighlighterError(Exception):
    """Raised when highlighting fails."""


@dataclass
class HighlightedLine:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    status: str  # 'added' | 'removed' | 'changed' | 'context'

    def as_dict(self) -> Dict:
        return {
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "status": self.status,
        }


@dataclass
class HighlightResult:
    lines: List[HighlightedLine] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {"lines": [ln.as_dict() for ln in self.lines]}


def _context_keys(all_keys: List[str], changed: set, context: int) -> set:
    """Return keys within *context* positions of any changed key."""
    indices = {i for i, k in enumerate(all_keys) if k in changed}
    result: set = set()
    for idx in indices:
        for offset in range(-context, context + 1):
            j = idx + offset
            if 0 <= j < len(all_keys):
                result.add(all_keys[j])
    return result


def highlight(
    config_a: Dict,
    config_b: Dict,
    context: int = 2,
) -> HighlightResult:
    """Produce a highlighted line-by-line view of differences with context.

    Args:
        config_a: baseline config ("old").
        config_b: current config ("new").
        context: number of surrounding unchanged keys to include.

    Returns:
        HighlightResult with annotated lines.
    """
    if not isinstance(config_a, dict) or not isinstance(config_b, dict):
        raise HighlighterError("Both configs must be dicts")
    if context < 0:
        raise HighlighterError("context must be >= 0")

    result: DiffResult = diff_configs(config_a, config_b)
    all_keys: List[str] = sorted(
        set(config_a) | set(config_b),
        key=lambda k: k.lower(),
    )

    changed_keys: set = (
        set(result.added) | set(result.removed) | set(result.changed)
    )
    visible: set = _context_keys(all_keys, changed_keys, context)

    lines: List[HighlightedLine] = []
    for key in all_keys:
        if key not in visible:
            continue
        if key in result.added:
            lines.append(HighlightedLine(key, None, str(config_b[key]), "added"))
        elif key in result.removed:
            lines.append(HighlightedLine(key, str(config_a[key]), None, "removed"))
        elif key in result.changed:
            lines.append(
                HighlightedLine(key, str(config_a[key]), str(config_b[key]), "changed")
            )
        else:
            val = str(config_a.get(key, config_b.get(key)))
            lines.append(HighlightedLine(key, val, val, "context"))

    return HighlightResult(lines=lines)
