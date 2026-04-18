"""Resolve environment variable references within config values."""

import os
import re
from typing import Dict, Optional

ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)")


class ResolveError(Exception):
    """Raised when an environment variable cannot be resolved."""


def resolve_value(value: str, env: Optional[Dict[str, str]] = None) -> str:
    """Replace ${VAR} or $VAR references in value using env or os.environ."""
    if env is None:
        env = dict(os.environ)

    def replacer(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2)
        if var_name not in env:
            raise ResolveError(f"Undefined environment variable: {var_name!r}")
        return env[var_name]

    return ENV_VAR_PATTERN.sub(replacer, value)


def resolve_config(
    config: Dict[str, str],
    env: Optional[Dict[str, str]] = None,
    strict: bool = True,
) -> Dict[str, str]:
    """Return a new config dict with all env-var references resolved.

    Args:
        config: Flat string-to-string mapping (e.g. loaded .env / JSON).
        env: Override lookup table; defaults to os.environ.
        strict: If True, raise ResolveError on missing vars; otherwise leave
                the original reference in place.
    """
    resolved: Dict[str, str] = {}
    for key, raw in config.items():
        if not isinstance(raw, str):
            resolved[key] = raw
            continue
        try:
            resolved[key] = resolve_value(raw, env)
        except ResolveError:
            if strict:
                raise
            resolved[key] = raw
    return resolved
