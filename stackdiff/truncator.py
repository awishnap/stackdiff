"""truncator.py — truncate long string values in a config dict.

Useful for display purposes when values are very long (e.g. JWT tokens,
certificate blobs, base64-encoded secrets).
"""

from __future__ import annotations

from typing import Any


class TruncatorError(Exception):
    """Raised when truncation cannot be applied."""


_DEFAULT_MAX_LEN = 80
_DEFAULT_PLACEHOLDER = "..."


def truncate_value(value: Any, max_len: int = _DEFAULT_MAX_LEN, placeholder: str = _DEFAULT_PLACEHOLDER) -> Any:
    """Truncate *value* if it is a string longer than *max_len*.

    Non-string values are returned unchanged.
    """
    if max_len < 1:
        raise TruncatorError(f"max_len must be >= 1, got {max_len}")
    if not isinstance(value, str):
        return value
    if len(value) <= max_len:
        return value
    cut = max(0, max_len - len(placeholder))
    return value[:cut] + placeholder


def truncate_config(
    config: dict[str, Any],
    max_len: int = _DEFAULT_MAX_LEN,
    placeholder: str = _DEFAULT_PLACEHOLDER,
    keys: list[str] | None = None,
) -> dict[str, Any]:
    """Return a new config dict with long string values truncated.

    Parameters
    ----------
    config:
        Source config mapping.
    max_len:
        Maximum allowed string length before truncation.
    placeholder:
        Suffix appended to truncated strings (counts toward *max_len*).
    keys:
        Optional allow-list of keys to truncate.  When *None* every key
        is considered.
    """
    if not isinstance(config, dict):
        raise TruncatorError("config must be a dict")
    result: dict[str, Any] = {}
    for k, v in config.items():
        if keys is None or k in keys:
            result[k] = truncate_value(v, max_len=max_len, placeholder=placeholder)
        else:
            result[k] = v
    return result
