"""Tests for stackdiff/scoper.py."""
import pytest

from stackdiff.scoper import (
    ScopeError,
    list_scopes,
    scope_config,
    scope_summary,
)


FLAT_CONFIG = {
    "db.host": "localhost",
    "db.port": "5432",
    "cache.host": "redis",
    "cache.ttl": "300",
    "APP_DEBUG": "true",
}


def test_scope_config_basic():
    result = scope_config(FLAT_CONFIG, "db")
    assert result == {"host": "localhost", "port": "5432"}


def test_scope_config_keep_prefix():
    result = scope_config(FLAT_CONFIG, "db", strip_prefix=False)
    assert "db.host" in result
    assert "db.port" in result


def test_scope_config_no_match_returns_empty():
    result = scope_config(FLAT_CONFIG, "unknown")
    assert result == {}


def test_scope_config_custom_separator():
    config = {"db__host": "localhost", "db__port": "5432", "other": "val"}
    result = scope_config(config, "db", separator="__")
    assert result == {"host": "localhost", "port": "5432"}


def test_scope_config_non_dict_raises():
    with pytest.raises(ScopeError):
        scope_config(["a", "b"], "db")  # type: ignore[arg-type]


def test_scope_config_empty_scope_raises():
    with pytest.raises(ScopeError):
        scope_config(FLAT_CONFIG, "")


def test_scope_config_whitespace_scope_raises():
    with pytest.raises(ScopeError):
        scope_config(FLAT_CONFIG, "   ")


def test_list_scopes_basic():
    scopes = list_scopes(FLAT_CONFIG)
    assert scopes == ["cache", "db"]


def test_list_scopes_no_prefixes_returns_empty():
    config = {"HOST": "localhost", "PORT": "8080"}
    assert list_scopes(config) == []


def test_list_scopes_custom_separator():
    config = {"db__host": "h", "db__port": "p", "cache__ttl": "60"}
    assert list_scopes(config, separator="__") == ["cache", "db"]


def test_list_scopes_non_dict_raises():
    with pytest.raises(ScopeError):
        list_scopes("not-a-dict")  # type: ignore[arg-type]


def test_scope_summary_plural():
    scoped = {"host": "localhost", "port": "5432"}
    assert scope_summary(scoped, "db") == "Scope 'db': 2 keys"


def test_scope_summary_singular():
    scoped = {"host": "localhost"}
    assert scope_summary(scoped, "db") == "Scope 'db': 1 key"


def test_scope_summary_empty():
    assert scope_summary({}, "missing") == "Scope 'missing': 0 keys"
