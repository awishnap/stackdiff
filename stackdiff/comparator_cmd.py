"""comparator_cmd.py — CLI sub-commands for managing named comparisons."""
from __future__ import annotations

import argparse
import sys

from stackdiff.comparator import (
    ComparatorError,
    ComparisonSpec,
    list_specs,
    load_spec,
    run_comparison,
    save_spec,
)
from stackdiff.reporter import format_report


def cmd_save(args: argparse.Namespace) -> None:
    """Persist a new comparison spec."""
    spec = ComparisonSpec(
        name=args.name,
        local_path=args.local,
        remote_path=args.remote,
        mask_sensitive=not args.no_mask,
        tags=args.tags or [],
    )
    try:
        path = save_spec(spec, args.store_dir)
        print(f"Saved comparison spec '{spec.name}' → {path}")
    except ComparatorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    """List all saved comparison specs."""
    names = list_specs(args.store_dir)
    if not names:
        print("No comparison specs saved.")
    else:
        for name in names:
            print(name)


def cmd_run(args: argparse.Namespace) -> None:
    """Run a saved comparison and print the diff report."""
    try:
        spec = load_spec(args.name, args.store_dir)
        result = run_comparison(spec)
        print(format_report(result))
        if result.added or result.removed or result.changed:
            sys.exit(1)
    except ComparatorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_comparator_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("compare", help="Manage and run named config comparisons")
    sub = p.add_subparsers(dest="compare_cmd", required=True)

    # save
    ps = sub.add_parser("save", help="Save a named comparison spec")
    ps.add_argument("name")
    ps.add_argument("--local", required=True, help="Path to local config file")
    ps.add_argument("--remote", required=True, help="Path to remote/deployed config file")
    ps.add_argument("--no-mask", action="store_true", help="Do not mask sensitive values")
    ps.add_argument("--tags", nargs="*", help="Optional tags")
    ps.add_argument("--store-dir", default=".stackdiff/comparisons")
    ps.set_defaults(func=cmd_save)

    # list
    pl = sub.add_parser("list", help="List saved comparison specs")
    pl.add_argument("--store-dir", default=".stackdiff/comparisons")
    pl.set_defaults(func=cmd_list)

    # run
    pr = sub.add_parser("run", help="Run a saved comparison")
    pr.add_argument("name")
    pr.add_argument("--store-dir", default=".stackdiff/comparisons")
    pr.set_defaults(func=cmd_run)
