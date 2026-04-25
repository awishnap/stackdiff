"""splitter_cmd.py — CLI sub-commands for config splitting."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.splitter import SplitterError, split_by_glob, split_by_prefix


def cmd_prefix(args: argparse.Namespace) -> None:
    """Split a config file by key prefixes and print the resulting groups."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    prefixes = [p for p in args.prefix if p]  # strip empty strings
    if not prefixes:
        print("error: at least one --prefix required", file=sys.stderr)
        sys.exit(1)

    try:
        groups = split_by_prefix(
            config,
            prefixes,
            strip_prefix=args.strip,
            default_group=args.default_group or "__other__",
        )
    except SplitterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(groups, indent=2))


def cmd_glob(args: argparse.Namespace) -> None:
    """Split a config file using glob patterns (name=pattern pairs)."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    patterns: dict[str, str] = {}
    for pair in args.pattern:
        if "=" not in pair:
            print(f"error: pattern must be name=glob, got {pair!r}", file=sys.stderr)
            sys.exit(1)
        name, _, glob = pair.partition("=")
        patterns[name] = glob

    if not patterns:
        print("error: at least one --pattern required", file=sys.stderr)
        sys.exit(1)

    try:
        groups = split_by_glob(
            config,
            patterns,
            default_group=args.default_group or "__other__",
        )
    except SplitterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(groups, indent=2))


def build_splitter_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    sp = subparsers.add_parser("split", help="split config keys into named groups")
    ssp = sp.add_subparsers(dest="split_cmd", required=True)

    p_prefix = ssp.add_parser("prefix", help="split by key prefix")
    p_prefix.add_argument("file", help="config file to split")
    p_prefix.add_argument("--prefix", action="append", default=[], metavar="PREFIX", help="prefix to match (repeatable)")
    p_prefix.add_argument("--strip", action="store_true", help="strip matched prefix from output keys")
    p_prefix.add_argument("--default-group", default="__other__", metavar="NAME", help="group name for unmatched keys")
    p_prefix.set_defaults(func=cmd_prefix)

    p_glob = ssp.add_parser("glob", help="split by glob pattern")
    p_glob.add_argument("file", help="config file to split")
    p_glob.add_argument("--pattern", action="append", default=[], metavar="NAME=GLOB", help="name=glob pair (repeatable)")
    p_glob.add_argument("--default-group", default="__other__", metavar="NAME", help="group name for unmatched keys")
    p_glob.set_defaults(func=cmd_glob)
