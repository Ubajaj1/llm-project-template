"""
Pluggable cache backends.
Implement CacheBackend to use any storage: Redis, Memcached, etc.
"""
import time
from abc import ABC, abstractmethod
from collections import OrderedDict


class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None: ...

    @abstractmethod
    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...


class InMemoryBackend(CacheBackend):
    """LRU dict with per-entry TTL. Zero extra dependencies."""

    def __init__(self, max_size: int = 1000) -> None:
        self.max_size = max_size
        # key -> (value, expires_at)
        self._store: OrderedDict[str, tuple[str, float]] = OrderedDict()

    def get(self, key: str) -> str | None:
        if key not in self._store:
            return None
        value, expires_at = self._store[key]
        if time.time() > expires_at:
            del self._store[key]
            return None
        self._store.move_to_end(key)  # mark as recently used
        return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        elif len(self._store) >= self.max_size:
            self._store.popitem(last=False)  # evict LRU
        self._store[key] = (value, time.time() + ttl_seconds)
