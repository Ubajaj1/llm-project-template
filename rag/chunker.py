"""
Split documents into chunks for embedding.
Strategy matters: wrong chunk size is one of the top RAG failure modes.
"""
from enum import StrEnum

from .ingest import Document


class ChunkStrategy(StrEnum):
    FIXED = "fixed"           # fixed token count, fast, baseline
    RECURSIVE = "recursive"   # split on paragraph → sentence → word
    SEMANTIC = "semantic"     # split on embedding similarity shifts


class Chunker:
    def __init__(
        self,
        strategy: ChunkStrategy = ChunkStrategy.RECURSIVE,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    ) -> None:
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, document: Document) -> list[Document]:
        """Split a document into chunks using the configured strategy."""
        raise NotImplementedError
