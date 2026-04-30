"""Tests for stackdiff.differ_cluster."""
import pytest

from stackdiff.differ_cluster import ClusterError, ClusterResult, cluster_configs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def identical_pair():
    cfg = {"HOST": "localhost", "PORT": "5432", "DB": "mydb"}
    return {"a": cfg.copy(), "b": cfg.copy()}


@pytest.fixture()
def divergent_trio():
    return {
        "prod": {"HOST": "prod.example.com", "PORT": "443", "SSL": "true"},
        "staging": {"HOST": "staging.example.com", "PORT": "443", "SSL": "true"},
        "local": {"HOST": "localhost", "PORT": "8080", "DEBUG": "1"},
    }


# ---------------------------------------------------------------------------
# cluster_configs
# ---------------------------------------------------------------------------

def test_cluster_identical_pair_in_same_cluster(identical_pair):
    result = cluster_configs(identical_pair, threshold=0.9)
    assert isinstance(result, ClusterResult)
    # Both labels should end up in a single cluster
    all_members = [m for members in result.clusters.values() for m in members]
    assert "a" in all_members
    assert "b" in all_members
    assert len(result.clusters) == 1


def test_cluster_divergent_configs_separate(divergent_trio):
    # With a high threshold, 'local' should not join prod/staging cluster
    result = cluster_configs(divergent_trio, threshold=0.95)
    # prod and staging are very similar; local should be its own centroid
    centroids = list(result.clusters.keys())
    assert len(centroids) >= 2


def test_cluster_low_threshold_merges_all(divergent_trio):
    result = cluster_configs(divergent_trio, threshold=0.0)
    all_members = [m for members in result.clusters.values() for m in members]
    assert set(all_members) == {"prod", "staging", "local"}
    assert len(result.clusters) == 1


def test_cluster_single_config_raises():
    with pytest.raises(ClusterError, match="At least two"):
        cluster_configs({"only": {"A": "1"}})


def test_cluster_empty_raises():
    with pytest.raises(ClusterError):
        cluster_configs({})


def test_cluster_invalid_threshold_raises(identical_pair):
    with pytest.raises(ClusterError, match="threshold"):
        cluster_configs(identical_pair, threshold=1.5)


def test_centroid_scores_between_0_and_1(divergent_trio):
    result = cluster_configs(divergent_trio, threshold=0.5)
    for score in result.centroid_scores.values():
        assert 0.0 <= score <= 1.0


def test_as_dict_contains_expected_keys(identical_pair):
    result = cluster_configs(identical_pair)
    d = result.as_dict()
    assert "clusters" in d
    assert "centroid_scores" in d


def test_summary_returns_string(divergent_trio):
    result = cluster_configs(divergent_trio, threshold=0.5)
    s = result.summary()
    assert isinstance(s, str)
    assert "Clusters" in s


def test_all_labels_appear_exactly_once(divergent_trio):
    result = cluster_configs(divergent_trio, threshold=0.5)
    all_members = [m for members in result.clusters.values() for m in members]
    assert sorted(all_members) == sorted(divergent_trio.keys())
    # No duplicates
    assert len(all_members) == len(set(all_members))
