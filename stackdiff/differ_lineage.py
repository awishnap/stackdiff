"""differ_lineage.py — trace the lineage of a key's value across a sequence of configs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


class LineageError(Exception):
    """Raised when lineage tracing fails."""


@dataclass
class LineageEntry:
    label: str
    value: Optional[Any]
    changed: bool  # True if value differs from the previous entry

    def as_dict(self) -> Dict[str, Any]:
        return {"label": self.label, "value": self.value, "changed": self.changed}


@dataclass
class KeyLineage:
    key: str
    entries: List[LineageEntry] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {"key": self.key, "entries": [e.as_dict() for e in self.entries]}

    @property
    def total_changes(self) -> int:
        return sum(1 for e in self.entries if e.changed)

    @property
    def first_seen(self) -> Optional[str]:
        for e in self.entries:
            if e.value is not None:
                return e.label
        return None

    @property
    def last_value(self) -> Optional[Any]:
        for e in reversed(self.entries):
            if e.value is not None:
                return e.value
        return None


def trace_key(
    key: str,
    configs: Sequence[Dict[str, Any]],
    labels: Optional[Sequence[str]] = None,
) -> KeyLineage:
    """Trace the value of *key* across an ordered sequence of configs."""
    if not configs:
        raise LineageError("configs must be a non-empty sequence")
    if labels is not None and len(labels) != len(configs):
        raise LineageError("labels length must match configs length")

    resolved_labels = list(labels) if labels else [str(i) for i in range(len(configs))]

    entries: List[LineageEntry] = []
    prev: Optional[Any] = object()  # sentinel — distinct from any real value

    for label, cfg in zip(resolved_labels, configs):
        if not isinstance(cfg, dict):
            raise LineageError(f"config for label '{label}' is not a dict")
        value = cfg.get(key)  # None when absent
        changed = value != prev if prev is not object() else False
        prev = value
        entries.append(LineageEntry(label=label, value=value, changed=changed))

    return KeyLineage(key=key, entries=entries)


def trace_all_keys(
    configs: Sequence[Dict[str, Any]],
    labels: Optional[Sequence[str]] = None,
) -> List[KeyLineage]:
    """Return a KeyLineage for every key that appears in any config."""
    if not configs:
        raise LineageError("configs must be a non-empty sequence")
    all_keys: List[str] = []
    seen: set = set()
    for cfg in configs:
        if not isinstance(cfg, dict):
            raise LineageError("all configs must be dicts")
        for k in cfg:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)
    return [trace_key(k, configs, labels) for k in all_keys]
