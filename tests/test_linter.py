"""Tests for stackdiff.linter."""
import pytest

from stackdiff.linter import (
    LinterError,
    LintIssue,
    LintResult,
    lint_config,
)


# ---------------------------------------------------------------------------
# lint_config — basic happy path
# ---------------------------------------------------------------------------

def test_clean_config_has_no_issues():
    result = lint_config({"HOST": "localhost", "PORT": "5432"})
    assert isinstance(result, LintResult)
    assert result.issues == []
    assert not result.has_errors()


def test_empty_config_has_no_issues():
    result = lint_config({})
    assert result.issues == []


# ---------------------------------------------------------------------------
# EMPTY_VALUE
# ---------------------------------------------------------------------------

def test_empty_string_value_raises_warning():
    result = lint_config({"DB_PASS": ""})
    codes = [i.code for i in result.issues]
    assert "EMPTY_VALUE" in codes
    assert result.issues[0].severity == "warning"


def test_none_value_raises_warning():
    result = lint_config({"API_KEY": None})
    codes = [i.code for i in result.issues]
    assert "EMPTY_VALUE" in codes


def test_zero_value_is_not_flagged():
    result = lint_config({"RETRIES": 0})
    assert not any(i.code == "EMPTY_VALUE" for i in result.issues)


# ---------------------------------------------------------------------------
# WHITESPACE_KEY
# ---------------------------------------------------------------------------

def test_leading_whitespace_key_is_error():
    result = lint_config({" HOST": "localhost"})
    codes = [i.code for i in result.issues]
    assert "WHITESPACE_KEY" in codes
    assert any(i.severity == "error" for i in result.issues if i.code == "WHITESPACE_KEY")


def test_trailing_whitespace_key_is_error():
    result = lint_config({"HOST ": "localhost"})
    assert any(i.code == "WHITESPACE_KEY" for i in result.issues)


# ---------------------------------------------------------------------------
# DUPLICATE_CASE
# ---------------------------------------------------------------------------

def test_duplicate_case_keys_are_error():
    result = lint_config({"host": "a", "HOST": "b"})
    codes = [i.code for i in result.issues]
    assert "DUPLICATE_CASE" in codes
    assert any(i.severity == "error" for i in result.issues if i.code == "DUPLICATE_CASE")


def test_no_duplicate_case_when_keys_differ():
    result = lint_config({"host": "a", "port": "b"})
    assert not any(i.code == "DUPLICATE_CASE" for i in result.issues)


# ---------------------------------------------------------------------------
# LintResult helpers
# ---------------------------------------------------------------------------

def test_summary_counts_errors_and_warnings():
    result = lint_config({" KEY": "", "dup": "x", "DUP": "y"})
    s = result.summary()
    assert "error" in s
    assert "warning" in s


def test_has_errors_false_for_warnings_only():
    result = lint_config({"EMPTY": ""})
    assert not result.has_errors()
    assert result.warnings


# ---------------------------------------------------------------------------
# LinterError
# ---------------------------------------------------------------------------

def test_non_dict_raises_linter_error():
    with pytest.raises(LinterError):
        lint_config(["not", "a", "dict"])  # type: ignore[arg-type]
