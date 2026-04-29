"""compressor_cmd.py — CLI sub-command for compressing diff output."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import load_config, ConfigLoadError
from stackdiff.differ import diff_configs
from stackdiff.compressor import compress, compression_ratio, CompressorError


def cmd_run(args: argparse.Namespace) -> None:  # pragma: no cover (integration)
    try:
        cfg_a = load_config(args.file_a)
        cfg_b = load_config(args.file_b)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    result = diff_configs(cfg_a, cfg_b)

    try:
        compressed = compress(result, keep_unchanged_keys=args.keep_keys)
    except CompressorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.ratio:
        ratio = compression_ratio(result)
        print(f"compression ratio: {ratio:.2%}")
        return

    print(json.dumps(compressed.as_dict(), indent=2))


def build_compressor_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "compress",
        help="Show only changed/added/removed keys; suppress unchanged entries.",
    )
    p.add_argument("file_a", help="Base config file (local / staging).")
    p.add_argument("file_b", help="Target config file (remote / prod).")
    p.add_argument(
        "--keep-keys",
        action="store_true",
        default=False,
        help="Include list of unchanged key names in output.",
    )
    p.add_argument(
        "--ratio",
        action="store_true",
        default=False,
        help="Print compression ratio instead of full compressed diff.",
    )
    p.set_defaults(func=cmd_run)
    return p
