"""
Performance benchmarking module for Phase 5 optimization.

This module provides comprehensive benchmarking capabilities to establish
performance baselines and measure optimization improvements.
"""

import time
import statistics
import asyncio
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path

from ..session_manager import SessionManager
from ..agent_team import AgentTeam
from ..communication import CommunicationManager


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark."""
    benchmark_name: str
    operation: str
    duration: float
    memory_usage_mb: float
    cpu_usage_percent: float
    iterations: int
    avg_duration: float
    min_duration: float
    max_duration: float
    std_deviation: float
    throughput: float  # operations per second
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking framework.
    
    Provides benchmarking capabilities for:
    - Agent operations
    - Communication patterns
    - Data processing
    - System operations
    """
    
    def __init__(self, results_dir: str = "benchmark_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results: List[BenchmarkResult] = []
        self.baselines: Dict[str, BenchmarkResult] = {}
        
    async def benchmark_agent_operations(
        self,
        agent_type: str,
        operation: str,
        iterations: int = 100,
        warmup_iterations: int = 10
    ) -> BenchmarkResult:
        """
        Benchmark agent operations.
        
        Args:
            agent_type: Type of agent to benchmark
            operation: Operation to benchmark
            iterations: Number of iterations to run
            warmup_iterations: Number of warmup iterations
            
        Returns:
            BenchmarkResult with performance metrics
        """
        print(f"Benchmarking {agent_type} agent - {operation} operation")
        
        # Warmup
        session_manager = SessionManager()
        session = await session_manager.create_session("benchmark_user")
        agent_team = AgentTeam(session_manager)
        
        for _ in range(warmup_iterations):
            try:
                if operation == "risk_analysis":
                    await agent_team.analyze_risk("New York", "weather", "7d")
                elif operation == "historical_analysis":
                    await agent_team.analyze_historical_data("New York", "2024-01-01", "2024-12-31")
                elif operation == "recommendation":
                    await agent_team.get_recommendations("New York", "weather")
                else:
                    await agent_team.process_request(f"Benchmark {operation}")
            except Exception:
                pass  # Ignore warmup errors
        
        # Actual benchmarking
        durations = []
        memory_usage = []
        cpu_usage = []
        
        start_time = time.time()
        
        for i in range(iterations):
            iteration_start = time.time()
            
            try:
                if operation == "risk_analysis":
                    result = await agent_team.analyze_risk("New York", "weather", "7d")
                elif operation == "historical_analysis":
                    result = await agent_team.analyze_historical_data("New York", "2024-01-01", "2024-12-31")
                elif operation == "recommendation":
                    result = await agent_team.get_recommendations("New York", "weather")
                else:
                    result = await agent_team.process_request(f"Benchmark {operation} iteration {i}")
                
                duration = time.time() - iteration_start
                durations.append(duration)
                
                # Record system metrics (simplified)
                memory_usage.append(100.0)  # Placeholder
                cpu_usage.append(50.0)      # Placeholder
                
            except Exception as e:
                print(f"Benchmark iteration {i} failed: {e}")
                continue
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            std_deviation = statistics.stdev(durations) if len(durations) > 1 else 0
            throughput = len(durations) / total_time
        else:
            avg_duration = min_duration = max_duration = std_deviation = throughput = 0
        
        avg_memory = statistics.mean(memory_usage) if memory_usage else 0
        avg_cpu = statistics.mean(cpu_usage) if cpu_usage else 0
        
        result = BenchmarkResult(
            benchmark_name=f"{agent_type}_{operation}",
            operation=operation,
            duration=total_time,
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            iterations=len(durations),
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            std_deviation=std_deviation,
            throughput=throughput,
            timestamp=datetime.now(),
            metadata={
                "agent_type": agent_type,
                "warmup_iterations": warmup_iterations,
                "successful_iterations": len(durations)
            }
        )
        
        self.results.append(result)
        return result
    
    async def benchmark_communication_patterns(
        self,
        pattern: str,
        message_size: int = 1024,
        iterations: int = 100
    ) -> BenchmarkResult:
        """
        Benchmark communication patterns.
        
        Args:
            pattern: Communication pattern to benchmark
            message_size: Size of messages in bytes
            iterations: Number of iterations
            
        Returns:
            BenchmarkResult with performance metrics
        """
        print(f"Benchmarking communication pattern: {pattern}")
        
        session_manager = SessionManager()
        session = await session_manager.create_session("benchmark_user")
        comm_manager = CommunicationManager(session_manager)
        
        # Generate test message
        test_message = "x" * message_size
        
        durations = []
        start_time = time.time()
        
        for i in range(iterations):
            iteration_start = time.time()
            
            try:
                if pattern == "a2a":
                    # Test A2A communication
                    await comm_manager.send_a2a_message(
                        sender_id="benchmark_sender",
                        recipient_id="benchmark_recipient",
                        content=test_message,
                        message_type="benchmark"
                    )
                elif pattern == "traditional":
                    # Test traditional communication
                    await comm_manager.send_message(
                        sender="benchmark_sender",
                        recipient="benchmark_recipient",
                        message=test_message
                    )
                elif pattern == "broadcast":
                    # Test broadcast communication
                    await comm_manager.broadcast_message(
                        sender="benchmark_sender",
                        message=test_message,
                        recipients=["agent1", "agent2", "agent3"]
                    )
                
                duration = time.time() - iteration_start
                durations.append(duration)
                
            except Exception as e:
                print(f"Communication benchmark iteration {i} failed: {e}")
                continue
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            std_deviation = statistics.stdev(durations) if len(durations) > 1 else 0
            throughput = len(durations) / total_time
        else:
            avg_duration = min_duration = max_duration = std_deviation = throughput = 0
        
        result = BenchmarkResult(
            benchmark_name=f"communication_{pattern}",
            operation=pattern,
            duration=total_time,
            memory_usage_mb=0,  # Placeholder
            cpu_usage_percent=0,  # Placeholder
            iterations=len(durations),
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            std_deviation=std_deviation,
            throughput=throughput,
            timestamp=datetime.now(),
            metadata={
                "message_size": message_size,
                "pattern": pattern,
                "successful_iterations": len(durations)
            }
        )
        
        self.results.append(result)
        return result
    
    async def benchmark_data_processing(
        self,
        data_size_mb: int,
        operation: str,
        iterations: int = 10
    ) -> BenchmarkResult:
        """
        Benchmark data processing operations.
        
        Args:
            data_size_mb: Size of data to process in MB
            operation: Data processing operation
            iterations: Number of iterations
            
        Returns:
            BenchmarkResult with performance metrics
        """
        print(f"Benchmarking data processing: {operation} with {data_size_mb}MB data")
        
        session_manager = SessionManager()
        session = await session_manager.create_session("benchmark_user")
        agent_team = AgentTeam(session_manager)
        
        # Generate test data
        test_data = "x" * (data_size_mb * 1024 * 1024)  # Convert MB to bytes
        
        durations = []
        start_time = time.time()
        
        for i in range(iterations):
            iteration_start = time.time()
            
            try:
                if operation == "ingestion":
                    # Simulate data ingestion
                    await agent_team.ingest_data(test_data, "benchmark_source")
                elif operation == "transformation":
                    # Simulate data transformation
                    await agent_team.transform_data(test_data, "benchmark_transformation")
                elif operation == "validation":
                    # Simulate data validation
                    await agent_team.validate_data(test_data)
                elif operation == "analysis":
                    # Simulate data analysis
                    await agent_team.analyze_data(test_data, "benchmark_analysis")
                
                duration = time.time() - iteration_start
                durations.append(duration)
                
            except Exception as e:
                print(f"Data processing benchmark iteration {i} failed: {e}")
                continue
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            std_deviation = statistics.stdev(durations) if len(durations) > 1 else 0
            throughput = len(durations) / total_time
        else:
            avg_duration = min_duration = max_duration = std_deviation = throughput = 0
        
        result = BenchmarkResult(
            benchmark_name=f"data_processing_{operation}_{data_size_mb}mb",
            operation=operation,
            duration=total_time,
            memory_usage_mb=data_size_mb,
            cpu_usage_percent=0,  # Placeholder
            iterations=len(durations),
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            std_deviation=std_deviation,
            throughput=throughput,
            timestamp=datetime.now(),
            metadata={
                "data_size_mb": data_size_mb,
                "operation": operation,
                "successful_iterations": len(durations)
            }
        )
        
        self.results.append(result)
        return result
    
    def establish_baselines(self):
        """Establish performance baselines from current results."""
        for result in self.results:
            baseline_key = f"{result.benchmark_name}_{result.operation}"
            self.baselines[baseline_key] = result
        
        print(f"Established {len(self.baselines)} performance baselines")
    
    def compare_with_baseline(self, result: BenchmarkResult) -> Dict[str, Any]:
        """Compare a result with its baseline."""
        baseline_key = f"{result.benchmark_name}_{result.operation}"
        baseline = self.baselines.get(baseline_key)
        
        if not baseline:
            return {"status": "no_baseline", "message": "No baseline available for comparison"}
        
        comparison = {
            "status": "compared",
            "baseline": baseline_key,
            "improvements": {}
        }
        
        # Compare key metrics
        if result.avg_duration < baseline.avg_duration:
            improvement = ((baseline.avg_duration - result.avg_duration) / baseline.avg_duration) * 100
            comparison["improvements"]["response_time"] = f"{improvement:.2f}% faster"
        else:
            degradation = ((result.avg_duration - baseline.avg_duration) / baseline.avg_duration) * 100
            comparison["improvements"]["response_time"] = f"{degradation:.2f}% slower"
        
        if result.throughput > baseline.throughput:
            improvement = ((result.throughput - baseline.throughput) / baseline.throughput) * 100
            comparison["improvements"]["throughput"] = f"{improvement:.2f}% higher"
        else:
            degradation = ((baseline.throughput - result.throughput) / baseline.throughput) * 100
            comparison["improvements"]["throughput"] = f"{degradation:.2f}% lower"
        
        return comparison
    
    def generate_report(self) -> str:
        """Generate a comprehensive benchmarking report."""
        if not self.results:
            return "No benchmark results available."
        
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE BENCHMARKING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now()}")
        report.append(f"Total benchmarks: {len(self.results)}")
        report.append(f"Baselines established: {len(self.baselines)}")
        report.append("")
        
        # Group results by operation type
        operation_groups = {}
        for result in self.results:
            op_type = result.operation.split('_')[0] if '_' in result.operation else result.operation
            if op_type not in operation_groups:
                operation_groups[op_type] = []
            operation_groups[op_type].append(result)
        
        for op_type, results in operation_groups.items():
            report.append(f"--- {op_type.upper()} OPERATIONS ---")
            report.append("")
            
            for result in results:
                report.append(f"Benchmark: {result.benchmark_name}")
                report.append(f"  Average Duration: {result.avg_duration:.3f}s")
                report.append(f"  Min Duration: {result.min_duration:.3f}s")
                report.append(f"  Max Duration: {result.max_duration:.3f}s")
                report.append(f"  Throughput: {result.throughput:.2f} ops/sec")
                report.append(f"  Memory Usage: {result.memory_usage_mb:.2f} MB")
                report.append(f"  CPU Usage: {result.cpu_usage_percent:.2f}%")
                
                # Compare with baseline if available
                comparison = self.compare_with_baseline(result)
                if comparison["status"] == "compared":
                    report.append("  Baseline Comparison:")
                    for metric, improvement in comparison["improvements"].items():
                        report.append(f"    {metric}: {improvement}")
                
                report.append("")
        
        return "\n".join(report)
    
    def save_results(self, filename: str = None):
        """Save benchmark results to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.results_dir / f"benchmark_results_{timestamp}.txt"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"Benchmark results saved to: {filename}")
        return filename
    
    def save_baselines(self, filename: str = None):
        """Save performance baselines to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.results_dir / f"performance_baselines_{timestamp}.json"
        
        baselines_data = {}
        for key, baseline in self.baselines.items():
            baselines_data[key] = {
                "benchmark_name": baseline.benchmark_name,
                "operation": baseline.operation,
                "avg_duration": baseline.avg_duration,
                "throughput": baseline.throughput,
                "memory_usage_mb": baseline.memory_usage_mb,
                "cpu_usage_percent": baseline.cpu_usage_percent,
                "timestamp": baseline.timestamp.isoformat()
            }
        
        with open(filename, 'w') as f:
            json.dump(baselines_data, f, indent=2)
        
        print(f"Performance baselines saved to: {filename}")
        return filename 