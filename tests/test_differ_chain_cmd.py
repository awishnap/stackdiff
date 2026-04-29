"""Tests for stackdiff.differ_chain_cmd."""
import argparse
import json
import os
import sys
from pathlib import Path

import pytest

from stackdiff.differ_chain_cmd import build_chain_parser, cmd_run


@pytest.fixture()
def cfg_files(tmp_path: Path):
    dev = tmp_path / "dev.json"
    stg = tmp_path / "stg.json"
    prd = tmp_path / "prd.json"
    dev.write_text(json.dumps({"HOST": "dev", "PORT": "8000", "DEBUG": "true"}))
    stg.write_text(json.dumps({"HOST": "stg", "PORT": "8000", "DEBUG": "false", "NEW": "1"}))
    prd.write_text(json.dumps({"HOST": "prd", "PORT": "443", "DEBUG": "false"}))
    return {"dev": str(dev), "stg": str(stg), "prd": str(prd)}


def _args(**kwargs):
    defaults = {"files": [], "labels": "", "summary": False}
    defaults.update(kwargs)
    ns = argparse.Namespace(**defaults)
    return ns


def test_build_chain_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_chain_parser(sub)
    args = parser.parse_args(["chain", "a.json", "b.json"])
    assert args.files == ["a.json", "b.json"]


def test_cmd_run_outputs_json(cfg_files, capsys):
    args = _args(files=[cfg_files["dev"], cfg_files["stg"]])
    cmd_run(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) == 1
    assert "left" in data[0]


def test_cmd_run_summary_flag(cfg_files, capsys):
    args = _args(files=[cfg_files["dev"], cfg_files["stg"]], summary=True)
    cmd_run(args)
    out = capsys.readouterr().out
    assert "->" in out


def test_cmd_run_three_files_two_links(cfg_files, capsys):
    args = _args(files=[cfg_files["dev"], cfg_files["stg"], cfg_files["prd"]])
    cmd_run(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 2


def test_cmd_run_custom_labels(cfg_files, capsys):
    args = _args(
        files=[cfg_files["dev"], cfg_files["stg"]],
        labels="dev,staging",
    )
    cmd_run(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data[0]["left"] == "dev"
    assert data[0]["right"] == "staging"


def test_cmd_run_labels_mismatch_exits(cfg_files):
    args = _args(
        files=[cfg_files["dev"], cfg_files["stg"]],
        labels="only-one",
    )
    with pytest.raises(SystemExit) as exc:
        cmd_run(args)
    assert exc.value.code == 1


def test_cmd_run_bad_file_exits(tmp_path):
    args = _args(files=[str(tmp_path / "missing.json"), str(tmp_path / "also_missing.json")])
    with pytest.raises(SystemExit) as exc:
        cmd_run(args)
    assert exc.value.code == 1
