"""CLI sub-commands for the transformer feature."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.transformer import (
    TransformerError,
    apply_transforms,
    lowercase_keys,
    prefix_keys,
    strip_values,
    uppercase_keys,
)

_BUILTIN: dict = {
    "uppercase": uppercase_keys,
    "lowercase": lowercase_keys,
    "strip": strip_values,
}


def _resolve_transforms(names: List[str], prefix: str | None):
    """Build a list of transform functions from CLI arguments."""
    fns = []
    for name in names:
        if name not in _BUILTIN:
            print(f"error: unknown transform {name!r}", file=sys.stderr)
            sys.exit(1)
        fns.append(_BUILTIN[name])
    if prefix is not None:
        fns.append(prefix_keys(prefix))
    return fns


def cmd_run(args: argparse.Namespace) -> None:
    """Load a config file, apply transforms, and print the result as JSON."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    transforms = _resolve_transforms(
        args.transform or [],
        getattr(args, "prefix", None),
    )

    try:
        result = apply_transforms(config, transforms)
    except TransformerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


def build_transformer_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *transform* sub-command."""
    p = subparsers.add_parser(
        "transform",
        help="apply key/value transforms to a config file",
    )
    p.add_argument("file", help="path to config file (.env, .json, .yaml)")
    p.add_argument(
        "-t",
        "--transform",
        action="append",
        metavar="NAME",
        help="built-in transform to apply: uppercase, lowercase, strip (repeatable)",
    )
    p.add_argument(
        "--prefix",
        metavar="PREFIX",
        default=None,
        help="prepend PREFIX to every key (applied last)",
    )
    p.set_defaults(func=cmd_run)
