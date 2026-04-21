"""Tests for stackdiff.tagger_cmd."""

import argparse
import sys

import pytest

from stackdiff.tagger import add_tag
from stackdiff.tagger_cmd import (
    build_tagger_parser,
    cmd_add,
    cmd_clear,
    cmd_find,
    cmd_list,
    cmd_remove,
)


@pytest.fixture()
def tags_dir(tmp_path):
    return str(tmp_path / "tags")


def _args(tags_dir, **kwargs):
    ns = argparse.Namespace(tags_dir=tags_dir, **kwargs)
    return ns


def test_cmd_add_prints_confirmation(tags_dir, capsys):
    cmd_add(_args(tags_dir, name="prod", tag="critical"))
    out = capsys.readouterr().out
    assert "critical" in out
    assert "prod" in out


def test_cmd_list_shows_tags(tags_dir, capsys):
    add_tag(tags_dir, "staging", "beta")
    cmd_list(_args(tags_dir, name="staging"))
    assert "beta" in capsys.readouterr().out


def test_cmd_list_empty(tags_dir, capsys):
    cmd_list(_args(tags_dir, name="nobody"))
    assert "No tags" in capsys.readouterr().out


def test_cmd_remove_success(tags_dir, capsys):
    add_tag(tags_dir, "prod", "live")
    cmd_remove(_args(tags_dir, name="prod", tag="live"))
    assert "removed" in capsys.readouterr().out


def test_cmd_remove_missing_exits(tags_dir):
    with pytest.raises(SystemExit):
        cmd_remove(_args(tags_dir, name="prod", tag="ghost"))


def test_cmd_find_returns_names(tags_dir, capsys):
    add_tag(tags_dir, "prod", "critical")
    add_tag(tags_dir, "staging", "critical")
    cmd_find(_args(tags_dir, tag="critical"))
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_cmd_find_no_match(tags_dir, capsys):
    cmd_find(_args(tags_dir, tag="ghost"))
    assert "No entries" in capsys.readouterr().out


def test_cmd_clear_removes_all(tags_dir, capsys):
    add_tag(tags_dir, "prod", "a")
    add_tag(tags_dir, "prod", "b")
    cmd_clear(_args(tags_dir, name="prod"))
    assert "cleared" in capsys.readouterr().out


def test_build_tagger_parser_registers_subcommand(tags_dir):
    root = argparse.ArgumentParser()
    subs = root.add_subparsers(dest="cmd")
    build_tagger_parser(subs, tags_dir)
    args = root.parse_args(["tag", "list", "prod"])
    assert args.name == "prod"
