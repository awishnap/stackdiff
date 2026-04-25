"""Tests for stackdiff.sorter_cmd."""

import argparse
import json
import os
import pytest

from stackdiff.sorter_cmd import cmd_run, build_sorter_parser


@pytest.fixture()
def cfg_file(tmp_path):
    data = {"zebra": "z", "apple": "a", "mango": "m"}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    return str(p)


def _args(**kwargs):
    defaults = {
        "strategy": "alpha",
        "reverse": False,
        "order": None,
        "drop_missing": False,
        "output": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_run_alpha_sort(cfg_file, capsys):
    args = _args(file=cfg_file)
    cmd_run(args)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert list(parsed.keys()) == ["apple", "mango", "zebra"]


def test_cmd_run_reverse_sort(cfg_file, capsys):
    args = _args(file=cfg_file, reverse=True)
    cmd_run(args)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert list(parsed.keys()) == ["zebra", "mango", "apple"]


def test_cmd_run_length_strategy(cfg_file, capsys):
    args = _args(file=cfg_file, strategy="length")
    cmd_run(args)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    # "apple" and "zebra" and "mango" are all 5 chars; order may vary but all present
    assert set(parsed.keys()) == {"apple", "zebra", "mango"}


def test_cmd_run_explicit_order(cfg_file, capsys):
    args = _args(file=cfg_file, order=["mango", "zebra"])
    cmd_run(args)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    keys = list(parsed.keys())
    assert keys[0] == "mango"
    assert keys[1] == "zebra"
    assert "apple" in keys


def test_cmd_run_drop_missing(cfg_file, capsys):
    args = _args(file=cfg_file, order=["apple"], drop_missing=True)
    cmd_run(args)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert list(parsed.keys()) == ["apple"]


def test_cmd_run_writes_output_file(cfg_file, tmp_path):
    out_file = str(tmp_path / "sorted.json")
    args = _args(file=cfg_file, output=out_file)
    cmd_run(args)
    assert os.path.isfile(out_file)
    with open(out_file) as fh:
        parsed = json.load(fh)
    assert list(parsed.keys()) == ["apple", "mango", "zebra"]


def test_cmd_run_bad_file_exits(tmp_path):
    args = _args(file=str(tmp_path / "missing.json"))
    with pytest.raises(SystemExit):
        cmd_run(args)


def test_build_sorter_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_sorter_parser(sub)
    parsed = root.parse_args(["sort", "myfile.json"])
    assert parsed.file == "myfile.json"
    assert parsed.strategy == "alpha"
