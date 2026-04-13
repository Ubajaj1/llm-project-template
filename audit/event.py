"""
Audit event — immutable record of every LLM call.
Distinct from tracing (Langfuse): tracing is for debugging, audit is for accountability.
"""
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class AuditEvent:
    request_id: str
    user_id: str
    model: str
    prompt_hash: str           # SHA-256 of input; full text stored if audit_store_raw_prompts=True
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    status: str                # "ok" | "error" | "blocked_by_guardrail" | "rate_limited"
    guardrail_flags: list[str] = field(default_factory=list)
    ts: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw_prompt: str | None = None  # populated only when audit_store_raw_prompts=True
