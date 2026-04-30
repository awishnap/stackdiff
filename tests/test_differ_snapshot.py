"""Tests for stackdiff.differ_snapshot."""
from __future__ import annotations

import json
import os
import pytest

from stackdiff.differ_snapshot import (
    diff_against_snapshot,
    SnapshotDiffError,
    SnapshotDiffResult,
)
from stackdiff.snapshot import save_snapshot


@pytest.fixture()
def snap_dir(tmp_path):
    return str(tmp_path / "snaps")


@pytest.fixture()
def saved_snap(snap_dir):
    cfg = {"HOST": "db.internal", "PORT": "5432", "DEBUG": "false"}
    save_snapshot("prod-2024", cfg, snap_dir=snap_dir)
    return cfg


def test_no_drift_when_identical(snap_dir, saved_snap):
    result = diff_against_snapshot("prod-2024", dict(saved_snap), snap_dir=snap_dir)
    assert not result.has_drift()


def test_detects_changed_value(snap_dir, saved_snap):
    live = dict(saved_snap)
    live["PORT"] = "5433"
    result = diff_against_snapshot("prod-2024", live, snap_dir=snap_dir)
    assert result.has_drift()
    assert "PORT" in result.diff.changed


def test_detects_added_key(snap_dir, saved_snap):
    live = dict(saved_snap)
    live["NEW_KEY"] = "value"
    result = diff_against_snapshot("prod-2024", live, snap_dir=snap_dir)
    assert "NEW_KEY" in result.diff.added


def test_detects_removed_key(snap_dir, saved_snap):
    live = {k: v for k, v in saved_snap.items() if k != "DEBUG"}
    result = diff_against_snapshot("prod-2024", live, snap_dir=snap_dir)
    assert "DEBUG" in result.diff.removed


def test_missing_snapshot_raises(snap_dir):
    with pytest.raises(SnapshotDiffError):
        diff_against_snapshot("nonexistent", {"A": "1"}, snap_dir=snap_dir)


def test_non_dict_live_config_raises(snap_dir, saved_snap):
    with pytest.raises(SnapshotDiffError):
        diff_against_snapshot("prod-2024", "not-a-dict", snap_dir=snap_dir)  # type: ignore


def test_as_dict_keys(snap_dir, saved_snap):
    live = dict(saved_snap)
    live["PORT"] = "9999"
    result = diff_against_snapshot("prod-2024", live, snap_dir=snap_dir)
    d = result.as_dict()
    assert "snapshot_name" in d
    assert "added" in d
    assert "removed" in d
    assert "changed" in d
    assert "unchanged" in d


def test_summary_no_drift(snap_dir, saved_snap):
    result = diff_against_snapshot("prod-2024", dict(saved_snap), snap_dir=snap_dir)
    assert "No drift" in result.summary()


def test_summary_with_drift(snap_dir, saved_snap):
    live = dict(saved_snap)
    live["HOST"] = "db.external"
    result = diff_against_snapshot("prod-2024", live, snap_dir=snap_dir)
    assert "changed" in result.summary()
