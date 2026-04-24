"""CLI sub-commands for baseline management."""

from __future__ import annotations

import argparse
import sys

from stackdiff.baseline import (
    BaselineError,
    compare_to_baseline,
    delete_baseline,
    list_baselines,
    load_baseline,
    save_baseline,
)
from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.reporter import format_report


def cmd_save(args: argparse.Namespace) -> None:
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    path = save_baseline(args.name, config, args.baseline_dir)
    print(f"Baseline '{args.name}' saved to {path}")


def cmd_list(args: argparse.Namespace) -> None:
    names = list_baselines(args.baseline_dir)
    if not names:
        print("No baselines saved.")
    else:
        for name in names:
            print(name)


def cmd_delete(args: argparse.Namespace) -> None:
    try:
        delete_baseline(args.name, args.baseline_dir)
        print(f"Baseline '{args.name}' deleted.")
    except BaselineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_compare(args: argparse.Namespace) -> None:
    try:
        config = load_config(args.file)
        result = compare_to_baseline(args.name, config, args.baseline_dir)
    except (BaselineError, ConfigLoadError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(format_report(result))


def build_baseline_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("baseline", help="Manage config baselines")
    p.add_argument("--baseline-dir", default=".stackdiff/baselines")
    sub = p.add_subparsers(dest="baseline_cmd", required=True)

    sv = sub.add_parser("save", help="Save current config as a baseline")
    sv.add_argument("name")
    sv.add_argument("file")
    sv.set_defaults(func=cmd_save)

    ls = sub.add_parser("list", help="List saved baselines")
    ls.set_defaults(func=cmd_list)

    rm = sub.add_parser("delete", help="Delete a baseline")
    rm.add_argument("name")
    rm.set_defaults(func=cmd_delete)

    cmp = sub.add_parser("compare", help="Compare a config file against a baseline")
    cmp.add_argument("name")
    cmp.add_argument("file")
    cmp.set_defaults(func=cmd_compare)
