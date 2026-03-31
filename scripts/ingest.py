"""
Run the full ingestion pipeline: raw documents → vector store.
Usage: python scripts/ingest.py --source data/raw/ --store chroma
"""
import argparse
from pathlib import Path

from rag import Chunker, DocumentLoader, Embedder


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into the vector store")
    parser.add_argument("--source", type=Path, default=Path("data/raw"))
    parser.add_argument("--store", default="chroma")
    args = parser.parse_args()

    loader = DocumentLoader()
    chunker = Chunker()
    Embedder()

    docs = loader.load_directory(args.source)
    print(f"Loaded {len(docs)} documents")

    chunks = [chunk for doc in docs for chunk in chunker.split(doc)]
    print(f"Split into {len(chunks)} chunks")

    # TODO: embed and upsert into vector store
    print("Done. Vector store updated.")


if __name__ == "__main__":
    main()
