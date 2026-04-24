"""redactor.py – remove or replace keys from a config dict by pattern."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, Iterable, List, Optional


class RedactorError(Exception):
    """Raised when redaction configuration is invalid."""


def _compile_patterns(patterns: Iterable[str]) -> List[re.Pattern]:
    """Convert glob patterns to compiled regex objects."""
    compiled = []
    for p in patterns:
        if not p:
            raise RedactorError(f"Empty pattern is not allowed: {p!r}")
        compiled.append(re.compile(fnmatch.translate(p), re.IGNORECASE))
    return compiled


def redact_keys(
    config: Dict[str, str],
    patterns: Iterable[str],
    placeholder: str = "<REDACTED>",
) -> Dict[str, str]:
    """Return a copy of *config* with matching keys replaced by *placeholder*.

    Args:
        config: Source key/value mapping.
        patterns: Glob patterns matched case-insensitively against keys.
        placeholder: Value written for every matched key.

    Returns:
        New dict; original is not mutated.
    """
    compiled = _compile_patterns(patterns)
    result: Dict[str, str] = {}
    for key, value in config.items():
        if any(rx.match(key) for rx in compiled):
            result[key] = placeholder
        else:
            result[key] = value
    return result


def drop_keys(
    config: Dict[str, str],
    patterns: Iterable[str],
) -> Dict[str, str]:
    """Return a copy of *config* with matching keys entirely removed.

    Args:
        config: Source key/value mapping.
        patterns: Glob patterns matched case-insensitively against keys.

    Returns:
        New dict without matched keys; original is not mutated.
    """
    compiled = _compile_patterns(patterns)
    return {
        key: value
        for key, value in config.items()
        if not any(rx.match(key) for rx in compiled)
    }


def apply_redaction(
    config: Dict[str, str],
    patterns: Iterable[str],
    placeholder: Optional[str] = "<REDACTED>",
) -> Dict[str, str]:
    """High-level helper: drop keys when *placeholder* is None, else replace."""
    if placeholder is None:
        return drop_keys(config, patterns)
    return redact_keys(config, patterns, placeholder)
