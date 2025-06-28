"""
Performance monitoring module for Phase 5.

This module provides comprehensive performance monitoring capabilities including:
- Real-time performance metrics
- Resource usage tracking
- Performance alerts
- Performance dashboards
"""

import json
import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import psutil

try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    timestamp: datetime


@dataclass
class ApplicationMetrics:
    """Application-specific performance metrics."""
    request_count: int
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    error_rate: float
    active_sessions: int
    cache_hit_rate: float
    timestamp: datetime


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.

    Features:
    - Real-time system metrics collection
    - Application performance tracking
    - Performance alerts and notifications
    - Prometheus metrics export
    - Performance dashboard data
    """

    def __init__(
        self,
        collection_interval: float = 1.0,
        history_size: int = 3600,  # 1 hour of data at 1-second intervals
        enable_prometheus: bool = True
    ):
        self.collection_interval = collection_interval
        self.history_size = history_size
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE

        # Metrics storage
        self.system_metrics_history = deque(maxlen=history_size)
        self.application_metrics_history = deque(maxlen=history_size)
        self.custom_metrics_history = deque(maxlen=history_size)

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.collection_lock = threading.Lock()

        # Alert handlers
        self.alert_handlers: list[Callable] = []
        self.alert_thresholds: dict[str, dict[str, float]] = {}

        # Prometheus metrics
        self.prometheus_metrics = {}
        if self.enable_prometheus:
            self._setup_prometheus_metrics()

        # Performance tracking
        self.request_times = deque(maxlen=1000)
        self.error_count = 0
        self.request_count = 0
        self.session_count = 0

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        self.prometheus_metrics = {
            'request_total': Counter('mas_requests_total', 'Total requests', ['endpoint', 'method']),
            'request_duration': Histogram('mas_request_duration_seconds', 'Request duration', ['endpoint']),
            'error_total': Counter('mas_errors_total', 'Total errors', ['type']),
            'system_cpu': Gauge('mas_system_cpu_percent', 'CPU usage percentage'),
            'system_memory': Gauge('mas_system_memory_percent', 'Memory usage percentage'),
            'system_memory_bytes': Gauge('mas_system_memory_bytes', 'Memory usage in bytes'),
            'active_sessions': Gauge('mas_active_sessions', 'Number of active sessions'),
            'cache_hit_rate': Gauge('mas_cache_hit_rate', 'Cache hit rate percentage')
        }

    def start_monitoring(self):
        """Start performance monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        self.logger.info("Performance monitoring stopped")

    def _monitoring_worker(self):
        """Background worker for metrics collection."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                with self.collection_lock:
                    self.system_metrics_history.append(system_metrics)

                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                with self.collection_lock:
                    self.application_metrics_history.append(app_metrics)

                # Update Prometheus metrics
                if self.enable_prometheus:
                    self._update_prometheus_metrics(system_metrics, app_metrics)

                # Check alerts
                self._check_alerts(system_metrics, app_metrics)

                time.sleep(self.collection_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring worker: {e}")
                time.sleep(self.collection_interval)

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system-wide performance metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / 1024 / 1024 if disk_io else 0
            disk_write_mb = disk_io.write_bytes / 1024 / 1024 if disk_io else 0

            # Network I/O
            net_io = psutil.net_io_counters()
            net_sent_mb = net_io.bytes_sent / 1024 / 1024 if net_io else 0
            net_recv_mb = net_io.bytes_recv / 1024 / 1024 if net_io else 0

            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                network_io_sent_mb=net_sent_mb,
                network_io_recv_mb=net_recv_mb,
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0, memory_percent=0, memory_used_mb=0,
                disk_io_read_mb=0, disk_io_write_mb=0,
                network_io_sent_mb=0, network_io_recv_mb=0,
                timestamp=datetime.now()
            )

    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-specific performance metrics."""
        try:
            # Calculate response time statistics
            if self.request_times:
                response_times = list(self.request_times)
                avg_response_time = sum(response_times) / len(response_times)
                sorted_times = sorted(response_times)
                p95_index = int(len(sorted_times) * 0.95)
                p99_index = int(len(sorted_times) * 0.99)
                p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else 0
                p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else 0
            else:
                avg_response_time = p95_response_time = p99_response_time = 0

            # Calculate error rate
            error_rate = (self.error_count / max(self.request_count, 1)) * 100

            return ApplicationMetrics(
                request_count=self.request_count,
                response_time_avg=avg_response_time,
                response_time_p95=p95_response_time,
                response_time_p99=p99_response_time,
                error_rate=error_rate,
                active_sessions=self.session_count,
                cache_hit_rate=0.0,  # Will be updated by cache manager
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error collecting application metrics: {e}")
            return ApplicationMetrics(
                request_count=0, response_time_avg=0, response_time_p95=0,
                response_time_p99=0, error_rate=0, active_sessions=0,
                cache_hit_rate=0, timestamp=datetime.now()
            )

    def _update_prometheus_metrics(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Update Prometheus metrics."""
        try:
            self.prometheus_metrics['system_cpu'].set(system_metrics.cpu_percent)
            self.prometheus_metrics['system_memory'].set(system_metrics.memory_percent)
            self.prometheus_metrics['system_memory_bytes'].set(system_metrics.memory_used_mb * 1024 * 1024)
            self.prometheus_metrics['active_sessions'].set(app_metrics.active_sessions)
            self.prometheus_metrics['cache_hit_rate'].set(app_metrics.cache_hit_rate)
        except Exception as e:
            self.logger.error(f"Error updating Prometheus metrics: {e}")

    def track_request(self, endpoint: str, method: str, duration: float, success: bool = True):
        """Track a request for performance monitoring."""
        self.request_count += 1
        self.request_times.append(duration)

        if not success:
            self.error_count += 1

        if self.enable_prometheus:
            try:
                self.prometheus_metrics['request_total'].labels(endpoint=endpoint, method=method).inc()
                self.prometheus_metrics['request_duration'].labels(endpoint=endpoint).observe(duration)
                if not success:
                    self.prometheus_metrics['error_total'].labels(type='request').inc()
            except Exception as e:
                self.logger.error(f"Error tracking request in Prometheus: {e}")

    def update_session_count(self, count: int):
        """Update the active session count."""
        self.session_count = count

    def update_cache_hit_rate(self, hit_rate: float):
        """Update the cache hit rate."""
        if self.application_metrics_history:
            # Update the most recent application metrics
            with self.collection_lock:
                if self.application_metrics_history:
                    latest = self.application_metrics_history[-1]
                    latest.cache_hit_rate = hit_rate

    def add_alert_handler(self, handler: Callable[[str, dict[str, Any]], None]):
        """Add an alert handler function."""
        self.alert_handlers.append(handler)

    def set_alert_threshold(self, metric_name: str, threshold_type: str, value: float):
        """Set an alert threshold for a metric."""
        if metric_name not in self.alert_thresholds:
            self.alert_thresholds[metric_name] = {}
        self.alert_thresholds[metric_name][threshold_type] = value

    def _check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Check for alert conditions."""
        alerts = []

        # Check system metrics
        if 'cpu_percent' in self.alert_thresholds:
            threshold = self.alert_thresholds['cpu_percent'].get('high', 90)
            if system_metrics.cpu_percent > threshold:
                alerts.append({
                    'type': 'high_cpu',
                    'message': f'CPU usage is {system_metrics.cpu_percent:.1f}% (threshold: {threshold}%)',
                    'value': system_metrics.cpu_percent,
                    'threshold': threshold
                })

        if 'memory_percent' in self.alert_thresholds:
            threshold = self.alert_thresholds['memory_percent'].get('high', 90)
            if system_metrics.memory_percent > threshold:
                alerts.append({
                    'type': 'high_memory',
                    'message': f'Memory usage is {system_metrics.memory_percent:.1f}% (threshold: {threshold}%)',
                    'value': system_metrics.memory_percent,
                    'threshold': threshold
                })

        # Check application metrics
        if 'error_rate' in self.alert_thresholds:
            threshold = self.alert_thresholds['error_rate'].get('high', 5)
            if app_metrics.error_rate > threshold:
                alerts.append({
                    'type': 'high_error_rate',
                    'message': f'Error rate is {app_metrics.error_rate:.1f}% (threshold: {threshold}%)',
                    'value': app_metrics.error_rate,
                    'threshold': threshold
                })

        if 'response_time_avg' in self.alert_thresholds:
            threshold = self.alert_thresholds['response_time_avg'].get('high', 2.0)
            if app_metrics.response_time_avg > threshold:
                alerts.append({
                    'type': 'high_response_time',
                    'message': f'Average response time is {app_metrics.response_time_avg:.3f}s (threshold: {threshold}s)',
                    'value': app_metrics.response_time_avg,
                    'threshold': threshold
                })

        # Trigger alert handlers
        for alert in alerts:
            for handler in self.alert_handlers:
                try:
                    handler(alert['type'], alert)
                except Exception as e:
                    self.logger.error(f"Error in alert handler: {e}")

    def get_current_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""
        with self.collection_lock:
            system_metrics = self.system_metrics_history[-1] if self.system_metrics_history else None
            app_metrics = self.application_metrics_history[-1] if self.application_metrics_history else None

        return {
            'system': {
                'cpu_percent': system_metrics.cpu_percent if system_metrics else 0,
                'memory_percent': system_metrics.memory_percent if system_metrics else 0,
                'memory_used_mb': system_metrics.memory_used_mb if system_metrics else 0,
                'disk_io_read_mb': system_metrics.disk_io_read_mb if system_metrics else 0,
                'disk_io_write_mb': system_metrics.disk_io_write_mb if system_metrics else 0,
                'network_io_sent_mb': system_metrics.network_io_sent_mb if system_metrics else 0,
                'network_io_recv_mb': system_metrics.network_io_recv_mb if system_metrics else 0,
                'timestamp': system_metrics.timestamp.isoformat() if system_metrics else None
            },
            'application': {
                'request_count': app_metrics.request_count if app_metrics else 0,
                'response_time_avg': app_metrics.response_time_avg if app_metrics else 0,
                'response_time_p95': app_metrics.response_time_p95 if app_metrics else 0,
                'response_time_p99': app_metrics.response_time_p99 if app_metrics else 0,
                'error_rate': app_metrics.error_rate if app_metrics else 0,
                'active_sessions': app_metrics.active_sessions if app_metrics else 0,
                'cache_hit_rate': app_metrics.cache_hit_rate if app_metrics else 0,
                'timestamp': app_metrics.timestamp.isoformat() if app_metrics else None
            }
        }

    def get_metrics_history(self, duration_minutes: int = 60) -> dict[str, list[dict[str, Any]]]:
        """Get metrics history for the specified duration."""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)

        with self.collection_lock:
            system_history = [
                {
                    'cpu_percent': m.cpu_percent,
                    'memory_percent': m.memory_percent,
                    'memory_used_mb': m.memory_used_mb,
                    'timestamp': m.timestamp.isoformat()
                }
                for m in self.system_metrics_history
                if m.timestamp >= cutoff_time
            ]

            app_history = [
                {
                    'request_count': m.request_count,
                    'response_time_avg': m.response_time_avg,
                    'error_rate': m.error_rate,
                    'active_sessions': m.active_sessions,
                    'cache_hit_rate': m.cache_hit_rate,
                    'timestamp': m.timestamp.isoformat()
                }
                for m in self.application_metrics_history
                if m.timestamp >= cutoff_time
            ]

        return {
            'system': system_history,
            'application': app_history
        }

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if not self.enable_prometheus:
            return "# Prometheus metrics not available\n"

        try:
            return generate_latest()
        except Exception as e:
            self.logger.error(f"Error generating Prometheus metrics: {e}")
            return "# Error generating metrics\n"

    def reset_metrics(self):
        """Reset all metrics counters."""
        self.request_count = 0
        self.error_count = 0
        self.session_count = 0
        self.request_times.clear()

        with self.collection_lock:
            self.system_metrics_history.clear()
            self.application_metrics_history.clear()
            self.custom_metrics_history.clear()

        self.logger.info("Performance metrics reset")

    def export_metrics(self, filename: str = None) -> str:
        """Export metrics to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"

        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'current_metrics': self.get_current_metrics(),
            'metrics_history': self.get_metrics_history(),
            'alert_thresholds': self.alert_thresholds
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Performance metrics exported to {filename}")
        return filename
