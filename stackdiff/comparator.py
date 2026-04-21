"""comparator.py — named comparison profiles that bundle two config sources
and run the full diff pipeline, returning a labelled result."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Optional

from stackdiff.config_loader import load_config
from stackdiff.differ import DiffResult, diff_configs
from stackdiff.masker import mask_config


class ComparatorError(Exception):
    """Raised when a named comparison cannot be built or executed."""


@dataclass
class ComparisonSpec:
    """Describes a named pair of config sources to compare."""
    name: str
    local_path: str
    remote_path: str
    mask_sensitive: bool = True
    tags: list = field(default_factory=list)


def _spec_path(store_dir: str, name: str) -> Path:
    return Path(store_dir) / f"{name}.json"


def save_spec(spec: ComparisonSpec, store_dir: str) -> Path:
    """Persist a ComparisonSpec to *store_dir*."""
    path = _spec_path(store_dir, spec.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(spec), indent=2))
    return path


def load_spec(name: str, store_dir: str) -> ComparisonSpec:
    """Load a previously saved ComparisonSpec by name."""
    path = _spec_path(store_dir, name)
    if not path.exists():
        raise ComparatorError(f"No comparison spec found for '{name}'")
    data = json.loads(path.read_text())
    return ComparisonSpec(**data)


def list_specs(store_dir: str) -> list[str]:
    """Return names of all saved comparison specs."""
    d = Path(store_dir)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.json"))


def run_comparison(spec: ComparisonSpec) -> DiffResult:
    """Execute a comparison defined by *spec* and return a DiffResult."""
    try:
        local_cfg: Dict[str, Any] = load_config(spec.local_path)
        remote_cfg: Dict[str, Any] = load_config(spec.remote_path)
    except Exception as exc:
        raise ComparatorError(f"Failed to load configs for '{spec.name}': {exc}") from exc

    if spec.mask_sensitive:
        local_cfg = mask_config(local_cfg)
        remote_cfg = mask_config(remote_cfg)

    return diff_configs(local_cfg, remote_cfg)
