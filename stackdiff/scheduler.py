"""Scheduled diff runs: define, persist, and trigger scheduled comparisons."""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional


class SchedulerError(Exception):
    pass


@dataclass
class ScheduleEntry:
    name: str
    profile: str
    interval_seconds: int
    last_run: Optional[float] = None
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


def _schedule_path(schedules_dir: str) -> Path:
    return Path(schedules_dir) / "schedules.json"


def _load_raw(schedules_dir: str) -> List[dict]:
    p = _schedule_path(schedules_dir)
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)


def _save_raw(schedules_dir: str, entries: List[dict]) -> None:
    p = _schedule_path(schedules_dir)
    Path(schedules_dir).mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(entries, f, indent=2)


def list_schedules(schedules_dir: str) -> List[ScheduleEntry]:
    return [ScheduleEntry(**e) for e in _load_raw(schedules_dir)]


def add_schedule(schedules_dir: str, entry: ScheduleEntry) -> None:
    entries = _load_raw(schedules_dir)
    if any(e["name"] == entry.name for e in entries):
        raise SchedulerError(f"Schedule '{entry.name}' already exists.")
    entries.append(asdict(entry))
    _save_raw(schedules_dir, entries)


def remove_schedule(schedules_dir: str, name: str) -> None:
    entries = _load_raw(schedules_dir)
    new = [e for e in entries if e["name"] != name]
    if len(new) == len(entries):
        raise SchedulerError(f"Schedule '{name}' not found.")
    _save_raw(schedules_dir, new)


def due_schedules(schedules_dir: str) -> List[ScheduleEntry]:
    now = time.time()
    result = []
    for entry in list_schedules(schedules_dir):
        if not entry.enabled:
            continue
        if entry.last_run is None or (now - entry.last_run) >= entry.interval_seconds:
            result.append(entry)
    return result


def mark_ran(schedules_dir: str, name: str) -> None:
    entries = _load_raw(schedules_dir)
    for e in entries:
        if e["name"] == name:
            e["last_run"] = time.time()
            _save_raw(schedules_dir, entries)
            return
    raise SchedulerError(f"Schedule '{name}' not found.")


def update_schedule(schedules_dir: str, name: str, **kwargs) -> None:
    """Update fields of an existing schedule entry by name.

    Raises SchedulerError if the schedule does not exist or if an
    attempt is made to change the entry's name to one that already exists.
    """
    entries = _load_raw(schedules_dir)
    for e in entries:
        if e["name"] == name:
            new_name = kwargs.get("name")
            if new_name and new_name != name and any(x["name"] == new_name for x in entries):
                raise SchedulerError(f"Schedule '{new_name}' already exists.")
            invalid = [k for k in kwargs if k not in ScheduleEntry.__dataclass_fields__]
            if invalid:
                raise SchedulerError(f"Unknown field(s): {', '.join(invalid)}")
            e.update(kwargs)
            _save_raw(schedules_dir, entries)
            return
    raise SchedulerError(f"Schedule '{name}' not found.")
