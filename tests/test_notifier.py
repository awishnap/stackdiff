"""Tests for stackdiff.notifier."""

from __future__ import annotations

import json
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from stackdiff.differ import DiffResult
from stackdiff.notifier import (
    NotifyConfig,
    NotifyError,
    notify,
    notify_email,
    notify_webhook,
)


def _result(added=None, removed=None, changed=None) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or {},
        unchanged={},
    )


# ── threshold guard ────────────────────────────────────────────────────────────

def test_below_threshold_skips_email():
    cfg = NotifyConfig(channel="email", threshold=5)
    result = _result(added=["A"])  # total=1 < 5
    with patch("smtplib.SMTP") as mock_smtp:
        notify_email(result, cfg)
        mock_smtp.assert_not_called()


def test_below_threshold_skips_webhook():
    cfg = NotifyConfig(channel="webhook", threshold=5, webhook_url="http://x")
    result = _result(added=["A"])
    with patch("urllib.request.urlopen") as mock_open:
        notify_webhook(result, cfg)
        mock_open.assert_not_called()


# ── email ──────────────────────────────────────────────────────────────────────

def test_notify_email_sends_message():
    cfg = NotifyConfig(
        channel="email",
        smtp_host="localhost",
        smtp_port=25,
        sender="a@x.com",
        recipient="b@x.com",
        threshold=1,
    )
    result = _result(added=["KEY"])
    mock_server = MagicMock()
    with patch("smtplib.SMTP", return_value=mock_server) as mock_cls:
        mock_cls.return_value.__enter__ = lambda s: mock_server
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        notify_email(result, cfg)
        mock_server.sendmail.assert_called_once()


def test_notify_email_raises_on_smtp_error():
    import smtplib

    cfg = NotifyConfig(
        channel="email", smtp_host="bad", sender="a@x", recipient="b@x", threshold=1
    )
    result = _result(added=["K"])
    with patch("smtplib.SMTP", side_effect=smtplib.SMTPException("boom")):
        with pytest.raises(NotifyError, match="Email delivery failed"):
            notify_email(result, cfg)


# ── webhook ────────────────────────────────────────────────────────────────────

def test_notify_webhook_posts_json():
    cfg = NotifyConfig(
        channel="webhook", webhook_url="http://hook.local/post", threshold=1
    )
    result = _result(removed=["OLD"])
    fake_resp = SimpleNamespace(status=200)
    fake_resp.__enter__ = lambda s: fake_resp
    fake_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=fake_resp) as mock_open:
        notify_webhook(result, cfg)
        mock_open.assert_called_once()


def test_notify_webhook_raises_on_http_error():
    import urllib.error

    cfg = NotifyConfig(
        channel="webhook", webhook_url="http://hook.local/post", threshold=1
    )
    result = _result(added=["X"])
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("refused"),
    ):
        with pytest.raises(NotifyError, match="Webhook delivery failed"):
            notify_webhook(result, cfg)


# ── dispatch ───────────────────────────────────────────────────────────────────

def test_notify_unknown_channel_raises():
    cfg = NotifyConfig(channel="slack")
    with pytest.raises(NotifyError, match="Unknown notification channel"):
        notify(_result(added=["K"]), cfg)
