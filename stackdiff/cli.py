"""CLI entry point for stackdiff."""

import argparse
import sys

from stackdiff.config_loader import load_config, ConfigLoadError
from stackdiff.fetcher import fetch_json_config, fetch_env_config, FetchError
from stackdiff.differ import diff_configs
from stackdiff.reporter import print_report


def _load_remote(url: str, fmt: str) -> dict:
    if fmt == "json":
        return fetch_json_config(url)
    return fetch_env_config(url)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff",
        description="Compare deployed vs local environment configs.",
    )
    parser.add_argument("local", help="Path to local config file (.env, .json, .yaml)")
    parser.add_argument(
        "remote",
        help="Remote config: a file path or HTTP(S) URL",
    )
    parser.add_argument(
        "--remote-format",
        choices=["env", "json", "yaml"],
        default="env",
        help="Format of the remote config when fetched via URL (default: env)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        local_cfg = load_config(args.local)
    except ConfigLoadError as exc:
        print(f"Error loading local config: {exc}", file=sys.stderr)
        return 1

    try:
        if args.remote.startswith("http://") or args.remote.startswith("https://"):
            remote_cfg = _load_remote(args.remote, args.remote_format)
        else:
            remote_cfg = load_config(args.remote)
    except (FetchError, ConfigLoadError) as exc:
        print(f"Error loading remote config: {exc}", file=sys.stderr)
        return 1

    result = diff_configs(local_cfg, remote_cfg)
    print_report(result, use_color=not args.no_color)
    return 0 if not result else 1


if __name__ == "__main__":
    sys.exit(main())
