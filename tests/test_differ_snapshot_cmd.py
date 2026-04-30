"""Tests for stackdiff.differ_snapshot_cmd."""
from __future__ import annotations

import argparse
import json
import os
import sys
import pytest

from stackdiff.snapshot import save_snapshot
from stackdiff.differ_snapshot_cmd import build_snapshot_diff_parser, cmd_run


@pytest.fixture()
def snap_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return str(d)


@pytest.fixture()
def cfg_file(tmp_path):
    p = tmp_path / "live.json"
    p.write_text(json.dumps({"HOST": "db.internal", "PORT": "5432"}))
    return str(p)


@pytest.fixture()
def _saved(snap_dir):
    save_snapshot("prod", {"HOST": "db.internal", "PORT": "5432"}, snap_dir=snap_dir)


def _args(snap_dir, cfg_file, summary=False, **kw):
    ns = argparse.Namespace(
        snapshot="prod",
        config=cfg_file,
        snap_dir=snap_dir,
        summary=summary,
        **kw,
    )
    return ns


def test_build_snapshot_diff_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_snapshot_diff_parser(sub)
    args = root.parse_args(["snapshot-diff", "mysnap", "cfg.json"])
    assert args.snapshot == "mysnap"
    assert args.config == "cfg.json"


def test_cmd_run_no_drift_exits_0(snap_dir, cfg_file, _saved, capsys):
    args = _args(snap_dir, cfg_file)
    cmd_run(args)  # should not raise SystemExit
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["snapshot_name"] == "prod"


def test_cmd_run_drift_exits_2(snap_dir, tmp_path, _saved, capsys):
    live = tmp_path / "live2.json"
    live.write_text(json.dumps({"HOST": "db.external", "PORT": "5432"}))
    args = _args(snap_dir, str(live))
    with pytest.raises(SystemExit) as exc:
        cmd_run(args)
    assert exc.value.code == 2


def test_cmd_run_summary_flag(snap_dir, cfg_file, _saved, capsys):
    args = _args(snap_dir, cfg_file, summary=True)
    cmd_run(args)
    out = capsys.readouterr().out
    assert "prod" in out


def test_cmd_run_bad_config_exits_1(snap_dir, _saved):
    args = _args(snap_dir, "/nonexistent/path.json")
    with pytest.raises(SystemExit) as exc:
        cmd_run(args)
    assert exc.value.code == 1


def test_cmd_run_missing_snapshot_exits_1(snap_dir, cfg_file):
    args = argparse.Namespace(
        snapshot="ghost",
        config=cfg_file,
        snap_dir=snap_dir,
        summary=False,
    )
    with pytest.raises(SystemExit) as exc:
        cmd_run(args)
    assert exc.value.code == 1
