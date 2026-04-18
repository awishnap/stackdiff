"""Tests for stackdiff.snapshot_cmd CLI helpers."""

import argparse
import json
import os

import pytest

from stackdiff.snapshot_cmd import cmd_diff, cmd_list, cmd_save


def _make_args(**kwargs):
    defaults = {"snapshot_dir": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def dirs(tmp_path):
    snap_dir = str(tmp_path / "snaps")
    cfg_file = str(tmp_path / "staging.env")
    with open(cfg_file, "w") as fh:
        fh.write("HOST=db\nPORT=5432\n")
    return snap_dir, cfg_file


def test_cmd_save_creates_snapshot(dirs):
    snap_dir, cfg_file = dirs
    args = _make_args(name="staging", file=cfg_file, snapshot_dir=snap_dir)
    rc = cmd_save(args)
    assert rc == 0
    assert os.path.exists(os.path.join(snap_dir, "staging.json"))


def test_cmd_save_bad_file(dirs, capsys):
    snap_dir, _ = dirs
    args = _make_args(name="x", file="/no/such/file.env", snapshot_dir=snap_dir)
    rc = cmd_save(args)
    assert rc == 1
    assert "error" in capsys.readouterr().err


def test_cmd_list_empty(dirs, capsys):
    snap_dir, _ = dirs
    args = _make_args(snapshot_dir=snap_dir)
    rc = cmd_list(args)
    assert rc == 0
    assert "No snapshots" in capsys.readouterr().out


def test_cmd_list_shows_names(dirs, capsys):
    snap_dir, cfg_file = dirs
    save_args = _make_args(name="prod", file=cfg_file, snapshot_dir=snap_dir)
    cmd_save(save_args)
    list_args = _make_args(snapshot_dir=snap_dir)
    cmd_list(list_args)
    assert "prod" in capsys.readouterr().out


def test_cmd_diff_no_changes(dirs, capsys):
    snap_dir, cfg_file = dirs
    cmd_save(_make_args(name="s", file=cfg_file, snapshot_dir=snap_dir))
    rc = cmd_diff(_make_args(name="s", file=cfg_file, snapshot_dir=snap_dir))
    assert rc == 0


def test_cmd_diff_missing_snapshot(dirs, capsys):
    snap_dir, cfg_file = dirs
    rc = cmd_diff(_make_args(name="ghost", file=cfg_file, snapshot_dir=snap_dir))
    assert rc == 1
    assert "error" in capsys.readouterr().err
