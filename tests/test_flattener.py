"""Tests for stackdiff.flattener."""

from __future__ import annotations

import json
import os
import pytest

from stackdiff.flattener import FlattenerError, flatten, unflatten


# ---------------------------------------------------------------------------
# flatten
# ---------------------------------------------------------------------------

def test_flatten_simple_nested():
    config = {"db": {"host": "localhost", "port": 5432}}
    assert flatten(config) == {"db.host": "localhost", "db.port": 5432}


def test_flatten_already_flat():
    config = {"HOST": "localhost", "PORT": "5432"}
    assert flatten(config) == config


def test_flatten_deeply_nested():
    config = {"a": {"b": {"c": "deep"}}}
    assert flatten(config) == {"a.b.c": "deep"}


def test_flatten_custom_separator():
    config = {"db": {"host": "localhost"}}
    assert flatten(config, sep="__") == {"db__host": "localhost"}


def test_flatten_empty_dict():
    assert flatten({}) == {}


def test_flatten_preserves_empty_nested_dict_as_value():
    # An empty nested dict cannot be flattened further; kept as-is.
    config = {"opts": {}}
    assert flatten(config) == {"opts": {}}


def test_flatten_non_dict_raises():
    with pytest.raises(FlattenerError):
        flatten(["not", "a", "dict"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# unflatten
# ---------------------------------------------------------------------------

def test_unflatten_basic():
    flat = {"db.host": "localhost", "db.port": 5432}
    assert unflatten(flat) == {"db": {"host": "localhost", "port": 5432}}


def test_unflatten_no_sep_keys_unchanged():
    flat = {"HOST": "localhost", "PORT": "5432"}
    assert unflatten(flat) == flat


def test_unflatten_deeply_nested():
    flat = {"a.b.c": "deep"}
    assert unflatten(flat) == {"a": {"b": {"c": "deep"}}}


def test_unflatten_custom_separator():
    flat = {"db__host": "localhost"}
    assert unflatten(flat, sep="__") == {"db": {"host": "localhost"}}


def test_unflatten_empty_dict():
    assert unflatten({}) == {}


def test_unflatten_non_dict_raises():
    with pytest.raises(FlattenerError):
        unflatten("not-a-dict")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# round-trip
# ---------------------------------------------------------------------------

def test_roundtrip_flatten_unflatten():
    original = {"app": {"name": "stackdiff", "version": "1.0"}, "debug": True}
    assert unflatten(flatten(original)) == original
