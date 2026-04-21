"""Tests for stackdiff/comparator.py"""
import json
import pytest
from pathlib import Path

from stackdiff.comparator import (
    ComparatorError,
    ComparisonSpec,
    list_specs,
    load_spec,
    run_comparison,
    save_spec,
)


@pytest.fixture()
def store_dir(tmp_path: Path) -> str:
    return str(tmp_path / "comparisons")


@pytest.fixture()
def cfg_files(tmp_path: Path):
    local = tmp_path / "local.json"
    remote = tmp_path / "remote.json"
    local.write_text(json.dumps({"KEY": "val", "PORT": "8080"}))
    remote.write_text(json.dumps({"KEY": "val", "PORT": "9090", "EXTRA": "new"}))
    return str(local), str(remote)


def test_save_and_load_roundtrip(store_dir, cfg_files):
    local, remote = cfg_files
    spec = ComparisonSpec(name="prod", local_path=local, remote_path=remote)
    save_spec(spec, store_dir)
    loaded = load_spec("prod", store_dir)
    assert loaded.name == "prod"
    assert loaded.local_path == local
    assert loaded.remote_path == remote


def test_save_returns_path(store_dir, cfg_files):
    local, remote = cfg_files
    spec = ComparisonSpec(name="staging", local_path=local, remote_path=remote)
    path = save_spec(spec, store_dir)
    assert Path(path).exists()


def test_list_specs_empty(store_dir):
    assert list_specs(store_dir) == []


def test_list_specs_after_save(store_dir, cfg_files):
    local, remote = cfg_files
    for name in ("alpha", "beta"):
        save_spec(ComparisonSpec(name=name, local_path=local, remote_path=remote), store_dir)
    assert list_specs(store_dir) == ["alpha", "beta"]


def test_load_missing_raises(store_dir):
    with pytest.raises(ComparatorError, match="No comparison spec"):
        load_spec("ghost", store_dir)


def test_run_comparison_detects_diff(store_dir, cfg_files):
    local, remote = cfg_files
    spec = ComparisonSpec(name="test", local_path=local, remote_path=remote, mask_sensitive=False)
    result = run_comparison(spec)
    assert "PORT" in result.changed
    assert "EXTRA" in result.added


def test_run_comparison_no_diff(tmp_path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"A": "1"}))
    spec = ComparisonSpec(name="same", local_path=str(cfg), remote_path=str(cfg), mask_sensitive=False)
    result = run_comparison(spec)
    assert not result.added and not result.removed and not result.changed


def test_run_comparison_bad_path_raises():
    spec = ComparisonSpec(name="bad", local_path="/no/such/file.json", remote_path="/no/such/file.json")
    with pytest.raises(ComparatorError, match="Failed to load"):
        run_comparison(spec)
