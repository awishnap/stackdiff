"""scoper_cmd.py — CLI sub-commands for scoper (scope, list-scopes)."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.scoper import ScopeError, list_scopes, scope_config, scope_summary


def cmd_scope(args: argparse.Namespace) -> None:
    """Filter config to a single scope and print as JSON."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        scoped = scope_config(
            config,
            args.scope,
            separator=args.separator,
            strip_prefix=not args.keep_prefix,
        )
    except ScopeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        print(scope_summary(scoped, args.scope))
    else:
        print(json.dumps(scoped, indent=2))


def cmd_list(args: argparse.Namespace) -> None:
    """List all top-level scopes present in a config file."""
    try:
        config = load_config(args.file)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        scopes = list_scopes(config, separator=args.separator)
    except ScopeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if scopes:
        for s in scopes:
            print(s)
    else:
        print("(no scopes found)")


def build_scoper_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("scope", help="Scope-based config filtering commands")
    sp = p.add_subparsers(dest="scope_cmd", required=True)

    # scope filter
    p_scope = sp.add_parser("filter", help="Filter config to a named scope")
    p_scope.add_argument("file", help="Config file path")
    p_scope.add_argument("scope", help="Scope prefix (e.g. 'db')")
    p_scope.add_argument("--separator", default=".", help="Key separator (default '.')")
    p_scope.add_argument("--keep-prefix", action="store_true", help="Do not strip scope prefix from keys")
    p_scope.add_argument("--summary", action="store_true", help="Print summary line instead of JSON")
    p_scope.set_defaults(func=cmd_scope)

    # scope list
    p_list = sp.add_parser("list", help="List scopes found in a config file")
    p_list.add_argument("file", help="Config file path")
    p_list.add_argument("--separator", default=".", help="Key separator (default '.')")
    p_list.set_defaults(func=cmd_list)
