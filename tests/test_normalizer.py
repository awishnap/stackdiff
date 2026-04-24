"""Tests for stackdiff.normalizer."""

import pytest

from stackdiff.normalizer import NormalizerError, normalize_config, normalize_value


# ---------------------------------------------------------------------------
# normalize_value
# ---------------------------------------------------------------------------

def test_normalize_value_strips_whitespace():
    assert normalize_value("  hello  ") == "hello"


def test_normalize_value_no_strip_when_disabled():
    assert normalize_value("  hello  ", strip_strings=False) == "  hello  "


def test_normalize_value_coerces_true_strings():
    for s in ("true", "True", "TRUE", "yes", "Yes", "1", "on", "ON"):
        assert normalize_value(s) is True, f"Expected True for {s!r}"


def test_normalize_value_coerces_false_strings():
    for s in ("false", "False", "FALSE", "no", "No", "0", "off", "OFF"):
        assert normalize_value(s) is False, f"Expected False for {s!r}"


def test_normalize_value_no_coerce_when_disabled():
    assert normalize_value("true", coerce_booleans=False) == "true"


def test_normalize_value_passthrough_int():
    assert normalize_value(42) == 42


def test_normalize_value_passthrough_none():
    assert normalize_value(None) is None


def test_normalize_value_passthrough_bool():
    assert normalize_value(True) is True


# ---------------------------------------------------------------------------
# normalize_config
# ---------------------------------------------------------------------------

def test_normalize_config_strips_and_coerces():
    cfg = {"host": "  localhost  ", "debug": "true", "port": 8080}
    result = normalize_config(cfg)
    assert result == {"host": "localhost", "debug": True, "port": 8080}


def test_normalize_config_selective_keys():
    cfg = {"host": "  localhost  ", "label": "  keep spaces  "}
    result = normalize_config(cfg, keys=["host"])
    assert result["host"] == "localhost"
    assert result["label"] == "  keep spaces  "


def test_normalize_config_returns_new_dict():
    cfg = {"key": "value"}
    result = normalize_config(cfg)
    assert result is not cfg


def test_normalize_config_empty_dict():
    assert normalize_config({}) == {}


def test_normalize_config_raises_on_non_dict():
    with pytest.raises(NormalizerError, match="Expected a dict"):
        normalize_config(["not", "a", "dict"])  # type: ignore[arg-type]


def test_normalize_config_false_string_becomes_bool():
    cfg = {"enabled": "no"}
    result = normalize_config(cfg)
    assert result["enabled"] is False
