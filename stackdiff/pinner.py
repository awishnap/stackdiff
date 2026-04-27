"""Pin a config key to an expected value and detect deviations."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any


class PinnerError(Exception):
    """Raised when a pinning operation fails."""


@dataclass
class PinViolation:
    key: str
    pinned: Any
    actual: Any

    def as_dict(self) -> dict:
        return {"key": self.key, "pinned": self.pinned, "actual": self.actual}


@dataclass
class PinResult:
    violations: list[PinViolation] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations and not self.missing

    def summary(self) -> str:
        if self.ok:
            return "All pinned keys match."
        parts = []
        if self.violations:
            parts.append(f"{len(self.violations)} violation(s)")
        if self.missing:
            parts.append(f"{len(self.missing)} missing key(s)")
        return "; ".join(parts) + "."


def _pins_path(store_dir: str, name: str) -> str:
    return os.path.join(store_dir, f"{name}.pins.json")


def save_pins(store_dir: str, name: str, pins: dict[str, Any]) -> str:
    if not isinstance(pins, dict):
        raise PinnerError("pins must be a dict")
    os.makedirs(store_dir, exist_ok=True)
    path = _pins_path(store_dir, name)
    with open(path, "w") as fh:
        json.dump(pins, fh, indent=2)
    return path


def load_pins(store_dir: str, name: str) -> dict[str, Any]:
    path = _pins_path(store_dir, name)
    if not os.path.exists(path):
        raise PinnerError(f"No pins found for '{name}'")
    with open(path) as fh:
        return json.load(fh)


def list_pins(store_dir: str) -> list[str]:
    if not os.path.isdir(store_dir):
        return []
    return [
        f[: -len(".pins.json")]
        for f in sorted(os.listdir(store_dir))
        if f.endswith(".pins.json")
    ]


def check_pins(pins: dict[str, Any], config: dict[str, Any]) -> PinResult:
    """Compare pinned key/value expectations against a live config."""
    if not isinstance(config, dict):
        raise PinnerError("config must be a dict")
    result = PinResult()
    for key, expected in pins.items():
        if key not in config:
            result.missing.append(key)
        elif config[key] != expected:
            result.violations.append(PinViolation(key=key, pinned=expected, actual=config[key]))
    return result
