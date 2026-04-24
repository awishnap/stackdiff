"""Template rendering for config values using simple placeholder substitution."""

from __future__ import annotations

import re
from typing import Any


class TemplaterError(Exception):
    """Raised when template rendering fails."""


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")


def render_value(value: str, context: dict[str, Any], strict: bool = True) -> str:
    """Replace {{key}} placeholders in *value* using *context*.

    Args:
        value: Template string that may contain ``{{ key }}`` placeholders.
        context: Mapping of placeholder names to replacement values.
        strict: If True, raise TemplaterError for unknown placeholders.

    Returns:
        The rendered string.
    """
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in context:
            if strict:
                raise TemplaterError(f"Unknown placeholder: '{key}'")
            return match.group(0)
        return str(context[key])

    return _PLACEHOLDER_RE.sub(_replace, value)


def render_config(
    config: dict[str, Any],
    context: dict[str, Any],
    strict: bool = True,
) -> dict[str, Any]:
    """Render all string values in *config* against *context*.

    Non-string values are passed through unchanged.

    Args:
        config: The configuration dict whose string values may contain placeholders.
        context: Placeholder substitution mapping.
        strict: Forwarded to :func:`render_value`.

    Returns:
        A new dict with rendered values.
    """
    if not isinstance(config, dict):
        raise TemplaterError("config must be a dict")
    if not isinstance(context, dict):
        raise TemplaterError("context must be a dict")

    rendered: dict[str, Any] = {}
    for key, val in config.items():
        if isinstance(val, str):
            rendered[key] = render_value(val, context, strict=strict)
        else:
            rendered[key] = val
    return rendered
