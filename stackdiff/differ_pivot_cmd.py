"""CLI sub-command: pivot – render a diff as a flat per-key table."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.differ import diff_configs
from stackdiff.differ_pivot import PivotError, pivot_diff


def cmd_run(args: argparse.Namespace) -> None:
    try:
        cfg_a = load_config(args.file_a)
        cfg_b = load_config(args.file_b)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        result = diff_configs(cfg_a, cfg_b)
        table = pivot_diff(result, include_unchanged=args.include_unchanged)
    except PivotError as exc:
        print(f"pivot error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.status:
        statuses = [s.strip() for s in args.status.split(",")]
        table = table.filter_status(*statuses)

    if args.summary:
        counts: dict[str, int] = {}
        for row in table.rows:
            counts[row.status] = counts.get(row.status, 0) + 1
        print(json.dumps(counts, indent=2))
    else:
        print(json.dumps(table.as_dict(), indent=2))


def build_pivot_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "pivot",
        help="show diff as a flat per-key table",
    )
    p.add_argument("file_a", help="baseline config file")
    p.add_argument("file_b", help="target config file")
    p.add_argument(
        "--include-unchanged",
        action="store_true",
        default=False,
        help="include unchanged keys in the output",
    )
    p.add_argument(
        "--status",
        default="",
        metavar="STATUSES",
        help="comma-separated list of statuses to include (e.g. added,changed)",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="print status counts instead of full table",
    )
    p.set_defaults(func=cmd_run)
    return p
