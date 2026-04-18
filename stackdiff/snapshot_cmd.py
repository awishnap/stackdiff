"""CLI helpers for snapshot sub-commands (save / load / list)."""

from __future__ import annotations

import argparse
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.differ import diff_configs
from stackdiff.reporter import print_report
from stackdiff.snapshot import SnapshotError, list_snapshots, load_snapshot, save_snapshot


def cmd_save(args: argparse.Namespace) -> int:
    """Load a local config file and persist it as a named snapshot."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        path = save_snapshot(args.name, config, snapshot_dir=args.snapshot_dir)
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Snapshot '{args.name}' saved to {path}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List all stored snapshots."""
    names = list_snapshots(args.snapshot_dir)
    if not names:
        print("No snapshots found.")
    else:
        for name in names:
            print(name)
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    """Diff a local config file against a saved snapshot."""
    try:
        local = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        snap = load_snapshot(args.name, snapshot_dir=args.snapshot_dir)
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = diff_configs(snap, local)
    print_report(result, label_a=f"snapshot:{args.name}", label_b=args.file)
    return 1 if result.added or result.removed or result.changed else 0


def build_snapshot_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--snapshot-dir", default=".stackdiff_snapshots", metavar="DIR")

    p_save = subparsers.add_parser("snapshot-save", parents=[common], help="Save a config snapshot")
    p_save.add_argument("name", help="Snapshot name")
    p_save.add_argument("file", help="Config file to snapshot")
    p_save.set_defaults(func=cmd_save)

    p_list = subparsers.add_parser("snapshot-list", parents=[common], help="List snapshots")
    p_list.set_defaults(func=cmd_list)

    p_diff = subparsers.add_parser("snapshot-diff", parents=[common], help="Diff file vs snapshot")
    p_diff.add_argument("name", help="Snapshot name")
    p_diff.add_argument("file", help="Local config file")
    p_diff.set_defaults(func=cmd_diff)
