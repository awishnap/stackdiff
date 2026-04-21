"""CLI sub-commands for managing config tags."""

from __future__ import annotations

import argparse
import sys

from stackdiff.tagger import (
    TaggerError,
    add_tag,
    clear_tags,
    find_by_tag,
    list_tags,
    remove_tag,
)


def cmd_add(args: argparse.Namespace) -> None:
    try:
        add_tag(args.tags_dir, args.name, args.tag)
        print(f"Tag '{args.tag}' added to '{args.name}'.")
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_remove(args: argparse.Namespace) -> None:
    try:
        remove_tag(args.tags_dir, args.name, args.tag)
        print(f"Tag '{args.tag}' removed from '{args.name}'.")
    except TaggerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    tags = list_tags(args.tags_dir, args.name)
    if tags:
        for t in tags:
            print(t)
    else:
        print(f"No tags for '{args.name}'.")


def cmd_find(args: argparse.Namespace) -> None:
    names = find_by_tag(args.tags_dir, args.tag)
    if names:
        for n in names:
            print(n)
    else:
        print(f"No entries tagged '{args.tag}'.")


def cmd_clear(args: argparse.Namespace) -> None:
    clear_tags(args.tags_dir, args.name)
    print(f"All tags cleared for '{args.name}'.")


def build_tagger_parser(
    subparsers: argparse._SubParsersAction,
    tags_dir: str,
) -> None:
    p = subparsers.add_parser("tag", help="Manage config tags")
    p.set_defaults(tags_dir=tags_dir)
    sub = p.add_subparsers(dest="tag_cmd", required=True)

    pa = sub.add_parser("add", help="Add a tag")
    pa.add_argument("name")
    pa.add_argument("tag")
    pa.set_defaults(func=cmd_add)

    pr = sub.add_parser("remove", help="Remove a tag")
    pr.add_argument("name")
    pr.add_argument("tag")
    pr.set_defaults(func=cmd_remove)

    pl = sub.add_parser("list", help="List tags for an entry")
    pl.add_argument("name")
    pl.set_defaults(func=cmd_list)

    pf = sub.add_parser("find", help="Find entries by tag")
    pf.add_argument("tag")
    pf.set_defaults(func=cmd_find)

    pc = sub.add_parser("clear", help="Clear all tags for an entry")
    pc.add_argument("name")
    pc.set_defaults(func=cmd_clear)
