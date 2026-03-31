"""
Agent harness: the invisible runtime layer between your agent logic and the LLM.
You write the agent logic. The harness handles everything that can go wrong.
"""
from dataclasses import dataclass


@dataclass
class HarnessConfig:
    max_tokens_total: int = 100_000      # hard budget across all turns
    max_turns: int = 20                   # circuit breaker: stop runaway loops
    checkpoint_every_n_turns: int = 5    # resume from here after a crash
    max_cost_usd: float = 0.50           # kill the run if cost exceeds this


class AgentHarness:
    """
    Wraps an agent run with:
    - Context budget enforcement (not just recency pruning)
    - Circuit breaker on runaway loops
    - Mid-run checkpointing so crashes don't replay from scratch
    - Cumulative cost limits
    """

    def __init__(self, config: HarnessConfig | None = None) -> None:
        self.config = config or HarnessConfig()
        self._turn_count = 0
        self._total_cost = 0.0
        self._checkpoints: list[dict] = []

    def check_budget(self, token_count: int) -> None:
        if token_count > self.config.max_tokens_total:
            raise RuntimeError(f"Token budget exceeded: {token_count}")

    def check_turns(self) -> None:
        if self._turn_count >= self.config.max_turns:
            raise RuntimeError(f"Turn limit reached: {self._turn_count}")

    def check_cost(self, cost: float) -> None:
        self._total_cost += cost
        if self._total_cost > self.config.max_cost_usd:
            raise RuntimeError(f"Cost limit exceeded: ${self._total_cost:.4f}")

    def checkpoint(self, state: dict) -> None:
        self._checkpoints.append(state)
