"""Tests for stackdiff.differ_overlap."""

import pytest

from stackdiff.differ_overlap import (
    OverlapError,
    OverlapResult,
    analyze_overlap,
    overlap_summary,
)


def test_shared_keys_identified():
    a = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    b = {"HOST": "prod.example.com", "PORT": "5432", "TIMEOUT": "30"}
    result = analyze_overlap(a, b)
    assert sorted(result.shared_keys) == ["HOST", "PORT"]


def test_only_in_a():
    a = {"HOST": "x", "DEBUG": "true"}
    b = {"HOST": "y"}
    result = analyze_overlap(a, b)
    assert result.only_in_a == ["DEBUG"]
    assert result.only_in_b == []


def test_only_in_b():
    a = {"HOST": "x"}
    b = {"HOST": "y", "TIMEOUT": "30"}
    result = analyze_overlap(a, b)
    assert result.only_in_b == ["TIMEOUT"]
    assert result.only_in_a == []


def test_agreed_keys_same_value():
    a = {"PORT": "5432", "HOST": "different"}
    b = {"PORT": "5432", "HOST": "also-different"}
    result = analyze_overlap(a, b)
    assert "PORT" in result.agreed_keys
    assert "HOST" in result.disagreed_keys


def test_disagreed_keys_different_value():
    a = {"HOST": "staging", "PORT": "5432"}
    b = {"HOST": "prod", "PORT": "5432"}
    result = analyze_overlap(a, b)
    assert "HOST" in result.disagreed_keys
    assert "PORT" in result.agreed_keys


def test_overlap_ratio_all_shared():
    a = {"A": "1", "B": "2"}
    b = {"A": "1", "B": "2"}
    result = analyze_overlap(a, b)
    assert result.overlap_ratio == 1.0


def test_overlap_ratio_no_shared():
    a = {"A": "1"}
    b = {"B": "2"}
    result = analyze_overlap(a, b)
    assert result.overlap_ratio == 0.0


def test_agreement_ratio_full_agreement():
    a = {"A": "1", "B": "2"}
    b = {"A": "1", "B": "2"}
    result = analyze_overlap(a, b)
    assert result.agreement_ratio == 1.0


def test_agreement_ratio_no_agreement():
    a = {"A": "1", "B": "2"}
    b = {"A": "9", "B": "8"}
    result = analyze_overlap(a, b)
    assert result.agreement_ratio == 0.0


def test_empty_configs_return_empty_result():
    result = analyze_overlap({}, {})
    assert result.shared_keys == []
    assert result.only_in_a == []
    assert result.only_in_b == []
    assert result.overlap_ratio == 1.0
    assert result.agreement_ratio == 1.0


def test_non_dict_raises():
    with pytest.raises(OverlapError):
        analyze_overlap(["a"], {"a": "1"})  # type: ignore[arg-type]


def test_as_dict_keys():
    result = analyze_overlap({"X": "1"}, {"X": "2"})
    d = result.as_dict()
    assert "shared_keys" in d
    assert "only_in_a" in d
    assert "only_in_b" in d
    assert "agreed_keys" in d
    assert "disagreed_keys" in d
    assert "overlap_ratio" in d
    assert "agreement_ratio" in d


def test_overlap_summary_format():
    a = {"A": "1", "B": "2", "C": "3"}
    b = {"A": "1", "B": "99", "D": "4"}
    result = analyze_overlap(a, b)
    summary = overlap_summary(result)
    assert "shared=" in summary
    assert "only_a=" in summary
    assert "only_b=" in summary
    assert "agreed=" in summary
    assert "disagreed=" in summary
