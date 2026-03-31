"""
LLM call tracer: log every call with input, output, latency, and token counts.
You can't debug what you can't observe. Wire this in from day 1.
Supports Langfuse and LangSmith — configure via LANGFUSE_* or LANGSMITH_API_KEY.
"""
import time
from dataclasses import dataclass, field
from datetime import datetime

from core.config import settings


@dataclass
class Trace:
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


class Tracer:
    def __init__(self) -> None:
        self.enabled = settings.tracing_enabled

    def trace(self, model: str, fn, *args, **kwargs):
        """Wrap an LLM call and emit a trace."""
        if not self.enabled:
            return fn(*args, **kwargs)
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        (time.perf_counter() - start) * 1000
        # TODO: parse token counts and compute cost, emit to Langfuse/LangSmith
        return result
