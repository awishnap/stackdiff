"""Tests for stackdiff.differ_heatmap."""
import pytest

from stackdiff.differ import DiffResult
from stackdiff.differ_heatmap import (
    HeatmapError,
    build_heatmap,
    heatmap_summary,
)


def _result(added=None, removed=None, changed=None, unchanged=None):
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
    )


def test_build_heatmap_counts_changed_keys():
    r1 = _result(changed={"HOST": ("a", "b"), "PORT": ("80", "443")})
    r2 = _result(changed={"HOST": ("b", "c")})
    hm = build_heatmap([r1, r2])
    keys = [e.key for e in hm.entries]
    assert "HOST" in keys
    assert "PORT" in keys


def test_build_heatmap_host_has_count_2():
    r1 = _result(changed={"HOST": ("a", "b")})
    r2 = _result(changed={"HOST": ("b", "c")})
    hm = build_heatmap([r1, r2])
    entry = next(e for e in hm.entries if e.key == "HOST")
    assert entry.change_count == 2


def test_build_heatmap_counts_added_keys():
    r = _result(added={"NEW_KEY": "value"})
    hm = build_heatmap([r])
    keys = [e.key for e in hm.entries]
    assert "NEW_KEY" in keys


def test_build_heatmap_counts_removed_keys():
    r = _result(removed={"OLD_KEY": "gone"})
    hm = build_heatmap([r])
    keys = [e.key for e in hm.entries]
    assert "OLD_KEY" in keys


def test_build_heatmap_frequency_calculation():
    r1 = _result(changed={"X": ("1", "2")})
    r2 = _result(unchanged={"X": "2"})
    hm = build_heatmap([r1, r2])
    entry = next(e for e in hm.entries if e.key == "X")
    assert entry.frequency == pytest.approx(0.5)


def test_build_heatmap_total_diffs():
    results = [_result(changed={"A": ("x", "y")}) for _ in range(7)]
    hm = build_heatmap(results)
    assert hm.total_diffs == 7


def test_build_heatmap_top_n_limits_entries():
    r = _result(changed={k: ("a", "b") for k in "ABCDE"})
    hm = build_heatmap([r], top_n=3)
    assert len(hm.entries) == 3


def test_build_heatmap_empty_raises():
    with pytest.raises(HeatmapError):
        build_heatmap([])


def test_heatmap_top_returns_n_entries():
    results = [_result(changed={k: ("a", "b") for k in "ABCDE"})]
    hm = build_heatmap(results)
    assert len(hm.top(2)) == 2


def test_heatmap_as_dict_structure():
    r = _result(changed={"DB_HOST": ("old", "new")})
    hm = build_heatmap([r])
    d = hm.as_dict()
    assert "total_diffs" in d
    assert "entries" in d
    assert d["entries"][0]["key"] == "DB_HOST"


def test_heatmap_summary_contains_key():
    r = _result(changed={"SECRET_KEY": ("a", "b")})
    hm = build_heatmap([r])
    summary = heatmap_summary(hm)
    assert "SECRET_KEY" in summary


def test_heatmap_summary_no_changes():
    r = _result(unchanged={"STABLE": "value"})
    hm = build_heatmap([r])
    summary = heatmap_summary(hm)
    assert "no changes" in summary
