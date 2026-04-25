"""caster_cmd.py — CLI sub-commands for the caster module."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from stackdiff.caster import CasterError, cast_config, cast_summary
from stackdiff.config_loader import ConfigLoadError, load_config


def cmd_run(args: argparse.Namespace) -> None:
    """Apply a type-map JSON file to a config file and print the result."""
    try:
        config = load_config(args.config)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.type_map, encoding="utf-8") as fh:
            type_map = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error loading type map: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(type_map, dict):
        print("error: type map must be a JSON object", file=sys.stderr)
        sys.exit(1)

    try:
        casted = cast_config(config, type_map, strict=not args.lenient)
    except CasterError as exc:
        print(f"cast error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        print(cast_summary(config, casted))
    else:
        print(json.dumps(casted, indent=2))


def build_caster_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *cast* sub-command onto *subparsers*."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        "cast",
        help="Cast config values to explicit types via a type-map JSON file",
    )
    p.add_argument("config", help="Path to the config file (JSON/YAML/.env)")
    p.add_argument("type_map", help="Path to a JSON file mapping keys to types")
    p.add_argument(
        "--lenient",
        action="store_true",
        help="Skip keys in the type map that are absent from the config",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a human-readable summary instead of the full casted config",
    )
    p.set_defaults(func=cmd_run)
