"""
Shared cache utilities for Pythia data providers.
"""
import time
from typing import Any, Dict, Optional

class SimpleCache:
    def __init__(self, ttl: int = 300):
        self._cache: Dict[str, tuple] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry:
            ts, val = entry
            if time.time() - ts < self._ttl:
                return val
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (time.time(), value)
