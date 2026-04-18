"""Tests for stackdiff.auditor."""

import pytest
from pathlib import Path

from stackdiff.auditor import (
    AuditError,
    record_event,
    load_events,
    clear_log,
)


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    return tmp_path / "audit.jsonl"


def test_record_and_load_single_event(log_file):
    record_event("diff", {"env": "staging"}, log_path=log_file)
    events = load_events(log_path=log_file)
    assert len(events) == 1
    assert events[0]["action"] == "diff"
    assert events[0]["env"] == "staging"


def test_record_multiple_events(log_file):
    record_event("diff", {"env": "staging"}, log_path=log_file)
    record_event("snapshot", {"name": "v1"}, log_path=log_file)
    events = load_events(log_path=log_file)
    assert len(events) == 2
    assert events[1]["action"] == "snapshot"


def test_event_has_timestamp(log_file):
    record_event("diff", {}, log_path=log_file)
    events = load_events(log_path=log_file)
    assert "timestamp" in events[0]
    assert "T" in events[0]["timestamp"]  # ISO format


def test_load_events_missing_file(log_file):
    events = load_events(log_path=log_file)
    assert events == []


def test_clear_log(log_file):
    record_event("diff", {"env": "prod"}, log_path=log_file)
    clear_log(log_path=log_file)
    events = load_events(log_path=log_file)
    assert events == []


def test_record_event_bad_path():
    bad_path = Path("/no_such_dir/audit.jsonl")
    with pytest.raises(AuditError):
        record_event("diff", {}, log_path=bad_path)


def test_load_events_bad_path(tmp_path):
    bad = tmp_path / "audit.jsonl"
    bad.write_text("not json\n", encoding="utf-8")
    with pytest.raises(AuditError):
        load_events(log_path=bad)


def test_clear_log_bad_path():
    with pytest.raises(AuditError):
        clear_log(log_path=Path("/no_such_dir/audit.jsonl"))
