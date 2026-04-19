"""Tests for stackdiff.scheduler."""
import time
import pytest
from stackdiff.scheduler import (
    ScheduleEntry,
    SchedulerError,
    add_schedule,
    due_schedules,
    list_schedules,
    mark_ran,
    remove_schedule,
)


@pytest.fixture
def sched_dir(tmp_path):
    return str(tmp_path / "schedules")


def _entry(name="nightly", profile="prod", interval=3600):
    return ScheduleEntry(name=name, profile=profile, interval_seconds=interval)


def test_list_empty(sched_dir):
    assert list_schedules(sched_dir) == []


def test_add_and_list(sched_dir):
    add_schedule(sched_dir, _entry())
    entries = list_schedules(sched_dir)
    assert len(entries) == 1
    assert entries[0].name == "nightly"
    assert entries[0].profile == "prod"


def test_add_duplicate_raises(sched_dir):
    add_schedule(sched_dir, _entry())
    with pytest.raises(SchedulerError, match="already exists"):
        add_schedule(sched_dir, _entry())


def test_remove_schedule(sched_dir):
    add_schedule(sched_dir, _entry())
    remove_schedule(sched_dir, "nightly")
    assert list_schedules(sched_dir) == []


def test_remove_missing_raises(sched_dir):
    with pytest.raises(SchedulerError, match="not found"):
        remove_schedule(sched_dir, "ghost")


def test_due_schedules_never_run(sched_dir):
    add_schedule(sched_dir, _entry(interval=3600))
    due = due_schedules(sched_dir)
    assert len(due) == 1


def test_due_schedules_recently_run(sched_dir):
    add_schedule(sched_dir, _entry(interval=3600))
    mark_ran(sched_dir, "nightly")
    due = due_schedules(sched_dir)
    assert due == []


def test_due_schedules_overdue(sched_dir):
    entry = ScheduleEntry(name="fast", profile="staging", interval_seconds=1, last_run=time.time() - 10)
    add_schedule(sched_dir, entry)
    due = due_schedules(sched_dir)
    assert any(e.name == "fast" for e in due)


def test_disabled_schedule_not_due(sched_dir):
    entry = ScheduleEntry(name="off", profile="prod", interval_seconds=1, enabled=False)
    add_schedule(sched_dir, entry)
    assert due_schedules(sched_dir) == []


def test_mark_ran_missing_raises(sched_dir):
    with pytest.raises(SchedulerError, match="not found"):
        mark_ran(sched_dir, "ghost")
