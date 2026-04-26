"""Tests for stackdiff.scorer."""
from __future__ import annotations

import argparse
import json
import pytest

from stackdiff.scorer import score_configs, ScorerError, SimilarityScore
from stackdiff.scorer_cmd import build_scorer_parser, cmd_score


# ---------------------------------------------------------------------------
# score_configs unit tests
# ---------------------------------------------------------------------------

def test_identical_configs_score_is_1():
    cfg = {"A": "1", "B": "2"}
    s = score_configs(cfg, cfg.copy())
    assert s.score == 1.0
    assert s.grade == "A"
    assert s.matched_keys == 2


def test_completely_different_configs_score_is_0():
    s = score_configs({"A": "1"}, {"B": "2"})
    assert s.score == 0.0
    assert s.grade == "F"
    assert s.matched_keys == 0


def test_partial_match_score():
    local = {"A": "1", "B": "2", "C": "3", "D": "4"}
    remote = {"A": "1", "B": "2", "C": "X", "E": "5"}
    s = score_configs(local, remote)
    # unchanged: A, B  (2)
    # changed: C       (1)
    # removed: D       (1)
    # added: E         (1)
    # total = 5, matched = 2  => 0.4
    assert s.total_keys == 5
    assert s.matched_keys == 2
    assert s.score == pytest.approx(0.4, abs=1e-4)
    assert s.grade == "D"


def test_empty_configs_score_is_1():
    s = score_configs({}, {})
    assert s.score == 1.0
    assert s.grade == "A"


def test_non_dict_raises():
    with pytest.raises(ScorerError):
        score_configs(["a"], {"a": 1})  # type: ignore[arg-type]


def test_grade_boundaries():
    from stackdiff.scorer import _grade
    assert _grade(0.95) == "A"
    assert _grade(0.90) == "A"
    assert _grade(0.89) == "B"
    assert _grade(0.75) == "B"
    assert _grade(0.74) == "C"
    assert _grade(0.60) == "C"
    assert _grade(0.59) == "D"
    assert _grade(0.40) == "D"
    assert _grade(0.39) == "F"


def test_as_dict_keys():
    s = score_configs({"X": "1"}, {"X": "1"})
    d = s.as_dict()
    assert set(d.keys()) == {"total_keys", "matched_keys", "score", "grade"}


# ---------------------------------------------------------------------------
# scorer_cmd tests
# ---------------------------------------------------------------------------

def _make_args(local, remote, json_out=False, min_score=None):
    ns = argparse.Namespace(local=local, remote=remote, json=json_out, min_score=min_score)
    return ns


def test_cmd_score_prints_grade(tmp_path, capsys):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text('{"K": "1"}')
    b.write_text('{"K": "1"}')
    cmd_score(_make_args(str(a), str(b)))
    out = capsys.readouterr().out
    assert "A" in out
    assert "100.00%" in out


def test_cmd_score_json_output(tmp_path, capsys):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text('{"K": "1"}')
    b.write_text('{"K": "2"}')
    cmd_score(_make_args(str(a), str(b), json_out=True))
    data = json.loads(capsys.readouterr().out)
    assert "score" in data and "grade" in data


def test_cmd_score_min_score_fail(tmp_path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text('{"K": "1"}')
    b.write_text('{"X": "9"}')
    with pytest.raises(SystemExit) as exc:
        cmd_score(_make_args(str(a), str(b), min_score=0.9))
    assert exc.value.code == 2


def test_cmd_score_bad_file_exits(tmp_path):
    with pytest.raises(SystemExit) as exc:
        cmd_score(_make_args(str(tmp_path / "missing.json"), str(tmp_path / "also.json")))
    assert exc.value.code == 1


def test_build_scorer_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_scorer_parser(sub)
    args = root.parse_args(["score", "a.json", "b.json"])
    assert args.local == "a.json"
    assert args.remote == "b.json"
