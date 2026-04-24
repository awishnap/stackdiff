"""Tests for stackdiff.baseline_cmd."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

from stackdiff.baseline_cmd import build_baseline_parser, cmd_compare, cmd_delete, cmd_list, cmd_save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path / "baselines")


@pytest.fixture()
def cfg_file(tmp_path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"HOST": "db", "PORT": "5432"}))
    return str(p)


def _args(**kwargs):
    ns = argparse.Namespace(baseline_dir=".baselines")
    ns.__dict__.update(kwargs)
    return ns


def test_cmd_save_creates_baseline(base_dir, cfg_file, capsys):
    args = _args(baseline_dir=base_dir, name="prod", file=cfg_file)
    cmd_save(args)
    out = capsys.readouterr().out
    assert "prod" in out


def test_cmd_save_bad_file_exits(base_dir):
    args = _args(baseline_dir=base_dir, name="x", file="/no/such/file.json")
    with pytest.raises(SystemExit):
        cmd_save(args)


def test_cmd_list_empty(base_dir, capsys):
    args = _args(baseline_dir=base_dir)
    cmd_list(args)
    assert "No baselines" in capsys.readouterr().out


def test_cmd_list_shows_names(base_dir, cfg_file, capsys):
    save_args = _args(baseline_dir=base_dir, name="staging", file=cfg_file)
    cmd_save(save_args)
    cmd_list(_args(baseline_dir=base_dir))
    assert "staging" in capsys.readouterr().out


def test_cmd_delete_removes(base_dir, cfg_file, capsys):
    cmd_save(_args(baseline_dir=base_dir, name="old", file=cfg_file))
    cmd_delete(_args(baseline_dir=base_dir, name="old"))
    assert "deleted" in capsys.readouterr().out


def test_cmd_delete_missing_exits(base_dir):
    with pytest.raises(SystemExit):
        cmd_delete(_args(baseline_dir=base_dir, name="ghost"))


def test_cmd_compare_output(base_dir, cfg_file, capsys):
    cmd_save(_args(baseline_dir=base_dir, name="base", file=cfg_file))
    cmd_compare(_args(baseline_dir=base_dir, name="base", file=cfg_file))
    out = capsys.readouterr().out
    assert out  # report printed


def test_build_baseline_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    build_baseline_parser(sub)
    args = parser.parse_args(["baseline", "list"])
    assert args.cmd == "baseline"
