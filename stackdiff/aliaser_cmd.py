"""aliaser_cmd.py – CLI sub-commands for managing key aliases."""
from __future__ import annotations

import argparse
import sys

from stackdiff.aliaser import AliasError, add_alias, list_aliases, remove_alias


def cmd_add(args: argparse.Namespace) -> None:
    try:
        add_alias(args.store_dir, args.group, args.canonical, args.alias)
        print(f"Alias '{args.alias}' -> '{args.canonical}' added to group '{args.group}'.")
    except AliasError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_remove(args: argparse.Namespace) -> None:
    try:
        remove_alias(args.store_dir, args.group, args.canonical, args.alias)
        print(f"Alias '{args.alias}' removed from '{args.canonical}' in group '{args.group}'.")
    except AliasError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    data = list_aliases(args.store_dir, args.group)
    if not data:
        print(f"No aliases defined in group '{args.group}'.")
        return
    for canonical, alias_list in sorted(data.items()):
        print(f"{canonical}: {', '.join(alias_list)}")


def build_alias_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("alias", help="manage key aliases")
    p.add_argument("--store-dir", default=".stackdiff/aliases", dest="store_dir")
    sub = p.add_subparsers(dest="alias_cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="add an alias for a canonical key")
    p_add.add_argument("group", help="alias group name")
    p_add.add_argument("canonical", help="canonical (primary) key name")
    p_add.add_argument("alias", help="alias key name")
    p_add.set_defaults(func=cmd_add)

    # remove
    p_rm = sub.add_parser("remove", help="remove an alias")
    p_rm.add_argument("group")
    p_rm.add_argument("canonical")
    p_rm.add_argument("alias")
    p_rm.set_defaults(func=cmd_remove)

    # list
    p_ls = sub.add_parser("list", help="list all aliases in a group")
    p_ls.add_argument("group")
    p_ls.set_defaults(func=cmd_list)
