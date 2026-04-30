"""Tests for stackdiff.differ_rank."""
import pytest

from stackdiff.differ_rank import RankError, RankEntry, RankResult, rank_configs


REFERENCE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false", "WORKERS": "4"}


def test_rank_result_has_all_candidates():
    candidates = {
        "staging": {"HOST": "staging.example.com", "PORT": "5432", "DEBUG": "true", "WORKERS": "4"},
        "prod": {"HOST": "prod.example.com", "PORT": "5433", "DEBUG": "false", "WORKERS": "8"},
    }
    result = rank_configs(REFERENCE, candidates)
    assert len(result.entries) == 2


def test_most_divergent_ranked_first():
    candidates = {
        "small_diff": {"HOST": "localhost", "PORT": "5432", "DEBUG": "true", "WORKERS": "4"},
        "big_diff": {"HOST": "other", "PORT": "9999", "DEBUG": "true", "WORKERS": "1"},
    }
    result = rank_configs(REFERENCE, candidates)
    assert result.entries[0].label == "big_diff"
    assert result.entries[1].label == "small_diff"


def test_rank_numbers_are_sequential():
    candidates = {"a": {"HOST": "x"}, "b": {"HOST": "y", "PORT": "1"}}
    result = rank_configs(REFERENCE, candidates)
    ranks = [e.rank for e in result.entries]
    assert ranks == list(range(1, len(ranks) + 1))


def test_total_diff_counts_added_removed_changed():
    candidates = {
        "mixed": {"HOST": "new", "PORT": "5432", "EXTRA": "val"},
    }
    result = rank_configs(REFERENCE, candidates)
    entry = result.entries[0]
    assert entry.changed >= 1   # HOST changed
    assert entry.added >= 1     # EXTRA added
    assert entry.removed >= 1   # DEBUG and WORKERS removed
    assert entry.total_diff == entry.added + entry.removed + entry.changed


def test_identical_config_has_zero_diff():
    candidates = {"clone": dict(REFERENCE)}
    result = rank_configs(REFERENCE, candidates)
    entry = result.entries[0]
    assert entry.total_diff == 0


def test_reference_label_stored():
    result = rank_configs({}, {"a": {}}, reference_label="baseline")
    assert result.reference_label == "baseline"


def test_empty_candidates_raises():
    with pytest.raises(RankError, match="empty"):
        rank_configs(REFERENCE, {})


def test_non_dict_candidate_raises():
    with pytest.raises(RankError, match="not a dict"):
        rank_configs(REFERENCE, {"bad": ["not", "a", "dict"]})


def test_as_dict_structure():
    candidates = {"env": {"HOST": "remote"}}
    result = rank_configs(REFERENCE, candidates, reference_label="ref")
    d = result.as_dict()
    assert d["reference_label"] == "ref"
    assert isinstance(d["entries"], list)
    entry_d = d["entries"][0]
    for key in ("rank", "label", "added", "removed", "changed", "total_diff"):
        assert key in entry_d


def test_single_candidate_rank_is_1():
    candidates = {"only": {"HOST": "changed"}}
    result = rank_configs(REFERENCE, candidates)
    assert result.entries[0].rank == 1
