"""
Batch Processing and Orchestration for Multi-Step Data Aggregation

This module provides utilities for:
- Batch processing of data loader requests
- Multi-step workflow orchestration with provenance tracking
- Error aggregation and propagation
- Metrics collection across workflow steps

References:
    - Google Cloud Agent SDK: https://cloud.google.com/agent-sdk/docs
    - Google Cloud Agent Engine: https://cloud.google.com/agent-engine/docs
    - See docs/2-DATA/GEE A2A ADK.md for full implementation plan
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from enums import (
    DataErrorType,
    DataLoadStatus,
    DataProvenance,
    ErrorSeverity,
)

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """A single step in a multi-step workflow."""
    name: str
    handler: Callable
    dependencies: list[str] = field(default_factory=list)
    timeout_seconds: float = 30.0
    retry_count: int = 3
    retry_backoff_seconds: float = 1.0   # 0 disables; doubles per attempt, capped at 30s
    

@dataclass
class StepResult:
    """Result of a workflow step execution."""
    step_name: str
    status: DataLoadStatus
    data: Any = None
    provenance: DataProvenance | None = None
    error_type: DataErrorType | None = None
    error: str | None = None
    latency_ms: float = 0.0
    retries: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for aggregation."""
        return {
            "step_name": self.step_name,
            "status": self.status.value if self.status else None,
            "provenance": self.provenance.value if self.provenance else None,
            "error_type": self.error_type.value if self.error_type else None,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "retries": self.retries,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class WorkflowResult:
    """Aggregated result of a multi-step workflow."""
    workflow_name: str
    status: DataLoadStatus
    steps: list[StepResult] = field(default_factory=list)
    aggregated_data: dict[str, Any] = field(default_factory=dict)
    total_latency_ms: float = 0.0
    error_count: int = 0
    provenance_chain: list[str] = field(default_factory=list)
    
    def add_step_result(self, result: StepResult) -> None:
        """Add a step result and update aggregations."""
        self.steps.append(result)
        self.total_latency_ms += result.latency_ms
        
        if result.status == DataLoadStatus.ERROR:
            self.error_count += 1
            self.status = DataLoadStatus.ERROR
        
        if result.provenance:
            self.provenance_chain.append(f"{result.step_name}:{result.provenance.value}")
        
        if result.data is not None:
            self.aggregated_data[result.step_name] = result.data
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for return."""
        return {
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "aggregated_data": self.aggregated_data,
            "total_latency_ms": self.total_latency_ms,
            "error_count": self.error_count,
            "provenance_chain": self.provenance_chain,
        }


class BatchProcessor:
    """
    Processes multiple data loader requests in batch.
    
    Features:
    - Parallel execution of independent requests
    - Error aggregation and partial success handling
    - Metrics collection for all requests
    """
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(
        self,
        requests: list[dict[str, Any]],
        handler: Callable,
    ) -> dict[str, Any]:
        """
        Process a batch of requests.
        
        Args:
            requests: List of request dicts (each with params for handler)
            handler: Async callable to process each request
        
        Returns:
            dict: Batch result with status, results, and metrics
        """
        start_time = time.time()
        results = []
        errors = []
        
        async def process_one(request: dict[str, Any], index: int) -> dict[str, Any]:
            async with self.semaphore:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(**request)
                    else:
                        result = handler(**request)
                    return {"index": index, "result": result, "error": None}
                except Exception as e:
                    logger.error(f"Batch request {index} failed: {e}")
                    return {
                        "index": index,
                        "result": None,
                        "error": str(e),
                    }
        
        tasks = [process_one(req, i) for i, req in enumerate(requests)]
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        for item in completed:
            if isinstance(item, Exception):
                errors.append(str(item))
            elif item.get("error"):
                errors.append(item["error"])
                results.append(item)
            else:
                results.append(item)
        
        total_latency_ms = (time.time() - start_time) * 1000

        # Honest top-level status: ERROR only when EVERYTHING failed; a mixed
        # batch is PARTIAL so callers don't discard the successes.
        if not errors:
            status = DataLoadStatus.SUCCESS
        elif len(errors) < len(requests):
            status = DataLoadStatus.PARTIAL
        else:
            status = DataLoadStatus.ERROR

        return {
            "status": status,
            "results": results,
            "errors": errors,
            "total_count": len(requests),
            "success_count": len(requests) - len(errors),
            "error_count": len(errors),
            "total_latency_ms": total_latency_ms,
        }


class WorkflowOrchestrator:
    """
    Orchestrates multi-step workflows with provenance tracking.
    
    Features:
    - Sequential execution with dependency resolution
    - Provenance chain tracking
    - Error propagation with actionable messages
    - Metrics aggregation across steps
    
    Example:
        orchestrator = WorkflowOrchestrator()
        
        steps = [
            WorkflowStep(name="fetch_data", handler=fetch_handler),
            WorkflowStep(name="analyze", handler=analyze_handler, dependencies=["fetch_data"]),
            WorkflowStep(name="report", handler=report_handler, dependencies=["analyze"]),
        ]
        
        result = await orchestrator.execute_workflow("risk_analysis", steps, context)
    """
    
    def __init__(self):
        self.completed_steps: dict[str, StepResult] = {}
    
    async def execute_workflow(
        self,
        workflow_name: str,
        steps: list[WorkflowStep],
        context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """
        Execute a multi-step workflow.
        
        Args:
            workflow_name: Name for logging and metrics
            steps: List of workflow steps to execute
            context: Shared context dict passed to all handlers
        
        Returns:
            WorkflowResult: Aggregated result with provenance chain
        """
        context = context or {}
        result = WorkflowResult(workflow_name=workflow_name, status=DataLoadStatus.SUCCESS)
        self.completed_steps = {}
        
        # Topological sort for dependency resolution
        sorted_steps = self._topological_sort(steps)
        
        for step in sorted_steps:
            step_result = await self._execute_step(step, context)
            result.add_step_result(step_result)
            self.completed_steps[step.name] = step_result
            
            # Add step data to context for downstream steps
            if step_result.data is not None:
                context[step.name] = step_result.data
            
            # Stop on error unless step is optional
            if step_result.status == DataLoadStatus.ERROR:
                logger.error(f"Workflow {workflow_name} failed at step {step.name}")
                break
        
        return result
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        context: dict[str, Any],
    ) -> StepResult:
        """Execute a single workflow step with retry logic."""
        start_time = time.time()
        retries = 0
        last_error = None
        
        while retries <= step.retry_count:
            try:
                logger.info(f"Executing workflow step: {step.name} (attempt {retries + 1})")
                
                if asyncio.iscoroutinefunction(step.handler):
                    result = await asyncio.wait_for(
                        step.handler(context),
                        timeout=step.timeout_seconds,
                    )
                else:
                    result = step.handler(context)
                
                latency_ms = (time.time() - start_time) * 1000
                
                # Parse result if it's a standardized dict
                if isinstance(result, dict):
                    return StepResult(
                        step_name=step.name,
                        status=result.get("status", DataLoadStatus.SUCCESS),
                        data=result.get("data"),
                        provenance=result.get("provenance"),
                        error_type=result.get("error_type"),
                        error=result.get("error"),
                        latency_ms=latency_ms,
                        retries=retries,
                    )
                else:
                    return StepResult(
                        step_name=step.name,
                        status=DataLoadStatus.SUCCESS,
                        data=result,
                        latency_ms=latency_ms,
                        retries=retries,
                    )
                    
            except asyncio.TimeoutError:
                last_error = f"Step {step.name} timed out after {step.timeout_seconds}s"
                logger.warning(last_error)
                retries += 1
                await self._backoff(step, retries)

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Step {step.name} failed: {e}")
                retries += 1
                await self._backoff(step, retries)
        
        # All retries exhausted
        latency_ms = (time.time() - start_time) * 1000
        return StepResult(
            step_name=step.name,
            status=DataLoadStatus.ERROR,
            error_type=DataErrorType.UNKNOWN,
            error=f"Step failed after {retries} retries: {last_error}",
            latency_ms=latency_ms,
            retries=retries,
        )
    
    async def _backoff(self, step: WorkflowStep, retries: int) -> None:
        """Exponential backoff between retry attempts (transport-level failures only).
        Sleeps only when another attempt remains; retry_backoff_seconds=0 disables."""
        if retries <= step.retry_count and step.retry_backoff_seconds > 0:
            delay = min(step.retry_backoff_seconds * 2 ** (retries - 1), 30.0)
            logger.info(f"Step {step.name}: backing off {delay:.1f}s before attempt {retries + 1}")
            await asyncio.sleep(delay)

    def _topological_sort(self, steps: list[WorkflowStep]) -> list[WorkflowStep]:
        """Sort steps by dependencies (topological order).

        Raises ValueError on a dependency cycle — a cyclic workflow can never
        run its steps dependencies-first, so it must fail loudly here rather
        than execute in an arbitrary order.
        """
        step_map = {s.name: s for s in steps}
        visited = set()
        in_progress = set()
        result = []

        def visit(step: WorkflowStep, path: tuple[str, ...]):
            if step.name in visited:
                return
            if step.name in in_progress:
                cycle = " -> ".join(path + (step.name,))
                raise ValueError(f"dependency cycle in workflow steps: {cycle}")
            in_progress.add(step.name)
            for dep_name in step.dependencies:
                if dep_name in step_map:
                    visit(step_map[dep_name], path + (step.name,))
            in_progress.discard(step.name)
            visited.add(step.name)
            result.append(step)

        for step in steps:
            visit(step, ())

        return result
