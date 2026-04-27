"""Tests for stackdiff.digester."""
import pytest

from stackdiff.digester import (
    DigestComparison,
    DigesterError,
    compare_configs,
    hash_config,
)


# ---------------------------------------------------------------------------
# hash_config
# ---------------------------------------------------------------------------

def test_hash_config_returns_string():
    result = hash_config({"KEY": "value"})
    assert isinstance(result, str)
    assert len(result) == 64  # sha256 hex length


def test_hash_config_deterministic():
    cfg = {"A": "1", "B": "2"}
    assert hash_config(cfg) == hash_config(cfg)


def test_hash_config_key_order_independent():
    a = {"X": "1", "Y": "2"}
    b = {"Y": "2", "X": "1"}
    assert hash_config(a) == hash_config(b)


def test_hash_config_different_values_differ():
    assert hash_config({"K": "v1"}) != hash_config({"K": "v2"})


def test_hash_config_different_keys_differ():
    assert hash_config({"A": "v"}) != hash_config({"B": "v"})


def test_hash_config_empty_dict():
    digest = hash_config({})
    assert isinstance(digest, str)
    assert len(digest) > 0


def test_hash_config_non_dict_raises():
    with pytest.raises(DigesterError, match="Expected dict"):
        hash_config(["not", "a", "dict"])  # type: ignore[arg-type]


def test_hash_config_md5_algorithm():
    result = hash_config({"K": "v"}, algorithm="md5")
    assert len(result) == 32  # md5 hex length


def test_hash_config_unknown_algorithm_raises():
    with pytest.raises(DigesterError, match="Unknown hash algorithm"):
        hash_config({"K": "v"}, algorithm="not-a-real-algo")


# ---------------------------------------------------------------------------
# compare_configs
# ---------------------------------------------------------------------------

def test_compare_configs_identical_match():
    cfg = {"HOST": "localhost", "PORT": "5432"}
    cmp = compare_configs(cfg, cfg.copy())
    assert cmp.match is True
    assert cmp.left_digest == cmp.right_digest


def test_compare_configs_different_no_match():
    left = {"HOST": "staging"}
    right = {"HOST": "prod"}
    cmp = compare_configs(left, right)
    assert cmp.match is False
    assert cmp.left_digest != cmp.right_digest


def test_compare_configs_stores_algorithm():
    cmp = compare_configs({"A": "1"}, {"A": "1"}, algorithm="md5")
    assert cmp.algorithm == "md5"


def test_compare_configs_as_dict_keys():
    cmp = compare_configs({"A": "1"}, {"B": "2"})
    d = cmp.as_dict()
    assert set(d.keys()) == {"left_digest", "right_digest", "algorithm", "match"}


def test_compare_configs_as_dict_match_false():
    cmp = compare_configs({"A": "x"}, {"A": "y"})
    assert cmp.as_dict()["match"] is False
