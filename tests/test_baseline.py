"""Tests for stackdiff.baseline."""

from __future__ import annotations

import pytest

from stackdiff.baseline import (
    BaselineError,
    compare_to_baseline,
    delete_baseline,
    list_baselines,
    load_baseline,
    save_baseline,
)


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path / "baselines")


def test_save_and_load_roundtrip(base_dir):
    cfg = {"HOST": "localhost", "PORT": "5432"}
    save_baseline("prod", cfg, base_dir)
    loaded = load_baseline("prod", base_dir)
    assert loaded == cfg


def test_save_returns_path(base_dir):
    path = save_baseline("staging", {"KEY": "val"}, base_dir)
    assert path.exists()
    assert path.stem == "staging"


def test_load_missing_raises(base_dir):
    with pytest.raises(BaselineError, match="not found"):
        load_baseline("ghost", base_dir)


def test_list_empty(base_dir):
    assert list_baselines(base_dir) == []


def test_list_multiple(base_dir):
    save_baseline("alpha", {}, base_dir)
    save_baseline("beta", {}, base_dir)
    assert list_baselines(base_dir) == ["alpha", "beta"]


def test_delete_removes_baseline(base_dir):
    save_baseline("tmp", {"X": "1"}, base_dir)
    delete_baseline("tmp", base_dir)
    assert "tmp" not in list_baselines(base_dir)


def test_delete_missing_raises(base_dir):
    with pytest.raises(BaselineError, match="not found"):
        delete_baseline("none", base_dir)


def test_compare_detects_changes(base_dir):
    save_baseline("v1", {"A": "1", "B": "2"}, base_dir)
    current = {"A": "1", "B": "99", "C": "new"}
    result = compare_to_baseline("v1", current, base_dir)
    assert "B" in result.changed
    assert "C" in result.added


def test_compare_no_diff(base_dir):
    cfg = {"X": "hello"}
    save_baseline("same", cfg, base_dir)
    result = compare_to_baseline("same", cfg, base_dir)
    assert not result.added
    assert not result.removed
    assert not result.changed
