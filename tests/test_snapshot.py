"""Tests for stackdiff.snapshot."""

import pytest

from stackdiff.snapshot import (
    SnapshotError,
    list_snapshots,
    load_snapshot,
    save_snapshot,
    snapshot_path,
)


@pytest.fixture()
def snap_dir(tmp_path):
    return str(tmp_path / "snaps")


def test_save_and_load_roundtrip(snap_dir):
    cfg = {"HOST": "localhost", "PORT": "5432"}
    save_snapshot("staging", cfg, snapshot_dir=snap_dir)
    loaded = load_snapshot("staging", snapshot_dir=snap_dir)
    assert loaded == cfg


def test_save_returns_path(snap_dir):
    path = save_snapshot("prod", {"K": "V"}, snapshot_dir=snap_dir)
    assert path.endswith("prod.json")


def test_load_missing_snapshot_raises(snap_dir):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot("ghost", snapshot_dir=snap_dir)


def test_list_snapshots_empty(snap_dir):
    assert list_snapshots(snap_dir) == []


def test_list_snapshots_returns_names(snap_dir):
    save_snapshot("alpha", {}, snapshot_dir=snap_dir)
    save_snapshot("beta", {}, snapshot_dir=snap_dir)
    assert list_snapshots(snap_dir) == ["alpha", "beta"]


def test_snapshot_path_format(snap_dir):
    p = snapshot_path("myenv", snap_dir)
    assert p.endswith("myenv.json")


def test_overwrite_snapshot(snap_dir):
    save_snapshot("env", {"A": "1"}, snapshot_dir=snap_dir)
    save_snapshot("env", {"A": "2"}, snapshot_dir=snap_dir)
    loaded = load_snapshot("env", snapshot_dir=snap_dir)
    assert loaded["A"] == "2"


def test_save_snapshot_invalid_dir():
    """Writing to an unwritable path should raise SnapshotError."""
    with pytest.raises(SnapshotError):
        save_snapshot("x", {}, snapshot_dir="/proc/no_such_dir_stackdiff")
