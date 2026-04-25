"""Tests for stackdiff.deduplicator."""

import pytest

from stackdiff.deduplicator import (
    DeduplicatorError,
    dedup_summary,
    drop_duplicate_keys,
    find_duplicate_values,
    has_duplicates,
)


# ---------------------------------------------------------------------------
# find_duplicate_values
# ---------------------------------------------------------------------------

def test_find_duplicates_detects_shared_value():
    cfg = {"a": "x", "b": "y", "c": "x"}
    result = find_duplicate_values(cfg)
    assert "x" in result
    assert set(result["x"]) == {"a", "c"}


def test_find_duplicates_no_duplicates_returns_empty():
    cfg = {"a": "1", "b": "2", "c": "3"}
    assert find_duplicate_values(cfg) == {}


def test_find_duplicates_ignores_unhashable_values():
    cfg = {"a": [1, 2], "b": [1, 2], "c": "ok"}
    result = find_duplicate_values(cfg)
    assert result == {}


def test_find_duplicates_non_dict_raises():
    with pytest.raises(DeduplicatorError):
        find_duplicate_values(["not", "a", "dict"])  # type: ignore[arg-type]


def test_find_duplicates_multiple_groups():
    cfg = {"a": 1, "b": 2, "c": 1, "d": 2, "e": 3}
    result = find_duplicate_values(cfg)
    assert set(result[1]) == {"a", "c"}
    assert set(result[2]) == {"b", "d"}
    assert 3 not in result


# ---------------------------------------------------------------------------
# has_duplicates
# ---------------------------------------------------------------------------

def test_has_duplicates_true():
    assert has_duplicates({"a": "v", "b": "v"}) is True


def test_has_duplicates_false():
    assert has_duplicates({"a": "v", "b": "w"}) is False


# ---------------------------------------------------------------------------
# drop_duplicate_keys
# ---------------------------------------------------------------------------

def test_drop_duplicate_keys_keep_first():
    cfg = {"a": "x", "b": "y", "c": "x"}
    result = drop_duplicate_keys(cfg, keep="first")
    assert "a" in result
    assert "c" not in result
    assert result["b"] == "y"


def test_drop_duplicate_keys_keep_last():
    cfg = {"a": "x", "b": "y", "c": "x"}
    result = drop_duplicate_keys(cfg, keep="last")
    assert "c" in result
    assert "a" not in result


def test_drop_duplicate_keys_invalid_keep_raises():
    with pytest.raises(DeduplicatorError):
        drop_duplicate_keys({"a": 1}, keep="middle")


def test_drop_duplicate_keys_no_duplicates_unchanged():
    cfg = {"a": 1, "b": 2}
    assert drop_duplicate_keys(cfg) == cfg


# ---------------------------------------------------------------------------
# dedup_summary
# ---------------------------------------------------------------------------

def test_dedup_summary_no_duplicates():
    assert dedup_summary({"a": 1, "b": 2}) == "No duplicate values found."


def test_dedup_summary_with_duplicates():
    cfg = {"x": "val", "y": "val"}
    summary = dedup_summary(cfg)
    assert "1 duplicate value" in summary
    assert "val" in summary
