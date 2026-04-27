"""Tests for stackdiff.archiver."""
from __future__ import annotations

import json
import pytest

from stackdiff.archiver import (
    ArchiverError,
    delete_archive,
    list_archives,
    load_archive,
    save_archive,
)
from stackdiff.differ import diff_configs


@pytest.fixture()
def arc_dir(tmp_path):
    return str(tmp_path / "archives")


def _result():
    return diff_configs({"A": "1", "B": "2"}, {"A": "9", "C": "3"})


def test_save_and_load_roundtrip(arc_dir):
    result = _result()
    save_archive(arc_dir, "rel-1", result)
    data = load_archive(arc_dir, "rel-1")
    assert data["name"] == "rel-1"
    assert data["changed"] == {"A": {"old": "1", "new": "9"}}
    assert data["removed"] == {"B": "2"}
    assert data["added"] == {"C": "3"}


def test_save_returns_path(arc_dir):
    path = save_archive(arc_dir, "rel-2", _result())
    assert path.endswith("rel-2.json")


def test_save_stores_meta(arc_dir):
    save_archive(arc_dir, "rel-3", _result(), meta={"env": "prod"})
    data = load_archive(arc_dir, "rel-3")
    assert data["meta"]["env"] == "prod"


def test_save_invalid_name_raises(arc_dir):
    with pytest.raises(ArchiverError):
        save_archive(arc_dir, "bad/name", _result())


def test_load_missing_raises(arc_dir):
    with pytest.raises(ArchiverError, match="not found"):
        load_archive(arc_dir, "ghost")


def test_list_archives_empty(arc_dir):
    assert list_archives(arc_dir) == []


def test_list_archives_returns_names(arc_dir):
    save_archive(arc_dir, "z-last", _result())
    save_archive(arc_dir, "a-first", _result())
    names = list_archives(arc_dir)
    assert names == ["a-first", "z-last"]


def test_delete_archive_removes_entry(arc_dir):
    save_archive(arc_dir, "to-del", _result())
    delete_archive(arc_dir, "to-del")
    assert "to-del" not in list_archives(arc_dir)


def test_delete_missing_raises(arc_dir):
    with pytest.raises(ArchiverError, match="not found"):
        delete_archive(arc_dir, "nope")


def test_saved_at_present(arc_dir):
    save_archive(arc_dir, "ts-check", _result())
    data = load_archive(arc_dir, "ts-check")
    assert "saved_at" in data
    assert data["saved_at"].endswith("+00:00")
