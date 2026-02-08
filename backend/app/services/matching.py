"""
Enhanced product matching with multi-stage algorithm:
1. Exact identifier matching (SKU, EAN, UPC)
2. Fuzzy text matching
3. ML-based semantic matching
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

from .normalization import normalize_title, extract_attributes, guess_brand
from .embeddings import embeddings


class MatchType(str, Enum):
    """Type of match found"""
    EXACT_IDENTIFIER = "exact_identifier"
    FUZZY_TEXT = "fuzzy_text"
    SEMANTIC = "semantic"
    NO_MATCH = "no_match"


@dataclass
class MatchResult:
    """Result of product matching"""
    is_match: bool
    confidence: float
    match_type: MatchType
    title_score: float = 0.0
    price_score: float = 0.0
    brand_match: bool = False
    capacity_match: bool = False


def jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity between two sets"""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    union = len(a | b)
    return inter / union


def price_affinity(p1: Optional[float], p2: Optional[float]) -> float:
    """Calculate price similarity (0-1)"""
    if not p1 or not p2 or p1 <= 0 or p2 <= 0:
        return 0.0
    diff = abs(p1 - p2)
    base = max(p1, p2)
    ratio = diff / base
    # closer prices -> higher score
    return max(0.0, 1.0 - min(ratio, 1.0))


def exact_identifier_match(
    sku_a: Optional[str], 
    sku_b: Optional[str],
    ean_a: Optional[str] = None,
    ean_b: Optional[str] = None,
    upc_a: Optional[str] = None,
    upc_b: Optional[str] = None
) -> bool:
    """Check if products match by exact identifiers"""
    # SKU match
    if sku_a and sku_b and sku_a.strip().lower() == sku_b.strip().lower():
        return True
    
    # EAN match
    if ean_a and ean_b and ean_a.strip() == ean_b.strip():
        return True
    
    # UPC match
    if upc_a and upc_b and upc_a.strip() == upc_b.strip():
        return True
    
    return False


def score_pair(
    title_a: str, 
    price_a: Optional[float], 
    title_b: str, 
    price_b: Optional[float],
    sku_a: Optional[str] = None,
    sku_b: Optional[str] = None,
    ean_a: Optional[str] = None,
    ean_b: Optional[str] = None
) -> MatchResult:
    """
    Score a pair of products for matching
    Returns MatchResult with confidence and match type
    """
    
    # Stage 1: Exact identifier matching
    if exact_identifier_match(sku_a, sku_b, ean_a, ean_b):
        return MatchResult(
            is_match=True,
            confidence=1.0,
            match_type=MatchType.EXACT_IDENTIFIER
        )
    
    # Stage 2: Fuzzy text matching
    tna = normalize_title(title_a)
    tnb = normalize_title(title_b)
    tokens_a = set(tna.split())
    tokens_b = set(tnb.split())
    title_score = jaccard(tokens_a, tokens_b)

    attrs_a = extract_attributes(title_a)
    attrs_b = extract_attributes(title_b)
    capacity_match = (
        attrs_a.get("capacity_gb") is not None 
        and attrs_a.get("capacity_gb") == attrs_b.get("capacity_gb")
    )

    brand_a = guess_brand(title_a)
    brand_b = guess_brand(title_b)
    brand_match = (brand_a is not None and brand_a == brand_b)

    price_score = price_affinity(price_a, price_b)

    # Stage 3: Semantic matching with embeddings
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
        
        # High confidence threshold for semantic matching
        if score >= 0.80:
            match_type = MatchType.SEMANTIC
            is_match = True
        elif title_score >= 0.85 and brand_match:
            match_type = MatchType.FUZZY_TEXT
            is_match = True
        else:
            match_type = MatchType.NO_MATCH
            is_match = False
    else:
        # Fallback weights without embeddings
        score = (
            0.55 * title_score +
            0.25 * price_score +
            (0.12 if brand_match else 0.0) +
            (0.08 if capacity_match else 0.0)
        )
        
        # Fuzzy matching threshold
        if title_score >= 0.85 and brand_match:
            match_type = MatchType.FUZZY_TEXT
            is_match = True
        else:
            match_type = MatchType.NO_MATCH
            is_match = False
    
    return MatchResult(
        is_match=is_match,
        confidence=score,
        match_type=match_type,
        title_score=title_score,
        price_score=price_score,
        brand_match=brand_match,
        capacity_match=capacity_match
    )
