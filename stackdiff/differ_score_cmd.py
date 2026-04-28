"""CLI command for the scored diff feature."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import load_config, ConfigLoadError
from stackdiff.differ_score import scored_diff, ScoredDiffError


def cmd_run(args: argparse.Namespace) -> None:
    try:
        cfg_a = load_config(args.file_a)
        cfg_b = load_config(args.file_b)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        result = scored_diff(
            cfg_a,
            cfg_b,
            label_a=args.label_a or args.file_a,
            label_b=args.label_b or args.file_b,
        )
    except ScoredDiffError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result.as_dict(), indent=2))
    else:
        print(result.summary())
        d = result.diff
        if d.added:
            print("  added:", ", ".join(sorted(d.added)))
        if d.removed:
            print("  removed:", ", ".join(sorted(d.removed)))
        if d.changed:
            for k, (old, new) in sorted(d.changed.items()):
                print(f"  changed: {k}: {old!r} -> {new!r}")


def build_scored_diff_parser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "scored-diff",
        help="diff two configs and show a similarity score",
    )
    p.add_argument("file_a", help="first config file")
    p.add_argument("file_b", help="second config file")
    p.add_argument("--label-a", default="", help="display label for file_a")
    p.add_argument("--label-b", default="", help="display label for file_b")
    p.add_argument("--json", action="store_true", help="output as JSON")
    p.set_defaults(func=cmd_run)
    return p
