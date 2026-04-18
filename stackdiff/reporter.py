"""Format and print diff results to stdout."""

from typing import TextIO
import sys
from stackdiff.differ import DiffResult


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_report(result: DiffResult, use_color: bool = True) -> str:
    lines = []

    for key, value in sorted(result.added.items()):
        line = f"  + {key} = {value}"
        lines.append(_colorize(line, ANSI_GREEN, use_color))

    for key, value in sorted(result.removed.items()):
        line = f"  - {key} = {value}"
        lines.append(_colorize(line, ANSI_RED, use_color))

    for key, (old_val, new_val) in sorted(result.changed.items()):
        line = f"  ~ {key}: {old_val} -> {new_val}"
        lines.append(_colorize(line, ANSI_YELLOW, use_color))

    if not lines:
        msg = "  No differences found."
        lines.append(_colorize(msg, ANSI_GREEN, use_color))

    return "\n".join(lines)


def print_report(
    result: DiffResult,
    label: str = "",
    use_color: bool = True,
    file: TextIO = sys.stdout,
) -> None:
    if label:
        print(f"--- {label} ---", file=file)
    print(format_report(result, use_color=use_color), file=file)
    print(f"Summary: {result.summary()}", file=file)
