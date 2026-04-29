"""Higher-level helpers that combine differ_chain with other pipeline stages."""
from __future__ import annotations

from typing import Dict, List, Sequence

from stackdiff.differ_chain import DiffChain, build_chain, chain_summary
from stackdiff.masker import mask_config
from stackdiff.normalizer import normalize_config, NormalizerError


def masked_chain(
    configs: Sequence[Dict[str, object]],
    labels: Sequence[str] | None = None,
    patterns: Sequence[str] | None = None,
    placeholder: str = "***",
) -> DiffChain:
    """Mask sensitive keys in every config before building the chain.

    Args:
        configs:     Ordered config dicts.
        labels:      Optional display labels.
        patterns:    Additional glob patterns to treat as sensitive.
        placeholder: Replacement string for masked values.

    Returns:
        DiffChain built from the masked configs.
    """
    masked = [
        mask_config(cfg, extra_patterns=list(patterns or []), placeholder=placeholder)
        for cfg in configs
    ]
    return build_chain(masked, labels=labels)


def normalized_chain(
    configs: Sequence[Dict[str, object]],
    labels: Sequence[str] | None = None,
    lowercase_bools: bool = True,
    strip: bool = True,
) -> DiffChain:
    """Normalize every config before building the chain.

    Args:
        configs:        Ordered config dicts.
        labels:         Optional display labels.
        lowercase_bools: Coerce boolean-like strings to lowercase.
        strip:          Strip surrounding whitespace from string values.

    Returns:
        DiffChain built from the normalized configs.
    """
    normed = [
        normalize_config(cfg, strip=strip, coerce_bools=lowercase_bools)
        for cfg in configs
    ]
    return build_chain(normed, labels=labels)


def chain_change_hotspots(
    chain: DiffChain,
    top_n: int = 5,
) -> List[Dict[str, object]]:
    """Return the keys that changed most frequently across all chain links.

    Args:
        chain: A built DiffChain.
        top_n: Maximum number of hotspot keys to return.

    Returns:
        List of dicts [{"key": ..., "count": ...}] sorted by count descending.
    """
    freq: Dict[str, int] = {}
    for link in chain.links:
        for key in link.result.changed:
            freq[key] = freq.get(key, 0) + 1
        for key in link.result.added:
            freq[key] = freq.get(key, 0) + 1
        for key in link.result.removed:
            freq[key] = freq.get(key, 0) + 1

    sorted_keys = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    return [{"key": k, "count": c} for k, c in sorted_keys[:top_n]]
