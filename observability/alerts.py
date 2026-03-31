"""
Alert thresholds: latency, error rate, cost spikes.
Add your alerting integration here (PagerDuty, Slack webhook, etc.)
"""


class AlertManager:
    def __init__(self, latency_p99_ms: float = 5000, error_rate_threshold: float = 0.05) -> None:
        self.latency_p99_ms = latency_p99_ms
        self.error_rate_threshold = error_rate_threshold

    def check_latency(self, latency_ms: float) -> None:
        if latency_ms > self.latency_p99_ms:
            self._fire(f"High latency: {latency_ms:.0f}ms exceeds {self.latency_p99_ms}ms")

    def check_error_rate(self, rate: float) -> None:
        if rate > self.error_rate_threshold:
            self._fire(f"Error rate {rate:.1%} exceeds threshold {self.error_rate_threshold:.1%}")

    def _fire(self, message: str) -> None:
        # TODO: integrate with your alerting system
        raise RuntimeError(f"ALERT: {message}")
