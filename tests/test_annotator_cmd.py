"""Tests for stackdiff.annotator_cmd."""
import argparse
import pytest
from stackdiff.annotator_cmd import (
    build_annotator_parser,
    cmd_add,
    cmd_get,
    cmd_list,
    cmd_remove,
    cmd_clear,
)


@pytest.fixture()
def notes_dir(tmp_path):
    return str(tmp_path / "notes")


def _args(notes_dir, **kwargs):
    base = argparse.Namespace(store_dir=notes_dir)
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


def test_cmd_add_prints_confirmation(notes_dir, capsys):
    cmd_add(_args(notes_dir, namespace="prod", key="DB_HOST", note="Primary RDS."))
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "prod" in out


def test_cmd_add_empty_note_exits(notes_dir):
    with pytest.raises(SystemExit):
        cmd_add(_args(notes_dir, namespace="prod", key="K", note="  "))


def test_cmd_get_shows_notes(notes_dir, capsys):
    cmd_add(_args(notes_dir, namespace="prod", key="TIMEOUT", note="Set to 30s."))
    cmd_get(_args(notes_dir, namespace="prod", key="TIMEOUT"))
    out = capsys.readouterr().out
    assert "Set to 30s." in out


def test_cmd_get_no_notes_message(notes_dir, capsys):
    cmd_get(_args(notes_dir, namespace="prod", key="MISSING"))
    out = capsys.readouterr().out
    assert "No notes" in out


def test_cmd_list_shows_keys(notes_dir, capsys):
    cmd_add(_args(notes_dir, namespace="staging", key="API_URL", note="Changed."))
    cmd_list(_args(notes_dir, namespace="staging"))
    out = capsys.readouterr().out
    assert "API_URL" in out


def test_cmd_list_empty_namespace(notes_dir, capsys):
    cmd_list(_args(notes_dir, namespace="empty"))
    out = capsys.readouterr().out
    assert "No annotated" in out


def test_cmd_remove_prints_count(notes_dir, capsys):
    cmd_add(_args(notes_dir, namespace="prod", key="X", note="n1"))
    cmd_add(_args(notes_dir, namespace="prod", key="X", note="n2"))
    cmd_remove(_args(notes_dir, namespace="prod", key="X"))
    out = capsys.readouterr().out
    assert "2" in out


def test_cmd_clear_removes_all(notes_dir, capsys):
    cmd_add(_args(notes_dir, namespace="prod", key="A", note="a"))
    cmd_clear(_args(notes_dir, namespace="prod"))
    cmd_list(_args(notes_dir, namespace="prod"))
    out = capsys.readouterr().out
    assert "No annotated" in out


def test_build_annotator_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    build_annotator_parser(subs)
    args = parser.parse_args(["annotate", "--store-dir", "/tmp", "list", "prod"])
    assert args.cmd == "annotate"
    assert args.namespace == "prod"
