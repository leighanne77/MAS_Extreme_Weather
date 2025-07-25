import asyncio
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any


class MetricsCollector:
    """Collects performance metrics and resource usage."""

    def __init__(self):
        self.metrics = {}
        self.resource_usage = {}
        self.logger = logging.getLogger("metrics")

    @contextmanager
    def track(self, operation: str):
        """Track operation performance."""
        start_time = datetime.now()
        try:
            yield
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics[operation] = {
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }

    @contextmanager
    def track_error(self):
        """Track error metrics."""
        try:
            yield
        except Exception as e:
            self.metrics["errors"] = self.metrics.get("errors", 0) + 1
            self.logger.error(f"Error occurred: {str(e)}")
            raise

    def get_metrics(self) -> dict[str, Any]:
        """Get collected metrics."""
        return self.metrics

    def get_resource_usage(self) -> dict[str, Any]:
        """Get resource usage metrics."""
        return self.resource_usage

class CircuitBreaker:
    """Implements circuit breaker pattern."""

    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.is_open = False

    def is_allowed(self) -> bool:
        """Check if operation is allowed."""
        if not self.is_open:
            return True

        if self.last_failure_time:
            time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
            if time_since_failure >= self.reset_timeout:
                self.reset()
                return True

        return False

    def record_failure(self):
        """Record a failure."""
        self.failures += 1
        self.last_failure_time = datetime.now()
        if self.failures >= self.failure_threshold:
            self.is_open = True

    def reset(self):
        """Reset circuit breaker."""
        self.failures = 0
        self.last_failure_time = None
        self.is_open = False

    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "is_open": self.is_open,
            "failures": self.failures,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }

class WorkerPool:
    """Manages a pool of workers for parallel processing."""

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)

    async def execute(self, func: callable, *args, **kwargs) -> Any:
        """Execute function with worker pool."""
        async with self.semaphore:
            return await func(*args, **kwargs)

    def get_resource_usage(self) -> dict[str, Any]:
        """Get resource usage metrics."""
        return {
            "max_workers": self.max_workers,
            "available_workers": self.semaphore._value,
            "active_workers": self.max_workers - self.semaphore._value
        }

    def get_status(self) -> dict[str, Any]:
        """Get worker pool status."""
        return {
            "max_workers": self.max_workers,
            "available_workers": self.semaphore._value,
            "active_workers": self.max_workers - self.semaphore._value
        }

class Monitoring:
    """Monitors system state and performance."""

    def __init__(self):
        self.metrics = MetricsCollector()
        self.logger = logging.getLogger("monitoring")

    @contextmanager
    def track_request(self):
        """Track request processing."""
        with self.metrics.track("request"):
            try:
                yield
            except Exception:
                with self.metrics.track_error():
                    raise

    @contextmanager
    def track_workflow(self):
        """Track workflow execution."""
        with self.metrics.track("workflow"):
            try:
                yield
            except Exception:
                with self.metrics.track_error():
                    raise

    def track_operation(self, operation: str, metadata: dict[str, Any] = None):
        """Track operation with metadata."""
        self.metrics.metrics[operation] = {
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get monitoring metrics."""
        return self.metrics.get_metrics()

    def get_resource_usage(self) -> dict[str, Any]:
        """Get resource usage metrics."""
        return self.metrics.get_resource_usage()

class Buffer:
    """Implements pipeline stage buffering."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.buffer = asyncio.Queue(maxsize=max_size)

    async def execute(self, func: callable, *args, **kwargs) -> Any:
        """Execute function with buffering."""
        await self.buffer.put((func, args, kwargs))
        return await self._process_buffer()

    async def _process_buffer(self) -> Any:
        """Process buffered items."""
        func, args, kwargs = await self.buffer.get()
        try:
            return await func(*args, **kwargs)
        finally:
            self.buffer.task_done()

    def get_status(self) -> dict[str, Any]:
        """Get buffer status."""
        return {
            "max_size": self.max_size,
            "current_size": self.buffer.qsize(),
            "is_full": self.buffer.full(),
            "is_empty": self.buffer.empty()
        }
