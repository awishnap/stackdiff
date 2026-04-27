"""Tests for stackdiff.pruner."""

from __future__ import annotations

import json
import pytest

from stackdiff.pruner import (
    PrunerError,
    prune_by_pattern,
    prune_by_type,
    prune_by_value,
    prune_summary,
)


# ---------------------------------------------------------------------------
# prune_by_pattern
# ---------------------------------------------------------------------------

def test_prune_by_pattern_exact_match():
    cfg = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = prune_by_pattern(cfg, ["HOST"])
    assert "HOST" not in result
    assert "PORT" in result


def test_prune_by_pattern_wildcard():
    cfg = {"DB_HOST": "x", "DB_PORT": "5432", "APP_ENV": "prod"}
    result = prune_by_pattern(cfg, ["DB_*"])
    assert result == {"APP_ENV": "prod"}


def test_prune_by_pattern_multiple_patterns():
    cfg = {"SECRET": "s", "TOKEN": "t", "HOST": "h"}
    result = prune_by_pattern(cfg, ["secret", "token"])
    assert result == {"HOST": "h"}


def test_prune_by_pattern_case_insensitive():
    cfg = {"Password": "abc", "USER": "root"}
    result = prune_by_pattern(cfg, ["password"])
    assert "Password" not in result
    assert "USER" in result


def test_prune_by_pattern_no_match_returns_original():
    cfg = {"A": 1, "B": 2}
    result = prune_by_pattern(cfg, ["Z*"])
    assert result == cfg


def test_prune_by_pattern_empty_patterns_raises():
    with pytest.raises(PrunerError):
        prune_by_pattern({"A": 1}, [])


def test_prune_by_pattern_non_dict_raises():
    with pytest.raises(PrunerError):
        prune_by_pattern(["not", "a", "dict"], ["*"])  # type: ignore


# ---------------------------------------------------------------------------
# prune_by_value
# ---------------------------------------------------------------------------

def test_prune_by_value_removes_matching_value():
    cfg = {"A": "", "B": "hello", "C": ""}
    result = prune_by_value(cfg, [""])
    assert result == {"B": "hello"}


def test_prune_by_value_type_sensitive():
    cfg = {"A": 0, "B": False, "C": "0"}
    # only drop int 0, not bool False or str "0"
    result = prune_by_value(cfg, [0])
    assert "A" not in result
    assert "B" in result  # False == 0 but type differs
    assert "C" in result


def test_prune_by_value_no_match_returns_original():
    cfg = {"X": 99}
    assert prune_by_value(cfg, ["nope"]) == cfg


# ---------------------------------------------------------------------------
# prune_by_type
# ---------------------------------------------------------------------------

def test_prune_by_type_removes_none_values():
    cfg = {"A": None, "B": "val", "C": None}
    result = prune_by_type(cfg, [type(None)])
    assert result == {"B": "val"}


def test_prune_by_type_removes_ints():
    cfg = {"PORT": 5432, "HOST": "localhost", "WORKERS": 4}
    result = prune_by_type(cfg, [int])
    assert result == {"HOST": "localhost"}


def test_prune_by_type_empty_types_raises():
    with pytest.raises(PrunerError):
        prune_by_type({"A": 1}, [])


# ---------------------------------------------------------------------------
# prune_summary
# ---------------------------------------------------------------------------

def test_prune_summary_counts():
    original = {"A": 1, "B": 2, "C": 3}
    pruned = {"A": 1}
    s = prune_summary(original, pruned)
    assert s["original_count"] == 3
    assert s["pruned_count"] == 1
    assert s["removed_count"] == 2
    assert set(s["removed_keys"]) == {"B", "C"}


def test_prune_summary_no_removals():
    cfg = {"A": 1}
    s = prune_summary(cfg, cfg)
    assert s["removed_count"] == 0
    assert s["removed_keys"] == []
