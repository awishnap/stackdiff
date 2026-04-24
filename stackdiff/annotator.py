"""annotator.py — attach freeform notes to named config keys."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List


class AnnotatorError(Exception):
    """Raised for annotation storage errors."""


def _notes_path(store_dir: str, namespace: str) -> Path:
    return Path(store_dir) / f"{namespace}.notes.json"


def _load_raw(store_dir: str, namespace: str) -> Dict[str, List[str]]:
    path = _notes_path(store_dir, namespace)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise AnnotatorError(f"Corrupt notes file {path}: {exc}") from exc


def _save_raw(store_dir: str, namespace: str, data: Dict[str, List[str]]) -> None:
    path = _notes_path(store_dir, namespace)
    Path(store_dir).mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_note(store_dir: str, namespace: str, key: str, note: str) -> None:
    """Append *note* to the list of notes for *key* in *namespace*."""
    if not note.strip():
        raise AnnotatorError("Note text must not be empty.")
    data = _load_raw(store_dir, namespace)
    data.setdefault(key, []).append(note)
    _save_raw(store_dir, namespace, data)


def get_notes(store_dir: str, namespace: str, key: str) -> List[str]:
    """Return all notes for *key* in *namespace* (empty list if none)."""
    return _load_raw(store_dir, namespace).get(key, [])


def remove_notes(store_dir: str, namespace: str, key: str) -> int:
    """Delete all notes for *key*. Returns the number of notes removed."""
    data = _load_raw(store_dir, namespace)
    removed = data.pop(key, [])
    _save_raw(store_dir, namespace, data)
    return len(removed)


def list_annotated_keys(store_dir: str, namespace: str) -> List[str]:
    """Return sorted list of keys that have at least one note."""
    return sorted(_load_raw(store_dir, namespace).keys())


def clear_notes(store_dir: str, namespace: str) -> None:
    """Remove the entire notes file for *namespace*."""
    path = _notes_path(store_dir, namespace)
    if path.exists():
        path.unlink()
