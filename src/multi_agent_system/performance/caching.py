"""
Caching module for Phase 5 performance optimization.

This module provides multi-level caching strategies including:
- L1 (memory) caching
- L2 (Redis) caching
- Cache invalidation strategies
- Cache warming
- Cache monitoring
"""

import hashlib
import json
import logging
import pickle
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Any

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from cachetools import TTLCache


@dataclass
class CacheStats:
    """Cache statistics and metrics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    size: int = 0
    max_size: int = 0
    hit_rate: float = 0.0
    last_updated: datetime = None

    def update_hit_rate(self):
        """Update hit rate based on current hits and misses."""
        total = self.hits + self.misses
        self.hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        self.last_updated = datetime.now()


class CacheManager:
    """
    Multi-level cache manager with L1 (memory) and L2 (Redis) caching.

    Features:
    - TTL-based memory caching
    - Redis-based persistent caching
    - Automatic cache invalidation
    - Cache warming capabilities
    - Performance monitoring
    """

    def __init__(
        self,
        l1_max_size: int = 1000,
        l1_ttl: int = 300,  # 5 minutes
        l2_enabled: bool = True,
        l2_ttl: int = 3600,  # 1 hour
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0
    ):
        self.l1_max_size = l1_max_size
        self.l1_ttl = l1_ttl
        self.l2_enabled = l2_enabled
        self.l2_ttl = l2_ttl

        # Initialize L1 cache (memory)
        self.l1_cache = TTLCache(maxsize=l1_max_size, ttl=l1_ttl)

        # Initialize L2 cache (Redis)
        self.l2_cache = None
        if l2_enabled and REDIS_AVAILABLE:
            try:
                self.l2_cache = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=False  # Keep as bytes for pickle
                )
                # Test connection
                self.l2_cache.ping()
                print("L2 cache (Redis) initialized successfully")
            except Exception as e:
                print(f"Failed to initialize L2 cache (Redis): {e}")
                self.l2_cache = None

        # Statistics
        self.stats = CacheStats(max_size=l1_max_size)
        self.stats_lock = threading.Lock()

        # Cache warming queue
        self.warming_queue = []
        self.warming_thread = None
        self.warming_active = False

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def _generate_key(self, key: str | Any) -> str:
        """Generate a cache key from various input types."""
        if isinstance(key, str):
            return f"mas_cache:{key}"

        # For complex objects, create a hash
        key_str = json.dumps(key, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"mas_cache:{key_hash}"

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize a value for storage in L2 cache."""
        try:
            return pickle.dumps(value)
        except Exception as e:
            self.logger.warning(f"Failed to serialize value: {e}")
            return pickle.dumps(str(value))

    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize a value from L2 cache."""
        try:
            return pickle.loads(value)
        except Exception as e:
            self.logger.warning(f"Failed to deserialize value: {e}")
            return None

    def get(self, key: str | Any) -> Any | None:
        """
        Get a value from cache (L1 first, then L2).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        cache_key = self._generate_key(key)

        # Try L1 cache first
        if cache_key in self.l1_cache:
            with self.stats_lock:
                self.stats.hits += 1
                self.stats.update_hit_rate()
            return self.l1_cache[cache_key]

        # Try L2 cache if available
        if self.l2_cache:
            try:
                value = self.l2_cache.get(cache_key)
                if value is not None:
                    deserialized_value = self._deserialize_value(value)
                    if deserialized_value is not None:
                        # Store in L1 cache for future access
                        self.l1_cache[cache_key] = deserialized_value
                        with self.stats_lock:
                            self.stats.hits += 1
                            self.stats.update_hit_rate()
                        return deserialized_value
            except Exception as e:
                self.logger.warning(f"L2 cache get failed: {e}")

        # Cache miss
        with self.stats_lock:
            self.stats.misses += 1
            self.stats.update_hit_rate()
        return None

    def set(self, key: str | Any, value: Any, ttl: int | None = None) -> bool:
        """
        Set a value in both L1 and L2 caches.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (overrides default)

        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_key(key)
        success = True

        # Set in L1 cache
        try:
            self.l1_cache[cache_key] = value
        except Exception as e:
            self.logger.warning(f"L1 cache set failed: {e}")
            success = False

        # Set in L2 cache if available
        if self.l2_cache:
            try:
                serialized_value = self._serialize_value(value)
                cache_ttl = ttl if ttl is not None else self.l2_ttl
                self.l2_cache.setex(cache_key, cache_ttl, serialized_value)
            except Exception as e:
                self.logger.warning(f"L2 cache set failed: {e}")
                success = False

        with self.stats_lock:
            self.stats.sets += 1
            self.stats.size = len(self.l1_cache)

        return success

    def delete(self, key: str | Any) -> bool:
        """
        Delete a value from both L1 and L2 caches.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_key(key)
        success = True

        # Delete from L1 cache
        try:
            if cache_key in self.l1_cache:
                del self.l1_cache[cache_key]
        except Exception as e:
            self.logger.warning(f"L1 cache delete failed: {e}")
            success = False

        # Delete from L2 cache if available
        if self.l2_cache:
            try:
                self.l2_cache.delete(cache_key)
            except Exception as e:
                self.logger.warning(f"L2 cache delete failed: {e}")
                success = False

        with self.stats_lock:
            self.stats.deletes += 1
            self.stats.size = len(self.l1_cache)

        return success

    def clear(self) -> bool:
        """
        Clear all caches.

        Returns:
            True if successful, False otherwise
        """
        success = True

        # Clear L1 cache
        try:
            self.l1_cache.clear()
        except Exception as e:
            self.logger.warning(f"L1 cache clear failed: {e}")
            success = False

        # Clear L2 cache if available
        if self.l2_cache:
            try:
                # Clear only our cache keys
                pattern = "mas_cache:*"
                keys = self.l2_cache.keys(pattern)
                if keys:
                    self.l2_cache.delete(*keys)
            except Exception as e:
                self.logger.warning(f"L2 cache clear failed: {e}")
                success = False

        with self.stats_lock:
            self.stats.size = 0

        return success

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: Pattern to match (supports wildcards)

        Returns:
            Number of entries invalidated
        """
        invalidated_count = 0

        # Invalidate L1 cache entries
        keys_to_delete = []
        for key in self.l1_cache.keys():
            if pattern in key:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            try:
                del self.l1_cache[key]
                invalidated_count += 1
            except Exception as e:
                self.logger.warning(f"L1 cache pattern invalidation failed: {e}")

        # Invalidate L2 cache entries if available
        if self.l2_cache:
            try:
                pattern_keys = self.l2_cache.keys(f"mas_cache:*{pattern}*")
                if pattern_keys:
                    self.l2_cache.delete(*pattern_keys)
                    invalidated_count += len(pattern_keys)
            except Exception as e:
                self.logger.warning(f"L2 cache pattern invalidation failed: {e}")

        with self.stats_lock:
            self.stats.size = len(self.l1_cache)

        return invalidated_count

    def warm_cache(self, warming_function: Callable, *args, **kwargs):
        """
        Add a cache warming task to the queue.

        Args:
            warming_function: Function to call for cache warming
            *args: Arguments for the warming function
            **kwargs: Keyword arguments for the warming function
        """
        self.warming_queue.append((warming_function, args, kwargs))

        # Start warming thread if not already running
        if not self.warming_active:
            self.start_cache_warming()

    def start_cache_warming(self):
        """Start the cache warming thread."""
        if self.warming_thread and self.warming_thread.is_alive():
            return

        self.warming_active = True
        self.warming_thread = threading.Thread(target=self._warming_worker, daemon=True)
        self.warming_thread.start()

    def stop_cache_warming(self):
        """Stop the cache warming thread."""
        self.warming_active = False
        if self.warming_thread:
            self.warming_thread.join()

    def _warming_worker(self):
        """Background worker for cache warming."""
        while self.warming_active:
            if self.warming_queue:
                try:
                    warming_function, args, kwargs = self.warming_queue.pop(0)
                    warming_function(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Cache warming failed: {e}")
            else:
                time.sleep(1)  # Wait for new warming tasks

    def get_stats(self) -> CacheStats:
        """Get current cache statistics."""
        with self.stats_lock:
            stats_copy = CacheStats(
                hits=self.stats.hits,
                misses=self.stats.misses,
                sets=self.stats.sets,
                deletes=self.stats.deletes,
                size=self.stats.size,
                max_size=self.stats.max_size,
                hit_rate=self.stats.hit_rate,
                last_updated=self.stats.last_updated
            )
        return stats_copy

    def reset_stats(self):
        """Reset cache statistics."""
        with self.stats_lock:
            self.stats = CacheStats(max_size=self.l1_max_size)

    def get_cache_info(self) -> dict[str, Any]:
        """Get comprehensive cache information."""
        stats = self.get_stats()

        info = {
            "l1_cache": {
                "enabled": True,
                "max_size": self.l1_max_size,
                "current_size": stats.size,
                "ttl": self.l1_ttl
            },
            "l2_cache": {
                "enabled": self.l2_cache is not None,
                "ttl": self.l2_ttl
            },
            "statistics": {
                "hits": stats.hits,
                "misses": stats.misses,
                "sets": stats.sets,
                "deletes": stats.deletes,
                "hit_rate": f"{stats.hit_rate:.2f}%",
                "last_updated": stats.last_updated.isoformat() if stats.last_updated else None
            },
            "warming": {
                "active": self.warming_active,
                "queue_size": len(self.warming_queue)
            }
        }

        # Add L2 cache info if available
        if self.l2_cache:
            try:
                info["l2_cache"]["info"] = self.l2_cache.info()
            except Exception as e:
                info["l2_cache"]["error"] = str(e)

        return info


def cached(ttl: int | None = None, key_prefix: str = ""):
    """
    Decorator for caching function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys

    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)

            # Get cache manager (assuming it's available globally)
            cache_manager = getattr(func, '_cache_manager', None)
            if cache_manager is None:
                # Create a default cache manager
                cache_manager = CacheManager()
                func._cache_manager = cache_manager

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator
