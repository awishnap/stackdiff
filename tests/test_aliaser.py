"""Tests for stackdiff.aliaser."""
from __future__ import annotations

import pytest

from stackdiff.aliaser import (
    AliasError,
    add_alias,
    list_aliases,
    remove_alias,
    resolve_aliases,
)


@pytest.fixture()
def alias_dir(tmp_path):
    return str(tmp_path / "aliases")


def test_list_aliases_empty(alias_dir):
    assert list_aliases(alias_dir, "prod") == {}


def test_add_and_list(alias_dir):
    add_alias(alias_dir, "prod", "DB_HOST", "DATABASE_HOST")
    data = list_aliases(alias_dir, "prod")
    assert "DB_HOST" in data
    assert "DATABASE_HOST" in data["DB_HOST"]


def test_add_multiple_aliases_same_canonical(alias_dir):
    add_alias(alias_dir, "prod", "DB_HOST", "DATABASE_HOST")
    add_alias(alias_dir, "prod", "DB_HOST", "POSTGRES_HOST")
    data = list_aliases(alias_dir, "prod")
    assert set(data["DB_HOST"]) == {"DATABASE_HOST", "POSTGRES_HOST"}


def test_add_duplicate_alias_is_idempotent(alias_dir):
    add_alias(alias_dir, "prod", "DB_HOST", "DATABASE_HOST")
    add_alias(alias_dir, "prod", "DB_HOST", "DATABASE_HOST")
    data = list_aliases(alias_dir, "prod")
    assert data["DB_HOST"].count("DATABASE_HOST") == 1


def test_add_empty_canonical_raises(alias_dir):
    with pytest.raises(AliasError):
        add_alias(alias_dir, "prod", "", "DATABASE_HOST")


def test_add_empty_alias_raises(alias_dir):
    with pytest.raises(AliasError):
        add_alias(alias_dir, "prod", "DB_HOST", "")


def test_remove_alias(alias_dir):
    add_alias(alias_dir, "prod", "DB_HOST", "DATABASE_HOST")
    remove_alias(alias_dir, "prod", "DB_HOST", "DATABASE_HOST")
    data = list_aliases(alias_dir, "prod")
    assert "DB_HOST" not in data


def test_remove_missing_alias_raises(alias_dir):
    with pytest.raises(AliasError):
        remove_alias(alias_dir, "prod", "DB_HOST", "NOPE")


def test_resolve_aliases_renames_key(alias_dir):
    add_alias(alias_dir, "prod", "DB_HOST", "DATABASE_HOST")
    config = {"DATABASE_HOST": "localhost", "PORT": "5432"}
    resolved = resolve_aliases(config, alias_dir, "prod")
    assert "DB_HOST" in resolved
    assert resolved["DB_HOST"] == "localhost"
    assert "DATABASE_HOST" not in resolved


def test_resolve_aliases_canonical_wins_over_alias(alias_dir):
    add_alias(alias_dir, "prod", "DB_HOST", "DATABASE_HOST")
    config = {"DB_HOST": "primary", "DATABASE_HOST": "secondary"}
    resolved = resolve_aliases(config, alias_dir, "prod")
    assert resolved["DB_HOST"] == "primary"


def test_resolve_aliases_no_aliases_is_passthrough(alias_dir):
    config = {"KEY": "value"}
    resolved = resolve_aliases(config, alias_dir, "prod")
    assert resolved == config
