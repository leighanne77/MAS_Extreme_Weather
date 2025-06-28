"""
Performance optimization and testing module for Phase 5.

This module provides comprehensive performance testing, benchmarking,
and optimization capabilities for the Multi-Agent Climate Risk Analysis System.
"""

from .benchmarking import PerformanceBenchmark
from .caching import CacheManager
from .load_testing import LoadTester
from .monitoring import PerformanceMonitor
from .optimization import PerformanceOptimizer

__all__ = [
    'LoadTester',
    'PerformanceBenchmark',
    'PerformanceMonitor',
    'CacheManager',
    'PerformanceOptimizer'
]
