"""Tests for stackdiff.differ module."""

import pytest
from stackdiff.differ import diff_configs, DiffResult


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true", "SECRET": "abc"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "NEW_KEY": "value"}


def test_added_keys():
    result = diff_configs(BASE, TARGET)
    assert "NEW_KEY" in result.added
    assert result.added["NEW_KEY"] == "value"


def test_removed_keys():
    result = diff_configs(BASE, TARGET)
    assert "DEBUG" in result.removed
    assert "SECRET" in result.removed


def test_changed_keys():
    result = diff_configs(BASE, TARGET)
    assert "HOST" in result.changed
    old, new = result.changed["HOST"]
    assert old == "localhost"
    assert new == "prod.example.com"


def test_unchanged_keys():
    result = diff_configs(BASE, TARGET)
    assert "PORT" in result.unchanged
    assert result.unchanged["PORT"] == "5432"


def test_has_diff_true():
    result = diff_configs(BASE, TARGET)
    assert result.has_diff is True


def test_has_diff_false():
    result = diff_configs({"A": "1"}, {"A": "1"})
    assert result.has_diff is False


def test_ignore_keys():
    result = diff_configs(BASE, TARGET, ignore_keys=["HOST", "NEW_KEY", "DEBUG", "SECRET"])
    assert "HOST" not in result.changed
    assert "NEW_KEY" not in result.added


def test_summary_no_diff():
    result = diff_configs({"X": "1"}, {"X": "1"})
    assert result.summary() == "No differences found."


def test_summary_contains_symbols():
    result = diff_configs(BASE, TARGET)
    summary = result.summary()
    assert "+" in summary
    assert "-" in summary
    assert "~" in summary


def test_empty_configs():
    result = diff_configs({}, {})
    assert not result.has_diff
    assert result.summary() == "No differences found."
