"""Tests for stackdiff.sorter."""

import pytest
from stackdiff.sorter import (
    SorterError,
    sort_keys_alpha,
    sort_keys_by_value,
    sort_keys_by_length,
    sort_keys_explicit,
    apply_sort,
)


# ---------------------------------------------------------------------------
# sort_keys_alpha
# ---------------------------------------------------------------------------

def test_sort_keys_alpha_basic():
    cfg = {"zebra": 1, "apple": 2, "mango": 3}
    result = sort_keys_alpha(cfg)
    assert list(result.keys()) == ["apple", "mango", "zebra"]


def test_sort_keys_alpha_reverse():
    cfg = {"zebra": 1, "apple": 2, "mango": 3}
    result = sort_keys_alpha(cfg, reverse=True)
    assert list(result.keys()) == ["zebra", "mango", "apple"]


def test_sort_keys_alpha_case_insensitive():
    cfg = {"Beta": 1, "alpha": 2, "GAMMA": 3}
    result = sort_keys_alpha(cfg)
    assert list(result.keys()) == ["alpha", "Beta", "GAMMA"]


def test_sort_keys_alpha_non_dict_raises():
    with pytest.raises(SorterError):
        sort_keys_alpha(["a", "b"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# sort_keys_by_value
# ---------------------------------------------------------------------------

def test_sort_keys_by_value_basic():
    cfg = {"b": "zebra", "a": "apple", "c": "mango"}
    result = sort_keys_by_value(cfg)
    assert list(result.keys()) == ["a", "c", "b"]


def test_sort_keys_by_value_reverse():
    cfg = {"b": "zebra", "a": "apple", "c": "mango"}
    result = sort_keys_by_value(cfg, reverse=True)
    assert list(result.keys()) == ["b", "c", "a"]


# ---------------------------------------------------------------------------
# sort_keys_by_length
# ---------------------------------------------------------------------------

def test_sort_keys_by_length_basic():
    cfg = {"longkey": 1, "k": 2, "mid": 3}
    result = sort_keys_by_length(cfg)
    assert list(result.keys()) == ["k", "mid", "longkey"]


def test_sort_keys_by_length_reverse():
    cfg = {"longkey": 1, "k": 2, "mid": 3}
    result = sort_keys_by_length(cfg, reverse=True)
    assert list(result.keys()) == ["longkey", "mid", "k"]


# ---------------------------------------------------------------------------
# sort_keys_explicit
# ---------------------------------------------------------------------------

def test_sort_keys_explicit_ordered_first():
    cfg = {"c": 3, "a": 1, "b": 2}
    result = sort_keys_explicit(cfg, order=["b", "a"])
    keys = list(result.keys())
    assert keys[:2] == ["b", "a"]
    assert "c" in keys


def test_sort_keys_explicit_drop_missing():
    cfg = {"c": 3, "a": 1, "b": 2}
    result = sort_keys_explicit(cfg, order=["a"], drop_missing=True)
    assert list(result.keys()) == ["a"]


def test_sort_keys_explicit_empty_order_raises():
    with pytest.raises(SorterError):
        sort_keys_explicit({"a": 1}, order=[])


# ---------------------------------------------------------------------------
# apply_sort
# ---------------------------------------------------------------------------

def test_apply_sort_alpha():
    cfg = {"z": 1, "a": 2}
    assert list(apply_sort(cfg, strategy="alpha").keys()) == ["a", "z"]


def test_apply_sort_unknown_strategy_raises():
    with pytest.raises(SorterError, match="Unknown sort strategy"):
        apply_sort({"a": 1}, strategy="nonexistent")
