"""Tests for differ_matrix_cmd.py"""
from __future__ import annotations

import json
import os
import textwrap
from argparse import ArgumentParser
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from stackdiff.differ_matrix_cmd import build_matrix_parser, cmd_run


@pytest.fixture()
def cfg_files(tmp_path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    c = tmp_path / "c.json"
    a.write_text(json.dumps({"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}))
    b.write_text(json.dumps({"HOST": "prod.example.com", "PORT": "5432", "DEBUG": "false"}))
    c.write_text(json.dumps({"HOST": "staging.example.com", "PORT": "5433", "DEBUG": "false"}))
    return str(a), str(b), str(c)


def _args(**kwargs):
    defaults = dict(files=[], summary=False, most_divergent=False, json=False)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_build_matrix_parser_registers_subcommand():
    root = ArgumentParser()
    subs = root.add_subparsers()
    build_matrix_parser(subs)
    args = root.parse_args(["matrix", "a.json", "b.json"])
    assert args.func is cmd_run
    assert args.files == ["a.json", "b.json"]


def test_cmd_run_outputs_full_matrix(cfg_files, capsys):
    a, b, c = cfg_files
    cmd_run(_args(files=[a, b, c], json=True))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    # Expect 3 pairs from 3 files
    assert len(data) == 3


def test_cmd_run_summary_flag(cfg_files, capsys):
    a, b, _ = cfg_files
    cmd_run(_args(files=[a, b], summary=True))
    captured = capsys.readouterr()
    assert "Pairs compared" in captured.out
    assert "Total diffs" in captured.out


def test_cmd_run_summary_json(cfg_files, capsys):
    a, b, _ = cfg_files
    cmd_run(_args(files=[a, b], summary=True, json=True))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "pairs_compared" in data
    assert "total_diffs" in data


def test_cmd_run_most_divergent(cfg_files, capsys):
    a, b, c = cfg_files
    cmd_run(_args(files=[a, b, c], most_divergent=True, json=True))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "a" in data and "b" in data and "diff_count" in data


def test_cmd_run_too_few_files_exits(tmp_path):
    f = tmp_path / "only.json"
    f.write_text(json.dumps({"K": "v"}))
    with pytest.raises(SystemExit) as exc_info:
        cmd_run(_args(files=[str(f)]))
    assert exc_info.value.code == 1


def test_cmd_run_bad_file_exits(cfg_files):
    a, _, _ = cfg_files
    with pytest.raises(SystemExit) as exc_info:
        cmd_run(_args(files=[a, "/nonexistent/path.json"]))
    assert exc_info.value.code == 1
