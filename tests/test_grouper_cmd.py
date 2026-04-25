"""Tests for stackdiff.grouper_cmd."""
import argparse
import json
import os
import pytest

from stackdiff.grouper_cmd import build_grouper_parser, cmd_prefix, cmd_glob


@pytest.fixture()
def cfg_file(tmp_path):
    data = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "myapp",
        "LOG_LEVEL": "info",
    }
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    return str(p)


def _args(**kwargs):
    ns = argparse.Namespace(
        file=None,
        prefixes="DB,APP",
        separator="_",
        default_group="other",
        patterns=None,
    )
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_cmd_prefix_outputs_json(cfg_file, capsys):
    args = _args(file=cfg_file, prefixes="DB,APP")
    cmd_prefix(args)
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "DB" in result
    assert "DB_HOST" in result["DB"]


def test_cmd_prefix_default_group_present(cfg_file, capsys):
    args = _args(file=cfg_file, prefixes="DB", default_group="misc")
    cmd_prefix(args)
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "LOG_LEVEL" in result["misc"]


def test_cmd_prefix_bad_file_exits(tmp_path):
    args = _args(file=str(tmp_path / "missing.json"), prefixes="DB")
    with pytest.raises(SystemExit) as exc_info:
        cmd_prefix(args)
    assert exc_info.value.code == 1


def test_cmd_glob_outputs_json(cfg_file, capsys):
    patterns_json = json.dumps({"database": "DB_*", "app": "APP_*"})
    args = _args(file=cfg_file, patterns=patterns_json, default_group="other")
    cmd_glob(args)
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "DB_HOST" in result["database"]
    assert "APP_NAME" in result["app"]


def test_cmd_glob_bad_patterns_json_exits(cfg_file):
    args = _args(file=cfg_file, patterns="{not valid json", default_group="other")
    with pytest.raises(SystemExit) as exc_info:
        cmd_glob(args)
    assert exc_info.value.code == 1


def test_build_grouper_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    build_grouper_parser(subs)
    args = parser.parse_args(["group", "prefix", "myfile.json", "--prefixes", "DB"])
    assert args.prefixes == "DB"
