"""CLI sub-commands for profile management."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from stackdiff.profiler import (
    ProfileError,
    delete_profile,
    list_profiles,
    load_profile,
    save_profile,
)


def cmd_save(args: argparse.Namespace) -> None:
    base = Path(args.profiles_dir)
    try:
        with open(args.file) as fh:
            data = json.load(fh)
    except OSError as exc:
        print(f"error: cannot read file: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in '{args.file}': {exc}", file=sys.stderr)
        sys.exit(1)
    path = save_profile(args.name, data, base=base)
    print(f"Profile '{args.name}' saved to {path}")


def cmd_list(args: argparse.Namespace) -> None:
    base = Path(args.profiles_dir)
    names = list_profiles(base=base)
    if not names:
        print("No profiles saved.")
    else:
        for name in names:
            print(name)


def cmd_show(args: argparse.Namespace) -> None:
    base = Path(args.profiles_dir)
    try:
        data = load_profile(args.name, base=base)
    except ProfileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(data, indent=2))


def cmd_delete(args: argparse.Namespace) -> None:
    base = Path(args.profiles_dir)
    try:
        delete_profile(args.name, base=base)
    except ProfileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Profile '{args.name}' deleted.")


def build_profile_parser(sub: argparse._SubParsersAction, default_dir: str) -> None:
    p = sub.add_parser("profile", help="manage named profiles")
    p.add_argument("--profiles-dir", default=default_dir)
    ps = p.add_subparsers(dest="profile_cmd", required=True)

    sp = ps.add_parser("save", help="save a profile from a JSON file")
    sp.add_argument("name")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_save)

    lp = ps.add_parser("list", help="list saved profiles")
    lp.set_defaults(func=cmd_list)

    shp = ps.add_parser("show", help="print a profile")
    shp.add_argument("name")
    shp.set_defaults(func=cmd_show)

    dp = ps.add_parser("delete", help="delete a profile")
    dp.add_argument("name")
    dp.set_defaults(func=cmd_delete)
