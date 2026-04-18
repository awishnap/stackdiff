"""Tests for stackdiff.profile_cmd."""

import json
import sys
import argparse
import pytest
from pathlib import Path

from stackdiff.profile_cmd import cmd_save, cmd_list, cmd_show, cmd_delete
from stackdiff.profiler import save_profile


def _args(prof_dir, **kwargs):
    ns = argparse.Namespace(profiles_dir=str(prof_dir))
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


@pytest.fixture
def prof_dir(tmp_path):
    return tmp_path / "profiles"


def test_cmd_save_creates_profile(prof_dir, tmp_path, capsys):
    jf = tmp_path / "cfg.json"
    jf.write_text(json.dumps({"host": "localhost"}))
    cmd_save(_args(prof_dir, name="local", file=str(jf)))
    out = capsys.readouterr().out
    assert "local" in out


def test_cmd_save_bad_file(prof_dir, capsys):
    with pytest.raises(SystemExit):
        cmd_save(_args(prof_dir, name="x", file="/nonexistent/file.json"))


def test_cmd_list_empty(prof_dir, capsys):
    cmd_list(_args(prof_dir))
    assert "No profiles" in capsys.readouterr().out


def test_cmd_list_shows_names(prof_dir, capsys):
    save_profile("staging", {}, base=prof_dir)
    cmd_list(_args(prof_dir))
    assert "staging" in capsys.readouterr().out


def test_cmd_show_prints_json(prof_dir, capsys):
    save_profile("prod", {"url": "https://prod.example.com"}, base=prof_dir)
    cmd_show(_args(prof_dir, name="prod"))
    out = capsys.readouterr().out
    assert "prod.example.com" in out


def test_cmd_show_missing(prof_dir, capsys):
    with pytest.raises(SystemExit):
        cmd_show(_args(prof_dir, name="ghost"))


def test_cmd_delete(prof_dir, capsys):
    save_profile("old", {}, base=prof_dir)
    cmd_delete(_args(prof_dir, name="old"))
    assert "deleted" in capsys.readouterr().out


def test_cmd_delete_missing(prof_dir):
    with pytest.raises(SystemExit):
        cmd_delete(_args(prof_dir, name="missing"))
