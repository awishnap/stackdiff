"""Tests for stackdiff.filter."""
import pytest

from stackdiff.filter import (
    FilterError,
    apply_filters,
    exclude_keys,
    include_keys,
)

SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "s3cr3t",
    "APP_DEBUG": "true",
    "LOG_LEVEL": "info",
}


def test_include_keys_exact():
    result = include_keys(SAMPLE, ["DB_HOST"])
    assert result == {"DB_HOST": "localhost"}


def test_include_keys_glob():
    result = include_keys(SAMPLE, ["DB_*"])
    assert set(result) == {"DB_HOST", "DB_PORT"}


def test_include_keys_multiple_patterns():
    result = include_keys(SAMPLE, ["DB_*", "LOG_*"])
    assert set(result) == {"DB_HOST", "DB_PORT", "LOG_LEVEL"}


def test_include_keys_no_match_returns_empty():
    result = include_keys(SAMPLE, ["NOPE_*"])
    assert result == {}


def test_include_keys_empty_patterns_raises():
    with pytest.raises(FilterError):
        include_keys(SAMPLE, [])


def test_exclude_keys_exact():
    result = exclude_keys(SAMPLE, ["APP_SECRET"])
    assert "APP_SECRET" not in result
    assert len(result) == len(SAMPLE) - 1


def test_exclude_keys_glob():
    result = exclude_keys(SAMPLE, ["APP_*"])
    assert "APP_SECRET" not in result
    assert "APP_DEBUG" not in result
    assert "DB_HOST" in result


def test_exclude_keys_empty_patterns_raises():
    with pytest.raises(FilterError):
        exclude_keys(SAMPLE, [])


def test_apply_filters_include_only():
    result = apply_filters(SAMPLE, include=["DB_*"])
    assert set(result) == {"DB_HOST", "DB_PORT"}


def test_apply_filters_exclude_only():
    result = apply_filters(SAMPLE, exclude=["APP_*"])
    assert "APP_SECRET" not in result
    assert "APP_DEBUG" not in result


def test_apply_filters_include_then_exclude():
    result = apply_filters(SAMPLE, include=["APP_*"], exclude=["APP_SECRET"])
    assert result == {"APP_DEBUG": "true"}


def test_apply_filters_no_filters_returns_original():
    result = apply_filters(SAMPLE)
    assert result == SAMPLE
