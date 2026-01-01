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
import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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
        assert result_dict["status"] == "success"  # enum value is lowercase
        assert result_dict["provenance"] == "api"  # enum value is lowercase
        assert result_dict["latency_ms"] == 100.0
        assert result_dict["retries"] == 2
        assert "timestamp" in result_dict


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
        assert "step1:api" in workflow.provenance_chain  # enum value is lowercase
        assert "step2:static" in workflow.provenance_chain  # enum value is lowercase

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
        assert result_dict["status"] == "success"  # enum value is lowercase
        assert len(result_dict["steps"]) == 1
        assert result_dict["total_latency_ms"] == 100.0


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
        assert result["total_count"] == 3  # actual key name
        assert result["success_count"] == 3  # actual key name
        assert result["error_count"] == 0  # actual key name

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
        
        assert result["error_count"] == 1  # actual key name
        assert result["success_count"] == 2  # actual key name

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
        assert result["total_count"] == 2  # actual key name


class TestWorkflowOrchestrator:
    """Tests for WorkflowOrchestrator class."""

    def test_orchestrator_creation(self):
        """Test creating a WorkflowOrchestrator."""
        orchestrator = WorkflowOrchestrator()
        assert orchestrator.completed_steps == {}

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self):
        """Test executing a workflow successfully."""
        orchestrator = WorkflowOrchestrator()
        
        def step1_handler(context):
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": "result1",
                "provenance": DataProvenance.API,
            }
        
        def step2_handler(context):
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": "result2",
                "provenance": DataProvenance.STATIC,
            }
        
        steps = [
            WorkflowStep(name="step1", handler=step1_handler),
            WorkflowStep(name="step2", handler=step2_handler),
        ]
        
        result = await orchestrator.execute_workflow("test_workflow", steps)
        
        assert result.status == DataLoadStatus.SUCCESS
        assert len(result.steps) == 2
        assert result.aggregated_data["step1"] == "result1"
        assert result.aggregated_data["step2"] == "result2"
        assert len(result.provenance_chain) == 2

    @pytest.mark.asyncio
    async def test_execute_workflow_with_error(self):
        """Test executing a workflow with an error that exhausts retries."""
        orchestrator = WorkflowOrchestrator()
        
        def step1_handler(context):
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": "result1",
            }
        
        def step2_handler(context):
            raise ValueError("Step 2 failed")
        
        steps = [
            WorkflowStep(name="step1", handler=step1_handler),
            WorkflowStep(name="step2", handler=step2_handler, retry_count=0),  # No retries
        ]
        
        result = await orchestrator.execute_workflow("test_workflow", steps)
        
        assert result.status == DataLoadStatus.ERROR
        assert result.error_count == 1

    @pytest.mark.asyncio
    async def test_execute_workflow_context_passing(self):
        """Test that context is passed between steps."""
        orchestrator = WorkflowOrchestrator()
        
        def step1_handler(context):
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": {"value": 10},
            }
        
        # Step 2 accesses step 1's result via context
        def step2_handler(context):
            step1_value = context.get("step1", {}).get("value", 0)
            return {
                "status": DataLoadStatus.SUCCESS,
                "data": {"processed": True, "doubled": step1_value * 2},
            }
        
        steps = [
            WorkflowStep(name="step1", handler=step1_handler),
            WorkflowStep(name="step2", handler=step2_handler),
        ]
        
        result = await orchestrator.execute_workflow("test_workflow", steps)
        
        assert result.status == DataLoadStatus.SUCCESS
        assert "step1" in result.aggregated_data
        assert "step2" in result.aggregated_data
        assert result.aggregated_data["step2"]["doubled"] == 20


class TestIntegration:
    """Integration tests for batch processing and orchestration."""

    @pytest.mark.asyncio
    async def test_batch_in_workflow(self):
        """Test using batch processor within a workflow."""
        orchestrator = WorkflowOrchestrator()
        batch_processor = BatchProcessor(max_concurrent=3)
        
        async def batch_step_handler(context):
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
        
        steps = [
            WorkflowStep(name="batch_step", handler=batch_step_handler),
        ]
        
        result = await orchestrator.execute_workflow("batch_workflow", steps)
        
        assert result.status == DataLoadStatus.SUCCESS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
