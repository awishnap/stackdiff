"""Tests for stackdiff.patcher_cmd."""

from __future__ import annotations

import argparse
import json
import os

import pytest

from stackdiff.patcher_cmd import build_patcher_parser, cmd_apply


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def cfg_files(tmp_path):
    base = tmp_path / "base.json"
    target = tmp_path / "target.json"
    base.write_text(json.dumps({"A": "1", "B": "old"}))
    target.write_text(json.dumps({"A": "1", "B": "new", "C": "3"}))
    return str(base), str(target), tmp_path


def _args(**kwargs):
    defaults = {"strategy": "forward", "output": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# build_patcher_parser
# ---------------------------------------------------------------------------

def test_build_patcher_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_patcher_parser(sub)
    args = root.parse_args(["patch", "base.json", "target.json"])
    assert hasattr(args, "func")


# ---------------------------------------------------------------------------
# cmd_apply – stdout path
# ---------------------------------------------------------------------------

def test_cmd_apply_prints_patched_config(cfg_files, capsys):
    base, target, _ = cfg_files
    args = _args(base=base, target=target)
    cmd_apply(args)
    out = capsys.readouterr().out
    data = json.loads(out.split("\n", 1)[1])  # skip summary line
    assert data["B"] == "new"
    assert data["C"] == "3"


def test_cmd_apply_prints_summary(cfg_files, capsys):
    base, target, _ = cfg_files
    args = _args(base=base, target=target)
    cmd_apply(args)
    first_line = capsys.readouterr().out.splitlines()[0]
    assert "Patch" in first_line


def test_cmd_apply_writes_output_file(cfg_files):
    base, target, tmp_path = cfg_files
    out_file = str(tmp_path / "patched.json")
    args = _args(base=base, target=target, output=out_file)
    cmd_apply(args)
    assert os.path.exists(out_file)
    data = json.loads(open(out_file).read())
    assert data["B"] == "new"


def test_cmd_apply_no_diff_prints_nothing_to_patch(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"A": "1"}))
    args = _args(base=str(cfg), target=str(cfg))
    cmd_apply(args)
    out = capsys.readouterr().out
    assert "Nothing to patch" in out


def test_cmd_apply_bad_file_exits(tmp_path):
    missing = str(tmp_path / "nope.json")
    args = _args(base=missing, target=missing)
    with pytest.raises(SystemExit):
        cmd_apply(args)
