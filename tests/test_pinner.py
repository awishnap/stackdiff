"""Tests for stackdiff.pinner."""

import pytest

from stackdiff.pinner import (
    PinnerError,
    PinViolation,
    check_pins,
    list_pins,
    load_pins,
    save_pins,
)


@pytest.fixture()
def pin_dir(tmp_path):
    return str(tmp_path / "pins")


# --- save / load / list ---

def test_save_and_load_roundtrip(pin_dir):
    pins = {"HOST": "localhost", "PORT": 5432}
    save_pins(pin_dir, "db", pins)
    assert load_pins(pin_dir, "db") == pins


def test_save_returns_path(pin_dir):
    path = save_pins(pin_dir, "web", {"URL": "https://example.com"})
    assert path.endswith("web.pins.json")


def test_load_missing_raises(pin_dir):
    with pytest.raises(PinnerError, match="No pins found"):
        load_pins(pin_dir, "nonexistent")


def test_list_empty(pin_dir):
    assert list_pins(pin_dir) == []


def test_list_returns_names(pin_dir):
    save_pins(pin_dir, "alpha", {"A": 1})
    save_pins(pin_dir, "beta", {"B": 2})
    assert list_pins(pin_dir) == ["alpha", "beta"]


def test_save_non_dict_raises(pin_dir):
    with pytest.raises(PinnerError):
        save_pins(pin_dir, "bad", ["not", "a", "dict"])  # type: ignore


# --- check_pins ---

def test_check_pins_all_match():
    pins = {"HOST": "localhost", "PORT": 5432}
    config = {"HOST": "localhost", "PORT": 5432, "EXTRA": "ignored"}
    result = check_pins(pins, config)
    assert result.ok
    assert result.summary() == "All pinned keys match."


def test_check_pins_detects_violation():
    pins = {"HOST": "localhost"}
    config = {"HOST": "remotehost"}
    result = check_pins(pins, config)
    assert not result.ok
    assert len(result.violations) == 1
    v = result.violations[0]
    assert v.key == "HOST"
    assert v.pinned == "localhost"
    assert v.actual == "remotehost"


def test_check_pins_detects_missing():
    pins = {"MISSING_KEY": "value"}
    config = {"OTHER": "something"}
    result = check_pins(pins, config)
    assert not result.ok
    assert "MISSING_KEY" in result.missing


def test_check_pins_summary_multiple_issues():
    pins = {"A": 1, "B": 2, "C": 3}
    config = {"A": 99}  # B and C missing, A wrong
    result = check_pins(pins, config)
    summary = result.summary()
    assert "violation" in summary
    assert "missing" in summary


def test_check_pins_non_dict_config_raises():
    with pytest.raises(PinnerError):
        check_pins({"A": 1}, ["not", "a", "dict"])  # type: ignore


def test_pin_violation_as_dict():
    v = PinViolation(key="X", pinned="a", actual="b")
    d = v.as_dict()
    assert d == {"key": "X", "pinned": "a", "actual": "b"}
