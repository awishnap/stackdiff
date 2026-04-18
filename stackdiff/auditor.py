"""Audit log for config diff operations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

AUDIT_LOG_ENV = "STACKDIFF_AUDIT_LOG"
DEFAULT_AUDIT_LOG = ".stackdiff_audit.jsonl"


class AuditError(Exception):
    """Raised when audit log operations fail."""


def _audit_log_path() -> Path:
    return Path(os.environ.get(AUDIT_LOG_ENV, DEFAULT_AUDIT_LOG))


def record_event(
    action: str,
    details: Dict[str, Any],
    log_path: Path | None = None,
) -> None:
    """Append a single audit event to the JSONL log file."""
    path = log_path or _audit_log_path()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        **details,
    }
    try:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except OSError as exc:
        raise AuditError(f"Failed to write audit log {path}: {exc}") from exc


def load_events(log_path: Path | None = None) -> List[Dict[str, Any]]:
    """Return all audit events from the log file."""
    path = log_path or _audit_log_path()
    if not path.exists():
        return []
    events: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"Failed to read audit log {path}: {exc}") from exc
    return events


def clear_log(log_path: Path | None = None) -> None:
    """Truncate the audit log."""
    path = log_path or _audit_log_path()
    try:
        path.write_text("", encoding="utf-8")
    except OSError as exc:
        raise AuditError(f"Failed to clear audit log {path}: {exc}") from exc
