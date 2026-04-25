"""CLI sub-command: sort config keys."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from stackdiff.config_loader import load_config, ConfigLoadError
from stackdiff.sorter import apply_sort, sort_keys_explicit, SorterError


def cmd_run(args: argparse.Namespace) -> None:
    """Load a config file, sort its keys, and print the result."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.order:
            sorted_config = sort_keys_explicit(
                config,
                order=args.order,
                drop_missing=args.drop_missing,
            )
        else:
            sorted_config = apply_sort(
                config,
                strategy=args.strategy,
                reverse=args.reverse,
            )
    except SorterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                json.dump(sorted_config, fh, indent=2)
                fh.write("\n")
        except OSError as exc:
            print(f"error writing output: {exc}", file=sys.stderr)
            sys.exit(1)
        print(f"Sorted config written to {args.output}")
    else:
        print(json.dumps(sorted_config, indent=2))


def build_sorter_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the 'sort' sub-command."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "sort",
        help="Sort config keys using a chosen strategy",
    )
    parser.add_argument("file", help="Config file to sort (.env / .json / .yaml)")
    parser.add_argument(
        "--strategy",
        choices=["alpha", "value", "length"],
        default="alpha",
        help="Sort strategy (default: alpha)",
    )
    parser.add_argument("--reverse", action="store_true", help="Reverse the sort order")
    parser.add_argument(
        "--order",
        nargs="+",
        metavar="KEY",
        help="Explicit key order (remaining keys appended alphabetically)",
    )
    parser.add_argument(
        "--drop-missing",
        action="store_true",
        help="When --order is used, drop keys not listed in the order",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="Write sorted config to FILE as JSON")
    parser.set_defaults(func=cmd_run)
    return parser
