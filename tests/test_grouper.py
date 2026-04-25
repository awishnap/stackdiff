"""Tests for stackdiff.grouper."""
import pytest
from stackdiff.grouper import group_by_prefix, group_by_glob, merge_groups, GrouperError


CFG = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "myapp",
    "APP_ENV": "prod",
    "LOG_LEVEL": "info",
}


def test_group_by_prefix_basic():
    groups = group_by_prefix(CFG, ["DB", "APP"])
    assert "DB_HOST" in groups["DB"]
    assert "DB_PORT" in groups["DB"]
    assert "APP_NAME" in groups["APP"]
    assert "APP_ENV" in groups["APP"]


def test_group_by_prefix_default_group_catches_unmatched():
    groups = group_by_prefix(CFG, ["DB", "APP"], default_group="misc")
    assert "LOG_LEVEL" in groups["misc"]


def test_group_by_prefix_no_default_group_drops_unmatched():
    groups = group_by_prefix(CFG, ["DB"], default_group=None)
    assert "LOG_LEVEL" not in str(groups)
    assert "other" not in groups


def test_group_by_prefix_empty_prefixes_raises():
    with pytest.raises(GrouperError, match="prefixes"):
        group_by_prefix(CFG, [])


def test_group_by_prefix_non_dict_raises():
    with pytest.raises(GrouperError, match="dict"):
        group_by_prefix(["a", "b"], ["DB"])


def test_group_by_prefix_case_insensitive():
    groups = group_by_prefix(CFG, ["db"])
    assert "DB_HOST" in groups["db"]


def test_group_by_glob_basic():
    patterns = {"database": "DB_*", "application": "APP_*"}
    groups = group_by_glob(CFG, patterns)
    assert "DB_HOST" in groups["database"]
    assert "APP_NAME" in groups["application"]


def test_group_by_glob_default_group():
    patterns = {"database": "DB_*"}
    groups = group_by_glob(CFG, patterns, default_group="rest")
    assert "LOG_LEVEL" in groups["rest"]
    assert "APP_NAME" in groups["rest"]


def test_group_by_glob_no_default_drops_unmatched():
    patterns = {"database": "DB_*"}
    groups = group_by_glob(CFG, patterns, default_group=None)
    assert "LOG_LEVEL" not in str(groups)


def test_group_by_glob_empty_patterns_raises():
    with pytest.raises(GrouperError, match="patterns"):
        group_by_glob(CFG, {})


def test_group_by_glob_non_dict_raises():
    with pytest.raises(GrouperError, match="dict"):
        group_by_glob("not a dict", {"a": "*"})


def test_merge_groups_roundtrip():
    groups = group_by_prefix(CFG, ["DB", "APP"], default_group="misc")
    merged = merge_groups(groups)
    assert merged == CFG


def test_merge_groups_last_wins_on_collision():
    groups = {"a": {"KEY": "first"}, "b": {"KEY": "second"}}
    merged = merge_groups(groups)
    assert merged["KEY"] == "second"
