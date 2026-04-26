"""interpolator.py – substitute placeholder tokens in config values.

Supports ``{{KEY}}`` and ``${KEY}`` style tokens resolved from a
context dictionary.  Unknown keys raise ``InterpolatorError`` in strict
mode and are left unchanged in lenient mode.
"""

from __future__ import annotations

import re
from typing import Any

_CURLY_RE = re.compile(r"\{\{([^}]+)\}\}")
_DOLLAR_RE = re.compile(r"\$\{([^}]+)\}")


class InterpolatorError(Exception):
    """Raised when interpolation fails."""


def interpolate_value(
    value: Any,
    context: dict[str, str],
    *,
    strict: bool = True,
) -> Any:
    """Return *value* with all placeholders replaced from *context*.

    Non-string values are returned unchanged.
    """
    if not isinstance(value, str):
        return value

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1).strip()
        if key in context:
            return str(context[key])
        if strict:
            raise InterpolatorError(
                f"Interpolation key not found in context: '{key}'"
            )
        return match.group(0)  # preserve original token

    result = _CURLY_RE.sub(_replace, value)
    result = _DOLLAR_RE.sub(_replace, result)
    return result


def interpolate_config(
    config: dict[str, Any],
    context: dict[str, str],
    *,
    strict: bool = True,
) -> dict[str, Any]:
    """Return a new config dict with all string values interpolated.

    Args:
        config:  Source configuration mapping.
        context: Key/value pairs used to resolve placeholders.
        strict:  When *True* (default) unknown placeholders raise
                 :class:`InterpolatorError`; when *False* they are left
                 as-is.
    """
    if not isinstance(config, dict):
        raise InterpolatorError("config must be a dict")
    return {
        k: interpolate_value(v, context, strict=strict)
        for k, v in config.items()
    }
