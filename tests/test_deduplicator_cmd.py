"""Tests for stackdiff.deduplicator_cmd."""

from __future__ import annotations

import argparse
import json
import pathlib

import pytest

from stackdiff.deduplicator_cmd import build_dedup_parser, cmd_check, cmd_clean


@pytest.fixture()
def cfg_file(tmp_path: pathlib.Path):
    """Write a simple JSON config with a duplicate value and return its path."""
    data = {"A": "shared", "B": "unique", "C": "shared"}
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(data))
    return p


def _args(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


# ---------------------------------------------------------------------------
# build_dedup_parser
# ---------------------------------------------------------------------------

def test_build_dedup_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    build_dedup_parser(sub)
    args = parser.parse_args(["dedup", "check", "some_file.json"])
    assert args.file == "some_file.json"


# ---------------------------------------------------------------------------
# cmd_check
# ---------------------------------------------------------------------------

def test_cmd_check_exits_2_when_duplicates_found(cfg_file, capsys):
    args = _args(file=str(cfg_file))
    with pytest.raises(SystemExit) as exc_info:
        cmd_check(args)
    assert exc_info.value.code == 2
    out = capsys.readouterr().out
    assert "duplicate" in out.lower()


def test_cmd_check_no_exit_when_clean(tmp_path, capsys):
    p = tmp_path / "clean.json"
    p.write_text(json.dumps({"a": "1", "b": "2"}))
    args = _args(file=str(p))
    cmd_check(args)  # should not raise
    out = capsys.readouterr().out
    assert "No duplicate" in out


def test_cmd_check_bad_file_exits_1(tmp_path, capsys):
    args = _args(file=str(tmp_path / "missing.json"))
    with pytest.raises(SystemExit) as exc_info:
        cmd_check(args)
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# cmd_clean
# ---------------------------------------------------------------------------

def test_cmd_clean_keep_first_drops_later_key(cfg_file, capsys):
    args = _args(file=str(cfg_file), keep="first")
    cmd_clean(args)
    out = capsys.readouterr().out
    data = json.loads(out.split("dropped:")[0] if "dropped:" not in out.splitlines()[-1] else "\n".join(
        line for line in out.splitlines() if not line.startswith("dropped")
    ))
    assert "A" in data
    assert "C" not in data


def test_cmd_clean_keep_last_drops_earlier_key(cfg_file, capsys):
    args = _args(file=str(cfg_file), keep="last")
    cmd_clean(args)
    out = capsys.readouterr().out
    json_lines = [l for l in out.splitlines() if not l.startswith("dropped")]
    data = json.loads("\n".join(json_lines))
    assert "C" in data
    assert "A" not in data


def test_cmd_clean_reports_dropped_keys(cfg_file, capsys):
    args = _args(file=str(cfg_file), keep="first")
    cmd_clean(args)
    out = capsys.readouterr().out
    assert "dropped: C" in out
