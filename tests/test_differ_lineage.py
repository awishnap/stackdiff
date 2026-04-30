"""Tests for stackdiff.differ_lineage."""

import pytest

from stackdiff.differ_lineage import (
    KeyLineage,
    LineageEntry,
    LineageError,
    trace_all_keys,
    trace_key,
)


# ---------------------------------------------------------------------------
# trace_key
# ---------------------------------------------------------------------------

def test_trace_key_single_config_no_change():
    lineage = trace_key("HOST", [{"HOST": "localhost"}])
    assert len(lineage.entries) == 1
    assert lineage.entries[0].value == "localhost"
    assert lineage.entries[0].changed is False


def test_trace_key_value_unchanged_across_configs():
    configs = [{"HOST": "a"}, {"HOST": "a"}, {"HOST": "a"}]
    lineage = trace_key("HOST", configs)
    assert lineage.total_changes == 0


def test_trace_key_detects_change():
    configs = [{"HOST": "old"}, {"HOST": "new"}]
    lineage = trace_key("HOST", configs)
    assert lineage.entries[1].changed is True
    assert lineage.total_changes == 1


def test_trace_key_missing_key_gives_none():
    configs = [{"HOST": "x"}, {"PORT": "8080"}]
    lineage = trace_key("HOST", configs)
    assert lineage.entries[1].value is None
    assert lineage.entries[1].changed is True  # "x" -> None is a change


def test_trace_key_custom_labels():
    configs = [{"K": 1}, {"K": 2}]
    lineage = trace_key("K", configs, labels=["v1", "v2"])
    assert lineage.entries[0].label == "v1"
    assert lineage.entries[1].label == "v2"


def test_trace_key_labels_mismatch_raises():
    with pytest.raises(LineageError, match="labels length"):
        trace_key("K", [{"K": 1}, {"K": 2}], labels=["only-one"])


def test_trace_key_empty_configs_raises():
    with pytest.raises(LineageError, match="non-empty"):
        trace_key("K", [])


def test_trace_key_non_dict_config_raises():
    with pytest.raises(LineageError, match="not a dict"):
        trace_key("K", ["not-a-dict"])  # type: ignore[list-item]


def test_trace_key_first_seen():
    configs = [{"OTHER": 1}, {"K": "hello"}, {"K": "world"}]
    lineage = trace_key("K", configs, labels=["a", "b", "c"])
    assert lineage.first_seen == "b"


def test_trace_key_last_value():
    configs = [{"K": "first"}, {"K": "second"}, {"K": "third"}]
    lineage = trace_key("K", configs)
    assert lineage.last_value == "third"


def test_trace_key_as_dict_structure():
    lineage = trace_key("K", [{"K": 1}, {"K": 2}], labels=["x", "y"])
    d = lineage.as_dict()
    assert d["key"] == "K"
    assert len(d["entries"]) == 2
    assert d["entries"][0]["label"] == "x"


# ---------------------------------------------------------------------------
# trace_all_keys
# ---------------------------------------------------------------------------

def test_trace_all_keys_returns_one_lineage_per_unique_key():
    configs = [{"A": 1, "B": 2}, {"B": 3, "C": 4}]
    lineages = trace_all_keys(configs)
    keys = {l.key for l in lineages}
    assert keys == {"A", "B", "C"}


def test_trace_all_keys_preserves_insertion_order():
    configs = [{"Z": 1, "A": 2}, {"M": 3}]
    lineages = trace_all_keys(configs)
    assert lineages[0].key == "Z"
    assert lineages[1].key == "A"
    assert lineages[2].key == "M"


def test_trace_all_keys_empty_configs_raises():
    with pytest.raises(LineageError, match="non-empty"):
        trace_all_keys([])


def test_trace_all_keys_non_dict_raises():
    with pytest.raises(LineageError, match="must be dicts"):
        trace_all_keys([{"A": 1}, "bad"])  # type: ignore[list-item]
