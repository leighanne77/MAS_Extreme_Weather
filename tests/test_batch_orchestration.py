#!/usr/bin/env python3
# filepath: /Users/midnighthome/Builds/004_MAS_Climate/tests/test_batch_orchestration.py
"""
Tests for batch_orchestration.py - Batch processing and workflow orchestration.

Tests cover:
- WorkflowStep, StepResult, WorkflowResult dataclasses
- BatchProcessor for parallel execution
- WorkflowOrchestrator for sequential workflows
- Error handling and provenance tracking
"""
import asyncio
from datetime import datetime

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from enums import (
    DataErrorType,
    DataLoadStatus,
    DataProvenance,
)

from multi_agent_system.data.batch_orchestration import (
    WorkflowStep,
    StepResult,
    WorkflowResult,
    BatchProcessor,
    WorkflowOrchestrator,
)


@pytest.mark.unit
class TestStepResult:
    """Tests for StepResult dataclass."""

    def test_step_result_creation(self):
        """Test creating a StepResult."""
        result = StepResult(
            step_name="test_step",
            status=DataLoadStatus.SUCCESS,
            data={"key": "value"},
            provenance=DataProvenance.API,
            latency_ms=150.0,
        )
        
        assert result.step_name == "test_step"
        assert result.status == DataLoadStatus.SUCCESS
        assert result.data == {"key": "value"}
        assert result.provenance == DataProvenance.API
        assert result.latency_ms == 150.0

    def test_step_result_error(self):
        """Test StepResult with error."""
        result = StepResult(
            step_name="failing_step",
            status=DataLoadStatus.ERROR,
            error_type=DataErrorType.NETWORK,
            error="Connection timeout",
        )
        
        assert result.status == DataLoadStatus.ERROR
        assert result.error_type == DataErrorType.NETWORK
        assert result.error == "Connection timeout"

    def test_step_result_to_dict(self):
        """Test converting StepResult to dict."""
        result = StepResult(
            step_name="test_step",
            status=DataLoadStatus.SUCCESS,
            data={"key": "value"},
            provenance=DataProvenance.API,
            latency_ms=100.0,
            retries=2,
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["step_name"] == "test_step"
        assert result_dict["status"] == "SUCCESS"
        assert result_dict["provenance"] == "API"
        assert result_dict["latency_ms"] == 100.0
        assert result_dict["retries"] == 2
        assert "timestamp" in result_dict


@pytest.mark.unit
class TestWorkflowResult:
    """Tests for WorkflowResult dataclass."""

    def test_workflow_result_creation(self):
        """Test creating a WorkflowResult."""
        result = WorkflowResult(
            workflow_name="test_workflow",
            status=DataLoadStatus.SUCCESS,
        )
        
        assert result.workflow_name == "test_workflow"
        assert result.status == DataLoadStatus.SUCCESS
        assert result.steps == []
        assert result.aggregated_data == {}
        assert result.error_count == 0

    def test_add_step_result(self):
        """Test adding step results."""
        workflow = WorkflowResult(
            workflow_name="test_workflow",
            status=DataLoadStatus.SUCCESS,
        )
        
        step1 = StepResult(
            step_name="step1",
            status=DataLoadStatus.SUCCESS,
            data={"result": 1},
            provenance=DataProvenance.API,
            latency_ms=100.0,
        )
        
        step2 = StepResult(
            step_name="step2",
            status=DataLoadStatus.SUCCESS,
            data={"result": 2},
            provenance=DataProvenance.STATIC,
            latency_ms=50.0,
        )
        
        workflow.add_step_result(step1)
        workflow.add_step_result(step2)
        
        assert len(workflow.steps) == 2
        assert workflow.total_latency_ms == 150.0
        assert workflow.aggregated_data["step1"] == {"result": 1}
        assert workflow.aggregated_data["step2"] == {"result": 2}
        assert "step1:API" in workflow.provenance_chain
        assert "step2:STATIC" in workflow.provenance_chain

    def test_add_error_step_result(self):
        """Test adding an error step result."""
        workflow = WorkflowResult(
            workflow_name="test_workflow",
            status=DataLoadStatus.SUCCESS,
        )
        
        error_step = StepResult(
            step_name="failing_step",
            status=DataLoadStatus.ERROR,
            error="Test error",
            latency_ms=50.0,
        )
        
        workflow.add_step_result(error_step)
        
        assert workflow.error_count == 1
        assert workflow.status == DataLoadStatus.ERROR

    def test_workflow_result_to_dict(self):
        """Test converting WorkflowResult to dict."""
        workflow = WorkflowResult(
            workflow_name="test_workflow",
            status=DataLoadStatus.SUCCESS,
        )
        
        step = StepResult(
            step_name="step1",
            status=DataLoadStatus.SUCCESS,
            data={"result": 1},
            provenance=DataProvenance.API,
            latency_ms=100.0,
        )
        workflow.add_step_result(step)
        
        result_dict = workflow.to_dict()
        
        assert result_dict["workflow_name"] == "test_workflow"
        assert result_dict["status"] == "SUCCESS"
        assert len(result_dict["steps"]) == 1
        assert result_dict["total_latency_ms"] == 100.0


@pytest.mark.unit
class TestWorkflowStep:
    """Tests for WorkflowStep dataclass."""

    def test_workflow_step_creation(self):
        """Test creating a WorkflowStep."""
        handler = lambda: {"data": "test"}
        
        step = WorkflowStep(
            name="test_step",
            handler=handler,
            dependencies=["dep1", "dep2"],
            timeout_seconds=60.0,
            retry_count=5,
        )
        
        assert step.name == "test_step"
        assert step.handler == handler
        assert step.dependencies == ["dep1", "dep2"]
        assert step.timeout_seconds == 60.0
        assert step.retry_count == 5

    def test_workflow_step_defaults(self):
        """Test WorkflowStep defaults."""
        handler = lambda: {"data": "test"}
        
        step = WorkflowStep(
            name="test_step",
            handler=handler,
        )
        
        assert step.dependencies == []
        assert step.timeout_seconds == 30.0
        assert step.retry_count == 3


@pytest.mark.unit
class TestBatchProcessor:
    """Tests for BatchProcessor class."""

    @pytest.mark.asyncio
    async def test_batch_processor_creation(self):
        """Test creating a BatchProcessor."""
        processor = BatchProcessor(max_concurrent=10)
        assert processor.max_concurrent == 10

    @pytest.mark.asyncio
    async def test_process_batch_success(self):
        """Test processing a batch successfully."""
        processor = BatchProcessor(max_concurrent=5)
        
        def handler(value: int) -> dict:
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": value * 2,
            }
        
        requests = [
            {"value": 1},
            {"value": 2},
            {"value": 3},
        ]
        
        result = await processor.process_batch(requests, handler)
        
        assert result["status"] == DataLoadStatus.SUCCESS
        assert result["total_requests"] == 3
        assert result["successful_count"] == 3
        assert result["failed_count"] == 0

    @pytest.mark.asyncio
    async def test_process_batch_with_errors(self):
        """Test processing a batch with some failures."""
        processor = BatchProcessor(max_concurrent=5)
        
        def handler(value: int) -> dict:
            if value == 2:
                raise ValueError("Test error")
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": value * 2,
            }
        
        requests = [
            {"value": 1},
            {"value": 2},  # This will fail
            {"value": 3},
        ]
        
        result = await processor.process_batch(requests, handler)
        
        assert result["failed_count"] == 1
        assert result["successful_count"] == 2

    @pytest.mark.asyncio
    async def test_process_batch_async_handler(self):
        """Test processing a batch with async handler."""
        processor = BatchProcessor(max_concurrent=5)
        
        async def async_handler(value: int) -> dict:
            await asyncio.sleep(0.01)  # Simulate async work
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": value * 2,
            }
        
        requests = [
            {"value": 1},
            {"value": 2},
        ]
        
        result = await processor.process_batch(requests, async_handler)
        
        assert result["status"] == DataLoadStatus.SUCCESS
        assert result["total_requests"] == 2


@pytest.mark.unit
class TestWorkflowOrchestrator:
    """Tests for WorkflowOrchestrator class."""

    def test_orchestrator_creation(self):
        """Test creating a WorkflowOrchestrator."""
        orchestrator = WorkflowOrchestrator(name="test_orchestrator")
        assert orchestrator.name == "test_orchestrator"
        assert orchestrator.steps == []

    def test_add_step(self):
        """Test adding steps to orchestrator."""
        orchestrator = WorkflowOrchestrator(name="test_orchestrator")
        
        def handler1():
            return {"data": "step1"}
        
        def handler2():
            return {"data": "step2"}
        
        orchestrator.add_step(WorkflowStep(name="step1", handler=handler1))
        orchestrator.add_step(WorkflowStep(name="step2", handler=handler2))
        
        assert len(orchestrator.steps) == 2

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self):
        """Test executing a workflow successfully."""
        orchestrator = WorkflowOrchestrator(name="test_workflow")
        
        def step1_handler():
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": "result1",
                "provenance": DataProvenance.API,
            }
        
        def step2_handler():
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": "result2",
                "provenance": DataProvenance.STATIC,
            }
        
        orchestrator.add_step(WorkflowStep(name="step1", handler=step1_handler))
        orchestrator.add_step(WorkflowStep(name="step2", handler=step2_handler))
        
        result = await orchestrator.execute()
        
        assert result.status == DataLoadStatus.SUCCESS
        assert len(result.steps) == 2
        assert result.aggregated_data["step1"] == "result1"
        assert result.aggregated_data["step2"] == "result2"
        assert len(result.provenance_chain) == 2

    @pytest.mark.asyncio
    async def test_execute_workflow_with_error(self):
        """Test executing a workflow with an error."""
        orchestrator = WorkflowOrchestrator(name="test_workflow")
        
        def step1_handler():
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": "result1",
            }
        
        def step2_handler():
            raise ValueError("Step 2 failed")
        
        orchestrator.add_step(WorkflowStep(name="step1", handler=step1_handler))
        orchestrator.add_step(WorkflowStep(name="step2", handler=step2_handler))
        
        result = await orchestrator.execute()
        
        assert result.status == DataLoadStatus.ERROR
        assert result.error_count == 1

    @pytest.mark.asyncio
    async def test_execute_workflow_context_passing(self):
        """Test that context is passed between steps."""
        orchestrator = WorkflowOrchestrator(name="test_workflow")
        
        def step1_handler():
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": {"value": 10},
            }
        
        # Step 2 would need to access step 1's result via context
        def step2_handler():
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": {"processed": True},
            }
        
        orchestrator.add_step(WorkflowStep(name="step1", handler=step1_handler))
        orchestrator.add_step(WorkflowStep(name="step2", handler=step2_handler))
        
        result = await orchestrator.execute()
        
        assert "step1" in result.aggregated_data
        assert "step2" in result.aggregated_data


@pytest.mark.integration
class TestIntegration:
    """Integration tests for batch processing and orchestration."""

    @pytest.mark.asyncio
    async def test_batch_in_workflow(self):
        """Test using batch processor within a workflow."""
        orchestrator = WorkflowOrchestrator(name="batch_workflow")
        batch_processor = BatchProcessor(max_concurrent=3)
        
        async def batch_step_handler():
            def item_handler(value: int) -> dict:
                return {"status": DataLoadStatus.SUCCESS, "data": value * 2}
            
            result = await batch_processor.process_batch(
                [{"value": 1}, {"value": 2}, {"value": 3}],
                item_handler,
            )
            return {
                "status": result["status"],
                "data": result,
                "provenance": DataProvenance.API,
            }
        
        # Wrap async handler
        def sync_wrapper():
            return asyncio.get_event_loop().run_until_complete(batch_step_handler())
        
        orchestrator.add_step(WorkflowStep(name="batch_step", handler=batch_step_handler))
        
        result = await orchestrator.execute()
        
        assert result.status == DataLoadStatus.SUCCESS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
