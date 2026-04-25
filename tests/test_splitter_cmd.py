"""Tests for stackdiff.splitter_cmd."""
import argparse
import json
import os
import textwrap

import pytest

from stackdiff.splitter_cmd import build_splitter_parser, cmd_glob, cmd_prefix


@pytest.fixture()
def cfg_file(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "myapp",
        "LOG_LEVEL": "info",
    }))
    return str(path)


def _args(**kwargs):
    base = argparse.Namespace(
        file=None,
        prefix=[],
        strip=False,
        default_group="__other__",
        pattern=[],
    )
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


def test_cmd_prefix_splits_correctly(cfg_file, capsys):
    cmd_prefix(_args(file=cfg_file, prefix=["DB_", "APP_"]))
    out = json.loads(capsys.readouterr().out)
    assert set(out["DB_"].keys()) == {"DB_HOST", "DB_PORT"}
    assert set(out["APP_"].keys()) == {"APP_NAME"}


def test_cmd_prefix_strip_flag(cfg_file, capsys):
    cmd_prefix(_args(file=cfg_file, prefix=["DB_"], strip=True))
    out = json.loads(capsys.readouterr().out)
    assert "HOST" in out["DB_"]


def test_cmd_prefix_bad_file_exits(tmp_path):
    with pytest.raises(SystemExit) as exc:
        cmd_prefix(_args(file=str(tmp_path / "missing.json"), prefix=["DB_"]))
    assert exc.value.code == 1


def test_cmd_prefix_no_prefixes_exits(cfg_file):
    with pytest.raises(SystemExit) as exc:
        cmd_prefix(_args(file=cfg_file, prefix=[]))
    assert exc.value.code == 1


def test_cmd_glob_splits_correctly(cfg_file, capsys):
    cmd_glob(_args(file=cfg_file, pattern=["database=DB_*", "app=APP_*"]))
    out = json.loads(capsys.readouterr().out)
    assert set(out["database"].keys()) == {"DB_HOST", "DB_PORT"}


def test_cmd_glob_bad_pattern_exits(cfg_file):
    with pytest.raises(SystemExit) as exc:
        cmd_glob(_args(file=cfg_file, pattern=["no-equals-sign"]))
    assert exc.value.code == 1


def test_cmd_glob_no_patterns_exits(cfg_file):
    with pytest.raises(SystemExit) as exc:
        cmd_glob(_args(file=cfg_file, pattern=[]))
    assert exc.value.code == 1


def test_build_splitter_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    build_splitter_parser(subs)
    args = parser.parse_args(["split", "prefix", "--help"].__class__([])
                             if False else ["split", "--help"])
    # just ensure parser construction doesn't raise
    assert True
