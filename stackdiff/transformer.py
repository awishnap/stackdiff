"""Key/value transformation pipeline for config dicts."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

TransformFn = Callable[[str, Any], tuple[str, Any]]


class TransformerError(Exception):
    """Raised when a transformation step fails."""


def uppercase_keys(key: str, value: Any) -> tuple[str, Any]:
    """Transform: convert every key to upper-case."""
    return key.upper(), value


def lowercase_keys(key: str, value: Any) -> tuple[str, Any]:
    """Transform: convert every key to lower-case."""
    return key.lower(), value


def strip_values(key: str, value: Any) -> tuple[str, Any]:
    """Transform: strip leading/trailing whitespace from string values."""
    if isinstance(value, str):
        value = value.strip()
    return key, value


def prefix_keys(prefix: str) -> TransformFn:
    """Return a transform that prepends *prefix* to every key."""
    def _transform(key: str, value: Any) -> tuple[str, Any]:
        return f"{prefix}{key}", value
    return _transform


def apply_transforms(
    config: Dict[str, Any],
    transforms: List[TransformFn],
) -> Dict[str, Any]:
    """Apply a sequence of transform functions to every key/value pair.

    Each transform receives ``(key, value)`` and must return a
    ``(new_key, new_value)`` tuple.  Transforms are applied in order.

    Raises:
        TransformerError: if a duplicate key is produced after transformation.
    """
    if not transforms:
        return dict(config)

    result: Dict[str, Any] = {}
    for key, value in config.items():
        current_key, current_value = key, value
        for fn in transforms:
            try:
                current_key, current_value = fn(current_key, current_value)
            except Exception as exc:  # pragma: no cover
                raise TransformerError(
                    f"Transform {fn.__name__!r} failed on key {key!r}: {exc}"
                ) from exc
        if current_key in result:
            raise TransformerError(
                f"Duplicate key {current_key!r} produced by transforms."
            )
        result[current_key] = current_value
    return result
