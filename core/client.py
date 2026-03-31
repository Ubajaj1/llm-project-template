"""
LLM client wrapper. Swap providers here — not scattered across the codebase.
All LLM calls go through this class so tracing, retries, and cost tracking
are applied automatically.
"""
from typing import Any

import anthropic
import openai

from .config import settings
from .router import ModelRouter


class LLMClient:
    def __init__(self) -> None:
        self._anthropic = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._openai = openai.OpenAI(api_key=settings.openai_api_key)
        self.router = ModelRouter()

    def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        """Send a completion request. Routes to the appropriate provider."""
        model or self.router.select(messages)
        # TODO: add tracing, cost tracking, and retry logic here
        raise NotImplementedError

    async def complete_async(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Async variant for use inside agent loops."""
        raise NotImplementedError
