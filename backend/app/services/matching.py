"""
Lightweight product matching heuristics to identify identical items across sources
without changing the existing database schema. Purely additive.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .normalization import normalize_title, extract_attributes, guess_brand
from .embeddings import embeddings


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    union = len(a | b)
    return inter / union


def price_affinity(p1: Optional[float], p2: Optional[float]) -> float:
    if not p1 or not p2 or p1 <= 0 or p2 <= 0:
        return 0.0
    diff = abs(p1 - p2)
    base = max(p1, p2)
    ratio = diff / base
    # closer prices -> higher score
    return max(0.0, 1.0 - min(ratio, 1.0))


@dataclass
class MatchFeatures:
    title_score: float
    price_score: float
    brand_match: bool
    capacity_match: bool


def score_pair(title_a: str, price_a: Optional[float], title_b: str, price_b: Optional[float]) -> Tuple[float, MatchFeatures]:
    tna = normalize_title(title_a)
    tnb = normalize_title(title_b)
    tokens_a = set(tna.split())
    tokens_b = set(tnb.split())
    title_score = jaccard(tokens_a, tokens_b)

    attrs_a = extract_attributes(title_a)
    attrs_b = extract_attributes(title_b)
    capacity_match = (attrs_a.get("capacity_gb") is not None and attrs_a.get("capacity_gb") == attrs_b.get("capacity_gb"))

    brand_a = guess_brand(title_a)
    brand_b = guess_brand(title_b)
    brand_match = (brand_a is not None and brand_a == brand_b)

    price_score = price_affinity(price_a, price_b)

    # Optional embedding similarity
    emb_sim = embeddings.similarity(title_a, title_b)

    if emb_sim is not None:
        # Rebalanced weights when embeddings available
        score = (
            0.40 * title_score +
            0.20 * price_score +
            0.20 * emb_sim +
            (0.12 if brand_match else 0.0) +
            (0.08 if capacity_match else 0.0)
        )
    else:
        # Fallback weights
        score = (
            0.55 * title_score +
            0.25 * price_score +
            (0.12 if brand_match else 0.0) +
            (0.08 if capacity_match else 0.0)
        )
    return score, MatchFeatures(title_score, price_score, brand_match, capacity_match)
