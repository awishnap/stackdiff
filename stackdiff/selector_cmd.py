"""CLI sub-commands for the key selector."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.selector import SelectorError, deselect_keys, select_keys, selection_summary


def cmd_select(args: argparse.Namespace) -> None:
    """Keep only the specified keys from a config file."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        result = select_keys(
            config,
            keys=args.keys or [],
            patterns=args.pattern or [],
        )
    except SelectorError as exc:
        print(f"Selector error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        print(json.dumps(selection_summary(config, result), indent=2))
    else:
        print(json.dumps(result, indent=2))


def cmd_deselect(args: argparse.Namespace) -> None:
    """Drop the specified keys from a config file."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        result = deselect_keys(
            config,
            keys=args.keys or [],
            patterns=args.pattern or [],
        )
    except SelectorError as exc:
        print(f"Selector error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


def build_selector_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("file", help="Config file (JSON / YAML / .env)")
    common.add_argument("-k", "--keys", nargs="+", metavar="KEY", help="Exact key names")
    common.add_argument("-p", "--pattern", nargs="+", metavar="GLOB", help="Glob patterns")

    sel = subparsers.add_parser("select", parents=[common], help="Keep matching keys")
    sel.add_argument("--summary", action="store_true", help="Print count summary instead of config")
    sel.set_defaults(func=cmd_select)

    desel = subparsers.add_parser("deselect", parents=[common], help="Drop matching keys")
    desel.set_defaults(func=cmd_deselect)
