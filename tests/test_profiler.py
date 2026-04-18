"""Tests for stackdiff.profiler."""

import pytest
from pathlib import Path

from stackdiff.profiler import (
    ProfileError,
    delete_profile,
    list_profiles,
    load_profile,
    save_profile,
)


@pytest.fixture
def prof_dir(tmp_path):
    return tmp_path / "profiles"


def test_save_and_load_roundtrip(prof_dir):
    data = {"env": "staging", "url": "https://staging.example.com"}
    save_profile("staging", data, base=prof_dir)
    loaded = load_profile("staging", base=prof_dir)
    assert loaded == data


def test_save_returns_path(prof_dir):
    path = save_profile("prod", {"env": "prod"}, base=prof_dir)
    assert path.exists()
    assert path.suffix == ".json"


def test_load_missing_raises(prof_dir):
    with pytest.raises(ProfileError, match="not found"):
        load_profile("ghost", base=prof_dir)


def test_list_empty(prof_dir):
    assert list_profiles(base=prof_dir) == []


def test_list_multiple(prof_dir):
    save_profile("alpha", {}, base=prof_dir)
    save_profile("beta", {}, base=prof_dir)
    assert list_profiles(base=prof_dir) == ["alpha", "beta"]


def test_delete_profile(prof_dir):
    save_profile("temp", {"x": 1}, base=prof_dir)
    delete_profile("temp", base=prof_dir)
    assert "temp" not in list_profiles(base=prof_dir)


def test_delete_missing_raises(prof_dir):
    with pytest.raises(ProfileError):
        delete_profile("nope", base=prof_dir)


def test_overwrite_profile(prof_dir):
    save_profile("cfg", {"a": 1}, base=prof_dir)
    save_profile("cfg", {"a": 99}, base=prof_dir)
    assert load_profile("cfg", base=prof_dir)["a"] == 99
