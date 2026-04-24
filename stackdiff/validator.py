"""Validate config keys against a required schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


class ValidationError(Exception):
    pass


@dataclass
class ValidationResult:
    missing: List[str] = field(default_factory=list)
    type_mismatches: Dict[str, str] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return not self.missing and not self.type_mismatches

    def summary(self) -> str:
        lines = []
        if self.missing:
            lines.append("Missing keys: " + ", ".join(sorted(self.missing)))
        for key, msg in sorted(self.type_mismatches.items()):
            lines.append(f"Type mismatch [{key}]: {msg}")
        return "\n".join(lines) if lines else "OK"

    def raise_if_invalid(self) -> None:
        """Raise ValidationError with the summary message if validation failed."""
        if not self.valid:
            raise ValidationError(self.summary())

    def merge(self, other: ValidationResult) -> ValidationResult:
        """Return a new ValidationResult combining missing keys and type mismatches
        from both this result and *other*.
        """
        return ValidationResult(
            missing=list(set(self.missing) | set(other.missing)),
            type_mismatches={**self.type_mismatches, **other.type_mismatches},
        )


def validate_required(config: Dict, required_keys: Iterable[str]) -> ValidationResult:
    """Check that all required_keys are present in config."""
    result = ValidationResult()
    for key in required_keys:
        if key not in config:
            result.missing.append(key)
    return result


def validate_types(config: Dict, schema: Dict[str, type]) -> ValidationResult:
    """Check that values match expected Python types defined in schema."""
    result = ValidationResult()
    for key, expected_type in schema.items():
        if key not in config:
            result.missing.append(key)
            continue
        value = config[key]
        if not isinstance(value, expected_type):
            result.type_mismatches[key] = (
                f"expected {expected_type.__name__}, got {type(value).__name__}"
            )
    return result


def validate_config(config: Dict, required_keys: Iterable[str] = (), schema: Dict[str, type] = None) -> ValidationResult:
    """Run required-key and optional type checks, merging results."""
    req_result = validate_required(config, required_keys)
    if schema:
        type_result = validate_types(config, schema)
        return req_result.merge(type_result)
    return req_result
