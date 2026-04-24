"""CLI commands for drift detection against saved baselines.

Provides subcommands to run drift detection, display results,
and optionally export or notify based on detected drift.
"""

import argparse
import sys
from pathlib import Path

from stackdiff.baseline import BaselineError, load_baseline
from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.drift_detector import DriftError, detect_drift, summary as drift_summary
from stackdiff.exporter import ExportError, export_diff
from stackdiff.masker import mask_config
from stackdiff.reporter import format_report


def cmd_run(args: argparse.Namespace) -> None:
    """Run drift detection between a baseline and a local config file."""
    # Load the baseline
    try:
        baseline = load_baseline(args.name, store_dir=args.store_dir)
    except BaselineError as exc:
        print(f"[error] Could not load baseline '{args.name}': {exc}", file=sys.stderr)
        sys.exit(1)

    # Load the current config
    try:
        current = load_config(args.config)
    except ConfigLoadError as exc:
        print(f"[error] Could not load config '{args.config}': {exc}", file=sys.stderr)
        sys.exit(1)

    # Optionally mask sensitive values before comparison
    if args.mask:
        baseline = mask_config(baseline)
        current = mask_config(current)

    # Run drift detection
    try:
        report = detect_drift(
            baseline=baseline,
            current=current,
            baseline_name=args.name,
            store_dir=args.store_dir,
        )
    except DriftError as exc:
        print(f"[error] Drift detection failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # Display human-readable summary
    print(drift_summary(report))
    print()
    print(format_report(report.diff))

    # Optionally export the underlying diff result
    if args.export:
        export_path = Path(args.export)
        fmt = export_path.suffix.lstrip(".").lower() or "json"
        try:
            export_diff(report.diff, fmt=fmt, path=str(export_path))
            print(f"[info] Diff exported to {export_path}")
        except ExportError as exc:
            print(f"[error] Export failed: {exc}", file=sys.stderr)
            sys.exit(1)

    # Exit with non-zero status when drift is detected (useful for CI)
    if report.drift_detected:
        sys.exit(2)


def cmd_summary(args: argparse.Namespace) -> None:
    """Print a one-line drift summary without full diff output."""
    try:
        baseline = load_baseline(args.name, store_dir=args.store_dir)
    except BaselineError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        current = load_config(args.config)
    except ConfigLoadError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    if args.mask:
        baseline = mask_config(baseline)
        current = mask_config(current)

    try:
        report = detect_drift(
            baseline=baseline,
            current=current,
            baseline_name=args.name,
            store_dir=args.store_dir,
        )
    except DriftError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    print(drift_summary(report))

    if report.drift_detected:
        sys.exit(2)


def build_drift_report_parser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """Register 'drift' subcommand group onto an existing subparsers action."""
    drift_parser = subparsers.add_parser(
        "drift", help="Detect configuration drift against a saved baseline"
    )
    drift_sub = drift_parser.add_subparsers(dest="drift_cmd", required=True)

    # Shared arguments factory
    def _add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("name", help="Baseline name to compare against")
        p.add_argument("config", help="Path to the current config file")
        p.add_argument(
            "--store-dir",
            default=None,
            help="Directory where baselines are stored (default: ~/.stackdiff/baselines)",
        )
        p.add_argument(
            "--mask",
            action="store_true",
            help="Mask sensitive keys before comparison",
        )

    # drift run
    run_p = drift_sub.add_parser("run", help="Run drift detection and show full diff")
    _add_common(run_p)
    run_p.add_argument(
        "--export",
        metavar="FILE",
        default=None,
        help="Export diff to FILE (format inferred from extension: json, csv, md)",
    )
    run_p.set_defaults(func=cmd_run)

    # drift summary
    sum_p = drift_sub.add_parser("summary", help="Print a one-line drift summary")
    _add_common(sum_p)
    sum_p.set_defaults(func=cmd_summary)

    return drift_parser
