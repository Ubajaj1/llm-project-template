"""
Cost tracker: per-call and per-user-per-day cost accounting.
Set limits in .env — the harness will kill runs that exceed them.
"""
from core.config import settings

# Approximate costs per 1M tokens (update as pricing changes)
COST_TABLE = {
    "claude-opus-4-6":          {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-6":        {"input": 3.00,  "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 0.80,  "output": 4.00},
    "gpt-4o":                   {"input": 5.00,  "output": 15.00},
    "gpt-4o-mini":              {"input": 0.15,  "output": 0.60},
}


class CostTracker:
    def estimate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Return estimated cost in USD for a single call."""
        pricing = COST_TABLE.get(model, {"input": 0, "output": 0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000

    def check_call_limit(self, cost: float) -> None:
        if cost > settings.max_cost_per_call:
            raise ValueError(f"Single call cost ${cost:.4f} exceeds limit ${settings.max_cost_per_call}")
