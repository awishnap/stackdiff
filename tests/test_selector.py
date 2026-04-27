"""Tests for stackdiff.selector."""

from __future__ import annotations

import json
import textwrap

import pytest

from stackdiff.selector import (
    SelectorError,
    deselect_keys,
    select_keys,
    selection_summary,
)


CFG = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "prod", "APP_DEBUG": "false"}


# ---------------------------------------------------------------------------
# select_keys
# ---------------------------------------------------------------------------

def test_select_keys_exact():
    result = select_keys(CFG, keys=["DB_HOST", "APP_ENV"])
    assert result == {"DB_HOST": "localhost", "APP_ENV": "prod"}


def test_select_keys_glob():
    result = select_keys(CFG, patterns=["DB_*"])
    assert set(result) == {"DB_HOST", "DB_PORT"}


def test_select_keys_combined():
    result = select_keys(CFG, keys=["APP_ENV"], patterns=["DB_*"])
    assert set(result) == {"DB_HOST", "DB_PORT", "APP_ENV"}


def test_select_keys_no_match_returns_empty():
    result = select_keys(CFG, keys=["MISSING"])
    assert result == {}


def test_select_keys_no_criteria_raises():
    with pytest.raises(SelectorError, match="at least one"):
        select_keys(CFG)


def test_select_keys_non_dict_raises():
    with pytest.raises(SelectorError, match="must be a dict"):
        select_keys(["a", "b"], keys=["a"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# deselect_keys
# ---------------------------------------------------------------------------

def test_deselect_keys_exact():
    result = deselect_keys(CFG, keys=["DB_HOST", "DB_PORT"])
    assert set(result) == {"APP_ENV", "APP_DEBUG"}


def test_deselect_keys_glob():
    result = deselect_keys(CFG, patterns=["APP_*"])
    assert set(result) == {"DB_HOST", "DB_PORT"}


def test_deselect_keys_no_criteria_raises():
    with pytest.raises(SelectorError, match="at least one"):
        deselect_keys(CFG)


def test_deselect_keys_non_dict_raises():
    with pytest.raises(SelectorError):
        deselect_keys("not a dict", keys=["x"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# selection_summary
# ---------------------------------------------------------------------------

def test_selection_summary_counts():
    selected = select_keys(CFG, patterns=["DB_*"])
    summary = selection_summary(CFG, selected)
    assert summary["total"] == 4
    assert summary["kept"] == 2
    assert summary["dropped"] == 2


def test_selection_summary_all_kept():
    summary = selection_summary(CFG, CFG)
    assert summary["dropped"] == 0


def test_selection_summary_none_kept():
    summary = selection_summary(CFG, {})
    assert summary["kept"] == 0
    assert summary["dropped"] == 4
