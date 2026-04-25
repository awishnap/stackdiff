"""caster.py — cast config values to explicit types via a type map."""
from __future__ import annotations

from typing import Any, Dict


class CasterError(Exception):
    """Raised when a cast operation fails."""


_SUPPORTED = {"str", "int", "float", "bool"}


def _cast_value(value: Any, target: str) -> Any:
    """Cast *value* to *target* type string."""
    if target not in _SUPPORTED:
        raise CasterError(f"Unsupported target type: {target!r}")
    if target == "str":
        return str(value)
    if target == "int":
        try:
            return int(value)
        except (ValueError, TypeError) as exc:
            raise CasterError(f"Cannot cast {value!r} to int: {exc}") from exc
    if target == "float":
        try:
            return float(value)
        except (ValueError, TypeError) as exc:
            raise CasterError(f"Cannot cast {value!r} to float: {exc}") from exc
    if target == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in {"true", "1", "yes"}:
                return True
            if value.lower() in {"false", "0", "no"}:
                return False
            raise CasterError(f"Cannot cast string {value!r} to bool")
        return bool(value)
    raise CasterError(f"Unhandled target type: {target!r}")


def cast_config(
    config: Dict[str, Any],
    type_map: Dict[str, str],
    strict: bool = True,
) -> Dict[str, Any]:
    """Return a new config dict with values cast according to *type_map*.

    Args:
        config:   Source config dictionary.
        type_map: Mapping of key -> target type string (str/int/float/bool).
        strict:   When True, raise CasterError for keys in *type_map* that are
                  absent from *config*.  When False, missing keys are silently
                  skipped.
    """
    if not isinstance(config, dict):
        raise CasterError("config must be a dict")
    result = dict(config)
    for key, target in type_map.items():
        if key not in config:
            if strict:
                raise CasterError(f"Key {key!r} not found in config")
            continue
        result[key] = _cast_value(config[key], target)
    return result


def cast_summary(original: Dict[str, Any], casted: Dict[str, Any]) -> str:
    """Return a human-readable summary of what was cast."""
    lines = []
    for key in casted:
        orig_val = original.get(key)
        new_val = casted[key]
        if type(orig_val) is not type(new_val):
            lines.append(
                f"  {key}: {type(orig_val).__name__}({orig_val!r})"
                f" -> {type(new_val).__name__}({new_val!r})"
            )
    if not lines:
        return "No type changes applied."
    return "Cast changes:\n" + "\n".join(lines)
