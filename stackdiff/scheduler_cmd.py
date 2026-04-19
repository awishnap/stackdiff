"""CLI commands for managing diff schedules."""
from __future__ import annotations

import argparse
import sys

from stackdiff.scheduler import (
    ScheduleEntry,
    SchedulerError,
    add_schedule,
    due_schedules,
    list_schedules,
    remove_schedule,
)

DEFAULT_DIR = ".stackdiff/schedules"


def cmd_add(args: argparse.Namespace) -> None:
    entry = ScheduleEntry(
        name=args.name,
        profile=args.profile,
        interval_seconds=args.interval,
        tags=args.tags or [],
    )
    try:
        add_schedule(args.schedules_dir, entry)
        print(f"Schedule '{args.name}' added (every {args.interval}s, profile={args.profile}).")
    except SchedulerError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    entries = list_schedules(args.schedules_dir)
    if not entries:
        print("No schedules defined.")
        return
    for e in entries:
        status = "enabled" if e.enabled else "disabled"
        last = f"{e.last_run:.0f}" if e.last_run else "never"
        print(f"  {e.name}: profile={e.profile} interval={e.interval_seconds}s status={status} last_run={last}")


def cmd_remove(args: argparse.Namespace) -> None:
    try:
        remove_schedule(args.schedules_dir, args.name)
        print(f"Schedule '{args.name}' removed.")
    except SchedulerError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_due(args: argparse.Namespace) -> None:
    due = due_schedules(args.schedules_dir)
    if not due:
        print("No schedules are due.")
        return
    for e in due:
        print(f"  DUE: {e.name} (profile={e.profile})")


def build_schedule_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="stackdiff schedule")
        sub = parser.add_subparsers(dest="schedule_cmd")
    else:
        parser = subparsers.add_parser("schedule", help="Manage diff schedules")
        sub = parser.add_subparsers(dest="schedule_cmd")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--schedules-dir", default=DEFAULT_DIR)

    p_add = sub.add_parser("add", parents=[common])
    p_add.add_argument("name")
    p_add.add_argument("--profile", required=True)
    p_add.add_argument("--interval", type=int, default=3600)
    p_add.add_argument("--tags", nargs="*")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", parents=[common])
    p_list.set_defaults(func=cmd_list)

    p_remove = sub.add_parser("remove", parents=[common])
    p_remove.add_argument("name")
    p_remove.set_defaults(func=cmd_remove)

    p_due = sub.add_parser("due", parents=[common])
    p_due.set_defaults(func=cmd_due)

    return parser
