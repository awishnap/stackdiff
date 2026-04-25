"""Tests for stackdiff/caster.py"""
from __future__ import annotations

import pytest

from stackdiff.caster import CasterError, _cast_value, cast_config, cast_summary


# ---------------------------------------------------------------------------
# _cast_value
# ---------------------------------------------------------------------------

def test_cast_value_to_str():
    assert _cast_value(42, "str") == "42"


def test_cast_value_to_int():
    assert _cast_value("7", "int") == 7


def test_cast_value_to_int_invalid_raises():
    with pytest.raises(CasterError, match="Cannot cast"):
        _cast_value("abc", "int")


def test_cast_value_to_float():
    assert _cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_value_to_bool_true_strings():
    for s in ("true", "True", "TRUE", "1", "yes"):
        assert _cast_value(s, "bool") is True


def test_cast_value_to_bool_false_strings():
    for s in ("false", "False", "FALSE", "0", "no"):
        assert _cast_value(s, "bool") is False


def test_cast_value_to_bool_invalid_string_raises():
    with pytest.raises(CasterError, match="Cannot cast string"):
        _cast_value("maybe", "bool")


def test_cast_value_unsupported_type_raises():
    with pytest.raises(CasterError, match="Unsupported target type"):
        _cast_value("x", "list")


# ---------------------------------------------------------------------------
# cast_config
# ---------------------------------------------------------------------------

def test_cast_config_basic():
    config = {"port": "8080", "debug": "true", "name": "app"}
    result = cast_config(config, {"port": "int", "debug": "bool"})
    assert result["port"] == 8080
    assert result["debug"] is True
    assert result["name"] == "app"  # untouched


def test_cast_config_missing_key_strict_raises():
    with pytest.raises(CasterError, match="not found in config"):
        cast_config({"a": "1"}, {"b": "int"}, strict=True)


def test_cast_config_missing_key_lenient_skips():
    result = cast_config({"a": "1"}, {"b": "int"}, strict=False)
    assert result == {"a": "1"}


def test_cast_config_non_dict_raises():
    with pytest.raises(CasterError, match="must be a dict"):
        cast_config(["a", "b"], {})  # type: ignore[arg-type]


def test_cast_config_does_not_mutate_original():
    config = {"x": "10"}
    cast_config(config, {"x": "int"})
    assert config["x"] == "10"


# ---------------------------------------------------------------------------
# cast_summary
# ---------------------------------------------------------------------------

def test_cast_summary_shows_changes():
    original = {"port": "8080"}
    casted = {"port": 8080}
    summary = cast_summary(original, casted)
    assert "port" in summary
    assert "str" in summary
    assert "int" in summary


def test_cast_summary_no_changes():
    config = {"name": "app"}
    summary = cast_summary(config, config)
    assert summary == "No type changes applied."
