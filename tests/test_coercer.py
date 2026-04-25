"""Tests for stackdiff.coercer."""
import pytest

from stackdiff.coercer import (
    CoercerError,
    coerce_config,
    coerce_value,
    infer_types,
)


# ---------------------------------------------------------------------------
# coerce_value
# ---------------------------------------------------------------------------

def test_coerce_value_to_str():
    assert coerce_value(42, "str") == "42"


def test_coerce_value_to_int():
    assert coerce_value("7", "int") == 7


def test_coerce_value_to_int_invalid_raises():
    with pytest.raises(CoercerError, match="Cannot coerce"):
        coerce_value("abc", "int")


def test_coerce_value_to_float():
    assert coerce_value("3.14", "float") == pytest.approx(3.14)


def test_coerce_value_to_float_invalid_raises():
    with pytest.raises(CoercerError):
        coerce_value("not-a-float", "float")


def test_coerce_value_to_bool_true_variants():
    for literal in ("true", "yes", "1", "on", "True", "YES"):
        assert coerce_value(literal, "bool") is True


def test_coerce_value_to_bool_false_variants():
    for literal in ("false", "no", "0", "off", "False", "NO"):
        assert coerce_value(literal, "bool") is False


def test_coerce_value_to_bool_already_bool():
    assert coerce_value(True, "bool") is True
    assert coerce_value(False, "bool") is False


def test_coerce_value_to_bool_invalid_raises():
    with pytest.raises(CoercerError, match="Cannot coerce"):
        coerce_value("maybe", "bool")


def test_coerce_value_unknown_type_raises():
    with pytest.raises(CoercerError, match="Unknown target type"):
        coerce_value("x", "list")


# ---------------------------------------------------------------------------
# coerce_config
# ---------------------------------------------------------------------------

def test_coerce_config_applies_type_map():
    cfg = {"port": "8080", "debug": "true", "name": "app"}
    result = coerce_config(cfg, {"port": "int", "debug": "bool"})
    assert result["port"] == 8080
    assert result["debug"] is True
    assert result["name"] == "app"


def test_coerce_config_missing_key_skipped_by_default():
    cfg = {"host": "localhost"}
    result = coerce_config(cfg, {"port": "int"})
    assert "port" not in result


def test_coerce_config_missing_key_strict_raises():
    cfg = {"host": "localhost"}
    with pytest.raises(CoercerError, match="missing from config"):
        coerce_config(cfg, {"port": "int"}, strict=True)


def test_coerce_config_does_not_mutate_original():
    cfg = {"count": "5"}
    coerce_config(cfg, {"count": "int"})
    assert cfg["count"] == "5"


# ---------------------------------------------------------------------------
# infer_types
# ---------------------------------------------------------------------------

def test_infer_types_converts_int_string():
    assert infer_types({"x": "42"})["x"] == 42


def test_infer_types_converts_float_string():
    assert infer_types({"pi": "3.14"})["pi"] == pytest.approx(3.14)


def test_infer_types_converts_bool_string():
    assert infer_types({"flag": "true"})["flag"] is True
    assert infer_types({"flag": "off"})["flag"] is False


def test_infer_types_leaves_plain_strings():
    assert infer_types({"name": "alice"})["name"] == "alice"


def test_infer_types_leaves_non_strings_unchanged():
    cfg = {"count": 7, "ratio": 0.5, "active": True}
    assert infer_types(cfg) == cfg
