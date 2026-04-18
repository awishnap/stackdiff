"""Mask sensitive config values before display or diffing."""

import re
from typing import Dict, List, Optional

DEFAULT_PATTERNS: List[str] = [
    r"(?i)password",
    r"(?i)secret",
    r"(?i)token",
    r"(?i)api[_-]?key",
    r"(?i)private[_-]?key",
    r"(?i)auth",
]

MASK_PLACEHOLDER = "***"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def is_sensitive(key: str, patterns: Optional[List[re.Pattern]] = None) -> bool:
    """Return True if the key name matches any sensitive pattern."""
    if patterns is None:
        patterns = _compile_patterns(DEFAULT_PATTERNS)
    return any(p.search(key) for p in patterns)


def mask_config(
    config: Dict[str, str],
    extra_patterns: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a copy of config with sensitive values replaced by MASK_PLACEHOLDER.

    Args:
        config: Flat config mapping.
        extra_patterns: Additional regex patterns to treat as sensitive.
    """
    patterns = list(DEFAULT_PATTERNS)
    if extra_patterns:
        patterns.extend(extra_patterns)
    compiled = _compile_patterns(patterns)

    return {
        key: (MASK_PLACEHOLDER if is_sensitive(key, compiled) else value)
        for key, value in config.items()
    }
