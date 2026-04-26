"""Tests for stackdiff.interpolator."""

import pytest

from stackdiff.interpolator import (
    InterpolatorError,
    interpolate_value,
    interpolate_config,
)


# ---------------------------------------------------------------------------
# interpolate_value
# ---------------------------------------------------------------------------

def test_interpolate_value_curly_braces():
    result = interpolate_value("hello {{NAME}}", {"NAME": "world"})
    assert result == "hello world"


def test_interpolate_value_dollar_sign():
    result = interpolate_value("host=${HOST}", {"HOST": "localhost"})
    assert result == "host=localhost"


def test_interpolate_value_no_placeholders():
    assert interpolate_value("plain string", {}) == "plain string"


def test_interpolate_value_multiple_tokens():
    result = interpolate_value(
        "{{USER}}@{{HOST}}", {"USER": "alice", "HOST": "example.com"}
    )
    assert result == "alice@example.com"


def test_interpolate_value_mixed_styles():
    result = interpolate_value(
        "{{A}}-${B}", {"A": "foo", "B": "bar"}
    )
    assert result == "foo-bar"


def test_interpolate_value_non_string_passthrough():
    assert interpolate_value(42, {"X": "1"}) == 42
    assert interpolate_value(None, {}) is None
    assert interpolate_value(["a"], {}) == ["a"]


def test_interpolate_value_missing_strict_raises():
    with pytest.raises(InterpolatorError, match="MISSING"):
        interpolate_value("{{MISSING}}", {}, strict=True)


def test_interpolate_value_missing_lenient_preserves():
    result = interpolate_value("{{MISSING}}", {}, strict=False)
    assert result == "{{MISSING}}"


def test_interpolate_value_dollar_missing_lenient_preserves():
    result = interpolate_value("${NOPE}", {}, strict=False)
    assert result == "${NOPE}"


# ---------------------------------------------------------------------------
# interpolate_config
# ---------------------------------------------------------------------------

def test_interpolate_config_substitutes_all_values():
    cfg = {"db": "{{DB_HOST}}", "port": "${PORT}"}
    ctx = {"DB_HOST": "db.local", "PORT": "5432"}
    result = interpolate_config(cfg, ctx)
    assert result == {"db": "db.local", "port": "5432"}


def test_interpolate_config_non_string_values_unchanged():
    cfg = {"timeout": 30, "enabled": True, "name": "{{APP}}"}
    result = interpolate_config(cfg, {"APP": "myapp"})
    assert result["timeout"] == 30
    assert result["enabled"] is True
    assert result["name"] == "myapp"


def test_interpolate_config_non_dict_raises():
    with pytest.raises(InterpolatorError, match="dict"):
        interpolate_config(["a", "b"], {})  # type: ignore[arg-type]


def test_interpolate_config_strict_missing_raises():
    with pytest.raises(InterpolatorError):
        interpolate_config({"key": "{{UNDEFINED}}"}, {}, strict=True)


def test_interpolate_config_lenient_missing_preserved():
    result = interpolate_config({"key": "{{UNDEFINED}}"}, {}, strict=False)
    assert result["key"] == "{{UNDEFINED}}"


def test_interpolate_config_empty_config():
    assert interpolate_config({}, {"X": "1"}) == {}
