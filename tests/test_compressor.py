"""Tests for stackdiff.compressor."""
import pytest

from stackdiff.differ import DiffResult
from stackdiff.compressor import (
    CompressedDiff,
    CompressorError,
    compress,
    compression_ratio,
)


@pytest.fixture()
def mixed_result() -> DiffResult:
    return DiffResult(
        added={"NEW_KEY": "v"},
        removed={"OLD_KEY": "x"},
        changed={"HOST": ("old", "new")},
        unchanged={"PORT": "5432", "DB": "mydb"},
    )


def test_compress_drops_unchanged(mixed_result):
    cd = compress(mixed_result)
    assert "NEW_KEY" in cd.added
    assert "OLD_KEY" in cd.removed
    assert "HOST" in cd.changed
    assert cd.unchanged_count == 2


def test_compress_unchanged_keys_empty_by_default(mixed_result):
    cd = compress(mixed_result)
    assert cd.unchanged_keys == []


def test_compress_keep_unchanged_keys(mixed_result):
    cd = compress(mixed_result, keep_unchanged_keys=True)
    assert set(cd.unchanged_keys) == {"PORT", "DB"}


def test_compress_as_dict_keys(mixed_result):
    d = compress(mixed_result).as_dict()
    assert set(d.keys()) == {"added", "removed", "changed", "unchanged_count", "unchanged_keys"}


def test_compress_empty_result():
    result = DiffResult(added={}, removed={}, changed={}, unchanged={})
    cd = compress(result)
    assert cd.unchanged_count == 0
    assert cd.added == {}


def test_compress_only_unchanged():
    result = DiffResult(added={}, removed={}, changed={}, unchanged={"A": "1", "B": "2"})
    cd = compress(result)
    assert cd.unchanged_count == 2
    assert cd.added == {} and cd.removed == {} and cd.changed == {}


def test_compress_invalid_input_raises():
    with pytest.raises(CompressorError):
        compress({"not": "a DiffResult"})  # type: ignore[arg-type]


def test_compression_ratio_all_unchanged():
    result = DiffResult(added={}, removed={}, changed={}, unchanged={"A": "1"})
    assert compression_ratio(result) == pytest.approx(1.0)


def test_compression_ratio_none_unchanged(mixed_result):
    result = DiffResult(
        added={"A": "1"},
        removed={"B": "2"},
        changed={"C": ("old", "new")},
        unchanged={},
    )
    assert compression_ratio(result) == pytest.approx(0.0)


def test_compression_ratio_partial(mixed_result):
    # 2 unchanged out of 5 total
    ratio = compression_ratio(mixed_result)
    assert ratio == pytest.approx(2 / 5)


def test_compression_ratio_empty_is_one():
    result = DiffResult(added={}, removed={}, changed={}, unchanged={})
    assert compression_ratio(result) == pytest.approx(1.0)


def test_compression_ratio_invalid_raises():
    with pytest.raises(CompressorError):
        compression_ratio("bad")  # type: ignore[arg-type]
