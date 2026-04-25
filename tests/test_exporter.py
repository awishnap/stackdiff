"""Tests for stackdiff.exporter."""

import csv
import io
import json

import pytest

from stackdiff.differ import DiffResult
from stackdiff.exporter import ExportError, export_diff, export_csv, export_json, export_markdown


@pytest.fixture
def result():
    return DiffResult(
        added={"NEW_KEY": "newval"},
        removed={"OLD_KEY": "oldval"},
        changed={"HOST": ("localhost", "prod.host")},
        unchanged={"PORT": "8080"},
    )


def test_export_json_structure(result):
    out = export_json(result)
    data = json.loads(out)
    assert data["added"] == {"NEW_KEY": "newval"}
    assert data["removed"] == {"OLD_KEY": "oldval"}
    assert data["changed"]["HOST"] == {"old": "localhost", "new": "prod.host"}
    assert data["unchanged"] == {"PORT": "8080"}


def test_export_json_empty_diff():
    """Ensure export_json handles a fully empty diff without errors."""
    empty = DiffResult(added={}, removed={}, changed={}, unchanged={})
    out = export_json(empty)
    data = json.loads(out)
    assert data["added"] == {}
    assert data["removed"] == {}
    assert data["changed"] == {}
    assert data["unchanged"] == {}


def test_export_csv_headers(result):
    out = export_csv(result)
    reader = csv.reader(io.StringIO(out))
    headers = next(reader)
    assert headers == ["status", "key", "old_value", "new_value"]


def test_export_csv_rows(result):
    out = export_csv(result)
    rows = list(csv.reader(io.StringIO(out)))[1:]
    statuses = {r[0] for r in rows}
    assert statuses == {"added", "removed", "changed", "unchanged"}


def test_export_markdown_contains_headers(result):
    out = export_markdown(result)
    assert "## Added" in out
    assert "## Removed" in out
    assert "## Changed" in out


def test_export_markdown_contains_keys(result):
    out = export_markdown(result)
    assert "NEW_KEY" in out
    assert "OLD_KEY" in out
    assert "HOST" in out


def test_export_markdown_no_diff():
    empty = DiffResult(added={}, removed={}, changed={}, unchanged={"A": "1"})
    out = export_markdown(empty)
    assert "No differences found" in out


def test_export_diff_dispatches(result):
    assert export_diff(result, "json").startswith("{")
    assert "status" in export_diff(result, "csv")
    assert "#" in export_diff(result, "markdown")


def test_export_diff_invalid_format(result):
    with pytest.raises(ExportError, match="Unsupported format"):
        export_diff(result, "xml")  # type: ignore
