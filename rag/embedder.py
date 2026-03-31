"""Embedding model wrapper. Swap models here without touching retrieval code."""
from core.config import settings


class Embedder:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.embedding_model

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed with respect to settings.embedding_batch_size."""
        raise NotImplementedError
