"""Tests for stackdiff.transformer."""

import pytest

from stackdiff.transformer import (
    TransformerError,
    apply_transforms,
    lowercase_keys,
    prefix_keys,
    strip_values,
    uppercase_keys,
)


# ---------------------------------------------------------------------------
# uppercase_keys / lowercase_keys
# ---------------------------------------------------------------------------

def test_uppercase_keys():
    result = apply_transforms({"db_host": "localhost", "port": "5432"}, [uppercase_keys])
    assert result == {"DB_HOST": "localhost", "PORT": "5432"}


def test_lowercase_keys():
    result = apply_transforms({"DB_HOST": "localhost", "PORT": "5432"}, [lowercase_keys])
    assert result == {"db_host": "localhost", "port": "5432"}


# ---------------------------------------------------------------------------
# strip_values
# ---------------------------------------------------------------------------

def test_strip_values_removes_whitespace():
    result = apply_transforms({"key": "  value  "}, [strip_values])
    assert result["key"] == "value"


def test_strip_values_leaves_non_strings_unchanged():
    result = apply_transforms({"num": 42, "flag": True}, [strip_values])
    assert result == {"num": 42, "flag": True}


# ---------------------------------------------------------------------------
# prefix_keys
# ---------------------------------------------------------------------------

def test_prefix_keys_adds_prefix():
    result = apply_transforms({"host": "localhost"}, [prefix_keys("APP_")])
    assert result == {"APP_host": "localhost"}


def test_prefix_keys_empty_prefix_is_identity():
    cfg = {"a": 1, "b": 2}
    result = apply_transforms(cfg, [prefix_keys("")])
    assert result == cfg


# ---------------------------------------------------------------------------
# apply_transforms — composition
# ---------------------------------------------------------------------------

def test_chained_transforms_applied_in_order():
    # uppercase then prefix
    result = apply_transforms({"host": "  prod  "}, [strip_values, uppercase_keys])
    assert result == {"HOST": "prod"}


def test_empty_transforms_returns_copy():
    cfg = {"x": 1}
    result = apply_transforms(cfg, [])
    assert result == cfg
    assert result is not cfg


def test_empty_config_returns_empty_dict():
    result = apply_transforms({}, [uppercase_keys])
    assert result == {}


# ---------------------------------------------------------------------------
# Duplicate-key collision
# ---------------------------------------------------------------------------

def test_duplicate_key_raises_transformer_error():
    # uppercase_keys will map both "key" and "KEY" to "KEY"
    with pytest.raises(TransformerError, match="Duplicate key"):
        apply_transforms({"key": "a", "KEY": "b"}, [uppercase_keys])
