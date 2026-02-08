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


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class EmbeddingsService:
    """
    Lightweight text similarity using TF-IDF
    (Alternative to sentence-transformers to avoid CUDA dependencies)
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        self._is_fitted = False
    
    def similarity(self, text_a: str, text_b: str) -> Optional[float]:
        """
        Calculate cosine similarity between two texts using TF-IDF
        Returns: float between 0 and 1, or None if error
        """
        if not text_a or not text_b:
            return None
        
        try:
            # Fit and transform both texts
            vectors = self.vectorizer.fit_transform([text_a, text_b])
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(vectors[0:1], vectors[1:2])
            
            return float(similarity_matrix[0][0])
        except Exception:
            return None


# Global instance
embeddings = EmbeddingsService()
