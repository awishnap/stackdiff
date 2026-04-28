"""Tests for stackdiff.highlighter."""
import pytest

from stackdiff.highlighter import HighlighterError, highlight


CFG_A = {"HOST": "localhost", "PORT": "5432", "DB": "mydb", "USER": "admin", "PASS": "secret"}
CFG_B = {"HOST": "prod.host", "PORT": "5432", "DB": "mydb", "USER": "root", "PASS": "secret"}


def _statuses(result):
    return {ln.key: ln.status for ln in result.lines}


def test_changed_key_appears_as_changed():
    r = highlight({"A": "1"}, {"A": "2"}, context=0)
    assert len(r.lines) == 1
    assert r.lines[0].status == "changed"
    assert r.lines[0].old_value == "1"
    assert r.lines[0].new_value == "2"


def test_added_key_appears_as_added():
    r = highlight({}, {"X": "new"}, context=0)
    assert r.lines[0].status == "added"
    assert r.lines[0].old_value is None
    assert r.lines[0].new_value == "new"


def test_removed_key_appears_as_removed():
    r = highlight({"X": "old"}, {}, context=0)
    assert r.lines[0].status == "removed"
    assert r.lines[0].new_value is None


def test_unchanged_key_not_shown_without_context():
    r = highlight({"A": "1", "B": "same"}, {"A": "2", "B": "same"}, context=0)
    statuses = _statuses(r)
    assert "A" in statuses
    assert "B" not in statuses


def test_context_includes_neighbouring_keys():
    cfg_a = {"AA": "1", "BB": "x", "CC": "3"}
    cfg_b = {"AA": "1", "BB": "y", "CC": "3"}
    r = highlight(cfg_a, cfg_b, context=1)
    statuses = _statuses(r)
    assert statuses["BB"] == "changed"
    assert statuses["AA"] == "context"
    assert statuses["CC"] == "context"


def test_context_zero_omits_unchanged_neighbours():
    cfg_a = {"AA": "1", "BB": "x", "CC": "3"}
    cfg_b = {"AA": "1", "BB": "y", "CC": "3"}
    r = highlight(cfg_a, cfg_b, context=0)
    statuses = _statuses(r)
    assert "BB" in statuses
    assert "AA" not in statuses
    assert "CC" not in statuses


def test_identical_configs_produce_no_lines_with_zero_context():
    cfg = {"A": "1", "B": "2"}
    r = highlight(cfg, cfg, context=0)
    assert r.lines == []


def test_as_dict_contains_lines_key():
    r = highlight({"A": "1"}, {"A": "2"}, context=0)
    d = r.as_dict()
    assert "lines" in d
    assert d["lines"][0]["status"] == "changed"


def test_non_dict_config_a_raises():
    with pytest.raises(HighlighterError):
        highlight("not-a-dict", {"A": "1"})


def test_non_dict_config_b_raises():
    with pytest.raises(HighlighterError):
        highlight({"A": "1"}, ["not", "a", "dict"])


def test_negative_context_raises():
    with pytest.raises(HighlighterError):
        highlight({"A": "1"}, {"A": "2"}, context=-1)


def test_multiple_changed_keys_all_appear():
    r = highlight(CFG_A, CFG_B, context=0)
    statuses = _statuses(r)
    assert statuses["HOST"] == "changed"
    assert statuses["USER"] == "changed"
    assert "PORT" not in statuses
    assert "DB" not in statuses
    assert "PASS" not in statuses
