"""
Guardrail primitives: result type, ABCs, and policy enum.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class GuardrailPolicy(Enum):
    BLOCK = "block"        # raise GuardrailViolation on first failure
    WARN = "warn"          # log violation, continue
    LOG_ONLY = "log_only"  # silent pass-through — caller writes flags to audit


@dataclass
class GuardrailResult:
    passed: bool
    violations: list[str] = field(default_factory=list)


class GuardrailViolation(Exception):
    def __init__(self, violations: list[str]) -> None:
        self.violations = violations
        super().__init__(f"Guardrail blocked: {', '.join(violations)}")


class InputGuardrail(ABC):
    @abstractmethod
    def check(self, text: str) -> GuardrailResult: ...


class OutputGuardrail(ABC):
    @abstractmethod
    def check(self, text: str) -> GuardrailResult: ...
