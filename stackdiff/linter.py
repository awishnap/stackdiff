"""Config linter: checks for common issues in a config dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class LinterError(Exception):
    """Raised when the linter itself fails (not a lint finding)."""


@dataclass
class LintIssue:
    key: str
    code: str
    message: str
    severity: str = "warning"  # "warning" | "error"


@dataclass
class LintResult:
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def has_errors(self) -> bool:
        return bool(self.errors)

    def summary(self) -> str:
        e, w = len(self.errors), len(self.warnings)
        return f"{e} error(s), {w} warning(s)"


def _check_empty_values(config: dict[str, Any], issues: list[LintIssue]) -> None:
    for key, value in config.items():
        if value == "" or value is None:
            issues.append(
                LintIssue(key=key, code="EMPTY_VALUE",
                          message=f"Key '{key}' has an empty or null value.",
                          severity="warning")
            )


def _check_whitespace_keys(config: dict[str, Any], issues: list[LintIssue]) -> None:
    for key in config:
        if key != key.strip():
            issues.append(
                LintIssue(key=key, code="WHITESPACE_KEY",
                          message=f"Key '{key}' has leading or trailing whitespace.",
                          severity="error")
            )


def _check_duplicate_case(config: dict[str, Any], issues: list[LintIssue]) -> None:
    seen: dict[str, str] = {}
    for key in config:
        lower = key.lower()
        if lower in seen:
            issues.append(
                LintIssue(key=key, code="DUPLICATE_CASE",
                          message=(
                              f"Key '{key}' conflicts with '{seen[lower]}' "
                              "when compared case-insensitively."
                          ),
                          severity="error")
            )
        else:
            seen[lower] = key


def lint_config(config: dict[str, Any]) -> LintResult:
    """Run all lint checks on *config* and return a LintResult."""
    if not isinstance(config, dict):
        raise LinterError("lint_config expects a dict.")
    issues: list[LintIssue] = []
    _check_whitespace_keys(config, issues)
    _check_duplicate_case(config, issues)
    _check_empty_values(config, issues)
    return LintResult(issues=issues)
