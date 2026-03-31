"""
Hybrid retriever: dense vector search + BM25 keyword search.
Hybrid beats either alone on most real-world corpora.
"""
from .ingest import Document


class Retriever:
    def __init__(self, top_k: int = 20) -> None:
        self.top_k = top_k
        # TODO: initialise vector store and BM25 index

    def retrieve(self, query: str) -> list[Document]:
        """Return top_k candidates via hybrid search. Pass to reranker next."""
        raise NotImplementedError

    def _dense(self, query: str) -> list[Document]:
        raise NotImplementedError

    def _bm25(self, query: str) -> list[Document]:
        raise NotImplementedError

    def _fuse(self, dense: list[Document], bm25: list[Document]) -> list[Document]:
        """Reciprocal rank fusion."""
        raise NotImplementedError
