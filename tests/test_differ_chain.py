"""Tests for stackdiff.differ_chain."""
import pytest

from stackdiff.differ_chain import (
    ChainError,
    ChainLink,
    DiffChain,
    build_chain,
    chain_summary,
)


CFG_DEV = {"HOST": "dev.example.com", "PORT": "8000", "DEBUG": "true"}
CFG_STG = {"HOST": "stg.example.com", "PORT": "8000", "DEBUG": "false", "NEW_KEY": "1"}
CFG_PRD = {"HOST": "prd.example.com", "PORT": "443", "DEBUG": "false"}


def test_build_chain_returns_correct_link_count():
    chain = build_chain([CFG_DEV, CFG_STG, CFG_PRD])
    assert len(chain.links) == 2


def test_build_chain_single_config_raises():
    with pytest.raises(ChainError):
        build_chain([CFG_DEV])


def test_build_chain_empty_raises():
    with pytest.raises(ChainError):
        build_chain([])


def test_build_chain_labels_mismatch_raises():
    with pytest.raises(ChainError):
        build_chain([CFG_DEV, CFG_STG], labels=["only-one"])


def test_build_chain_default_labels():
    chain = build_chain([CFG_DEV, CFG_STG])
    assert chain.links[0].left_label == "config_0"
    assert chain.links[0].right_label == "config_1"


def test_build_chain_custom_labels():
    chain = build_chain([CFG_DEV, CFG_STG], labels=["dev", "staging"])
    assert chain.links[0].left_label == "dev"
    assert chain.links[0].right_label == "staging"


def test_chain_detects_changed_key():
    chain = build_chain([CFG_DEV, CFG_STG])
    link = chain.links[0]
    assert "HOST" in link.result.changed
    assert "DEBUG" in link.result.changed


def test_chain_detects_added_key():
    chain = build_chain([CFG_DEV, CFG_STG])
    link = chain.links[0]
    assert "NEW_KEY" in link.result.added


def test_chain_detects_removed_key():
    chain = build_chain([CFG_STG, CFG_PRD])
    link = chain.links[0]
    assert "NEW_KEY" in link.result.removed


def test_total_changes_sums_all_links():
    chain = build_chain([CFG_DEV, CFG_STG, CFG_PRD])
    assert chain.total_changes() > 0


def test_as_dict_structure():
    chain = build_chain([CFG_DEV, CFG_STG], labels=["dev", "stg"])
    d = chain.as_dict()
    assert isinstance(d, list)
    assert d[0]["left"] == "dev"
    assert d[0]["right"] == "stg"
    assert "added" in d[0]
    assert "removed" in d[0]
    assert "changed" in d[0]
    assert "unchanged" in d[0]


def test_chain_summary_format():
    chain = build_chain([CFG_DEV, CFG_STG], labels=["dev", "stg"])
    summary = chain_summary(chain)
    assert "dev -> stg" in summary
    assert "+" in summary


def test_chain_summary_empty_chain():
    chain = DiffChain(links=[])
    assert chain_summary(chain) == "(empty chain)"


def test_two_identical_configs_no_changes():
    chain = build_chain([CFG_DEV, CFG_DEV])
    assert chain.total_changes() == 0
