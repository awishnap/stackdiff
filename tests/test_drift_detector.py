"""Tests for stackdiff.drift_detector."""

from __future__ import annotations

import pytest

from stackdiff.baseline import save_baseline
from stackdiff.drift_detector import DriftError, DriftReport, detect_drift


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path / "baselines")


def test_no_drift_when_configs_match(base_dir):
    cfg = {"HOST": "localhost", "PORT": "5432"}
    save_baseline("prod", cfg, baselines_dir=base_dir)
    report = detect_drift("prod", cfg, baselines_dir=base_dir)
    assert report.drifted is False
    assert report.added == {}
    assert report.removed == {}
    assert report.changed == {}


def test_drift_detected_on_changed_value(base_dir):
    old = {"HOST": "localhost", "PORT": "5432"}
    new = {"HOST": "db.prod.example.com", "PORT": "5432"}
    save_baseline("prod", old, baselines_dir=base_dir)
    report = detect_drift("prod", new, baselines_dir=base_dir)
    assert report.drifted is True
    assert "HOST" in report.changed
    assert report.changed["HOST"] == ("localhost", "db.prod.example.com")


def test_drift_detected_on_added_key(base_dir):
    old = {"HOST": "localhost"}
    new = {"HOST": "localhost", "DEBUG": "true"}
    save_baseline("staging", old, baselines_dir=base_dir)
    report = detect_drift("staging", new, baselines_dir=base_dir)
    assert report.drifted is True
    assert "DEBUG" in report.added


def test_drift_detected_on_removed_key(base_dir):
    old = {"HOST": "localhost", "SECRET": "abc"}
    new = {"HOST": "localhost"}
    save_baseline("staging", old, baselines_dir=base_dir)
    report = detect_drift("staging", new, baselines_dir=base_dir)
    assert report.drifted is True
    assert "SECRET" in report.removed


def test_summary_no_drift(base_dir):
    cfg = {"A": "1"}
    save_baseline("env", cfg, baselines_dir=base_dir)
    report = detect_drift("env", cfg, baselines_dir=base_dir)
    assert "No drift" in report.summary()
    assert "env" in report.summary()


def test_summary_with_drift(base_dir):
    save_baseline("env", {"A": "1"}, baselines_dir=base_dir)
    report = detect_drift("env", {"A": "2", "B": "3"}, baselines_dir=base_dir)
    summary = report.summary()
    assert "Drift detected" in summary
    assert "changed" in summary
    assert "added" in summary


def test_missing_baseline_raises_drift_error(base_dir):
    with pytest.raises(DriftError, match="ghost"):
        detect_drift("ghost", {"A": "1"}, baselines_dir=base_dir)


def test_report_message_matches_summary(base_dir):
    cfg = {"X": "1"}
    save_baseline("b", cfg, baselines_dir=base_dir)
    report = detect_drift("b", {"X": "2"}, baselines_dir=base_dir)
    assert report.message == report.summary()
