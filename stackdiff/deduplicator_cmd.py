"""CLI subcommands for the deduplicator feature."""

from __future__ import annotations

import argparse
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.deduplicator import (
    DeduplicatorError,
    dedup_summary,
    drop_duplicate_keys,
    find_duplicate_values,
)


def cmd_check(args: argparse.Namespace) -> None:
    """Report duplicate values in a config file without modifying it."""
    try:
        cfg = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(dedup_summary(cfg))
    dupes = find_duplicate_values(cfg)
    if dupes:
        sys.exit(2)  # non-zero exit so CI pipelines can catch duplicates


def cmd_clean(args: argparse.Namespace) -> None:
    """Print a deduplicated version of a config file."""
    try:
        cfg = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        cleaned = drop_duplicate_keys(cfg, keep=args.keep)
    except DeduplicatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    removed = set(cfg) - set(cleaned)
    for key in sorted(removed):
        print(f"dropped: {key}")

    import json
    print(json.dumps(cleaned, indent=2))


def build_dedup_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'dedup' subcommands onto an existing subparsers action."""
    dedup = subparsers.add_parser("dedup", help="detect/remove duplicate config values")
    sub = dedup.add_subparsers(dest="dedup_cmd", required=True)

    # check
    p_check = sub.add_parser("check", help="report duplicate values")
    p_check.add_argument("file", help="config file to inspect")
    p_check.set_defaults(func=cmd_check)

    # clean
    p_clean = sub.add_parser("clean", help="print config with duplicates removed")
    p_clean.add_argument("file", help="config file to clean")
    p_clean.add_argument(
        "--keep",
        choices=["first", "last"],
        default="first",
        help="which occurrence to keep (default: first)",
    )
    p_clean.set_defaults(func=cmd_clean)
