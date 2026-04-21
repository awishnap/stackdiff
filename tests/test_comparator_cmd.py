"""Tests for stackdiff/comparator_cmd.py"""
import argparse
import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

from stackdiff.comparator_cmd import build_comparator_parser, cmd_list, cmd_run, cmd_save


@pytest.fixture()
def store_dir(tmp_path: Path) -> str:
    return str(tmp_path / "comparisons")


@pytest.fixture()
def cfg_files(tmp_path: Path):
    local = tmp_path / "local.json"
    remote = tmp_path / "remote.json"
    local.write_text(json.dumps({"KEY": "a", "PORT": "8080"}))
    remote.write_text(json.dumps({"KEY": "a", "PORT": "9090"}))
    return str(local), str(remote)


def _args(**kwargs):
    defaults = {"store_dir": ".stackdiff/comparisons", "no_mask": False, "tags": []}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_save_creates_spec(store_dir, cfg_files, capsys):
    local, remote = cfg_files
    args = _args(name="prod", local=local, remote=remote, store_dir=store_dir)
    cmd_save(args)
    out = capsys.readouterr().out
    assert "prod" in out


def test_cmd_save_bad_file_exits(store_dir):
    args = _args(name="bad", local="/no/file.json", remote="/no/file.json", store_dir=store_dir)
    # save itself should succeed; run will fail — just verify save doesn't crash here
    cmd_save(args)  # spec is saved even if paths don't exist yet


def test_cmd_list_empty(store_dir, capsys):
    args = _args(store_dir=store_dir)
    cmd_list(args)
    assert "No comparison specs" in capsys.readouterr().out


def test_cmd_list_shows_names(store_dir, cfg_files, capsys):
    local, remote = cfg_files
    for name in ("alpha", "beta"):
        cmd_save(_args(name=name, local=local, remote=remote, store_dir=store_dir))
    capsys.readouterr()  # flush save output
    cmd_list(_args(store_dir=store_dir))
    out = capsys.readouterr().out
    assert "alpha" in out and "beta" in out


def test_cmd_run_exits_nonzero_on_diff(store_dir, cfg_files):
    local, remote = cfg_files
    cmd_save(_args(name="diff-test", local=local, remote=remote, no_mask=True, store_dir=store_dir))
    args = _args(name="diff-test", store_dir=store_dir)
    with pytest.raises(SystemExit) as exc:
        cmd_run(args)
    assert exc.value.code == 1


def test_build_comparator_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers(dest="cmd")
    build_comparator_parser(subs)
    parsed = root.parse_args(["compare", "list", "--store-dir", "/tmp"])
    assert parsed.cmd == "compare"
