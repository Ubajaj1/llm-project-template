# Production-Grade Additions Design

**Date:** 2026-04-12
**Status:** Approved
**Scope:** Audit logging, semantic caching, rule-based guardrails, in-process rate limiting

---

## Background

The template already has: model routing, cost limits, Langfuse tracing, alert thresholds, hybrid RAG, and an evals harness. This spec adds four features that round out the production story for both FastAPI/Flask services and standalone scripts/batch pipelines.

---

## Architecture Overview

Four additions, each a peer module consistent with the existing structure:

```
llm-project-template/
├── audit/
│   ├── __init__.py
│   ├── event.py        # AuditEvent dataclass
│   ├── sinks.py        # AuditSink ABC + FileAuditSink
│   └── logger.py       # AuditLogger — wraps a sink
│
├── cache/
│   ├── __init__.py
│   ├── backends.py     # CacheBackend ABC + InMemoryBackend
│   └── semantic.py     # SemanticCache — embedding similarity lookup
│
├── guardrails/
│   ├── __init__.py
│   ├── base.py         # GuardrailResult, ABCs, GuardrailPolicy enum
│   ├── input.py        # PromptInjectionGuardrail, PIIInputGuardrail, LengthGuardrail
│   ├── output.py       # RefusalDetector, PIIOutputGuardrail, SchemaGuardrail
│   └── chain.py        # GuardrailChain — composable, policy-driven
│
├── core/
│   ├── config.py       # UPDATED — new settings for all four modules
│   └── rate_limiter.py # NEW — sliding window per user key
```

**Design principles:**
- Every backend is an ABC — swap `FileAuditSink → DatabaseSink`, `InMemoryBackend → RedisBackend` without touching call sites.
- Guardrails are composable — each is independent and testable in isolation.
- Rate limiter lives in `core/` as infrastructure, not a domain module.

---

## 1. Audit Logging (`audit/`)

**Purpose:** Tracing (Langfuse) is for debugging performance. Audit logging is for accountability — an immutable record of who asked what, at what cost, with what outcome. These serve different consumers (developers vs. compliance/security).

### `audit/event.py` — `AuditEvent` dataclass

| Field | Type | Notes |
|---|---|---|
| `request_id` | `str` | Ties to Langfuse trace |
| `user_id` | `str` | Who made the call |
| `model` | `str` | Which model was used |
| `prompt_hash` | `str` | SHA-256 of input — privacy-first default |
| `input_tokens` | `int` | |
| `output_tokens` | `int` | |
| `cost_usd` | `float` | |
| `latency_ms` | `float` | |
| `status` | `str` | `"ok"` \| `"error"` \| `"blocked_by_guardrail"` \| `"rate_limited"` |
| `guardrail_flags` | `list[str]` | e.g. `["pii_detected", "injection_attempt"]` |
| `ts` | `datetime` | UTC timestamp |

Raw prompt storage is opt-in via `AUDIT_STORE_RAW_PROMPTS=false` — off by default.

### `audit/sinks.py` — Pluggable backends

- `AuditSink` ABC: single `write(event: AuditEvent) -> None` method.
- `FileAuditSink`: appends newline-delimited JSON to a configurable path. No extra dependencies. Works for scripts and services.
- Swapping to a database or cloud sink: implement the ABC, change one config line.

### `audit/logger.py` — `AuditLogger`

- Wraps a sink.
- `log(event: AuditEvent) -> None` serializes and delegates to sink.
- Called after every LLM call completes (success or failure) — one call in the agent harness.

---

## 2. Caching (`cache/`)

**Purpose:** Avoid redundant LLM calls for semantically similar queries. Minimize cold-start latency.

### `cache/backends.py` — Pluggable storage

- `CacheBackend` ABC: `get(key: str) -> str | None`, `set(key, value, ttl_seconds: int) -> None`.
- `InMemoryBackend`: dict + per-entry expiry. Zero dependencies. Works for scripts and single-process services.
- Swap to `RedisBackend` for distributed/multi-worker: implement the ABC, change config.

### `cache/semantic.py` — `SemanticCache`

- Wraps any `CacheBackend`.
- On lookup: embed the incoming query, compare cosine similarity against stored query embeddings.
- On hit (similarity ≥ threshold): return cached response, log cache hit to audit.
- On miss: call LLM, store response + embedding, return result.
- Config: `CACHE_SIMILARITY_THRESHOLD=0.95`, `CACHE_TTL_SECONDS=3600`, `CACHE_MAX_SIZE=1000`.

### Cold-start optimization

- Heavy components (embedder, vector store, Chroma client) use lazy init — no penalty for scripts that don't use them.
- `make warmup` target: pre-loads embedder and hydrates cache from a configurable seed query file — useful for API services needing sub-second first response.

### Provider prompt caching (zero-code win)

- Anthropic's prompt caching activates when system prompt exceeds 1024 tokens and `cache_control` is set — saves ~90% on repeated system prompt tokens.
- Add `ANTHROPIC_PROMPT_CACHE=true` config flag. Document the one-line change in `core/client.py`.

---

## 3. Guardrails (`guardrails/`)

**Purpose:** Rule-based input/output validation. Fast — no extra LLM calls.

### `guardrails/base.py`

- `GuardrailResult(passed: bool, violations: list[str])`
- `InputGuardrail` ABC: `check(text: str) -> GuardrailResult`
- `OutputGuardrail` ABC: `check(text: str) -> GuardrailResult`
- `GuardrailPolicy` enum: `BLOCK | WARN | LOG_ONLY`

### `guardrails/input.py` — Input rules

| Guardrail | What it checks |
|---|---|
| `PromptInjectionGuardrail` | Regex patterns: "ignore previous instructions", "system:", "jailbreak", DAN-style overrides |
| `PIIInputGuardrail` | Regex for emails, phone numbers, SSNs, credit card numbers |
| `LengthGuardrail` | Max token count on input (default: 8000 tokens) |

### `guardrails/output.py` — Output rules

| Guardrail | What it checks |
|---|---|
| `RefusalDetector` | Catches "I cannot", "As an AI", "I'm not able to" — surfaces silent model refusals |
| `PIIOutputGuardrail` | Same regex patterns as input — catches PII the model echoed back |
| `SchemaGuardrail` | If structured output expected, validates response is valid JSON matching a schema |

### `guardrails/chain.py` — `GuardrailChain`

- Accepts a list of guardrails + a `GuardrailPolicy`.
- `BLOCK`: raises `GuardrailViolation` on first failure — call never reaches LLM (input) or caller (output).
- `WARN`: logs violation, continues.
- `LOG_ONLY`: records to audit log only, silent pass-through.
- Policy is per-chain — you can BLOCK on injection but WARN on PII.
- `GuardrailChain.run()` returns a `GuardrailResult` with all violations. The agent harness reads `result.violations` and writes them to `AuditEvent.guardrail_flags` before calling `AuditLogger.log()`. The chain itself has no knowledge of the audit system.

---

## 4. Rate Limiter (`core/rate_limiter.py`)

**Purpose:** Synchronous gate before LLM calls. Cost limits in config are checked asynchronously after the call — rate limiting prevents abuse before it starts.

- Sliding window counter per `user_id` key.
- Config: `RATE_LIMIT_RPM=60` (requests/minute), `RATE_LIMIT_TPM=100000` (tokens/minute).
- Raises `RateLimitExceeded` — caught by agent harness, logged to audit as `status="rate_limited"`.
- In-process dict-backed. For multi-worker deployments: implement a `RedisRateLimiter` using the same interface.

---

## Config Additions (`core/config.py`)

```python
# Audit
audit_enabled: bool = True
audit_log_path: str = "./data/audit/audit.jsonl"
audit_store_raw_prompts: bool = False

# Cache
cache_enabled: bool = True
cache_ttl_seconds: int = 3600
cache_similarity_threshold: float = 0.95
cache_max_size: int = 1000  # max number of cached query-response pairs (evicts LRU)
anthropic_prompt_cache: bool = True

# Guardrails
guardrails_input_policy: str = "block"   # block | warn | log_only
guardrails_output_policy: str = "warn"   # block | warn | log_only
guardrails_max_input_tokens: int = 8000

# Rate limiting
rate_limit_rpm: int = 60
rate_limit_tpm: int = 100_000
```

---

## What Was Deliberately Left Out

- **Authentication/authorization**: Application-specific, not an LLM template concern. Handle at the API gateway or web framework layer.
- **Async/streaming support**: Significant addition, not in scope. The template's sync pattern is intentional for simplicity.
- **LLM-as-judge guardrails**: Adds latency and cost. Rule-based covers 80% of cases. Opt-in for users who need it.
- **Retry logic**: Already referenced in the `agents/harness.py` stub (circuit breaker implies retry). Not a new module.

---

## Updated README Stack Table

| Layer | Default | Swap via |
|---|---|---|
| Audit log | JSONL file | `AuditSink` ABC |
| Cache backend | In-memory | `CacheBackend` ABC |
| Guardrails | Rule-based regex | Add guardrails to `GuardrailChain` |
| Rate limiter | In-process sliding window | Replace `RateLimiter` in `core/` |
