"""
GuardrailChain — compose multiple guardrails under a single policy.
"""
import logging

from .base import (
    GuardrailPolicy,
    GuardrailResult,
    GuardrailViolation,
    InputGuardrail,
    OutputGuardrail,
)

logger = logging.getLogger(__name__)


class GuardrailChain:
    """
    Run a list of guardrails and apply a single policy to all violations.

    BLOCK    → raises GuardrailViolation on first failure (default for input)
    WARN     → logs each violation, returns combined result (default for output)
    LOG_ONLY → silent pass-through; caller writes flags to AuditEvent.guardrail_flags
    """

    def __init__(
        self,
        guardrails: list[InputGuardrail | OutputGuardrail],
        policy: GuardrailPolicy = GuardrailPolicy.BLOCK,
    ) -> None:
        self.guardrails = guardrails
        self.policy = policy

    def run(self, text: str) -> GuardrailResult:
        """
        Run all guardrails. Returns GuardrailResult with combined violations.
        The caller (agent harness) writes result.violations to AuditEvent.guardrail_flags.
        """
        all_violations: list[str] = []
        for g in self.guardrails:
            result = g.check(text)
            if not result.passed:
                all_violations.extend(result.violations)
                if self.policy == GuardrailPolicy.BLOCK:
                    raise GuardrailViolation(all_violations)
                elif self.policy == GuardrailPolicy.WARN:
                    logger.warning("Guardrail violation: %s", result.violations)
        return GuardrailResult(passed=len(all_violations) == 0, violations=all_violations)
