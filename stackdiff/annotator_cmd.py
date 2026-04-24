"""annotator_cmd.py — CLI subcommands for managing config-key annotations."""
from __future__ import annotations

import argparse
import sys

from stackdiff.annotator import (
    AnnotatorError,
    add_note,
    get_notes,
    remove_notes,
    list_annotated_keys,
    clear_notes,
)

_DEFAULT_DIR = ".stackdiff/notes"


def cmd_add(args: argparse.Namespace) -> None:
    try:
        add_note(args.store_dir, args.namespace, args.key, args.note)
        print(f"Note added to '{args.key}' in namespace '{args.namespace}'.")
    except AnnotatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_get(args: argparse.Namespace) -> None:
    notes = get_notes(args.store_dir, args.namespace, args.key)
    if not notes:
        print(f"No notes for '{args.key}' in namespace '{args.namespace}'.")
        return
    for i, note in enumerate(notes, 1):
        print(f"  [{i}] {note}")


def cmd_remove(args: argparse.Namespace) -> None:
    count = remove_notes(args.store_dir, args.namespace, args.key)
    print(f"Removed {count} note(s) from '{args.key}'.")


def cmd_list(args: argparse.Namespace) -> None:
    keys = list_annotated_keys(args.store_dir, args.namespace)
    if not keys:
        print(f"No annotated keys in namespace '{args.namespace}'.")
        return
    for key in keys:
        print(f"  {key}")


def cmd_clear(args: argparse.Namespace) -> None:
    clear_notes(args.store_dir, args.namespace)
    print(f"Cleared all notes in namespace '{args.namespace}'.")


def build_annotator_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("annotate", help="Manage key annotations")
    p.add_argument("--store-dir", default=_DEFAULT_DIR)
    sub = p.add_subparsers(dest="annotate_cmd", required=True)

    pa = sub.add_parser("add", help="Add a note to a key")
    pa.add_argument("namespace")
    pa.add_argument("key")
    pa.add_argument("note")
    pa.set_defaults(func=cmd_add)

    pg = sub.add_parser("get", help="Show notes for a key")
    pg.add_argument("namespace")
    pg.add_argument("key")
    pg.set_defaults(func=cmd_get)

    pr = sub.add_parser("remove", help="Remove all notes for a key")
    pr.add_argument("namespace")
    pr.add_argument("key")
    pr.set_defaults(func=cmd_remove)

    pl = sub.add_parser("list", help="List annotated keys in a namespace")
    pl.add_argument("namespace")
    pl.set_defaults(func=cmd_list)

    pc = sub.add_parser("clear", help="Clear all notes in a namespace")
    pc.add_argument("namespace")
    pc.set_defaults(func=cmd_clear)
