"""Tests for stackdiff.differ_score."""

from __future__ import annotations

import pytest

from stackdiff.differ_score import scored_diff, ScoredDiffResult, ScoredDiffError


@pytest.fixture
def cfg_a():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true", "SHARED": "same"}


@pytest.fixture
def cfg_b():
    return {"HOST": "prod.example.com", "PORT": "5432", "EXTRA": "new", "SHARED": "same"}


def test_scored_diff_returns_scored_diff_result(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b)
    assert isinstance(result, ScoredDiffResult)


def test_scored_diff_detects_changed_key(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b)
    assert "HOST" in result.diff.changed


def test_scored_diff_detects_added_key(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b)
    assert "EXTRA" in result.diff.added


def test_scored_diff_detects_removed_key(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b)
    assert "DEBUG" in result.diff.removed


def test_scored_diff_unchanged_key(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b)
    assert "PORT" in result.diff.unchanged
    assert "SHARED" in result.diff.unchanged


def test_scored_diff_score_between_0_and_1(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b)
    assert 0.0 <= result.score.score <= 1.0


def test_scored_diff_identical_configs_score_is_1():
    cfg = {"A": "1", "B": "2"}
    result = scored_diff(cfg, cfg)
    assert result.score.score == pytest.approx(1.0)


def test_scored_diff_labels_stored(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b, label_a="staging", label_b="prod")
    assert result.label_a == "staging"
    assert result.label_b == "prod"


def test_scored_diff_as_dict_keys(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b, label_a="staging", label_b="prod")
    d = result.as_dict()
    assert set(d.keys()) == {"label_a", "label_b", "score", "diff"}
    assert d["label_a"] == "staging"
    assert "added" in d["diff"]
    assert "grade" in d["score"]


def test_scored_diff_summary_contains_labels(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b, label_a="staging", label_b="prod")
    s = result.summary()
    assert "staging" in s
    assert "prod" in s


def test_scored_diff_summary_contains_score(cfg_a, cfg_b):
    result = scored_diff(cfg_a, cfg_b)
    s = result.summary()
    assert "score=" in s
    assert "grade=" in s


def test_scored_diff_non_dict_raises():
    with pytest.raises(ScoredDiffError):
        scored_diff(["a", "b"], {"A": "1"})  # type: ignore
