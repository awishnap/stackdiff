"""Tests for stackdiff.redactor."""

import pytest

from stackdiff.redactor import (
    RedactorError,
    apply_redaction,
    drop_keys,
    redact_keys,
)


CFG = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "s3cr3t",
    "API_TOKEN": "tok_abc123",
    "DEBUG": "true",
    "PORT": "8080",
}


def test_redact_keys_exact_glob():
    result = redact_keys(CFG, ["SECRET_KEY"])
    assert result["SECRET_KEY"] == "<REDACTED>"
    assert result["DEBUG"] == "true"


def test_redact_keys_wildcard():
    result = redact_keys(CFG, ["*TOKEN*"])
    assert result["API_TOKEN"] == "<REDACTED>"
    assert result["DATABASE_URL"] == CFG["DATABASE_URL"]


def test_redact_keys_multiple_patterns():
    result = redact_keys(CFG, ["SECRET_KEY", "API_TOKEN"])
    assert result["SECRET_KEY"] == "<REDACTED>"
    assert result["API_TOKEN"] == "<REDACTED>"
    assert result["PORT"] == "8080"


def test_redact_keys_custom_placeholder():
    result = redact_keys(CFG, ["SECRET_KEY"], placeholder="***")
    assert result["SECRET_KEY"] == "***"


def test_redact_keys_case_insensitive():
    cfg = {"My_Secret": "value", "other": "ok"}
    result = redact_keys(cfg, ["*secret*"])
    assert result["My_Secret"] == "<REDACTED>"
    assert result["other"] == "ok"


def test_redact_keys_no_match_unchanged():
    result = redact_keys(CFG, ["NONEXISTENT*"])
    assert result == CFG


def test_redact_keys_does_not_mutate_original():
    original = {"SECRET": "val", "SAFE": "ok"}
    redact_keys(original, ["SECRET"])
    assert original["SECRET"] == "val"


def test_drop_keys_removes_matched():
    result = drop_keys(CFG, ["SECRET_KEY", "API_TOKEN"])
    assert "SECRET_KEY" not in result
    assert "API_TOKEN" not in result
    assert "PORT" in result


def test_drop_keys_wildcard():
    result = drop_keys(CFG, ["*URL*"])
    assert "DATABASE_URL" not in result
    assert len(result) == len(CFG) - 1


def test_drop_keys_no_match_returns_full_copy():
    result = drop_keys(CFG, ["NOTHING*"])
    assert result == CFG
    assert result is not CFG


def test_apply_redaction_replaces_by_default():
    result = apply_redaction(CFG, ["SECRET_KEY"])
    assert result["SECRET_KEY"] == "<REDACTED>"


def test_apply_redaction_drops_when_placeholder_none():
    result = apply_redaction(CFG, ["SECRET_KEY"], placeholder=None)
    assert "SECRET_KEY" not in result


def test_empty_pattern_raises():
    with pytest.raises(RedactorError):
        redact_keys(CFG, [""])
