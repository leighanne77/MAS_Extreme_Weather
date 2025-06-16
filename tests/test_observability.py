"""
Tests for observability system functionality.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock
import os
import json
from pathlib import Path
import aiofiles
import asyncio

from src.multi_agent_system.observability import (
    ObservabilityManager,
    InteractionType,
    DecisionPattern,
    ErrorSeverity,
    InteractionMetrics,
    DecisionMetrics,
    ErrorContext,
    Checkpoint,
    PatternMonitor
)

@pytest.fixture
def checkpoint_dir(tmp_path):
    return str(tmp_path / "checkpoints")

@pytest.fixture
def monitor(checkpoint_dir):
    return PatternMonitor(checkpoint_dir=checkpoint_dir)

@pytest.fixture
def manager(checkpoint_dir):
    return ObservabilityManager(checkpoint_dir=checkpoint_dir)

class TestObservabilityManager:
    """Test suite for ObservabilityManager functionality."""
    
    @pytest.mark.asyncio
    async def test_create_checkpoint(self, monitor):
        agent_id = "test_agent"
        state = {"status": "running"}
        context = {"location": "test"}
        tool_calls = [{"tool": "test_tool"}]
        
        checkpoint_id = await monitor.create_checkpoint(
            agent_id=agent_id,
            state=state,
            context=context,
            tool_calls=tool_calls,
            recovery_point="test_point",
            metadata={"test": "metadata"}
        )
        
        assert checkpoint_id is not None
        assert checkpoint_id.startswith("checkpoint_")
        
        # Verify checkpoint file exists
        checkpoint_path = Path(monitor.checkpoint_dir) / f"{checkpoint_id}.json"
        assert checkpoint_path.exists()
        
        # Verify checkpoint contents
        async with aiofiles.open(checkpoint_path, 'r') as f:
            data = json.loads(await f.read())
            assert data["agent_id"] == agent_id
            assert data["state"] == state
            assert data["context"] == context
            assert data["tool_calls"] == tool_calls
            assert data["recovery_point"] == "test_point"
            assert data["metadata"] == {"test": "metadata"}

    @pytest.mark.asyncio
    async def test_restore_checkpoint(self, monitor):
        # Create a checkpoint
        agent_id = "test_agent"
        state = {"status": "running"}
        context = {"location": "test"}
        tool_calls = [{"tool": "test_tool"}]
        
        checkpoint_id = await monitor.create_checkpoint(
            agent_id=agent_id,
            state=state,
            context=context,
            tool_calls=tool_calls
        )
        
        # Restore the checkpoint
        restored = await monitor.restore_checkpoint(checkpoint_id)
        assert restored is not None
        assert restored.agent_id == agent_id
        assert restored.state == state
        assert restored.context == context
        assert restored.tool_calls == tool_calls

    @pytest.mark.asyncio
    async def test_list_checkpoints(self, monitor):
        # Create multiple checkpoints
        agent_ids = ["agent1", "agent2"]
        for agent_id in agent_ids:
            await monitor.create_checkpoint(
                agent_id=agent_id,
                state={"status": "running"},
                context={"location": "test"},
                tool_calls=[{"tool": "test_tool"}]
            )
        
        # List all checkpoints
        all_checkpoints = await monitor.list_checkpoints()
        assert len(all_checkpoints) == 2
        
        # List checkpoints for specific agent
        agent1_checkpoints = await monitor.list_checkpoints(agent_id="agent1")
        assert len(agent1_checkpoints) == 1
        assert agent1_checkpoints[0]["agent_id"] == "agent1"

    @pytest.mark.asyncio
    async def test_delete_checkpoint(self, monitor):
        # Create a checkpoint
        checkpoint_id = await monitor.create_checkpoint(
            agent_id="test_agent",
            state={"status": "running"},
            context={"location": "test"},
            tool_calls=[{"tool": "test_tool"}]
        )
        
        # Delete the checkpoint
        success = await monitor.delete_checkpoint(checkpoint_id)
        assert success is True
        
        # Verify checkpoint is deleted
        checkpoint_path = Path(monitor.checkpoint_dir) / f"{checkpoint_id}.json"
        assert not checkpoint_path.exists()

    @pytest.mark.asyncio
    async def test_cleanup_old_checkpoints(self, monitor):
        # Create a checkpoint
        await monitor.create_checkpoint(
            agent_id="test_agent",
            state={"status": "running"},
            context={"location": "test"},
            tool_calls=[{"tool": "test_tool"}]
        )
        
        # Clean up old checkpoints (0 days old)
        deleted = await monitor.cleanup_old_checkpoints(max_age_days=0)
        assert deleted == 1
        
        # Verify all checkpoints are deleted
        checkpoints = await monitor.list_checkpoints()
        assert len(checkpoints) == 0

    @pytest.mark.asyncio
    async def test_concurrent_checkpoint_operations(self, monitor):
        # Create multiple checkpoints concurrently
        async def create_checkpoint(agent_id):
            return await monitor.create_checkpoint(
                agent_id=agent_id,
                state={"status": "running"},
                context={"location": "test"},
                tool_calls=[{"tool": "test_tool"}]
            )
        
        # Create 5 checkpoints concurrently
        tasks = [create_checkpoint(f"agent_{i}") for i in range(5)]
        checkpoint_ids = await asyncio.gather(*tasks)
        
        # Verify all checkpoints were created
        assert len(checkpoint_ids) == 5
        checkpoints = await monitor.list_checkpoints()
        assert len(checkpoints) == 5

    def test_track_error(
        self,
        manager: ObservabilityManager
    ):
        """Test error tracking.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        error_context = manager.track_error(
            agent_id="test_agent",
            error_type="test_error",
            severity=ErrorSeverity.MEDIUM,
            tool_name="test_tool",
            context={"location": "New York"},
            stack_trace="test stack trace"
        )
        
        assert error_context is not None
        assert isinstance(error_context, ErrorContext)
        assert error_context.agent_id == "test_agent"
        assert error_context.error_type == "test_error"
        assert error_context.severity == ErrorSeverity.MEDIUM
    
    def test_track_interaction(
        self,
        manager: ObservabilityManager
    ):
        """Test interaction tracking.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=5)
        
        metrics = manager.track_interaction(
            agent_id="test_agent",
            interaction_type=InteractionType.SEQUENTIAL,
            start_time=start_time,
            end_time=end_time,
            success=True,
            token_usage={"input": 100, "output": 50},
            context_size=1024,
            compressed_size=512
        )
        
        assert metrics is not None
        assert isinstance(metrics, InteractionMetrics)
        assert metrics.agent_id == "test_agent"
        assert metrics.interaction_type == InteractionType.SEQUENTIAL
        assert metrics.success is True
    
    def test_track_decision(
        self,
        manager: ObservabilityManager
    ):
        """Test decision tracking.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=5)
        
        metrics = manager.track_decision(
            agent_id="test_agent",
            pattern=DecisionPattern.BRANCHING,
            start_time=start_time,
            end_time=end_time,
            branches=3,
            max_depth=2,
            success_rate=0.8,
            error_rate=0.2,
            optimization_score=0.9
        )
        
        assert metrics is not None
        assert isinstance(metrics, DecisionMetrics)
        assert metrics.agent_id == "test_agent"
        assert metrics.pattern == DecisionPattern.BRANCHING
        assert metrics.success_rate == 0.8
    
    def test_get_agent_patterns(
        self,
        manager: ObservabilityManager
    ):
        """Test getting agent patterns.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        patterns = manager.get_agent_patterns("test_agent")
        assert patterns is not None
    
    def test_get_interaction_patterns(
        self,
        manager: ObservabilityManager
    ):
        """Test getting interaction patterns.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        patterns = manager.get_interaction_patterns()
        assert isinstance(patterns, dict)
    
    def test_get_decision_patterns(
        self,
        manager: ObservabilityManager
    ):
        """Test getting decision patterns.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        patterns = manager.get_decision_patterns()
        assert isinstance(patterns, dict)
    
    def test_get_error_patterns(
        self,
        manager: ObservabilityManager
    ):
        """Test getting error patterns.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        patterns = manager.get_error_patterns()
        assert isinstance(patterns, dict)
    
    def test_get_retry_patterns(
        self,
        manager: ObservabilityManager
    ):
        """Test getting retry patterns.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        patterns = manager.get_retry_patterns()
        assert isinstance(patterns, dict)
    
    def test_get_token_usage_patterns(
        self,
        manager: ObservabilityManager
    ):
        """Test getting token usage patterns.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        patterns = manager.get_token_usage_patterns()
        assert isinstance(patterns, dict)
    
    def test_get_context_patterns(
        self,
        manager: ObservabilityManager
    ):
        """Test getting context patterns.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        patterns = manager.get_context_patterns()
        assert isinstance(patterns, dict)
    
    def test_analyze_patterns(
        self,
        manager: ObservabilityManager
    ):
        """Test pattern analysis.
        
        Args:
            manager (ObservabilityManager): Manager instance
        """
        analysis = manager.analyze_patterns()
        assert isinstance(analysis, dict) 