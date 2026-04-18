"""Profile management: named sets of default options for environments."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

PROFILES_DIR = Path(os.environ.get("STACKDIFF_PROFILES_DIR", Path.home() / ".stackdiff" / "profiles"))


class ProfileError(Exception):
    pass


def _profile_path(name: str, base: Path = PROFILES_DIR) -> Path:
    return base / f"{name}.json"


def save_profile(name: str, data: dict[str, Any], base: Path = PROFILES_DIR) -> Path:
    """Persist a named profile to disk."""
    base.mkdir(parents=True, exist_ok=True)
    path = _profile_path(name, base)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
    return path


def load_profile(name: str, base: Path = PROFILES_DIR) -> dict[str, Any]:
    """Load a named profile from disk."""
    path = _profile_path(name, base)
    if not path.exists():
        raise ProfileError(f"Profile '{name}' not found at {path}")
    with open(path) as fh:
        return json.load(fh)


def list_profiles(base: Path = PROFILES_DIR) -> list[str]:
    """Return names of all saved profiles."""
    if not base.exists():
        return []
    return sorted(p.stem for p in base.glob("*.json"))


def delete_profile(name: str, base: Path = PROFILES_DIR) -> None:
    """Remove a named profile."""
    path = _profile_path(name, base)
    if not path.exists():
        raise ProfileError(f"Profile '{name}' not found")
    path.unlink()
