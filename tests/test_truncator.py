"""Tests for stackdiff.truncator."""

from __future__ import annotations

import pytest

from stackdiff.truncator import (
    TruncatorError,
    truncate_config,
    truncate_value,
)


# ---------------------------------------------------------------------------
# truncate_value
# ---------------------------------------------------------------------------

def test_truncate_value_short_string_unchanged():
    assert truncate_value("hello", max_len=10) == "hello"


def test_truncate_value_exact_length_unchanged():
    assert truncate_value("hello", max_len=5) == "hello"


def test_truncate_value_long_string_truncated():
    result = truncate_value("abcdefghij", max_len=6, placeholder="...")
    assert result == "abc..."
    assert len(result) == 6


def test_truncate_value_non_string_passthrough():
    assert truncate_value(12345, max_len=3) == 12345
    assert truncate_value(None, max_len=3) is None
    assert truncate_value([1, 2], max_len=3) == [1, 2]


def test_truncate_value_custom_placeholder():
    result = truncate_value("verylongvalue", max_len=8, placeholder="~~")
    assert result.endswith("~~")
    assert len(result) == 8


def test_truncate_value_invalid_max_len_raises():
    with pytest.raises(TruncatorError, match="max_len"):
        truncate_value("hello", max_len=0)


# ---------------------------------------------------------------------------
# truncate_config
# ---------------------------------------------------------------------------

def test_truncate_config_truncates_all_long_values():
    cfg = {"A": "x" * 100, "B": "short"}
    result = truncate_config(cfg, max_len=20)
    assert len(result["A"]) == 20
    assert result["B"] == "short"


def test_truncate_config_returns_new_dict():
    cfg = {"K": "value"}
    result = truncate_config(cfg)
    assert result is not cfg


def test_truncate_config_key_filter_only_truncates_listed_keys():
    cfg = {"TOKEN": "x" * 50, "NAME": "y" * 50}
    result = truncate_config(cfg, max_len=10, keys=["TOKEN"])
    assert len(result["TOKEN"]) == 10
    assert result["NAME"] == "y" * 50


def test_truncate_config_non_dict_raises():
    with pytest.raises(TruncatorError, match="dict"):
        truncate_config(["not", "a", "dict"])  # type: ignore[arg-type]


def test_truncate_config_preserves_non_string_values():
    cfg = {"PORT": 8080, "DEBUG": True, "RATIO": 0.5}
    result = truncate_config(cfg, max_len=2)
    assert result == cfg


def test_truncate_config_empty_config_returns_empty():
    assert truncate_config({}) == {}
