"""Load and parse environment config files (YAML/JSON/dotenv)."""

import json
import os
from pathlib import Path
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ConfigLoadError(Exception):
    pass


def load_dotenv_file(path: Path) -> dict[str, str]:
    config = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip().strip('"').strip("'")
    return config


def load_json_file(path: Path) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def load_yaml_file(path: Path) -> dict[str, Any]:
    if not HAS_YAML:
        raise ConfigLoadError("PyYAML is not installed. Run: pip install pyyaml")
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_config(path: str | os.PathLike) -> dict[str, Any]:
    """Auto-detect format and load config from file."""
    p = Path(path)
    if not p.exists():
        raise ConfigLoadError(f"Config file not found: {p}")

    suffix = p.suffix.lower()
    name = p.name.lower()

    if suffix in (".yaml", ".yml"):
        return load_yaml_file(p)
    elif suffix == ".json":
        return load_json_file(p)
    elif suffix == ".env" or name.startswith(".env"):
        return load_dotenv_file(p)
    else:
        raise ConfigLoadError(f"Unsupported config format: {p.suffix!r}")
