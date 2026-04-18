"""Tests for stackdiff.fetcher module."""

import json
from unittest.mock import patch, MagicMock
import pytest

from stackdiff.fetcher import fetch_url, fetch_json_config, fetch_env_config, FetchError


def _mock_urlopen(content: str, status: int = 200):
    cm = MagicMock()
    cm.__enter__ = lambda s: s
    cm.__exit__ = MagicMock(return_value=False)
    cm.read.return_value = content.encode("utf-8")
    cm.status = status
    return cm


@patch("urllib.request.urlopen")
def test_fetch_url_success(mock_open):
    mock_open.return_value = _mock_urlopen("KEY=value")
    result = fetch_url("http://example.com/config")
    assert result == "KEY=value"


@patch("urllib.request.urlopen")
def test_fetch_url_http_error(mock_open):
    import urllib.error
    mock_open.side_effect = urllib.error.HTTPError(
        url="http://x.com", code=404, msg="Not Found", hdrs={}, fp=None
    )
    with pytest.raises(FetchError, match="HTTP 404"):
        fetch_url("http://x.com/missing")


@patch("urllib.request.urlopen")
def test_fetch_url_connection_error(mock_open):
    import urllib.error
    mock_open.side_effect = urllib.error.URLError(reason="Connection refused")
    with pytest.raises(FetchError, match="Connection refused"):
        fetch_url("http://unreachable.local")


@patch("urllib.request.urlopen")
def test_fetch_json_config(mock_open):
    payload = {"DB_HOST": "localhost", "PORT": "5432"}
    mock_open.return_value = _mock_urlopen(json.dumps(payload))
    result = fetch_json_config("http://example.com/config.json")
    assert result == payload


@patch("urllib.request.urlopen")
def test_fetch_json_config_invalid_json(mock_open):
    mock_open.return_value = _mock_urlopen("not json!!")
    with pytest.raises(FetchError, match="Invalid JSON"):
        fetch_json_config("http://example.com/bad.json")


@patch("urllib.request.urlopen")
def test_fetch_env_config(mock_open):
    mock_open.return_value = _mock_urlopen("APP_ENV=production\nDEBUG=false\n")
    result = fetch_env_config("http://example.com/.env")
    assert result["APP_ENV"] == "production"
    assert result["DEBUG"] == "false"
