"""Key renaming/aliasing support for config dicts."""

from __future__ import annotations

from typing import Dict, List, Tuple


class RenamerError(Exception):
    """Raised when a rename operation fails."""


def _validate_mapping(mapping: Dict[str, str]) -> None:
    """Ensure mapping values are non-empty strings."""
    for old, new in mapping.items():
        if not isinstance(old, str) or not old:
            raise RenamerError(f"Invalid source key: {old!r}")
        if not isinstance(new, str) or not new:
            raise RenamerError(f"Invalid target key for {old!r}: {new!r}")


def rename_keys(
    config: Dict[str, str],
    mapping: Dict[str, str],
    *,
    strict: bool = False,
) -> Dict[str, str]:
    """Return a new config with keys renamed according to *mapping*.

    Args:
        config:  Source config dict.
        mapping: ``{old_key: new_key}`` pairs.
        strict:  If *True*, raise :class:`RenamerError` when a source key
                 listed in *mapping* is absent from *config*.

    Returns:
        A new dict with the requested keys renamed; all other keys are
        preserved unchanged.
    """
    _validate_mapping(mapping)

    missing = [k for k in mapping if k not in config]
    if strict and missing:
        raise RenamerError(
            f"Keys not found in config: {', '.join(sorted(missing))}"
        )

    result: Dict[str, str] = {}
    for key, value in config.items():
        new_key = mapping.get(key, key)
        if new_key in result:
            raise RenamerError(
                f"Rename collision: target key {new_key!r} already exists"
            )
        result[new_key] = value
    return result


def apply_renames(
    configs: List[Dict[str, str]],
    mapping: Dict[str, str],
    *,
    strict: bool = False,
) -> List[Dict[str, str]]:
    """Apply :func:`rename_keys` to each config in *configs*."""
    return [rename_keys(c, mapping, strict=strict) for c in configs]


def invert_mapping(mapping: Dict[str, str]) -> Dict[str, str]:
    """Return the inverse of *mapping* (new -> old).

    Raises :class:`RenamerError` if the mapping is not bijective.
    """
    inverted: Dict[str, str] = {}
    for old, new in mapping.items():
        if new in inverted:
            raise RenamerError(
                f"Cannot invert: duplicate target key {new!r}"
            )
        inverted[new] = old
    return inverted
