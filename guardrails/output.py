"""
Rule-based output guardrails. Applied to LLM responses before returning to caller.
"""
import json
import re

from ._patterns import PII_PATTERNS, REFUSAL_PATTERNS
from .base import GuardrailResult, OutputGuardrail


class RefusalDetector(OutputGuardrail):
    """Surface silent model refusals — useful for monitoring, defaults to WARN not BLOCK."""

    def __init__(self) -> None:
        self._patterns = [re.compile(p, re.IGNORECASE) for p in REFUSAL_PATTERNS]

    def check(self, text: str) -> GuardrailResult:
        if any(p.search(text) for p in self._patterns):
            return GuardrailResult(passed=False, violations=["model_refusal"])
        return GuardrailResult(passed=True)


class PIIOutputGuardrail(OutputGuardrail):
    """Catch PII the model may have echoed back or hallucinated."""

    def __init__(self) -> None:
        self._patterns = {k: re.compile(v) for k, v in PII_PATTERNS.items()}

    def check(self, text: str) -> GuardrailResult:
        found = [k for k, p in self._patterns.items() if p.search(text)]
        if found:
            return GuardrailResult(passed=False, violations=[f"pii_{t}" for t in found])
        return GuardrailResult(passed=True)


class SchemaGuardrail(OutputGuardrail):
    """
    Validate that the response is valid JSON, optionally checking required keys.
    For full JSON Schema validation, swap the required-key check for jsonschema.validate().
    """

    def __init__(self, required_keys: list[str] | None = None) -> None:
        self.required_keys = required_keys or []

    def check(self, text: str) -> GuardrailResult:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return GuardrailResult(passed=False, violations=["invalid_json"])
        missing = [k for k in self.required_keys if k not in data]
        if missing:
            return GuardrailResult(passed=False, violations=[f"missing_field:{k}" for k in missing])
        return GuardrailResult(passed=True)
