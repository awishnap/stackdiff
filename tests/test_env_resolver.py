"""Tests for stackdiff.env_resolver."""

import pytest
from stackdiff.env_resolver import ResolveError, resolve_value, resolve_config


ENV = {"HOME": "/home/user", "PORT": "8080", "APP": "myapp"}


def test_resolve_value_curly_braces():
    assert resolve_value("http://localhost:${PORT}", ENV) == "http://localhost:8080"


def test_resolve_value_dollar_sign():
    assert resolve_value("app=$APP", ENV) == "app=myapp"


def test_resolve_value_no_refs():
    assert resolve_value("plain-value", ENV) == "plain-value"


def test_resolve_value_multiple_refs():
    assert resolve_value("${APP}:${PORT}", ENV) == "myapp:8080"


def test_resolve_value_missing_raises():
    with pytest.raises(ResolveError, match="MISSING"):
        resolve_value("${MISSING}", ENV)


def test_resolve_config_basic():
    config = {"url": "http://localhost:${PORT}", "name": "${APP}"}
    result = resolve_config(config, ENV)
    assert result == {"url": "http://localhost:8080", "name": "myapp"}


def test_resolve_config_strict_raises():
    config = {"key": "${UNDEFINED}"}
    with pytest.raises(ResolveError):
        resolve_config(config, ENV, strict=True)


def test_resolve_config_non_strict_keeps_original():
    config = {"key": "${UNDEFINED}", "ok": "${PORT}"}
    result = resolve_config(config, ENV, strict=False)
    assert result["key"] == "${UNDEFINED}"
    assert result["ok"] == "8080"


def test_resolve_config_non_string_passthrough():
    config = {"count": 42, "flag": True}  # type: ignore[dict-item]
    result = resolve_config(config, ENV)  # type: ignore[arg-type]
    assert result["count"] == 42
    assert result["flag"] is True


def test_resolve_config_uses_os_environ(monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    result = resolve_config({"msg": "${MY_VAR}"})
    assert result["msg"] == "hello"
