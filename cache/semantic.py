"""
SemanticCache — wraps any CacheBackend with embedding-based similarity lookup.
Avoids redundant LLM calls for semantically equivalent queries.
"""
import hashlib
import math
from collections.abc import Callable

from .backends import CacheBackend, InMemoryBackend


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class SemanticCache:
    """
    Wraps a CacheBackend with embedding similarity lookup.

    embed_fn: callable that takes a string and returns a list of floats.
    Pass your Embedder instance's .embed method from rag/embedder.py.
    """

    def __init__(
        self,
        embed_fn: Callable[[str], list[float]],
        backend: CacheBackend | None = None,
        similarity_threshold: float = 0.95,
        ttl_seconds: int = 3600,
        max_size: int = 1000,
    ) -> None:
        self.embed_fn = embed_fn
        self.backend = backend or InMemoryBackend(max_size=max_size)
        self.threshold = similarity_threshold
        self.ttl = ttl_seconds
        # In-memory index: cache_key -> embedding (not persisted to backend)
        self._embeddings: dict[str, list[float]] = {}

    def get(self, query: str) -> str | None:
        """Return a cached response if a sufficiently similar query was seen before."""
        query_emb = self.embed_fn(query)
        for key, stored_emb in self._embeddings.items():
            if _cosine_similarity(query_emb, stored_emb) >= self.threshold:
                return self.backend.get(key)
        return None

    def set(self, query: str, response: str) -> None:
        """Store a query-response pair."""
        key = hashlib.sha256(query.encode()).hexdigest()[:16]
        self._embeddings[key] = self.embed_fn(query)
        self.backend.set(key, response, self.ttl)

    @classmethod
    def from_settings(cls, embed_fn: Callable[[str], list[float]]) -> "SemanticCache":
        from core.config import settings
        return cls(
            embed_fn=embed_fn,
            similarity_threshold=settings.cache_similarity_threshold,
            ttl_seconds=settings.cache_ttl_seconds,
            max_size=settings.cache_max_size,
        )
