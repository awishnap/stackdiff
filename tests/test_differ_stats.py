"""Tests for stackdiff.differ_stats."""

import pytest

from stackdiff.differ import diff_configs
from stackdiff.differ_stats import StatsError, compute_stats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(local, remote):
    return diff_configs(local, remote)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_compute_stats_counts_added():
    r = _result({}, {"NEW": "1"})
    stats = compute_stats([r])
    assert stats.added_count == 1
    assert stats.removed_count == 0
    assert stats.changed_count == 0


def test_compute_stats_counts_removed():
    r = _result({"OLD": "1"}, {})
    stats = compute_stats([r])
    assert stats.removed_count == 1
    assert stats.added_count == 0


def test_compute_stats_counts_changed():
    r = _result({"K": "a"}, {"K": "b"})
    stats = compute_stats([r])
    assert stats.changed_count == 1
    assert stats.unchanged_count == 0


def test_compute_stats_counts_unchanged():
    r = _result({"K": "same"}, {"K": "same"})
    stats = compute_stats([r])
    assert stats.unchanged_count == 1
    assert stats.changed_count == 0


def test_compute_stats_change_rate_all_changed():
    r = _result({"A": "1", "B": "2"}, {"A": "x", "B": "y"})
    stats = compute_stats([r])
    assert stats.change_rate == 1.0


def test_compute_stats_change_rate_partial():
    r = _result({"A": "1", "B": "2"}, {"A": "x", "B": "2"})
    stats = compute_stats([r])
    assert 0 < stats.change_rate < 1.0


def test_compute_stats_multiple_results_aggregate():
    r1 = _result({"A": "1"}, {"A": "2"})
    r2 = _result({}, {"B": "3"})
    stats = compute_stats([r1, r2])
    assert stats.changed_count == 1
    assert stats.added_count == 1


def test_compute_stats_most_volatile_keys():
    r1 = _result({"X": "1"}, {"X": "2"})
    r2 = _result({"X": "2"}, {"X": "3"})
    r3 = _result({"Y": "a"}, {"Y": "b"})
    stats = compute_stats([r1, r2, r3], top_n=2)
    assert stats.most_volatile_keys[0] == "X"
    assert len(stats.most_volatile_keys) <= 2


def test_compute_stats_top_n_respected():
    results = [_result({"K": str(i)}, {"K": str(i + 1)}) for i in range(10)]
    stats = compute_stats(results, top_n=3)
    assert len(stats.most_volatile_keys) <= 3


def test_compute_stats_empty_raises():
    with pytest.raises(StatsError, match="empty"):
        compute_stats([])


def test_compute_stats_invalid_top_n_raises():
    r = _result({"A": "1"}, {"A": "2"})
    with pytest.raises(StatsError, match="top_n"):
        compute_stats([r], top_n=0)
