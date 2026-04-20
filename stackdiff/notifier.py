"""Notification module: send alerts when diffs exceed thresholds."""

from __future__ import annotations

import json
import smtplib
import urllib.request
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from typing import Optional

from stackdiff.differ import DiffResult


class NotifyError(Exception):
    """Raised when a notification cannot be delivered."""


@dataclass
class NotifyConfig:
    """Holds settings for one notification channel."""

    channel: str  # "email" or "webhook"
    # email fields
    smtp_host: str = ""
    smtp_port: int = 587
    sender: str = ""
    recipient: str = ""
    # webhook fields
    webhook_url: str = ""
    # threshold: minimum total changes to trigger notification
    threshold: int = 1
    extra: dict = field(default_factory=dict)


def _should_notify(result: DiffResult, threshold: int) -> bool:
    total = len(result.added) + len(result.removed) + len(result.changed)
    return total >= threshold


def notify_email(result: DiffResult, cfg: NotifyConfig) -> None:
    """Send a diff summary via SMTP."""
    if not _should_notify(result, cfg.threshold):
        return
    body = (
        f"Added: {len(result.added)}  "
        f"Removed: {len(result.removed)}  "
        f"Changed: {len(result.changed)}"
    )
    msg = MIMEText(body)
    msg["Subject"] = "stackdiff alert: config drift detected"
    msg["From"] = cfg.sender
    msg["To"] = cfg.recipient
    try:
        with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=10) as server:
            server.sendmail(cfg.sender, [cfg.recipient], msg.as_string())
    except (smtplib.SMTPException, OSError) as exc:
        raise NotifyError(f"Email delivery failed: {exc}") from exc


def notify_webhook(result: DiffResult, cfg: NotifyConfig) -> None:
    """POST a JSON diff summary to a webhook URL."""
    if not _should_notify(result, cfg.threshold):
        return
    payload = json.dumps(
        {
            "added": list(result.added),
            "removed": list(result.removed),
            "changed": {k: list(v) for k, v in result.changed.items()},
        }
    ).encode()
    req = urllib.request.Request(
        cfg.webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status >= 400:
                raise NotifyError(f"Webhook returned HTTP {resp.status}")
    except urllib.error.URLError as exc:
        raise NotifyError(f"Webhook delivery failed: {exc}") from exc


def notify(result: DiffResult, cfg: NotifyConfig) -> None:
    """Dispatch to the appropriate channel."""
    if cfg.channel == "email":
        notify_email(result, cfg)
    elif cfg.channel == "webhook":
        notify_webhook(result, cfg)
    else:
        raise NotifyError(f"Unknown notification channel: {cfg.channel!r}")
