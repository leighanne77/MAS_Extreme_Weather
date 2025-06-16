"""
Tests for enhanced ADK coordinator with parallel execution, token tracking, and context compression.
"""

import pytest
import asyncio
from typing import Dict, List, Any
from datetime import datetime

from src.multi_agent_system.enhanced_coordinator import EnhancedADKCoordinator
from src.multi_agent_system.communication import CommunicationManager
from src.multi_agent_system.artifact_manager import ArtifactManager

# Test Categories
pytestmark = [
    pytest.mark.category("unit"),
    pytest.mark.timeout(30)
]

class TestEnhancedCoordinator:
    """Test suite for enhanced coordinator functionality."""
    
    @pytest.mark.asyncio
    async def test_parallel_execution(
        self,
        enhanced_coordinator: EnhancedADKCoordinator,
        mock_communication_manager: CommunicationManager,
        mock_artifact_manager: ArtifactManager
    ):
        """Test parallel execution of tasks.
        
        Args:
            enhanced_coordinator (EnhancedADKCoordinator): Coordinator instance
            mock_communication_manager (CommunicationManager): Communication manager
            mock_artifact_manager (ArtifactManager): Artifact manager
        """
        # Prepare test data
        tasks = [
            {"id": "task1", "type": "analysis"},
            {"id": "task2", "type": "analysis"},
            {"id": "task3", "type": "analysis"}
        ]
        context = {"shared": "data"}
        
        # Execute tasks
        results = await enhanced_coordinator.execute_parallel_tasks(tasks, context)
        
        # Verify results
        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)
        assert all("token_usage" in r for r in results)
    
    @pytest.mark.asyncio
    async def test_token_tracking(
        self,
        enhanced_coordinator: EnhancedADKCoordinator,
        mock_communication_manager: CommunicationManager
    ):
        """Test token usage tracking.
        
        Args:
            enhanced_coordinator (EnhancedADKCoordinator): Coordinator instance
            mock_communication_manager (CommunicationManager): Communication manager
        """
        # Prepare test data
        task = {"id": "test_task", "data": "test data"}
        context = {"shared": "test context"}
        
        # Execute task
        result = await enhanced_coordinator._execute_task_with_tracking(
            task,
            context
        )
        
        # Verify results
        assert result["status"] == "success"
        assert "token_usage" in result
        assert result["token_usage"].input_tokens > 0
        assert result["token_usage"].output_tokens > 0
    
    @pytest.mark.asyncio
    async def test_context_compression(
        self,
        enhanced_coordinator: EnhancedADKCoordinator
    ):
        """Test context compression and decompression.
        
        Args:
            enhanced_coordinator (EnhancedADKCoordinator): Coordinator instance
        """
        # Prepare test data
        context = {
            "large_data": "x" * 1000,  # Create large context
            "nested": {
                "data": "test",
                "numbers": [1, 2, 3, 4, 5]
            }
        }
        
        # Compress context
        compressed = enhanced_coordinator._compress_context(context)
        
        # Verify compression
        assert compressed.compressed_size < compressed.original_size
        assert compressed.compression_ratio < 1.0
        
        # Decompress and verify
        decompressed = enhanced_coordinator._decompress_context(compressed)
        assert decompressed == context
    
    @pytest.mark.asyncio
    async def test_concurrent_limiting(
        self,
        enhanced_coordinator: EnhancedADKCoordinator,
        mock_communication_manager: CommunicationManager
    ):
        """Test concurrent task limiting.
        
        Args:
            enhanced_coordinator (EnhancedADKCoordinator): Coordinator instance
            mock_communication_manager (CommunicationManager): Communication manager
        """
        # Prepare test data
        tasks = [
            {"id": f"task{i}", "type": "analysis"}
            for i in range(10)  # More tasks than max_concurrent
        ]
        context = {"shared": "data"}
        
        # Execute tasks
        results = await enhanced_coordinator.execute_parallel_tasks(tasks, context)
        
        # Verify results
        assert len(results) == 10
        assert all(r["status"] == "success" for r in results)
        
        # Verify concurrent execution limit
        active_tasks = len([
            t for t in enhanced_coordinator.parallel_tasks.values()
            if not t.done()
        ])
        assert active_tasks <= enhanced_coordinator.max_parallel_tasks
    
    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        enhanced_coordinator: EnhancedADKCoordinator,
        mock_communication_manager: CommunicationManager
    ):
        """Test error handling during task execution.
        
        Args:
            enhanced_coordinator (EnhancedADKCoordinator): Coordinator instance
            mock_communication_manager (CommunicationManager): Communication manager
        """
        # Prepare test data
        tasks = [
            {"id": "error_task", "type": "error"},  # Task that will fail
            {"id": "success_task", "type": "analysis"}  # Task that will succeed
        ]
        context = {"shared": "data"}
        
        # Execute tasks
        results = await enhanced_coordinator.execute_parallel_tasks(tasks, context)
        
        # Verify results
        assert len(results) == 2
        assert results[0]["status"] == "error"
        assert results[1]["status"] == "success"
        
        # Verify error details
        assert "error" in results[0]
        assert "task_id" in results[0]
        assert results[0]["task_id"] == "error_task" 