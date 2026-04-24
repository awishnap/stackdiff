"""Tests for stackdiff.annotator."""
import pytest
from stackdiff.annotator import (
    AnnotatorError,
    add_note,
    get_notes,
    remove_notes,
    list_annotated_keys,
    clear_notes,
)


@pytest.fixture()
def note_dir(tmp_path):
    return str(tmp_path / "notes")


def test_add_and_get_single_note(note_dir):
    add_note(note_dir, "prod", "DB_HOST", "Points to RDS primary.")
    assert get_notes(note_dir, "prod", "DB_HOST") == ["Points to RDS primary."]


def test_get_notes_missing_key_returns_empty(note_dir):
    assert get_notes(note_dir, "prod", "MISSING") == []


def test_add_multiple_notes_to_same_key(note_dir):
    add_note(note_dir, "prod", "API_KEY", "First note.")
    add_note(note_dir, "prod", "API_KEY", "Second note.")
    notes = get_notes(note_dir, "prod", "API_KEY")
    assert len(notes) == 2
    assert notes[0] == "First note."
    assert notes[1] == "Second note."


def test_add_empty_note_raises(note_dir):
    with pytest.raises(AnnotatorError, match="empty"):
        add_note(note_dir, "prod", "KEY", "   ")


def test_remove_notes_returns_count(note_dir):
    add_note(note_dir, "staging", "TIMEOUT", "Check this.")
    add_note(note_dir, "staging", "TIMEOUT", "And this.")
    count = remove_notes(note_dir, "staging", "TIMEOUT")
    assert count == 2
    assert get_notes(note_dir, "staging", "TIMEOUT") == []


def test_remove_notes_missing_key_returns_zero(note_dir):
    assert remove_notes(note_dir, "prod", "NOPE") == 0


def test_list_annotated_keys_sorted(note_dir):
    add_note(note_dir, "prod", "Z_KEY", "z")
    add_note(note_dir, "prod", "A_KEY", "a")
    add_note(note_dir, "prod", "M_KEY", "m")
    assert list_annotated_keys(note_dir, "prod") == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_annotated_keys_empty_namespace(note_dir):
    assert list_annotated_keys(note_dir, "empty") == []


def test_clear_notes_removes_file(note_dir, tmp_path):
    add_note(note_dir, "staging", "FOO", "bar")
    clear_notes(note_dir, "staging")
    assert list_annotated_keys(note_dir, "staging") == []


def test_clear_notes_nonexistent_namespace_is_noop(note_dir):
    clear_notes(note_dir, "ghost")  # should not raise


def test_notes_isolated_per_namespace(note_dir):
    add_note(note_dir, "prod", "KEY", "prod note")
    add_note(note_dir, "staging", "KEY", "staging note")
    assert get_notes(note_dir, "prod", "KEY") == ["prod note"]
    assert get_notes(note_dir, "staging", "KEY") == ["staging note"]
