"""Tests for stackdiff.summarizer."""

import pytest

from stackdiff.differ import DiffResult
from stackdiff.summarizer import (
    DiffSummary,
    SummarizerError,
    format_summary,
    summarize,
)


@pytest.fixture()
def simple_result() -> DiffResult:
    return DiffResult(
        added={"NEW_KEY": "val"},
        removed={"OLD_KEY": "gone"},
        changed={"HOST": ("localhost", "prod.host")},
        unchanged={"PORT": "8080", "DEBUG": "false"},
    )


def test_summarize_counts(simple_result: DiffResult) -> None:
    s = summarize(simple_result)
    assert s.added == 1
    assert s.removed == 1
    assert s.changed == 1
    assert s.unchanged == 2
    assert s.total_keys == 5


def test_summarize_change_rate(simple_result: DiffResult) -> None:
    s = summarize(simple_result)
    # 3 out of 5 keys changed
    assert abs(s.change_rate - 0.6) < 1e-6


def test_summarize_top_changed_sorted(simple_result: DiffResult) -> None:
    s = summarize(simple_result)
    assert s.top_changed == sorted(["NEW_KEY", "OLD_KEY", "HOST"])


def test_summarize_top_n_limits_results(simple_result: DiffResult) -> None:
    s = summarize(simple_result, top_n=1)
    assert len(s.top_changed) == 1


def test_summarize_top_n_zero(simple_result: DiffResult) -> None:
    s = summarize(simple_result, top_n=0)
    assert s.top_changed == []


def test_summarize_empty_diff() -> None:
    result = DiffResult(added={}, removed={}, changed={}, unchanged={"A": "1"})
    s = summarize(result)
    assert s.change_rate == 0.0
    assert s.top_changed == []


def test_summarize_all_empty_diff() -> None:
    result = DiffResult(added={}, removed={}, changed={}, unchanged={})
    s = summarize(result)
    assert s.total_keys == 0
    assert s.change_rate == 0.0


def test_summarize_invalid_input_raises() -> None:
    with pytest.raises(SummarizerError, match="Expected DiffResult"):
        summarize({"not": "a diff result"})  # type: ignore[arg-type]


def test_summarize_negative_top_n_raises(simple_result: DiffResult) -> None:
    with pytest.raises(SummarizerError, match="top_n"):
        summarize(simple_result, top_n=-1)


def test_as_dict_keys(simple_result: DiffResult) -> None:
    d = summarize(simple_result).as_dict()
    assert set(d.keys()) == {
        "total_keys", "added", "removed", "changed",
        "unchanged", "change_rate", "top_changed",
    }


def test_format_summary_contains_rate(simple_result: DiffResult) -> None:
    text = format_summary(summarize(simple_result))
    assert "60.0%" in text


def test_format_summary_no_changed_omits_top_line() -> None:
    result = DiffResult(added={}, removed={}, changed={}, unchanged={"X": "1"})
    text = format_summary(summarize(result))
    assert "Top changed" not in text
