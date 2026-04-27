"""pruner_cmd.py — CLI sub-commands for the pruner module."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.pruner import PrunerError, prune_by_pattern, prune_by_type, prune_by_value, prune_summary

_TYPE_MAP: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "none": type(None),
}


def cmd_run(args: argparse.Namespace) -> None:
    try:
        config = load_config(args.file)
    except (ConfigLoadError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.strategy == "pattern":
            result = prune_by_pattern(config, args.patterns)
        elif args.strategy == "value":
            raw_values: list = json.loads(args.values_json)
            result = prune_by_value(config, raw_values)
        elif args.strategy == "type":
            types = []
            for t in args.types:
                if t not in _TYPE_MAP:
                    print(f"error: unknown type '{t}'. choices: {list(_TYPE_MAP)}", file=sys.stderr)
                    sys.exit(1)
                types.append(_TYPE_MAP[t])
            result = prune_by_type(config, types)
        else:
            print(f"error: unknown strategy '{args.strategy}'", file=sys.stderr)
            sys.exit(1)
    except PrunerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    summary = prune_summary(config, result)
    if args.summary:
        print(json.dumps(summary, indent=2))
    else:
        print(json.dumps(result, indent=2))


def build_pruner_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("prune", help="remove keys from a config")
    p.add_argument("file", help="config file to prune")
    p.add_argument("--strategy", choices=["pattern", "value", "type"], default="pattern",
                   help="pruning strategy (default: pattern)")
    p.add_argument("--patterns", nargs="+", default=[], metavar="GLOB",
                   help="glob patterns to match keys (strategy=pattern)")
    p.add_argument("--values-json", default="[]", metavar="JSON",
                   help="JSON array of values to drop (strategy=value)")
    p.add_argument("--types", nargs="+", default=[], choices=list(_TYPE_MAP),
                   help="value types to drop (strategy=type)")
    p.add_argument("--summary", action="store_true",
                   help="print removal summary instead of pruned config")
    p.set_defaults(func=cmd_run)
