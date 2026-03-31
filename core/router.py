"""
Model router: select the right model per request based on cost, quality, or latency.
Change routing logic here without touching agent or RAG code.
"""
from .config import settings

# Route tiers: pick the tier per task type, not per call site
ROUTING_TABLE = {
    "fast": "claude-haiku-4-5-20251001",    # low latency, high volume
    "balanced": "claude-sonnet-4-6",         # default for most tasks
    "best": "claude-opus-4-6",               # complex reasoning, low volume
}


class ModelRouter:
    def select(self, messages: list[dict], tier: str = "balanced") -> str:
        """Return the model ID for a given tier."""
        return ROUTING_TABLE.get(tier, settings.default_model)

    def fallback(self) -> str:
        """Return the fallback model when the primary provider is unavailable."""
        return settings.fallback_model
