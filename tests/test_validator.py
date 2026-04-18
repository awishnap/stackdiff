"""Tests for stackdiff.validator."""

import pytest
from stackdiff.validator import (
    ValidationResult,
    validate_required,
    validate_types,
    validate_config,
)


def test_validate_required_all_present():
    result = validate_required({"HOST": "localhost", "PORT": "5432"}, ["HOST", "PORT"])
    assert result.valid


def test_validate_required_missing_key():
    result = validate_required({"HOST": "localhost"}, ["HOST", "PORT"])
    assert "PORT" in result.missing
    assert not result.valid


def test_validate_required_empty_config():
    result = validate_required({}, ["DB_URL", "SECRET_KEY"])
    assert set(result.missing) == {"DB_URL", "SECRET_KEY"}


def test_validate_types_correct():
    config = {"retries": 3, "debug": True, "host": "localhost"}
    schema = {"retries": int, "debug": bool, "host": str}
    result = validate_types(config, schema)
    assert result.valid


def test_validate_types_mismatch():
    config = {"retries": "three", "debug": True}
    schema = {"retries": int, "debug": bool}
    result = validate_types(config, schema)
    assert "retries" in result.type_mismatches
    assert "int" in result.type_mismatches["retries"]


def test_validate_types_missing_key():
    config = {"debug": True}
    schema = {"retries": int, "debug": bool}
    result = validate_types(config, schema)
    assert "retries" in result.missing


def test_validate_config_combined():
    config = {"HOST": "db", "PORT": 5432}
    result = validate_config(config, required_keys=["HOST", "PORT", "USER"], schema={"PORT": int})
    assert "USER" in result.missing
    assert result.type_mismatches == {}


def test_validation_result_summary_ok():
    result = ValidationResult()
    assert result.summary() == "OK"


def test_validation_result_summary_with_issues():
    result = ValidationResult(missing=["FOO"], type_mismatches={"BAR": "expected int, got str"})
    summary = result.summary()
    assert "FOO" in summary
    assert "BAR" in summary
