"""Tests for stackdiff.renamer."""

import pytest

from stackdiff.renamer import (
    RenamerError,
    apply_renames,
    invert_mapping,
    rename_keys,
)


# ---------------------------------------------------------------------------
# rename_keys
# ---------------------------------------------------------------------------

def test_rename_keys_basic():
    cfg = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = rename_keys(cfg, {"DB_HOST": "DATABASE_HOST"})
    assert result == {"DATABASE_HOST": "localhost", "DB_PORT": "5432"}


def test_rename_keys_multiple():
    cfg = {"A": "1", "B": "2", "C": "3"}
    result = rename_keys(cfg, {"A": "X", "B": "Y"})
    assert result == {"X": "1", "Y": "2", "C": "3"}


def test_rename_keys_missing_key_non_strict_is_ignored():
    cfg = {"A": "1"}
    result = rename_keys(cfg, {"MISSING": "NEW"}, strict=False)
    assert result == {"A": "1"}


def test_rename_keys_missing_key_strict_raises():
    cfg = {"A": "1"}
    with pytest.raises(RenamerError, match="Keys not found"):
        rename_keys(cfg, {"MISSING": "NEW"}, strict=True)


def test_rename_keys_collision_raises():
    cfg = {"A": "1", "B": "2"}
    with pytest.raises(RenamerError, match="collision"):
        rename_keys(cfg, {"A": "B"})


def test_rename_keys_empty_mapping_returns_copy():
    cfg = {"X": "10"}
    result = rename_keys(cfg, {})
    assert result == cfg
    assert result is not cfg


def test_rename_keys_invalid_source_key_raises():
    with pytest.raises(RenamerError, match="Invalid source key"):
        rename_keys({"A": "1"}, {"": "B"})


def test_rename_keys_invalid_target_key_raises():
    with pytest.raises(RenamerError, match="Invalid target key"):
        rename_keys({"A": "1"}, {"A": ""})


# ---------------------------------------------------------------------------
# apply_renames
# ---------------------------------------------------------------------------

def test_apply_renames_all_configs():
    configs = [{"A": "1"}, {"A": "2"}]
    results = apply_renames(configs, {"A": "Z"})
    assert results == [{"Z": "1"}, {"Z": "2"}]


def test_apply_renames_empty_list():
    assert apply_renames([], {"A": "B"}) == []


# ---------------------------------------------------------------------------
# invert_mapping
# ---------------------------------------------------------------------------

def test_invert_mapping_basic():
    mapping = {"old_key": "new_key", "foo": "bar"}
    assert invert_mapping(mapping) == {"new_key": "old_key", "bar": "foo"}


def test_invert_mapping_duplicate_target_raises():
    with pytest.raises(RenamerError, match="Cannot invert"):
        invert_mapping({"A": "Z", "B": "Z"})


def test_invert_mapping_roundtrip():
    mapping = {"HOST": "DB_HOST", "PORT": "DB_PORT"}
    assert invert_mapping(invert_mapping(mapping)) == mapping
