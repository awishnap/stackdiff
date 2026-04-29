"""CLI command for computing and displaying a diff matrix across multiple configs."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.differ_matrix import MatrixError, build_matrix, matrix_summary, most_divergent


def cmd_run(args: argparse.Namespace) -> None:
    configs: dict = {}
    for path in args.files:
        try:
            configs[path] = load_config(path)
        except ConfigLoadError as exc:
            print(f"error: cannot load '{path}': {exc}", file=sys.stderr)
            sys.exit(1)

    if len(configs) < 2:
        print("error: at least two config files are required", file=sys.stderr)
        sys.exit(1)

    try:
        matrix = build_matrix(configs)
    except MatrixError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        summary = matrix_summary(matrix)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Pairs compared : {summary['pairs_compared']}")
            print(f"Total diffs    : {summary['total_diffs']}")
            print(f"Avg diff/pair  : {summary['avg_diffs_per_pair']:.2f}")
            most_div = summary.get("most_divergent_pair")
            if most_div:
                print(f"Most divergent : {most_div[0]} <-> {most_div[1]}")
        return

    if args.most_divergent:
        pair = most_divergent(matrix)
        if pair is None:
            print("No pairs found.", file=sys.stderr)
            sys.exit(1)
        a, b, count = pair
        if args.json:
            print(json.dumps({"a": a, "b": b, "diff_count": count}))
        else:
            print(f"{a} <-> {b}  ({count} diffs)")
        return

    # Default: dump full matrix
    serialisable = {
        f"{a}::{b}": result.__dict__
        for (a, b), result in matrix.items()
    }
    print(json.dumps(serialisable, indent=2))


def build_matrix_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "matrix",
        help="compute pairwise diff matrix across multiple config files",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="config files to compare")
    p.add_argument("--summary", action="store_true", help="print aggregate summary")
    p.add_argument("--most-divergent", action="store_true", dest="most_divergent",
                   help="print the most divergent pair")
    p.add_argument("--json", action="store_true", help="output as JSON")
    p.set_defaults(func=cmd_run)
    return p
