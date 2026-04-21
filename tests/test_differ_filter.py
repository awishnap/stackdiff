"""Tests for stackdiff.differ_filter."""

import pytest

from stackdiff.differ_filter import (
    FilteredDiffError,
    filtered_diff,
    filtered_diff_summary,
)


LOCAL = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "abc123",
    "DEBUG": "true",
}

REMOTE = {
    "DB_HOST": "prod.db.internal",
    "DB_PORT": "5432",
    "SECRET_KEY": "xyz789",
    "LOG_LEVEL": "warn",
}


def test_filtered_diff_include_limits_keys():
    result = filtered_diff(LOCAL, REMOTE, include=["DB_*"])
    all_keys = set(result.added) | set(result.removed) | set(result.changed) | set(result.unchanged)
    assert all(k.startswith("DB_") for k in all_keys)


def test_filtered_diff_detects_changed_within_include():
    result = filtered_diff(LOCAL, REMOTE, include=["DB_HOST"])
    assert "DB_HOST" in result.changed


def test_filtered_diff_detects_unchanged_within_include():
    result = filtered_diff(LOCAL, REMOTE, include=["DB_PORT"])
    assert "DB_PORT" in result.unchanged


def test_filtered_diff_exclude_removes_keys():
    result = filtered_diff(LOCAL, REMOTE, exclude=["SECRET_KEY"])
    all_keys = set(result.added) | set(result.removed) | set(result.changed) | set(result.unchanged)
    assert "SECRET_KEY" not in all_keys


def test_filtered_diff_added_key_visible_without_filter():
    result = filtered_diff(LOCAL, REMOTE)
    assert "LOG_LEVEL" in result.added


def test_filtered_diff_added_key_hidden_by_exclude():
    result = filtered_diff(LOCAL, REMOTE, exclude=["LOG_LEVEL"])
    assert "LOG_LEVEL" not in result.added


def test_filtered_diff_empty_include_raises():
    with pytest.raises(FilteredDiffError):
        filtered_diff(LOCAL, REMOTE, include=[])


def test_filtered_diff_empty_exclude_raises():
    with pytest.raises(FilteredDiffError):
        filtered_diff(LOCAL, REMOTE, exclude=[])


def test_filtered_diff_summary_no_diff():
    msg = filtered_diff_summary({"A": "1"}, {"A": "1"})
    assert msg == "No differences found."


def test_filtered_diff_summary_with_changes():
    msg = filtered_diff_summary(LOCAL, REMOTE, include=["DB_*"])
    assert "changed" in msg


def test_filtered_diff_summary_reports_added():
    msg = filtered_diff_summary(LOCAL, REMOTE)
    assert "added" in msg
