"""
Optional text embedding service using sentence-transformers.
If the dependency is not installed, the service gracefully degrades to no-op.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _HAS_ST = True
except Exception:  # ImportError or other runtime failures
    SentenceTransformer = None  # type: ignore
    np = None  # type: ignore
    _HAS_ST = False


class EmbeddingService:
    def __init__(self) -> None:
        self.model: Optional[SentenceTransformer] = None
        if _HAS_ST:
            try:
                # light, fast, widely available
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                self.model = None

    @property
    def available(self) -> bool:
        return self.model is not None and _HAS_ST

    @lru_cache(maxsize=2048)
    def embed(self, text: str):
        if not self.available:
            return None
        return self.model.encode(text, normalize_embeddings=True)

    def similarity(self, a: str, b: str) -> Optional[float]:
        if not self.available:
            return None
        ea = self.embed(a)
        eb = self.embed(b)
        if ea is None or eb is None:
            return None
        # cosine since normalized
        sim = float((ea * eb).sum())
        # clamp to [0,1]
        if sim < 0:
            sim = 0.0
        elif sim > 1:
            sim = 1.0
        return sim


# singleton instance
embeddings = EmbeddingService()
