"""CLI sub-commands for snapshot-based diffing."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import load_config, ConfigLoadError
from stackdiff.differ_snapshot import diff_against_snapshot, SnapshotDiffError


def cmd_run(args: argparse.Namespace) -> None:
    """Diff a named snapshot against a local config file."""
    try:
        live_cfg = load_config(args.config)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    kwargs: dict = {}
    if args.snap_dir:
        kwargs["snap_dir"] = args.snap_dir

    try:
        result = diff_against_snapshot(
            snapshot_name=args.snapshot,
            live_config=live_cfg,
            label_a="snapshot",
            label_b=args.config,
            **kwargs,
        )
    except SnapshotDiffError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        print(result.summary())
    else:
        print(json.dumps(result.as_dict(), indent=2))

    if result.has_drift():
        sys.exit(2)


def build_snapshot_diff_parser(
    subparsers: "argparse._SubParsersAction",
) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "snapshot-diff",
        help="Diff a saved snapshot against a local config file.",
    )
    p.add_argument("snapshot", help="Name of the saved snapshot.")
    p.add_argument("config", help="Path to the local config file.")
    p.add_argument(
        "--snap-dir",
        default=None,
        metavar="DIR",
        help="Override snapshot storage directory.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary instead of full JSON.",
    )
    p.set_defaults(func=cmd_run)
    return p
