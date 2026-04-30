"""Tests for stackdiff.differ_graph."""
import pytest

from stackdiff.differ_graph import GraphError, build_graph


CFG_A = {"host": "localhost", "port": "5432", "debug": "true"}
CFG_B = {"host": "prod.db", "port": "5432", "debug": "false"}
CFG_C = {"host": "staging.db", "port": "5433", "timeout": "30"}


def test_build_graph_returns_correct_node_count():
    graph = build_graph({"a": CFG_A, "b": CFG_B})
    assert set(graph.nodes) == {"a", "b"}


def test_build_graph_single_edge_for_two_configs():
    graph = build_graph({"a": CFG_A, "b": CFG_B})
    assert len(graph.edges) == 1


def test_build_graph_three_configs_three_edges():
    graph = build_graph({"a": CFG_A, "b": CFG_B, "c": CFG_C})
    assert len(graph.edges) == 3


def test_build_graph_shared_keys_populated():
    graph = build_graph({"a": CFG_A, "b": CFG_B})
    edge = graph.edges[0]
    assert set(edge.shared_keys) == {"host", "port", "debug"}


def test_build_graph_diff_count_counts_changes():
    # A vs B: host changed, debug changed => diff_count == 2
    graph = build_graph({"a": CFG_A, "b": CFG_B})
    assert graph.edges[0].diff_count == 2


def test_build_graph_identical_configs_zero_diff():
    graph = build_graph({"x": CFG_A, "y": dict(CFG_A)})
    assert graph.edges[0].diff_count == 0


def test_build_graph_min_shared_keys_filters_edge():
    cfg_d = {"unrelated": "value"}
    graph = build_graph({"a": CFG_A, "d": cfg_d}, min_shared_keys=2)
    assert len(graph.edges) == 0


def test_build_graph_min_shared_keys_default_allows_single_shared():
    cfg_d = {"host": "other"}
    graph = build_graph({"a": CFG_A, "d": cfg_d})
    assert len(graph.edges) == 1


def test_build_graph_too_few_configs_raises():
    with pytest.raises(GraphError):
        build_graph({"only": CFG_A})


def test_build_graph_empty_raises():
    with pytest.raises(GraphError):
        build_graph({})


def test_as_dict_structure():
    graph = build_graph({"a": CFG_A, "b": CFG_B})
    d = graph.as_dict()
    assert "nodes" in d
    assert "edges" in d
    assert isinstance(d["edges"], list)
    assert "source" in d["edges"][0]
    assert "target" in d["edges"][0]


def test_summary_contains_node_and_edge_counts():
    graph = build_graph({"a": CFG_A, "b": CFG_B, "c": CFG_C})
    s = graph.summary()
    assert "3 nodes" in s
    assert "3 edges" in s


def test_most_connected_returns_node_with_most_edges():
    graph = build_graph({"a": CFG_A, "b": CFG_B, "c": CFG_C})
    # all nodes appear in 2 edges each for a 3-node complete graph
    result = graph.most_connected()
    assert result in graph.nodes


def test_most_connected_empty_edges_returns_empty():
    cfg_d = {"unique_key": "val"}
    graph = build_graph({"a": CFG_A, "d": cfg_d}, min_shared_keys=99)
    assert graph.most_connected() == ""
