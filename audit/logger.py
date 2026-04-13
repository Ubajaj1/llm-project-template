"""
AuditLogger — wraps a sink, called after every LLM call.
One call in the agent harness captures the full lifecycle: rate limit check,
guardrail result, model used, cost, and final status.
"""
import hashlib

from .event import AuditEvent
from .sinks import AuditSink, FileAuditSink


class AuditLogger:
    def __init__(self, sink: AuditSink, store_raw_prompts: bool = False) -> None:
        self.sink = sink
        self._store_raw = store_raw_prompts

    def log(self, event: AuditEvent) -> None:
        if not self._store_raw:
            event.raw_prompt = None
        self.sink.write(event)

    @staticmethod
    def hash_prompt(prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()

    @classmethod
    def from_settings(cls) -> "AuditLogger":
        from core.config import settings
        if not settings.audit_enabled:
            return _NoOpAuditLogger()  # type: ignore[return-value]
        return cls(
            sink=FileAuditSink(settings.audit_log_path),
            store_raw_prompts=settings.audit_store_raw_prompts,
        )


class _NoOpAuditLogger(AuditLogger):
    """Returned when audit_enabled=False. All calls are no-ops."""

    def __init__(self) -> None:
        pass  # no sink needed

    def log(self, event: AuditEvent) -> None:
        pass
