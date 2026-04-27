"""Tests for stackdiff/scoper_cmd.py."""
import argparse
import json
import sys

import pytest

from stackdiff.scoper_cmd import build_scoper_parser, cmd_list, cmd_scope


@pytest.fixture()
def cfg_file(tmp_path):
    data = {
        "db.host": "localhost",
        "db.port": "5432",
        "cache.host": "redis",
        "APP_DEBUG": "true",
    }
    f = tmp_path / "config.json"
    f.write_text(json.dumps(data))
    return str(f)


def _args(**kwargs):
    base = dict(separator=".", keep_prefix=False, summary=False)
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_cmd_scope_outputs_json(cfg_file, capsys):
    args = _args(file=cfg_file, scope="db")
    cmd_scope(args)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed == {"host": "localhost", "port": "5432"}


def test_cmd_scope_summary_flag(cfg_file, capsys):
    args = _args(file=cfg_file, scope="db", summary=True)
    cmd_scope(args)
    out = capsys.readouterr().out
    assert "Scope 'db'" in out
    assert "2 keys" in out


def test_cmd_scope_keep_prefix(cfg_file, capsys):
    args = _args(file=cfg_file, scope="db", keep_prefix=True)
    cmd_scope(args)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert "db.host" in parsed


def test_cmd_scope_bad_file_exits(tmp_path):
    args = _args(file=str(tmp_path / "missing.json"), scope="db")
    with pytest.raises(SystemExit) as exc_info:
        cmd_scope(args)
    assert exc_info.value.code == 1


def test_cmd_list_outputs_scopes(cfg_file, capsys):
    args = argparse.Namespace(file=cfg_file, separator=".")
    cmd_list(args)
    out = capsys.readouterr().out
    assert "cache" in out
    assert "db" in out


def test_cmd_list_no_scopes(tmp_path, capsys):
    f = tmp_path / "flat.json"
    f.write_text(json.dumps({"HOST": "localhost", "PORT": "8080"}))
    args = argparse.Namespace(file=str(f), separator=".")
    cmd_list(args)
    out = capsys.readouterr().out
    assert "no scopes" in out


def test_cmd_list_bad_file_exits(tmp_path):
    args = argparse.Namespace(file=str(tmp_path / "missing.json"), separator=".")
    with pytest.raises(SystemExit) as exc_info:
        cmd_list(args)
    assert exc_info.value.code == 1


def test_build_scoper_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers(dest="cmd")
    build_scoper_parser(subs)
    parsed = root.parse_args(["scope", "filter", "cfg.json", "db"])
    assert parsed.scope == "db"
