"""cloner_cmd.py — CLI sub-commands for cloning / remapping configs."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.cloner import ClonerError, clone_config, clone_subset, clone_summary


def cmd_clone(args: argparse.Namespace) -> None:
    """Deep-copy a config, optionally applying key/value transforms."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    key_transform = None
    if args.uppercase_keys:
        key_transform = str.upper
    elif args.lowercase_keys:
        key_transform = str.lower

    try:
        cloned = clone_config(config, key_transform=key_transform)
    except ClonerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        print(clone_summary(config, cloned))
    else:
        print(json.dumps(cloned, indent=2))


def cmd_subset(args: argparse.Namespace) -> None:
    """Extract a subset of keys from a config."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        result = clone_subset(config, args.keys)
    except ClonerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


def build_cloner_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'clone' and 'clone-subset' sub-commands."""
    p_clone = subparsers.add_parser("clone", help="Deep-copy a config file")
    p_clone.add_argument("file", help="Path to config file")
    p_clone.add_argument("--uppercase-keys", action="store_true", help="Upper-case all keys")
    p_clone.add_argument("--lowercase-keys", action="store_true", help="Lower-case all keys")
    p_clone.add_argument("--summary", action="store_true", help="Print summary instead of JSON")
    p_clone.set_defaults(func=cmd_clone)

    p_sub = subparsers.add_parser("clone-subset", help="Extract subset of keys from a config")
    p_sub.add_argument("file", help="Path to config file")
    p_sub.add_argument("keys", nargs="+", help="Keys to include in the subset")
    p_sub.set_defaults(func=cmd_subset)
