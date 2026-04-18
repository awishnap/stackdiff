"""Tests for stackdiff.reporter."""

import io
import pytest
from stackdiff.differ import diff_configs
from stackdiff.reporter import format_report, print_report


@pytest.fixture
def simple_diff():
    base = {"HOST": "localhost", "PORT": "5432", "OLD_KEY": "gone"}
    target = {"HOST": "prod.example.com", "PORT": "5432", "NEW_KEY": "here"}
    return diff_configs(base, target)


def test_format_report_contains_added(simple_diff):
    report = format_report(simple_diff, use_color=False)
    assert "+ NEW_KEY = here" in report


def test_format_report_contains_removed(simple_diff):
    report = format_report(simple_diff, use_color=False)
    assert "- OLD_KEY = gone" in report


def test_format_report_contains_changed(simple_diff):
    report = format_report(simple_diff, use_color=False)
    assert "~ HOST: localhost -> prod.example.com" in report


def test_format_report_no_diff():
    result = diff_configs({"A": "1"}, {"A": "1"})
    report = format_report(result, use_color=False)
    assert "No differences found" in report


def test_format_report_with_color(simple_diff):
    report = format_report(simple_diff, use_color=True)
    assert "\033[" in report


def test_print_report_writes_to_file(simple_diff):
    buf = io.StringIO()
    print_report(simple_diff, label="staging", use_color=False, file=buf)
    output = buf.getvalue()
    assert "--- staging ---" in output
    assert "Summary:" in output


def test_print_report_no_label(simple_diff):
    buf = io.StringIO()
    print_report(simple_diff, use_color=False, file=buf)
    output = buf.getvalue()
    assert "---" not in output
    assert "Summary:" in output
