"""Baseline management: save and compare configs against a named baseline."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

from stackdiff.differ import DiffResult, diff_configs


class BaselineError(Exception):
    """Raised when a baseline operation fails."""


def _baseline_path(name: str, directory: str) -> Path:
    return Path(directory) / f"{name}.json"


def save_baseline(name: str, config: Dict[str, str], directory: str) -> Path:
    """Persist *config* as a named baseline JSON file."""
    path = _baseline_path(name, directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
    return path


def load_baseline(name: str, directory: str) -> Dict[str, str]:
    """Load a previously saved baseline by name."""
    path = _baseline_path(name, directory)
    if not path.exists():
        raise BaselineError(f"Baseline '{name}' not found in {directory}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def list_baselines(directory: str) -> List[str]:
    """Return the names of all saved baselines in *directory*."""
    d = Path(directory)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.json"))


def delete_baseline(name: str, directory: str) -> None:
    """Remove a saved baseline; raises BaselineError if it does not exist."""
    path = _baseline_path(name, directory)
    if not path.exists():
        raise BaselineError(f"Baseline '{name}' not found in {directory}")
    path.unlink()


def compare_to_baseline(
    name: str, current: Dict[str, str], directory: str
) -> DiffResult:
    """Diff *current* config against the named baseline."""
    baseline = load_baseline(name, directory)
    return diff_configs(baseline, current)
