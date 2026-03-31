"""
Cross-encoder reranker. Run after retrieval, before context injection.
Retrieval casts a wide net (top 20). Reranking picks the best 5.
Skipping this step is the most common RAG quality mistake.
"""
from .ingest import Document


class Reranker:
    def __init__(self, top_n: int = 5) -> None:
        self.top_n = top_n

    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Score each candidate against the query, return top_n."""
        raise NotImplementedError
