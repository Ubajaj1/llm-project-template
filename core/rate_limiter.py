"""
In-process sliding window rate limiter per user key.
For multi-worker deployments, replace with a Redis-backed implementation
that satisfies the same RateLimiter interface.
"""
import time
from collections import deque


class RateLimitExceeded(Exception):
    def __init__(self, key: str, limit_type: str) -> None:
        self.key = key
        self.limit_type = limit_type
        super().__init__(f"Rate limit exceeded for {key!r}: {limit_type}")


class RateLimiter:
    """
    Sliding window counter tracking requests-per-minute and tokens-per-minute.
    Call check() before each LLM request; it raises RateLimitExceeded if over limit.
    """

    def __init__(self, rpm: int = 60, tpm: int = 100_000) -> None:
        self.rpm = rpm
        self.tpm = tpm
        self._req_windows: dict[str, deque[float]] = {}
        self._tok_windows: dict[str, deque[tuple[float, int]]] = {}

    def check(self, user_id: str, tokens: int = 0) -> None:
        """
        Raise RateLimitExceeded if user_id has exceeded RPM or TPM.
        tokens: estimated input token count (pass 0 to skip TPM check).
        """
        now = time.time()
        cutoff = now - 60.0

        reqs = self._req_windows.setdefault(user_id, deque())
        while reqs and reqs[0] < cutoff:
            reqs.popleft()
        if len(reqs) >= self.rpm:
            raise RateLimitExceeded(user_id, "rpm")
        reqs.append(now)

        if tokens > 0:
            toks = self._tok_windows.setdefault(user_id, deque())
            while toks and toks[0][0] < cutoff:
                toks.popleft()
            if sum(t for _, t in toks) + tokens > self.tpm:
                raise RateLimitExceeded(user_id, "tpm")
            toks.append((now, tokens))

    @classmethod
    def from_settings(cls) -> "RateLimiter":
        from .config import settings
        return cls(rpm=settings.rate_limit_rpm, tpm=settings.rate_limit_tpm)
