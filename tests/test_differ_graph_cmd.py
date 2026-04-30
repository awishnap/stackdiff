"""Tests for stackdiff.differ_graph_cmd."""
import argparse
import json
import os
import sys
from pathlib import Path

import pytest

from stackdiff.differ_graph_cmd import build_graph_parser, cmd_run


@pytest.fixture()
def cfg_files(tmp_path: Path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    c = tmp_path / "c.json"
    a.write_text(json.dumps({"host": "localhost", "port": "5432"}))
    b.write_text(json.dumps({"host": "prod.db", "port": "5432"}))
    c.write_text(json.dumps({"host": "staging", "port": "5433"}))
    return str(a), str(b), str(c)


def _args(**kwargs) -> argparse.Namespace:
    defaults = {"min_shared": 1, "summary": False, "func": cmd_run}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_graph_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_graph_parser(sub)
    parsed = parser.parse_args(["graph", "a.json", "b.json"])
    assert parsed.files == ["a.json", "b.json"]


def test_cmd_run_outputs_json(capsys, cfg_files):
    a, b, _ = cfg_files
    args = _args(files=[a, b])
    cmd_run(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "nodes" in data
    assert "edges" in data


def test_cmd_run_summary_flag(capsys, cfg_files):
    a, b, c = cfg_files
    args = _args(files=[a, b, c], summary=True)
    cmd_run(args)
    out = capsys.readouterr().out
    assert "nodes" in out
    assert "edges" in out


def test_cmd_run_bad_file_exits(tmp_path):
    args = _args(files=[str(tmp_path / "missing.json"), str(tmp_path / "also_missing.json")])
    with pytest.raises(SystemExit) as exc_info:
        cmd_run(args)
    assert exc_info.value.code == 1


def test_cmd_run_single_file_exits(cfg_files):
    a, _, _ = cfg_files
    args = _args(files=[a])
    with pytest.raises(SystemExit) as exc_info:
        cmd_run(args)
    assert exc_info.value.code == 1


def test_cmd_run_min_shared_filters_edges(capsys, cfg_files):
    a, b, _ = cfg_files
    args = _args(files=[a, b], min_shared=99)
    cmd_run(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["edges"] == []
