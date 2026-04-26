"""scorer_cmd.py — CLI sub-command: stackdiff score <local> <remote>"""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import load_config, ConfigLoadError
from stackdiff.scorer import score_configs, ScorerError


def cmd_score(args: argparse.Namespace) -> None:
    try:
        local = load_config(args.local)
        remote = load_config(args.remote)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        result = score_configs(local, remote)
    except ScorerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result.as_dict(), indent=2))
        return

    print(f"Score : {result.score:.2%}  [{result.grade}]")
    print(f"Keys  : {result.matched_keys} matched / {result.total_keys} total")

    if args.min_score is not None and result.score < args.min_score:
        print(
            f"FAIL  : score {result.score:.2%} is below "
            f"threshold {args.min_score:.2%}",
            file=sys.stderr,
        )
        sys.exit(2)


def build_scorer_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "score",
        help="compute similarity score between two config files",
    )
    p.add_argument("local", help="path to local config file")
    p.add_argument("remote", help="path to remote / reference config file")
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="output result as JSON",
    )
    p.add_argument(
        "--min-score",
        type=float,
        default=None,
        metavar="FLOAT",
        dest="min_score",
        help="exit 2 if score is below this threshold (0.0–1.0)",
    )
    p.set_defaults(func=cmd_score)
