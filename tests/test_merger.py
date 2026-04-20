"""Tests for stackdiff.merger."""

import pytest

from stackdiff.merger import MergeError, merge_configs


# ---------------------------------------------------------------------------
# last_wins (default)
# ---------------------------------------------------------------------------

def test_last_wins_basic():
    a = {"HOST": "localhost", "PORT": "5432"}
    b = {"PORT": "5433", "DB": "mydb"}
    result = merge_configs(a, b)
    assert result == {"HOST": "localhost", "PORT": "5433", "DB": "mydb"}


def test_last_wins_single_config():
    cfg = {"KEY": "value"}
    assert merge_configs(cfg) == {"KEY": "value"}


def test_last_wins_three_configs():
    a = {"X": "1"}
    b = {"X": "2", "Y": "2"}
    c = {"Y": "3", "Z": "3"}
    result = merge_configs(a, b, c)
    assert result == {"X": "2", "Y": "3", "Z": "3"}


# ---------------------------------------------------------------------------
# first_wins
# ---------------------------------------------------------------------------

def test_first_wins_preserves_earlier_value():
    a = {"HOST": "prod-host"}
    b = {"HOST": "staging-host", "PORT": "80"}
    result = merge_configs(a, b, strategy="first_wins")
    assert result["HOST"] == "prod-host"
    assert result["PORT"] == "80"


def test_first_wins_new_keys_from_later():
    a = {"A": "1"}
    b = {"B": "2"}
    result = merge_configs(a, b, strategy="first_wins")
    assert result == {"A": "1", "B": "2"}


# ---------------------------------------------------------------------------
# deep
# ---------------------------------------------------------------------------

def test_deep_merge_nested_dicts():
    a = {"db": {"host": "localhost", "port": 5432}}
    b = {"db": {"port": 5433, "name": "mydb"}}
    result = merge_configs(a, b, strategy="deep")
    assert result == {"db": {"host": "localhost", "port": 5433, "name": "mydb"}}


def test_deep_merge_scalar_overrides_scalar():
    a = {"KEY": "old"}
    b = {"KEY": "new"}
    result = merge_configs(a, b, strategy="deep")
    assert result["KEY"] == "new"


def test_deep_merge_non_dict_not_recursed():
    a = {"items": [1, 2, 3]}
    b = {"items": [4, 5]}
    result = merge_configs(a, b, strategy="deep")
    assert result["items"] == [4, 5]


# ---------------------------------------------------------------------------
# error cases
# ---------------------------------------------------------------------------

def test_no_configs_raises():
    with pytest.raises(MergeError, match="at least one"):
        merge_configs()


def test_unknown_strategy_raises():
    with pytest.raises(MergeError, match="Unknown merge strategy"):
        merge_configs({"A": "1"}, strategy="magic")


def test_non_dict_config_raises():
    with pytest.raises(MergeError, match="Expected dict"):
        merge_configs({"A": "1"}, ["not", "a", "dict"])  # type: ignore[arg-type]
