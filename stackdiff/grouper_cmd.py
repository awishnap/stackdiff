"""CLI commands for the grouper module."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import load_config, ConfigLoadError
from stackdiff.grouper import group_by_prefix, group_by_glob, GrouperError


def cmd_prefix(args: argparse.Namespace) -> None:
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    prefixes = [p.strip() for p in args.prefixes.split(",") if p.strip()]
    try:
        groups = group_by_prefix(
            config,
            prefixes,
            separator=args.separator,
            default_group=args.default_group or None,
        )
    except GrouperError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(groups, indent=2))


def cmd_glob(args: argparse.Namespace) -> None:
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        patterns = json.loads(args.patterns)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON for patterns: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        groups = group_by_glob(
            config,
            patterns,
            default_group=args.default_group or None,
        )
    except GrouperError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(groups, indent=2))


def build_grouper_parser(subparsers: argparse._SubParsersAction) -> None:
    grouper_p = subparsers.add_parser("group", help="Group config keys")
    gsub = grouper_p.add_subparsers(dest="group_cmd", required=True)

    prefix_p = gsub.add_parser("prefix", help="Group by key prefix")
    prefix_p.add_argument("file", help="Config file")
    prefix_p.add_argument("--prefixes", required=True, help="Comma-separated prefixes")
    prefix_p.add_argument("--separator", default="_", help="Prefix separator (default: _)")
    prefix_p.add_argument("--default-group", default="other", help="Group name for unmatched keys")
    prefix_p.set_defaults(func=cmd_prefix)

    glob_p = gsub.add_parser("glob", help="Group by glob pattern")
    glob_p.add_argument("file", help="Config file")
    glob_p.add_argument("--patterns", required=True, help='JSON object mapping group->glob, e.g. {"db":"DB_*"}')
    glob_p.add_argument("--default-group", default="other", help="Group name for unmatched keys")
    glob_p.set_defaults(func=cmd_glob)
