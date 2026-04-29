"""Tests for stackdiff.compressor_cmd."""
import argparse
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from stackdiff.compressor_cmd import build_compressor_parser, cmd_run


@pytest.fixture()
def cfg_files(tmp_path: Path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps({"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}))
    b.write_text(json.dumps({"HOST": "prod.example.com", "PORT": "5432", "NEW": "val"}))
    return str(a), str(b)


def _args(extra=None, **kwargs):
    base = {"keep_keys": False, "ratio": False}
    base.update(kwargs)
    if extra:
        base.update(extra)
    ns = argparse.Namespace(**base)
    return ns


def test_build_compressor_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    p = build_compressor_parser(subs)
    assert p is not None


def test_cmd_run_outputs_json(cfg_files, capsys):
    file_a, file_b = cfg_files
    args = _args(file_a=file_a, file_b=file_b)
    cmd_run(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "added" in data
    assert "removed" in data
    assert "changed" in data
    assert "unchanged_count" in data


def test_cmd_run_changed_key_present(cfg_files, capsys):
    file_a, file_b = cfg_files
    args = _args(file_a=file_a, file_b=file_b)
    cmd_run(args)
    data = json.loads(capsys.readouterr().out)
    assert "HOST" in data["changed"]


def test_cmd_run_unchanged_count_correct(cfg_files, capsys):
    file_a, file_b = cfg_files
    args = _args(file_a=file_a, file_b=file_b)
    cmd_run(args)
    data = json.loads(capsys.readouterr().out)
    # PORT is shared and unchanged
    assert data["unchanged_count"] >= 1


def test_cmd_run_ratio_flag(cfg_files, capsys):
    file_a, file_b = cfg_files
    args = _args(file_a=file_a, file_b=file_b, ratio=True)
    cmd_run(args)
    out = capsys.readouterr().out
    assert "compression ratio" in out
    assert "%" in out


def test_cmd_run_bad_file_exits(tmp_path):
    args = _args(file_a=str(tmp_path / "missing.json"), file_b=str(tmp_path / "also.json"))
    with pytest.raises(SystemExit) as exc_info:
        cmd_run(args)
    assert exc_info.value.code == 1
