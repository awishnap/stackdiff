"""CLI sub-commands for flattening / unflattening configs."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.flattener import FlattenerError, flatten, unflatten


def cmd_flatten(args: argparse.Namespace) -> None:  # noqa: D401
    """Flatten a nested config file and print the result as JSON."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        flat = flatten(config, sep=args.sep)
    except FlattenerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(flat, indent=2))


def cmd_unflatten(args: argparse.Namespace) -> None:  # noqa: D401
    """Unflatten a flat JSON config file back into a nested dict."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        nested = unflatten(config, sep=args.sep)
    except FlattenerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(nested, indent=2))


def build_flattener_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *flatten* and *unflatten* sub-commands."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("file", help="Path to config file")
    common.add_argument(
        "--sep",
        default=".",
        metavar="SEP",
        help="Key separator (default: '.')",
    )

    flat_p = subparsers.add_parser(
        "flatten",
        parents=[common],
        help="Flatten a nested config to dot-separated keys",
    )
    flat_p.set_defaults(func=cmd_flatten)

    unflat_p = subparsers.add_parser(
        "unflatten",
        parents=[common],
        help="Unflatten dot-separated keys back into a nested config",
    )
    unflat_p.set_defaults(func=cmd_unflatten)
