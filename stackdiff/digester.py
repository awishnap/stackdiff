"""digester.py — compute and compare content hashes for config dicts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


class DigesterError(Exception):
    """Raised when hashing or comparison fails."""


def _stable_json(config: Any) -> str:
    """Serialize *config* to a deterministic JSON string (sorted keys)."""
    if not isinstance(config, dict):
        raise DigesterError(f"Expected dict, got {type(config).__name__}")
    return json.dumps(config, sort_keys=True, ensure_ascii=True)


def hash_config(config: dict, algorithm: str = "sha256") -> str:
    """Return a hex digest of *config* serialized as stable JSON.

    Parameters
    ----------
    config:
        The configuration dictionary to hash.
    algorithm:
        Any algorithm name accepted by :func:`hashlib.new` (default ``sha256``).

    Returns
    -------
    str
        Lowercase hexadecimal digest string.
    """
    try:
        h = hashlib.new(algorithm)
    except ValueError as exc:
        raise DigesterError(f"Unknown hash algorithm '{algorithm}'") from exc

    payload = _stable_json(config).encode()
    h.update(payload)
    return h.hexdigest()


@dataclass
class DigestComparison:
    """Result of comparing two config digests."""

    left_digest: str
    right_digest: str
    algorithm: str
    match: bool

    def as_dict(self) -> dict:
        return {
            "left_digest": self.left_digest,
            "right_digest": self.right_digest,
            "algorithm": self.algorithm,
            "match": self.match,
        }


def compare_configs(
    left: dict,
    right: dict,
    algorithm: str = "sha256",
) -> DigestComparison:
    """Hash both configs and return a :class:`DigestComparison`."""
    left_digest = hash_config(left, algorithm)
    right_digest = hash_config(right, algorithm)
    return DigestComparison(
        left_digest=left_digest,
        right_digest=right_digest,
        algorithm=algorithm,
        match=(left_digest == right_digest),
    )
