"""
Pluggable audit sinks.
Implement AuditSink to write events anywhere: database, cloud logging, SIEM, etc.
"""
import json
from abc import ABC, abstractmethod
from pathlib import Path

from .event import AuditEvent


class AuditSink(ABC):
    @abstractmethod
    def write(self, event: AuditEvent) -> None: ...


class FileAuditSink(AuditSink):
    """Appends newline-delimited JSON to a file. No extra dependencies."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: AuditEvent) -> None:
        record: dict = {
            "request_id": event.request_id,
            "user_id": event.user_id,
            "model": event.model,
            "prompt_hash": event.prompt_hash,
            "input_tokens": event.input_tokens,
            "output_tokens": event.output_tokens,
            "cost_usd": event.cost_usd,
            "latency_ms": event.latency_ms,
            "status": event.status,
            "guardrail_flags": event.guardrail_flags,
            "ts": event.ts.isoformat(),
        }
        if event.raw_prompt is not None:
            record["raw_prompt"] = event.raw_prompt
        with self.path.open("a") as f:
            f.write(json.dumps(record) + "\n")
