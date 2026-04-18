"""Compare two config dictionaries and report differences."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiffResult:
    added: dict[str, Any] = field(default_factory=dict)
    removed: dict[str, Any] = field(default_factory=dict)
    changed: dict[str, tuple[Any, Any]] = field(default_factory=dict)
    unchanged: dict[str, Any] = field(default_factory=dict)

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = []
        for key, value in sorted(self.added.items()):
            lines.append(f"+ {key}={value}")
        for key, value in sorted(self.removed.items()):
            lines.append(f"- {key}={value}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "No differences found."


def diff_configs(
    base: dict[str, Any],
    target: dict[str, Any],
    ignore_keys: list[str] | None = None,
) -> DiffResult:
    """Compare base config against target config.

    Args:
        base: The reference config (e.g. local / staging).
        target: The config to compare against (e.g. deployed / prod).
        ignore_keys: Keys to exclude from comparison.

    Returns:
        DiffResult with categorised differences.
    """
    ignore = set(ignore_keys or [])
    base_keys = {k for k in base if k not in ignore}
    target_keys = {k for k in target if k not in ignore}

    result = DiffResult()

    for key in target_keys - base_keys:
        result.added[key] = target[key]

    for key in base_keys - target_keys:
        result.removed[key] = base[key]

    for key in base_keys & target_keys:
        if base[key] != target[key]:
            result.changed[key] = (base[key], target[key])
        else:
            result.unchanged[key] = base[key]

    return result
