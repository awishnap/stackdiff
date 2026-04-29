"""CLI sub-command: chain  — diff a sequence of config files in order."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.differ_chain import ChainError, build_chain, chain_summary


def cmd_run(args: argparse.Namespace) -> None:
    configs = []
    labels = []
    for path in args.files:
        try:
            configs.append(load_config(path))
            labels.append(path)
        except ConfigLoadError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)

    if args.labels:
        raw = [l.strip() for l in args.labels.split(",")]
        if len(raw) != len(configs):
            print(
                f"error: --labels count ({len(raw)}) must match file count ({len(configs)}).",
                file=sys.stderr,
            )
            sys.exit(1)
        labels = raw

    try:
        chain = build_chain(configs, labels)
    except ChainError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        print(chain_summary(chain))
    else:
        print(json.dumps(chain.as_dict(), indent=2))


def build_chain_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "chain",
        help="Diff an ordered sequence of config files (e.g. dev -> staging -> prod).",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more config files in order.",
    )
    p.add_argument(
        "--labels",
        default="",
        metavar="LABELS",
        help="Comma-separated display labels (must match number of files).",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a compact summary instead of full JSON.",
    )
    p.set_defaults(func=cmd_run)
