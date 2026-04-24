"""Tests for stackdiff.templater."""

from __future__ import annotations

import pytest

from stackdiff.templater import TemplaterError, render_config, render_value


# ---------------------------------------------------------------------------
# render_value
# ---------------------------------------------------------------------------

def test_render_value_single_placeholder():
    assert render_value("Hello, {{ name }}!", {"name": "world"}) == "Hello, world!"


def test_render_value_multiple_placeholders():
    result = render_value("{{ host }}:{{ port }}", {"host": "localhost", "port": "5432"})
    assert result == "localhost:5432"


def test_render_value_no_placeholders():
    assert render_value("plain string", {}) == "plain string"


def test_render_value_unknown_strict_raises():
    with pytest.raises(TemplaterError, match="Unknown placeholder: 'missing'"):
        render_value("{{ missing }}", {}, strict=True)


def test_render_value_unknown_lenient_preserves():
    result = render_value("{{ missing }}", {}, strict=False)
    assert "missing" in result


def test_render_value_numeric_context():
    result = render_value("count={{ total }}", {"total": 42})
    assert result == "count=42"


def test_render_value_whitespace_in_placeholder():
    result = render_value("{{  key  }}", {"key": "val"})
    assert result == "val"


# ---------------------------------------------------------------------------
# render_config
# ---------------------------------------------------------------------------

def test_render_config_replaces_string_values():
    config = {"url": "http://{{ host }}/api", "timeout": 30}
    context = {"host": "example.com"}
    result = render_config(config, context)
    assert result["url"] == "http://example.com/api"
    assert result["timeout"] == 30


def test_render_config_non_string_values_unchanged():
    config = {"enabled": True, "retries": 3, "tags": ["a", "b"]}
    result = render_config(config, {})
    assert result == config


def test_render_config_empty_config():
    assert render_config({}, {"key": "val"}) == {}


def test_render_config_strict_raises_on_unknown():
    config = {"dsn": "postgres://{{ user }}:{{ pass }}@localhost"}
    with pytest.raises(TemplaterError):
        render_config(config, {"user": "admin"}, strict=True)


def test_render_config_lenient_leaves_unknown():
    config = {"dsn": "postgres://{{ user }}:{{ pass }}@localhost"}
    result = render_config(config, {"user": "admin"}, strict=False)
    assert "admin" in result["dsn"]
    assert "{{ pass }}" in result["dsn"]


def test_render_config_invalid_config_type_raises():
    with pytest.raises(TemplaterError, match="config must be a dict"):
        render_config(["not", "a", "dict"], {})  # type: ignore[arg-type]


def test_render_config_invalid_context_type_raises():
    with pytest.raises(TemplaterError, match="context must be a dict"):
        render_config({"k": "v"}, "not-a-dict")  # type: ignore[arg-type]
