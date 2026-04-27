"""Tests for stackdiff.sanitizer."""

from __future__ import annotations

import pytest

from stackdiff.sanitizer import (
    SanitizerError,
    collapse_whitespace,
    normalize_newlines,
    remove_control_chars,
    sanitize_config,
    sanitize_value,
    strip_whitespace,
)


# ---------------------------------------------------------------------------
# unit helpers
# ---------------------------------------------------------------------------

def test_strip_whitespace_string():
    assert strip_whitespace("  hello  ") == "hello"


def test_strip_whitespace_non_string_passthrough():
    assert strip_whitespace(42) == 42
    assert strip_whitespace(None) is None


def test_remove_control_chars_removes_null():
    assert remove_control_chars("ab\x00cd") == "abcd"


def test_remove_control_chars_removes_tab_and_bell():
    result = remove_control_chars("a\tb\x07c")
    # \t is control char (0x09), \x07 is BEL
    assert result == "abc"


def test_remove_control_chars_non_string_passthrough():
    assert remove_control_chars(3.14) == 3.14


def test_collapse_whitespace_multiple_spaces():
    assert collapse_whitespace("foo   bar") == "foo bar"


def test_collapse_whitespace_mixed_whitespace():
    assert collapse_whitespace("foo\t\tbar") == "foo bar"


def test_collapse_whitespace_non_string_passthrough():
    assert collapse_whitespace([1, 2]) == [1, 2]


def test_normalize_newlines_crlf():
    assert normalize_newlines("a\r\nb") == "a\nb"


def test_normalize_newlines_cr_only():
    assert normalize_newlines("a\rb") == "a\nb"


def test_normalize_newlines_non_string_passthrough():
    assert normalize_newlines(True) is True


# ---------------------------------------------------------------------------
# sanitize_value
# ---------------------------------------------------------------------------

def test_sanitize_value_strips_and_removes_control():
    assert sanitize_value("  hello\x00  ") == "hello"


def test_sanitize_value_collapse_disabled_by_default():
    result = sanitize_value("foo   bar")
    assert result == "foo   bar"  # internal spaces preserved


def test_sanitize_value_collapse_enabled():
    result = sanitize_value("foo   bar", collapse=True)
    assert result == "foo bar"


def test_sanitize_value_non_string_unchanged():
    assert sanitize_value(99) == 99
    assert sanitize_value(None) is None


# ---------------------------------------------------------------------------
# sanitize_config
# ---------------------------------------------------------------------------

def test_sanitize_config_basic():
    cfg = {"KEY": "  value  ", "NUM": 1}
    result = sanitize_config(cfg)
    assert result["KEY"] == "value"
    assert result["NUM"] == 1


def test_sanitize_config_with_collapse():
    cfg = {"MSG": "hello   world"}
    result = sanitize_config(cfg, collapse=True)
    assert result["MSG"] == "hello world"


def test_sanitize_config_empty_dict():
    assert sanitize_config({}) == {}


def test_sanitize_config_non_dict_raises():
    with pytest.raises(SanitizerError, match="Expected dict"):
        sanitize_config(["not", "a", "dict"])  # type: ignore[arg-type]


def test_sanitize_config_does_not_mutate_original():
    original = {"K": "  v  "}
    sanitize_config(original)
    assert original["K"] == "  v  "
