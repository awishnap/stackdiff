"""archiver_cmd.py – CLI sub-commands for managing diff archives."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.archiver import ArchiverError, delete_archive, list_archives, load_archive, save_archive
from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.differ import diff_configs


def cmd_save(args: argparse.Namespace) -> None:
    try:
        local = load_config(args.local)
        remote = load_config(args.remote)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    result = diff_configs(local, remote)
    meta = {"local": args.local, "remote": args.remote}
    path = save_archive(args.archive_dir, args.name, result, meta=meta)
    print(f"Archive saved: {path}")


def cmd_list(args: argparse.Namespace) -> None:
    names = list_archives(args.archive_dir)
    if not names:
        print("No archives found.")
    else:
        for n in names:
            print(n)


def cmd_show(args: argparse.Namespace) -> None:
    try:
        data = load_archive(args.archive_dir, args.name)
    except ArchiverError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(data, indent=2))


def cmd_delete(args: argparse.Namespace) -> None:
    try:
        delete_archive(args.archive_dir, args.name)
    except ArchiverError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Deleted archive: {args.name}")


def build_archive_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("archive", help="manage diff archives")
    p.add_argument("--archive-dir", default=".stackdiff/archives")
    sub = p.add_subparsers(dest="archive_cmd", required=True)

    ps = sub.add_parser("save", help="save a diff archive")
    ps.add_argument("name")
    ps.add_argument("local")
    ps.add_argument("remote")
    ps.set_defaults(func=cmd_save)

    pl = sub.add_parser("list", help="list saved archives")
    pl.set_defaults(func=cmd_list)

    psh = sub.add_parser("show", help="show archive contents")
    psh.add_argument("name")
    psh.set_defaults(func=cmd_show)

    pd = sub.add_parser("delete", help="delete an archive")
    pd.add_argument("name")
    pd.set_defaults(func=cmd_delete)
