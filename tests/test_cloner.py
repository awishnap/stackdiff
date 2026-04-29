"""Tests for stackdiff.cloner."""
from __future__ import annotations

import pytest

from stackdiff.cloner import ClonerError, clone_config, clone_subset, clone_summary


# ---------------------------------------------------------------------------
# clone_config
# ---------------------------------------------------------------------------

def test_clone_config_returns_equal_dict():
    cfg = {"A": "1", "B": "2"}
    result = clone_config(cfg)
    assert result == cfg


def test_clone_config_is_independent_copy():
    cfg = {"key": [1, 2, 3]}
    result = clone_config(cfg)
    result["key"].append(4)
    assert cfg["key"] == [1, 2, 3], "original should not be mutated"


def test_clone_config_key_transform_uppercase():
    cfg = {"host": "localhost", "port": "5432"}
    result = clone_config(cfg, key_transform=str.upper)
    assert set(result.keys()) == {"HOST", "PORT"}


def test_clone_config_key_transform_lowercase():
    cfg = {"HOST": "localhost", "PORT": "5432"}
    result = clone_config(cfg, key_transform=str.lower)
    assert "host" in result and "port" in result


def test_clone_config_value_transform_applied():
    cfg = {"a": "hello", "b": "world"}
    result = clone_config(cfg, value_transform=str.upper)
    assert result == {"a": "HELLO", "b": "WORLD"}


def test_clone_config_non_dict_raises():
    with pytest.raises(ClonerError, match="Expected dict"):
        clone_config(["not", "a", "dict"])  # type: ignore[arg-type]


def test_clone_config_key_transform_non_string_result_raises():
    with pytest.raises(ClonerError, match="key_transform must return str"):
        clone_config({"a": 1}, key_transform=lambda k: 42)  # type: ignore[arg-type, return-value]


# ---------------------------------------------------------------------------
# clone_subset
# ---------------------------------------------------------------------------

def test_clone_subset_returns_only_requested_keys():
    cfg = {"a": 1, "b": 2, "c": 3}
    result = clone_subset(cfg, ["a", "c"])
    assert result == {"a": 1, "c": 3}


def test_clone_subset_missing_keys_ignored():
    cfg = {"a": 1}
    result = clone_subset(cfg, ["a", "z"])
    assert result == {"a": 1}


def test_clone_subset_empty_keys_returns_empty():
    cfg = {"a": 1, "b": 2}
    assert clone_subset(cfg, []) == {}


def test_clone_subset_non_dict_raises():
    with pytest.raises(ClonerError):
        clone_subset("not-a-dict", ["a"])  # type: ignore[arg-type]


def test_clone_subset_is_independent_copy():
    cfg = {"data": [1, 2]}
    result = clone_subset(cfg, ["data"])
    result["data"].append(3)
    assert cfg["data"] == [1, 2]


# ---------------------------------------------------------------------------
# clone_summary
# ---------------------------------------------------------------------------

def test_clone_summary_all_kept():
    cfg = {"a": 1, "b": 2}
    summary = clone_summary(cfg, {"a": 1, "b": 2})
    assert "keys kept   : 2" in summary
    assert "keys added  : 0" in summary
    assert "keys removed: 0" in summary


def test_clone_summary_keys_added():
    original = {"a": 1}
    cloned = {"a": 1, "B": 1}  # uppercase rename looks like add+remove
    summary = clone_summary(original, cloned)
    assert "keys added  : 1" in summary
    assert "keys removed: 1" in summary
