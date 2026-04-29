"""Tests for stackdiff.differ_pivot."""
from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path
from types import SimpleNamespace

import pytest

from stackdiff.differ import DiffResult, diff_configs
from stackdiff.differ_pivot import (
    PivotError,
    PivotRow,
    PivotTable,
    pivot_diff,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def result() -> DiffResult:
    a = {"host": "localhost", "port": "5432", "old_key": "gone"}
    b = {"host": "prod.db",   "port": "5432", "new_key": "here"}
    return diff_configs(a, b)


# ---------------------------------------------------------------------------
# pivot_diff – basic structure
# ---------------------------------------------------------------------------

def test_pivot_returns_pivot_table(result):
    table = pivot_diff(result)
    assert isinstance(table, PivotTable)


def test_pivot_added_key_present(result):
    table = pivot_diff(result)
    keys = [r.key for r in table.rows]
    assert "new_key" in keys


def test_pivot_removed_key_present(result):
    table = pivot_diff(result)
    keys = [r.key for r in table.rows]
    assert "old_key" in keys


def test_pivot_changed_key_present(result):
    table = pivot_diff(result)
    keys = [r.key for r in table.rows]
    assert "host" in keys


def test_pivot_unchanged_excluded_by_default(result):
    table = pivot_diff(result)
    statuses = {r.status for r in table.rows}
    assert "unchanged" not in statuses


def test_pivot_unchanged_included_when_flag_set(result):
    table = pivot_diff(result, include_unchanged=True)
    statuses = {r.status for r in table.rows}
    assert "unchanged" in statuses


def test_pivot_added_row_has_none_before(result):
    table = pivot_diff(result)
    row = next(r for r in table.rows if r.key == "new_key")
    assert row.before is None
    assert row.after == "here"


def test_pivot_removed_row_has_none_after(result):
    table = pivot_diff(result)
    row = next(r for r in table.rows if r.key == "old_key")
    assert row.after is None
    assert row.before == "gone"


def test_pivot_changed_row_has_both_values(result):
    table = pivot_diff(result)
    row = next(r for r in table.rows if r.key == "host")
    assert row.before == "localhost"
    assert row.after == "prod.db"


def test_pivot_non_diff_result_raises():
    with pytest.raises(PivotError):
        pivot_diff({"a": 1})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# PivotTable helpers
# ---------------------------------------------------------------------------

def test_filter_status_limits_rows(result):
    table = pivot_diff(result)
    filtered = table.filter_status("added")
    assert all(r.status == "added" for r in filtered.rows)


def test_keys_with_status(result):
    table = pivot_diff(result)
    changed = table.keys_with_status("changed")
    assert "host" in changed
    assert "port" not in changed


def test_as_dict_serialisable(result):
    table = pivot_diff(result, include_unchanged=True)
    data = table.as_dict()
    # Must round-trip through JSON without error
    assert json.loads(json.dumps(data)) == data
