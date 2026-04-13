"""
Warm up heavy components before serving traffic.
Pre-loads the embedder and hydrates the semantic cache with seed queries.

Create data/seed_queries.json with entries like:
    [{"query": "What is X?", "response": "X is ..."}]

Run with: make warmup
"""
import json
import sys
from pathlib import Path

SEED_PATH = Path("data/seed_queries.json")


def main() -> None:
    from rag.embedder import Embedder
    from cache.semantic import SemanticCache

    print("Loading embedder...")
    embedder = Embedder()

    print("Initializing semantic cache...")
    cache = SemanticCache.from_settings(embed_fn=embedder.embed)

    if not SEED_PATH.exists():
        print(f"No seed queries at {SEED_PATH} — skipping cache hydration.")
        print("Create that file to pre-populate the cache on startup.")
        return

    seed_data = json.loads(SEED_PATH.read_text())
    print(f"Hydrating cache with {len(seed_data)} seed queries...")
    for item in seed_data:
        cache.set(item["query"], item["response"])
    print("Done.")


if __name__ == "__main__":
    main()
