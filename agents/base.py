"""
Base agent class. Extend this — don't write raw LLM loops in application code.
Handles the ReAct loop: think → tool call → observe → repeat until done.
"""
from abc import ABC, abstractmethod
from core import LLMClient
from .tools.registry import ToolRegistry


class BaseAgent(ABC):
    def __init__(self, client: LLMClient, tools: ToolRegistry) -> None:
        self.client = client
        self.tools = tools
        self.history: list[dict] = []

    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        ...

    def run(self, user_input: str) -> str:
        """
        Run the agent loop until a final answer is produced.
        Override step() to customise the reasoning loop.
        """
        raise NotImplementedError

    def step(self, messages: list[dict]) -> dict:
        """Single think → act step. Returns the model's next message."""
        raise NotImplementedError

    def reset(self) -> None:
        self.history = []
