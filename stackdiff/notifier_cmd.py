"""CLI sub-commands for managing and testing notifications."""

from __future__ import annotations

import argparse
import sys

from stackdiff.differ import diff_configs
from stackdiff.config_loader import load_config, ConfigLoadError
from stackdiff.notifier import NotifyConfig, NotifyError, notify


def cmd_test(args: argparse.Namespace) -> None:
    """Load two config files, diff them, and fire a test notification."""
    try:
        local = load_config(args.local)
        remote = load_config(args.remote)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    result = diff_configs(local, remote)
    total = len(result.added) + len(result.removed) + len(result.changed)
    print(
        f"Diff: +{len(result.added)} -{len(result.removed)} ~{len(result.changed)} "
        f"(total {total})"
    )

    cfg = _build_notify_config(args)
    try:
        notify(result, cfg)
        print("Notification dispatched.")
    except NotifyError as exc:
        print(f"notify error: {exc}", file=sys.stderr)
        sys.exit(1)


def _build_notify_config(args: argparse.Namespace) -> NotifyConfig:
    channel = args.channel
    if channel == "email":
        return NotifyConfig(
            channel="email",
            smtp_host=args.smtp_host or "",
            smtp_port=int(args.smtp_port or 587),
            sender=args.sender or "",
            recipient=args.recipient or "",
            threshold=args.threshold,
        )
    if channel == "webhook":
        return NotifyConfig(
            channel="webhook",
            webhook_url=args.webhook_url or "",
            threshold=args.threshold,
        )
    # fallback — notify() will raise NotifyError for unknown channels
    return NotifyConfig(channel=channel, threshold=args.threshold)


def build_notify_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("notify", help="send diff notifications")
    sp = p.add_subparsers(dest="notify_cmd", required=True)

    test_p = sp.add_parser("test", help="diff two files and send a notification")
    test_p.add_argument("local", help="local config file")
    test_p.add_argument("remote", help="remote/reference config file")
    test_p.add_argument(
        "--channel",
        choices=["email", "webhook"],
        required=True,
        help="notification channel",
    )
    test_p.add_argument("--threshold", type=int, default=1, metavar="N")
    # email options
    test_p.add_argument("--smtp-host", dest="smtp_host", default="localhost")
    test_p.add_argument("--smtp-port", dest="smtp_port", default=587, type=int)
    test_p.add_argument("--sender", default="")
    test_p.add_argument("--recipient", default="")
    # webhook options
    test_p.add_argument("--webhook-url", dest="webhook_url", default="")
    test_p.set_defaults(func=cmd_test)
