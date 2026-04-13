"""
Rule-based input guardrails. No LLM calls — fast, deterministic.
"""
import re

from ._patterns import INJECTION_PATTERNS, PII_PATTERNS
from .base import GuardrailResult, InputGuardrail


class PromptInjectionGuardrail(InputGuardrail):
    """Detect common prompt injection attempts via regex."""

    def __init__(self) -> None:
        self._patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    def check(self, text: str) -> GuardrailResult:
        if any(p.search(text) for p in self._patterns):
            return GuardrailResult(passed=False, violations=["injection_attempt"])
        return GuardrailResult(passed=True)


class PIIInputGuardrail(InputGuardrail):
    """Detect PII in user input before it reaches the LLM."""

    def __init__(self) -> None:
        self._patterns = {k: re.compile(v) for k, v in PII_PATTERNS.items()}

    def check(self, text: str) -> GuardrailResult:
        found = [k for k, p in self._patterns.items() if p.search(text)]
        if found:
            return GuardrailResult(passed=False, violations=[f"pii_{t}" for t in found])
        return GuardrailResult(passed=True)


class LengthGuardrail(InputGuardrail):
    """Block inputs that exceed a token budget (approximate: 1 token ≈ 4 chars)."""

    def __init__(self, max_tokens: int = 8000) -> None:
        self._max_chars = max_tokens * 4

    def check(self, text: str) -> GuardrailResult:
        if len(text) > self._max_chars:
            return GuardrailResult(passed=False, violations=["input_too_long"])
        return GuardrailResult(passed=True)
