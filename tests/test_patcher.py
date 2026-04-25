"""Tests for stackdiff.patcher."""

from __future__ import annotations

import pytest

from stackdiff.differ import diff_configs
from stackdiff.patcher import PatchError, apply_patch, patch_summary


# ---------------------------------------------------------------------------
# apply_patch – forward strategy
# ---------------------------------------------------------------------------

def test_forward_patch_adds_keys():
    base = {"A": "1"}
    target = {"A": "1", "B": "2"}
    diff = diff_configs(base, target)
    result = apply_patch(base, diff)
    assert result == target


def test_forward_patch_removes_keys():
    base = {"A": "1", "B": "2"}
    target = {"A": "1"}
    diff = diff_configs(base, target)
    result = apply_patch(base, diff)
    assert result == target


def test_forward_patch_changes_values():
    base = {"A": "old"}
    target = {"A": "new"}
    diff = diff_configs(base, target)
    result = apply_patch(base, diff)
    assert result["A"] == "new"


def test_forward_patch_unchanged_keys_preserved():
    base = {"X": "keep", "Y": "old"}
    target = {"X": "keep", "Y": "new"}
    diff = diff_configs(base, target)
    result = apply_patch(base, diff)
    assert result["X"] == "keep"


def test_forward_patch_no_diff_returns_same():
    base = {"A": "1"}
    diff = diff_configs(base, base)
    result = apply_patch(base, diff)
    assert result == base


# ---------------------------------------------------------------------------
# apply_patch – reverse strategy
# ---------------------------------------------------------------------------

def test_reverse_patch_undoes_addition():
    base = {"A": "1"}
    target = {"A": "1", "B": "2"}
    diff = diff_configs(base, target)
    result = apply_patch(target, diff, strategy="reverse")
    assert "B" not in result


def test_reverse_patch_restores_removed_key():
    base = {"A": "1", "B": "2"}
    target = {"A": "1"}
    diff = diff_configs(base, target)
    result = apply_patch(target, diff, strategy="reverse")
    assert result["B"] == "2"


def test_reverse_patch_restores_changed_value():
    base = {"A": "old"}
    target = {"A": "new"}
    diff = diff_configs(base, target)
    result = apply_patch(target, diff, strategy="reverse")
    assert result["A"] == "old"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_unknown_strategy_raises():
    base = {"A": "1"}
    diff = diff_configs(base, base)
    with pytest.raises(PatchError, match="Unknown patch strategy"):
        apply_patch(base, diff, strategy="sideways")


# ---------------------------------------------------------------------------
# patch_summary
# ---------------------------------------------------------------------------

def test_patch_summary_forward_all_changes():
    diff = diff_configs({"A": "1", "B": "old"}, {"B": "new", "C": "3"})
    summary = patch_summary(diff, "forward")
    assert "applying" in summary
    assert "+1" in summary
    assert "-1" in summary
    assert "~1" in summary


def test_patch_summary_no_changes():
    diff = diff_configs({"A": "1"}, {"A": "1"})
    summary = patch_summary(diff)
    assert "no changes" in summary


def test_patch_summary_reverse_label():
    diff = diff_configs({}, {"X": "1"})
    summary = patch_summary(diff, "reverse")
    assert "reverting" in summary
