"""Tests for stackdiff.notifier_cmd."""

from __future__ import annotations

import argparse
import json
import os
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

from stackdiff.notifier_cmd import cmd_test, build_notify_parser


def _args(**kwargs) -> argparse.Namespace:
    defaults = dict(
        channel="webhook",
        threshold=1,
        smtp_host="localhost",
        smtp_port=587,
        sender="",
        recipient="",
        webhook_url="http://hook.test/",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _write_json(path, data):
    """Write *data* as JSON to *path* and return the path as a string."""
    path.write_text(json.dumps(data))
    return str(path)


# ── build_notify_parser ────────────────────────────────────────────────────────

def test_build_notify_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    build_notify_parser(sub)
    ns = parser.parse_args(
        [
            "notify", "test",
            "a.json", "b.json",
            "--channel", "webhook",
            "--webhook-url", "http://x",
        ]
    )
    assert ns.notify_cmd == "test"
    assert ns.channel == "webhook"


# ── cmd_test ───────────────────────────────────────────────────────────────────

def test_cmd_test_dispatches_webhook(tmp_path):
    local_f = tmp_path / "local.json"
    remote_f = tmp_path / "remote.json"
    _write_json(local_f, {"A": "1", "B": "2"})
    _write_json(remote_f, {"A": "1", "C": "3"})

    args = _args(local=str(local_f), remote=str(remote_f))

    fake_resp = SimpleNamespace(status=200)
    fake_resp.__enter__ = lambda s: fake_resp
    fake_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=fake_resp) as mock_open:
        cmd_test(args)
        mock_open.assert_called_once()


def test_cmd_test_below_threshold_no_call(tmp_path):
    local_f = tmp_path / "local.json"
    remote_f = tmp_path / "remote.json"
    _write_json(local_f, {"A": "1"})
    _write_json(remote_f, {"A": "1"})

    args = _args(local=str(local_f), remote=str(remote_f), threshold=5)

    with patch("urllib.request.urlopen") as mock_open:
        cmd_test(args)
        mock_open.assert_not_called()


def test_cmd_test_bad_file_exits(tmp_path):
    args = _args(local="no_such.json", remote="also_no.json")
    with pytest.raises(SystemExit) as exc_info:
        cmd_test(args)
    assert exc_info.value.code == 1


def test_cmd_test_notify_error_exits(tmp_path):
    import urllib.error

    local_f = tmp_path / "l.json"
    remote_f = tmp_path / "r.json"
    _write_json(local_f, {"X": "1"})
    _write_json(remote_f, {"Y": "2"})

    args = _args(local=str(local_f), remote=str(remote_f))

    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("refused"),
    ):
        with pytest.raises(SystemExit) as exc_info:
            cmd_test(args)
        assert exc_info.value.code == 1
