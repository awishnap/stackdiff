"""CLI sub-commands for the patcher feature."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.differ import diff_configs
from stackdiff.patcher import PatchError, apply_patch, patch_summary


def cmd_apply(args: argparse.Namespace) -> None:
    """Load two configs, compute diff, then patch *base* toward *target*."""
    try:
        base = load_config(args.base)
        target = load_config(args.target)
    except ConfigLoadError as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        sys.exit(1)

    diff = diff_configs(base, target)
    strategy = getattr(args, "strategy", "forward")

    print(patch_summary(diff, strategy))

    if not (diff.added or diff.removed or diff.changed):
        print("Nothing to patch.")
        return

    try:
        patched = apply_patch(base, diff, strategy=strategy)
    except PatchError as exc:
        print(f"Patch error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(patched, indent=2)
    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output + "\n")
        print(f"Patched config written to {args.output}")
    else:
        print(output)


def build_patcher_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *patch* sub-command."""
    p = subparsers.add_parser("patch", help="Apply a diff as a patch to a config")
    p.add_argument("base", help="Base config file")
    p.add_argument("target", help="Target config file (defines the desired state)")
    p.add_argument(
        "--strategy",
        choices=["forward", "reverse"],
        default="forward",
        help="forward: base→target  reverse: target→base (default: forward)",
    )
    p.add_argument("-o", "--output", default="", help="Write result to file instead of stdout")
    p.set_defaults(func=cmd_apply)
