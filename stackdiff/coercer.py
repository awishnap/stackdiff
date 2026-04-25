"""Type coercion utilities for config values."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class CoercerError(Exception):
    """Raised when a coercion cannot be performed."""


_TRUTHY = {"true", "yes", "1", "on"}
_FALSY = {"false", "no", "0", "off"}


def coerce_value(value: Any, target_type: str) -> Any:
    """Coerce *value* to *target_type* ("str", "int", "float", "bool").

    Raises CoercerError if the conversion is not possible.
    """
    if target_type == "str":
        return str(value)

    if target_type == "int":
        try:
            return int(value)
        except (ValueError, TypeError) as exc:
            raise CoercerError(f"Cannot coerce {value!r} to int: {exc}") from exc

    if target_type == "float":
        try:
            return float(value)
        except (ValueError, TypeError) as exc:
            raise CoercerError(f"Cannot coerce {value!r} to float: {exc}") from exc

    if target_type == "bool":
        if isinstance(value, bool):
            return value
        normalised = str(value).strip().lower()
        if normalised in _TRUTHY:
            return True
        if normalised in _FALSY:
            return False
        raise CoercerError(
            f"Cannot coerce {value!r} to bool: unrecognised literal {normalised!r}"
        )

    raise CoercerError(f"Unknown target type {target_type!r}")


def coerce_config(
    config: Dict[str, Any],
    type_map: Dict[str, str],
    *,
    strict: bool = False,
) -> Dict[str, Any]:
    """Apply *type_map* coercions to *config*.

    *type_map* maps key names to target type strings.  Keys present in
    *type_map* but absent from *config* are silently skipped unless
    *strict* is True, in which case a CoercerError is raised.
    """
    result = dict(config)
    for key, target_type in type_map.items():
        if key not in result:
            if strict:
                raise CoercerError(
                    f"Key {key!r} specified in type_map but missing from config"
                )
            continue
        result[key] = coerce_value(result[key], target_type)
    return result


def infer_types(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *config* with string values coerced to native types.

    Attempts int → float → bool → str in order.  Non-string values are
    left unchanged.
    """
    out: Dict[str, Any] = {}
    for key, value in config.items():
        if not isinstance(value, str):
            out[key] = value
            continue
        stripped = value.strip()
        try:
            out[key] = int(stripped)
            continue
        except ValueError:
            pass
        try:
            out[key] = float(stripped)
            continue
        except ValueError:
            pass
        if stripped.lower() in _TRUTHY:
            out[key] = True
            continue
        if stripped.lower() in _FALSY:
            out[key] = False
            continue
        out[key] = value
    return out
