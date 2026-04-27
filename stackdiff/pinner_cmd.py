"""CLI sub-commands for the pinner module."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.pinner import PinnerError, check_pins, list_pins, load_pins, save_pins


def cmd_save(args: argparse.Namespace) -> None:
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        sys.exit(1)

    keys = args.keys if args.keys else list(config.keys())
    pins = {k: config[k] for k in keys if k in config}
    unknown = [k for k in keys if k not in config]
    if unknown:
        print(f"Warning: keys not found in config: {', '.join(unknown)}", file=sys.stderr)

    try:
        path = save_pins(args.store, args.name, pins)
    except PinnerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Saved {len(pins)} pin(s) as '{args.name}' → {path}")


def cmd_list(args: argparse.Namespace) -> None:
    names = list_pins(args.store)
    if not names:
        print("No pins saved.")
    else:
        for name in names:
            print(name)


def cmd_check(args: argparse.Namespace) -> None:
    try:
        pins = load_pins(args.store, args.name)
    except PinnerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        sys.exit(1)

    result = check_pins(pins, config)
    print(result.summary())

    if result.missing:
        print("Missing keys: " + ", ".join(result.missing))
    for v in result.violations:
        print(f"  {v.key}: pinned={v.pinned!r}, actual={v.actual!r}")

    if not result.ok:
        sys.exit(2)


def build_pinner_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("pin", help="Manage pinned config key expectations")
    sp = p.add_subparsers(dest="pin_cmd", required=True)

    ps = sp.add_parser("save", help="Pin key values from a config file")
    ps.add_argument("name", help="Pin set name")
    ps.add_argument("file", help="Config file to read from")
    ps.add_argument("--store", default=".stackdiff/pins", help="Pin storage directory")
    ps.add_argument("--keys", nargs="+", help="Keys to pin (default: all)")
    ps.set_defaults(func=cmd_save)

    pl = sp.add_parser("list", help="List saved pin sets")
    pl.add_argument("--store", default=".stackdiff/pins")
    pl.set_defaults(func=cmd_list)

    pc = sp.add_parser("check", help="Check pinned values against a config")
    pc.add_argument("name", help="Pin set name")
    pc.add_argument("file", help="Config file to check")
    pc.add_argument("--store", default=".stackdiff/pins")
    pc.set_defaults(func=cmd_check)
