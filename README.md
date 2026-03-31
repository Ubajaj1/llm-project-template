# LLM Project Template

Production-ready Python starter for LLM projects: agents, RAG, evals, and observability.

## Structure

```
llm-project-template/
│
├── core/                          # Foundation — every other module imports from here
│   ├── client.py                  # LLM client wrapper: swap providers here, not across the codebase
│   ├── router.py                  # Route by cost / quality / latency — fast, balanced, best tiers
│   └── config.py                  # All env vars in one place, validated with Pydantic
│
├── agents/                        # Agent runtime
│   ├── base.py                    # Base agent: ReAct loop, retry, state, tool dispatch
│   ├── harness.py                 # Context budget, circuit breaker, checkpointing, cost limits
│   └── tools/
│       └── registry.py            # Register + validate tools before the agent can call them
│
├── rag/                           # Full retrieval pipeline
│   ├── ingest.py                  # Load and clean raw documents
│   ├── chunker.py                 # Split strategy: fixed / recursive / semantic
│   ├── embedder.py                # Embedding model wrapper — swap models here
│   ├── retriever.py               # Hybrid search: dense vector + BM25
│   └── reranker.py                # Cross-encoder rerank before context injection
│
├── prompts/                       # Versioned prompt templates
│   ├── v1/
│   │   ├── system.txt             # System prompt — edit here, not in Python source
│   │   └── user.txt               # User prompt template with {variable} slots
│   └── loader.py                  # Load by name + version: never hardcode prompts in code
│
├── evals/                         # Eval harness — set this up before you ship
│   ├── datasets/                  # Golden test sets: labeled question / answer / context triples
│   ├── metrics/
│   │   └── faithfulness.py        # RAGAS-style: faithfulness, relevancy, groundedness
│   └── runner.py                  # Run suite, print scores, fail CI below threshold
│
├── observability/                 # Don't run LLM apps blind
│   ├── tracer.py                  # Trace every call: input, output, latency, token counts
│   ├── cost.py                    # Per-call + per-user cost tracking with hard limits
│   └── alerts.py                  # Latency and error rate thresholds
│
├── tests/
│   ├── unit/                      # Fast, no API calls
│   └── integration/               # Hits real services, runs in CI on merge
│
├── data/
│   ├── raw/                       # Source documents — gitignored, never committed
│   └── processed/                 # Chunks + embeddings — gitignored
│
├── scripts/
│   ├── ingest.py                  # Run ingestion pipeline: raw docs → vector store
│   └── run_evals.py               # Run full eval suite locally before pushing
│
├── .github/workflows/
│   ├── ci.yml                     # Lint + type check + unit tests on every PR
│   └── evals.yml                  # Full eval suite runs on merge to main
│
├── .env.example                   # Every env var the project needs, documented
├── pyproject.toml                 # Dependencies + tool config (ruff, mypy, pytest)
└── Makefile                       # make install / ingest / evals / test / lint
```

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/llm-project-template
cd llm-project-template
make install

# 2. Configure
cp .env.example .env
# Fill in your API keys in .env

# 3. Ingest your documents
make ingest

# 4. Run evals
make evals

# 5. Run tests
make test
```

## Key decisions baked in

**Prompt versioning from day 1.** Prompts live in `prompts/v1/` as plain text files. When you improve a prompt, bump to `v2/` — you keep the history and can A/B test versions. Never hardcode prompt text in Python.

**Model switching in one place.** `core/client.py` wraps all LLM calls. To switch from Claude to GPT-4o, change one file — not fifty call sites.

**Evals before shipping.** The `evals/` folder is a first-class citizen, not an afterthought. Wire it into CI with `evals.yml` so regressions surface before they reach production.

**Observability from the start.** `observability/tracer.py` wraps every LLM call. Cost tracking and latency alerts are configured via env vars, not hardcoded.

**Hybrid RAG.** `rag/retriever.py` combines dense vector search and BM25. Hybrid consistently outperforms either alone. `rag/reranker.py` then picks the best chunks — skipping reranking is the most common RAG quality mistake.

## Stack

| Layer | Default | Swap via |
|-------|---------|---------|
| LLM | Anthropic Claude | `core/client.py` |
| Embeddings | OpenAI text-embedding-3-small | `rag/embedder.py` |
| Vector store | Chroma | `VECTOR_STORE` env var |
| Evals | RAGAS | `evals/metrics/` |
| Observability | Langfuse | `LANGFUSE_*` env vars |
| Config | Pydantic Settings | `core/config.py` |
