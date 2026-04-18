"""Fetch remote environment configs from URLs or SSH targets."""

import json
import urllib.request
import urllib.error
from typing import Optional


class FetchError(Exception):
    """Raised when a remote config cannot be fetched."""


def fetch_url(url: str, timeout: int = 10, headers: Optional[dict] = None) -> str:
    """Fetch raw text content from an HTTP/HTTPS URL."""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise FetchError(f"HTTP {exc.code} fetching {url}") from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"Failed to reach {url}: {exc.reason}") from exc


def fetch_json_config(url: str, timeout: int = 10, headers: Optional[dict] = None) -> dict:
    """Fetch a JSON config from a URL and return it as a dict."""
    raw = fetch_url(url, timeout=timeout, headers=headers)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FetchError(f"Invalid JSON from {url}: {exc}") from exc


def fetch_env_config(url: str, timeout: int = 10, headers: Optional[dict] = None) -> dict:
    """Fetch a .env-style config from a URL and return it as a dict."""
    from stackdiff.config_loader import load_dotenv_file
    import tempfile, os

    raw = fetch_url(url, timeout=timeout, headers=headers)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name
    try:
        return load_dotenv_file(tmp_path)
    finally:
        os.unlink(tmp_path)
