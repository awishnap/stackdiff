"""CLI command for differ_graph: build and inspect config diff graphs."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.differ_graph import GraphError, build_graph


def cmd_run(args: argparse.Namespace) -> None:
    configs = {}
    for path in args.files:
        try:
            configs[path] = load_config(path)
        except ConfigLoadError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)

    try:
        graph = build_graph(configs, min_shared_keys=args.min_shared)
    except GraphError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        print(graph.summary())
        if graph.edges:
            print(f"most connected: {graph.most_connected()}")
        return

    print(json.dumps(graph.as_dict(), indent=2))


def build_graph_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "graph",
        help="Build a relationship graph from multiple config diffs.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more config files to graph.",
    )
    p.add_argument(
        "--min-shared",
        type=int,
        default=1,
        metavar="N",
        dest="min_shared",
        help="Minimum shared keys required to create an edge (default: 1).",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary instead of full JSON.",
    )
    p.set_defaults(func=cmd_run)
