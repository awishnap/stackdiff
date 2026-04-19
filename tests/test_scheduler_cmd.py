"""Tests for stackdiff.scheduler_cmd."""
import argparse
import pytest
from stackdiff.scheduler_cmd import cmd_add, cmd_list, cmd_remove, cmd_due
from stackdiff.scheduler import add_schedule, ScheduleEntry


@pytest.fixture
def sched_dir(tmp_path):
    return str(tmp_path / "schedules")


def _args(sched_dir, **kwargs):
    defaults = dict(
        schedules_dir=sched_dir,
        name="daily",
        profile="prod",
        interval=3600,
        tags=None,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_add_creates_schedule(sched_dir, capsys):
    cmd_add(_args(sched_dir))
    out = capsys.readouterr().out
    assert "daily" in out
    assert "added" in out


def test_cmd_add_duplicate_exits(sched_dir):
    cmd_add(_args(sched_dir))
    with pytest.raises(SystemExit):
        cmd_add(_args(sched_dir))


def test_cmd_list_empty(sched_dir, capsys):
    cmd_list(_args(sched_dir))
    assert "No schedules" in capsys.readouterr().out


def test_cmd_list_shows_entries(sched_dir, capsys):
    cmd_add(_args(sched_dir))
    cmd_list(_args(sched_dir))
    out = capsys.readouterr().out
    assert "daily" in out
    assert "prod" in out


def test_cmd_remove_existing(sched_dir, capsys):
    cmd_add(_args(sched_dir))
    cmd_remove(_args(sched_dir, name="daily"))
    assert "removed" in capsys.readouterr().out


def test_cmd_remove_missing_exits(sched_dir):
    with pytest.raises(SystemExit):
        cmd_remove(_args(sched_dir, name="ghost"))


def test_cmd_due_none(sched_dir, capsys):
    cmd_due(_args(sched_dir))
    assert "No schedules" in capsys.readouterr().out


def test_cmd_due_lists_overdue(sched_dir, capsys):
    import time
    entry = ScheduleEntry(name="fast", profile="staging", interval_seconds=1, last_run=time.time() - 10)
    add_schedule(sched_dir, entry)
    cmd_due(_args(sched_dir))
    out = capsys.readouterr().out
    assert "fast" in out
