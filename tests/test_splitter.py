"""Tests for stackdiff.splitter."""
import pytest

from stackdiff.splitter import (
    SplitterError,
    merge_groups,
    split_by_glob,
    split_by_prefix,
)


CFG = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_DEBUG": "true",
    "APP_NAME": "myapp",
    "LOG_LEVEL": "info",
}


def test_split_by_prefix_basic():
    groups = split_by_prefix(CFG, ["DB_", "APP_"])
    assert set(groups["DB_"].keys()) == {"DB_HOST", "DB_PORT"}
    assert set(groups["APP_"].keys()) == {"APP_DEBUG", "APP_NAME"}
    assert groups["__other__"] == {"LOG_LEVEL": "info"}


def test_split_by_prefix_strip():
    groups = split_by_prefix(CFG, ["DB_"], strip_prefix=True)
    assert "HOST" in groups["DB_"]
    assert "PORT" in groups["DB_"]


def test_split_by_prefix_no_default_group_drops_unmatched():
    groups = split_by_prefix(CFG, ["DB_"], default_group=None)
    assert "__other__" not in groups
    assert "LOG_LEVEL" not in groups.get("DB_", {})


def test_split_by_prefix_empty_prefixes_raises():
    with pytest.raises(SplitterError, match="prefixes"):
        split_by_prefix(CFG, [])


def test_split_by_prefix_non_dict_raises():
    with pytest.raises(SplitterError, match="dict"):
        split_by_prefix(["a", "b"], ["a"])  # type: ignore[arg-type]


def test_split_by_prefix_first_match_wins():
    cfg = {"DB_APP_KEY": "val"}
    groups = split_by_prefix(cfg, ["DB_", "DB_APP_"])
    assert "DB_APP_KEY" in groups["DB_"]
    assert "DB_APP_KEY" not in groups["DB_APP_"]


def test_split_by_glob_basic():
    groups = split_by_glob(CFG, {"database": "DB_*", "app": "APP_*"})
    assert set(groups["database"].keys()) == {"DB_HOST", "DB_PORT"}
    assert set(groups["app"].keys()) == {"APP_DEBUG", "APP_NAME"}


def test_split_by_glob_default_group_captures_rest():
    groups = split_by_glob(CFG, {"database": "DB_*"})
    assert "LOG_LEVEL" in groups["__other__"]
    assert "APP_DEBUG" in groups["__other__"]


def test_split_by_glob_empty_patterns_raises():
    with pytest.raises(SplitterError, match="patterns"):
        split_by_glob(CFG, {})


def test_split_by_glob_non_dict_raises():
    with pytest.raises(SplitterError, match="dict"):
        split_by_glob("not-a-dict", {"g": "*"})  # type: ignore[arg-type]


def test_merge_groups_roundtrip():
    groups = split_by_prefix(CFG, ["DB_", "APP_"])
    merged = merge_groups(groups)
    assert merged == CFG


def test_merge_groups_last_wins_on_collision():
    groups = {"a": {"KEY": "first"}, "b": {"KEY": "second"}}
    merged = merge_groups(groups)
    assert merged["KEY"] == "second"
