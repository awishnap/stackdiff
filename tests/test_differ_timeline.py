"""Tests for stackdiff.differ_timeline."""
import pytest

from stackdiff.differ_timeline import (
    DiffTimeline,
    TimelineEntry,
    TimelineError,
    build_timeline,
)


CFG_V1 = {"host": "localhost", "port": "5432", "debug": "true"}
CFG_V2 = {"host": "db.prod", "port": "5432", "debug": "false", "timeout": "30"}
CFG_V3 = {"host": "db.prod", "port": "5433", "timeout": "60"}


def test_build_timeline_returns_correct_entry_count():
    tl = build_timeline([CFG_V1, CFG_V2, CFG_V3])
    assert len(tl.entries) == 2


def test_build_timeline_default_labels():
    tl = build_timeline([CFG_V1, CFG_V2])
    assert tl.entries[0].label == "step-1"


def test_build_timeline_custom_labels():
    tl = build_timeline([CFG_V1, CFG_V2, CFG_V3], labels=["v1-v2", "v2-v3"])
    assert tl.entries[0].label == "v1-v2"
    assert tl.entries[1].label == "v2-v3"


def test_build_timeline_single_config_raises():
    with pytest.raises(TimelineError, match="At least two"):
        build_timeline([CFG_V1])


def test_build_timeline_empty_raises():
    with pytest.raises(TimelineError):
        build_timeline([])


def test_build_timeline_label_count_mismatch_raises():
    with pytest.raises(TimelineError, match="2 labels"):
        build_timeline([CFG_V1, CFG_V2, CFG_V3], labels=["only-one"])


def test_first_entry_detects_changed_key():
    tl = build_timeline([CFG_V1, CFG_V2])
    assert "host" in tl.entries[0].diff.changed


def test_first_entry_detects_added_key():
    tl = build_timeline([CFG_V1, CFG_V2])
    assert "timeout" in tl.entries[0].diff.added


def test_second_entry_detects_removed_key():
    tl = build_timeline([CFG_V1, CFG_V2, CFG_V3])
    assert "debug" in tl.entries[1].diff.removed


def test_as_dict_structure():
    tl = build_timeline([CFG_V1, CFG_V2])
    d = tl.as_dict()
    assert "entries" in d
    entry = d["entries"][0]
    assert "label" in entry
    assert "added" in entry
    assert "removed" in entry
    assert "changed" in entry


def test_summary_step_count():
    tl = build_timeline([CFG_V1, CFG_V2, CFG_V3])
    s = tl.summary()
    assert s["steps"] == 2


def test_summary_total_added():
    tl = build_timeline([CFG_V1, CFG_V2])
    s = tl.summary()
    assert s["total_added"] == 1  # timeout added


def test_summary_most_active_step():
    tl = build_timeline([CFG_V1, CFG_V2, CFG_V3], labels=["alpha", "beta"])
    s = tl.summary()
    # v1→v2 has more changes than v2→v3
    assert s["most_active_step"] == "alpha"


def test_summary_empty_timeline_most_active_is_none():
    tl = DiffTimeline(entries=[])
    s = tl.summary()
    assert s["most_active_step"] is None
