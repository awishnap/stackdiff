"""Tests for stackdiff.tagger."""

import pytest

from stackdiff.tagger import (
    TaggerError,
    add_tag,
    clear_tags,
    find_by_tag,
    list_tags,
    remove_tag,
)


@pytest.fixture()
def tag_dir(tmp_path):
    return str(tmp_path / "tags")


def test_list_tags_empty(tag_dir):
    assert list_tags(tag_dir, "prod") == []


def test_add_and_list_tag(tag_dir):
    add_tag(tag_dir, "prod", "critical")
    assert list_tags(tag_dir, "prod") == ["critical"]


def test_add_multiple_tags(tag_dir):
    add_tag(tag_dir, "staging", "review")
    add_tag(tag_dir, "staging", "beta")
    tags = list_tags(tag_dir, "staging")
    assert "review" in tags
    assert "beta" in tags


def test_add_duplicate_tag_is_idempotent(tag_dir):
    add_tag(tag_dir, "prod", "critical")
    add_tag(tag_dir, "prod", "critical")
    assert list_tags(tag_dir, "prod").count("critical") == 1


def test_remove_tag(tag_dir):
    add_tag(tag_dir, "prod", "critical")
    remove_tag(tag_dir, "prod", "critical")
    assert list_tags(tag_dir, "prod") == []


def test_remove_missing_tag_raises(tag_dir):
    with pytest.raises(TaggerError, match="not found"):
        remove_tag(tag_dir, "prod", "ghost")


def test_find_by_tag_returns_matching_names(tag_dir):
    add_tag(tag_dir, "prod", "critical")
    add_tag(tag_dir, "staging", "critical")
    add_tag(tag_dir, "dev", "optional")
    result = find_by_tag(tag_dir, "critical")
    assert set(result) == {"prod", "staging"}


def test_find_by_tag_no_match(tag_dir):
    add_tag(tag_dir, "prod", "critical")
    assert find_by_tag(tag_dir, "nonexistent") == []


def test_clear_tags_removes_all(tag_dir):
    add_tag(tag_dir, "prod", "critical")
    add_tag(tag_dir, "prod", "live")
    clear_tags(tag_dir, "prod")
    assert list_tags(tag_dir, "prod") == []


def test_clear_tags_does_not_affect_others(tag_dir):
    add_tag(tag_dir, "prod", "critical")
    add_tag(tag_dir, "staging", "beta")
    clear_tags(tag_dir, "prod")
    assert list_tags(tag_dir, "staging") == ["beta"]
