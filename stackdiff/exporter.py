"""Export diff results to various output formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from stackdiff.differ import DiffResult

OutputFormat = Literal["json", "csv", "markdown"]


class ExportError(Exception):
    """Raised when export fails."""


def export_json(result: DiffResult) -> str:
    payload = {
        "added": result.added,
        "removed": result.removed,
        "changed": {
            k: {"old": old, "new": new}
            for k, (old, new) in result.changed.items()
        },
        "unchanged": result.unchanged,
    }
    return json.dumps(payload, indent=2)


def export_csv(result: DiffResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["status", "key", "old_value", "new_value"])
    for k, v in result.added.items():
        writer.writerow(["added", k, "", v])
    for k, v in result.removed.items():
        writer.writerow(["removed", k, v, ""])
    for k, (old, new) in result.changed.items():
        writer.writerow(["changed", k, old, new])
    for k, v in result.unchanged.items():
        writer.writerow(["unchanged", k, v, v])
    return buf.getvalue()


def export_markdown(result: DiffResult) -> str:
    lines = ["# Diff Report", ""]
    sections = [
        ("Added", [(k, "", v) for k, v in result.added.items()]),
        ("Removed", [(k, v, "") for k, v in result.removed.items()]),
        ("Changed", [(k, old, new) for k, (old, new) in result.changed.items()]),
    ]
    for title, rows in sections:
        if rows:
            lines += [f"## {title}", "", "| Key | Old | New |", "|-----|-----|-----|"]  
            for key, old, new in rows:
                lines.append(f"| `{key}` | `{old}` | `{new}` |")
            lines.append("")
    if not result.added and not result.removed and not result.changed:
        lines.append("_No differences found._")
    return "\n".join(lines)


def export_diff(result: DiffResult, fmt: OutputFormat = "json") -> str:
    if fmt == "json":
        return export_json(result)
    if fmt == "csv":
        return export_csv(result)
    if fmt == "markdown":
        return export_markdown(result)
    raise ExportError(f"Unsupported format: {fmt}")
