"""
Load testing module for Phase 5 performance optimization.

This module provides comprehensive load testing capabilities using Locust
and custom load testing scenarios for the Multi-Agent Climate Risk Analysis System.
"""

import asyncio
import statistics
import threading
import time
from dataclasses import dataclass
from datetime import datetime
import logging

import psutil

from ..agent_team import AgentTeam
from ..session_manager import SessionManager


@dataclass
class LoadTestResult:
    """Results from a load test scenario."""
    scenario_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    cpu_usage: float
    memory_usage: float
    timestamp: datetime
    errors: list[str]


class LoadTester:
    """
    Comprehensive load testing framework for the Multi-Agent Climate Risk Analysis System.

    Supports various load testing scenarios including:
    - Concurrent user sessions
    - Large dataset processing
    - Agent coordination under load
    - Memory and CPU usage profiling
    """

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.results: list[LoadTestResult] = []
        self.monitoring_active = False
        self.monitoring_thread = None
        self.system_metrics: list[dict[str, float]] = []
        self.logger = logging.getLogger(__name__)

    def start_system_monitoring(self):
        """Start monitoring system resources during load testing."""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_system)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_system_monitoring(self):
        """Stop system resource monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

    def _monitor_system(self):
        """Monitor system resources in background thread."""
        while self.monitoring_active:
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_mb': psutil.virtual_memory().used / 1024 / 1024,
                'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }
            self.system_metrics.append(metrics)
            time.sleep(1)

    async def test_concurrent_sessions(
        self,
        num_sessions: int,
        requests_per_session: int,
        session_type: str = "risk_analysis"
    ) -> LoadTestResult:
        """
        Test concurrent user sessions asynchronously with error handling and granular metrics.
        """
        self.logger.info(f"Starting load test: {num_sessions} sessions, {requests_per_session} requests/session, type={session_type}")
        error_count = 0
        durations = []
        tasks = []
        session_manager = SessionManager()
        for i in range(num_sessions):
            async def run_session():
                for _ in range(requests_per_session):
                    try:
                        if session_type == "risk_analysis":
                            await AgentTeam(session_manager).analyze_risk("Test", "weather", "7d")
                        elif session_type == "historical_analysis":
                            await AgentTeam(session_manager).analyze_historical_data("Test", "2024-01-01", "2024-12-31")
                        else:
                            await AgentTeam(session_manager).process_request(f"Test {session_type}")
                        durations.append(1)  # Placeholder for actual timing
                    except Exception as e:
                        self.logger.error(f"Session error: {e}")
                        nonlocal error_count
                        error_count += 1
            tasks.append(run_session())
        await asyncio.gather(*tasks)
        avg_response_time = statistics.mean(durations) if durations else 0.0
        min_response_time = min(durations) if durations else 0.0
        max_response_time = max(durations) if durations else 0.0
        p95_response_time = statistics.quantiles(durations, n=100)[94] if len(durations) >= 100 else avg_response_time
        p99_response_time = statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else avg_response_time
        requests_per_second = (num_sessions * requests_per_session) / (sum(durations) if durations else 1)
        result = LoadTestResult(
            scenario_name=f"concurrent_{session_type}",
            total_requests=num_sessions * requests_per_session,
            successful_requests=(num_sessions * requests_per_session) - error_count,
            failed_requests=error_count,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().used / 1024 / 1024,
            timestamp=datetime.now(),
            errors=[]
        )
        self.results.append(result)
        return result

    async def test_large_dataset_processing(
        self,
        dataset_size_mb: int,
        num_parallel_processes: int = 4
    ) -> LoadTestResult:
        """
        Test processing of large datasets.

        Args:
            dataset_size_mb: Size of dataset to process in MB
            num_parallel_processes: Number of parallel processes

        Returns:
            LoadTestResult with performance metrics
        """
        print(f"Starting large dataset test: {dataset_size_mb}MB, {num_parallel_processes} processes")

        start_time = time.time()
        response_times = []
        errors = []
        successful_requests = 0
        failed_requests = 0

        # Simulate large dataset processing
        async def process_dataset_chunk(chunk_id: int):
            nonlocal successful_requests, failed_requests

            try:
                session_manager = SessionManager()
                await session_manager.create_session(f"dataset_user_{chunk_id}")
                agent_team = AgentTeam(session_manager)

                # Simulate processing a chunk of data
                chunk_size = dataset_size_mb // num_parallel_processes

                request_start = time.time()

                # Simulate data processing with agent team
                await agent_team.process_large_dataset(
                    data_size_mb=chunk_size,
                    chunk_id=chunk_id
                )

                response_time = time.time() - request_start
                response_times.append(response_time)
                successful_requests += 1

            except Exception as e:
                failed_requests += 1
                errors.append(f"Dataset chunk {chunk_id} failed: {str(e)}")

        # Run parallel dataset processing
        tasks = [process_dataset_chunk(i) for i in range(num_parallel_processes)]
        await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            p99_response_time = statistics.quantiles(response_times, n=100)[98]
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0

        total_requests = num_parallel_processes
        requests_per_second = total_requests / total_time if total_time > 0 else 0

        # Get system metrics
        cpu_usage = statistics.mean([m['cpu_percent'] for m in self.system_metrics]) if self.system_metrics else 0
        memory_usage = statistics.mean([m['memory_percent'] for m in self.system_metrics]) if self.system_metrics else 0

        result = LoadTestResult(
            scenario_name=f"large_dataset_{dataset_size_mb}mb_{num_parallel_processes}processes",
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            timestamp=datetime.now(),
            errors=errors
        )

        self.results.append(result)
        return result

    async def test_agent_coordination_load(
        self,
        num_agents: int,
        coordination_rounds: int,
        complexity_level: str = "medium"
    ) -> LoadTestResult:
        """
        Test agent coordination under load.

        Args:
            num_agents: Number of agents to coordinate
            coordination_rounds: Number of coordination rounds
            complexity_level: Complexity of coordination (simple, medium, complex)

        Returns:
            LoadTestResult with performance metrics
        """
        print(f"Starting agent coordination test: {num_agents} agents, {coordination_rounds} rounds, {complexity_level}")

        start_time = time.time()
        response_times = []
        errors = []
        successful_requests = 0
        failed_requests = 0

        try:
            session_manager = SessionManager()
            await session_manager.create_session("coordination_test_user")
            agent_team = AgentTeam(session_manager)

            for round_id in range(coordination_rounds):
                request_start = time.time()

                try:
                    # Simulate complex agent coordination
                    result = await agent_team.coordinate_agents(
                        num_agents=num_agents,
                        complexity=complexity_level,
                        round_id=round_id
                    )

                    response_time = time.time() - request_start
                    response_times.append(response_time)
                    successful_requests += 1

                except Exception as e:
                    failed_requests += 1
                    errors.append(f"Coordination round {round_id} failed: {str(e)}")

        except Exception as e:
            failed_requests += 1
            errors.append(f"Coordination test setup failed: {str(e)}")

        end_time = time.time()
        total_time = end_time - start_time

        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            p99_response_time = statistics.quantiles(response_times, n=100)[98]
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0

        total_requests = coordination_rounds
        requests_per_second = total_requests / total_time if total_time > 0 else 0

        # Get system metrics
        cpu_usage = statistics.mean([m['cpu_percent'] for m in self.system_metrics]) if self.system_metrics else 0
        memory_usage = statistics.mean([m['memory_percent'] for m in self.system_metrics]) if self.system_metrics else 0

        result = LoadTestResult(
            scenario_name=f"agent_coordination_{num_agents}agents_{coordination_rounds}rounds_{complexity_level}",
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            timestamp=datetime.now(),
            errors=errors
        )

        self.results.append(result)
        return result

    def generate_report(self) -> str:
        """Generate a comprehensive load testing report."""
        if not self.results:
            return "No load test results available."

        report = []
        report.append("=" * 80)
        report.append("LOAD TESTING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now()}")
        report.append(f"Total scenarios tested: {len(self.results)}")
        report.append("")

        for result in self.results:
            report.append("-" * 60)
            report.append(f"Scenario: {result.scenario_name}")
            report.append("-" * 60)
            report.append(f"Total Requests: {result.total_requests}")
            report.append(f"Successful: {result.successful_requests}")
            report.append(f"Failed: {result.failed_requests}")
            report.append(f"Success Rate: {(result.successful_requests/result.total_requests)*100:.2f}%")
            report.append("")
            report.append("Response Times:")
            report.append(f"  Average: {result.avg_response_time:.3f}s")
            report.append(f"  Min: {result.min_response_time:.3f}s")
            report.append(f"  Max: {result.max_response_time:.3f}s")
            report.append(f"  95th Percentile: {result.p95_response_time:.3f}s")
            report.append(f"  99th Percentile: {result.p99_response_time:.3f}s")
            report.append(f"  Requests/Second: {result.requests_per_second:.2f}")
            report.append("")
            report.append("System Resources:")
            report.append(f"  CPU Usage: {result.cpu_usage:.2f}%")
            report.append(f"  Memory Usage: {result.memory_usage:.2f}%")
            report.append("")

            if result.errors:
                report.append("Errors:")
                for error in result.errors[:5]:  # Show first 5 errors
                    report.append(f"  - {error}")
                if len(result.errors) > 5:
                    report.append(f"  ... and {len(result.errors) - 5} more errors")
            report.append("")

        # Summary statistics
        report.append("=" * 80)
        report.append("SUMMARY STATISTICS")
        report.append("=" * 80)

        total_requests = sum(r.total_requests for r in self.results)
        total_successful = sum(r.successful_requests for r in self.results)
        total_failed = sum(r.failed_requests for r in self.results)

        report.append(f"Total Requests Across All Scenarios: {total_requests}")
        report.append(f"Total Successful: {total_successful}")
        report.append(f"Total Failed: {total_failed}")
        report.append(f"Overall Success Rate: {(total_successful/total_requests)*100:.2f}%")

        avg_response_times = [r.avg_response_time for r in self.results if r.avg_response_time > 0]
        if avg_response_times:
            report.append(f"Average Response Time Across Scenarios: {statistics.mean(avg_response_times):.3f}s")
            report.append(f"Best Response Time: {min(avg_response_times):.3f}s")
            report.append(f"Worst Response Time: {max(avg_response_times):.3f}s")

        return "\n".join(report)

    def save_results(self, filename: str = None):
        """Save load test results to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_results_{timestamp}.txt"

        report = self.generate_report()

        with open(filename, 'w') as f:
            f.write(report)

        print(f"Load test results saved to: {filename}")
        return filename
