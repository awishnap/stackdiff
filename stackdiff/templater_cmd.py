"""CLI sub-command: render a config file through a template context."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.templater import TemplaterError, render_config


def cmd_render(args: argparse.Namespace) -> None:
    """Load *config*, apply context from *context_file*, and print the result."""
    try:
        config = load_config(args.config)
    except ConfigLoadError as exc:
        print(f"error: cannot load config: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        context = load_config(args.context)
    except ConfigLoadError as exc:
        print(f"error: cannot load context: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(context, dict):
        print("error: context file must be a key/value mapping", file=sys.stderr)
        sys.exit(1)

    strict = not args.lenient
    try:
        result = render_config(config, context, strict=strict)
    except TemplaterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


def build_templater_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """Register the ``template`` sub-command on *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "template",
        help="Render placeholder values in a config file using a context file.",
    )
    parser.add_argument("config", help="Path to the config file with {{ placeholders }}.")
    parser.add_argument(
        "context",
        help="Path to a JSON/YAML/env file whose keys are placeholder names.",
    )
    parser.add_argument(
        "--lenient",
        action="store_true",
        default=False,
        help="Leave unknown placeholders unchanged instead of raising an error.",
    )
    parser.set_defaults(func=cmd_render)
