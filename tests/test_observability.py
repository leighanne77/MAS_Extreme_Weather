"""
Tests for agent pattern monitoring and observability system.
"""

import pytest
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from multi_tool_agent.observability import (
    PatternMonitor,
    InteractionType,
    DecisionPattern,
    ErrorSeverity,
    InteractionMetrics,
    DecisionMetrics,
    AgentPatterns,
    Checkpoint,
    ErrorContext,
    RecoveryStrategy
)

# Test Categories
pytestmark = [
    pytest.mark.category("unit"),
    pytest.mark.timeout(30)
]

class TestPatternMonitor:
    """Test suite for pattern monitoring functionality."""
    
    @pytest.fixture
    def monitor(self, tmp_path) -> PatternMonitor:
        """Create a pattern monitor instance.
        
        Args:
            tmp_path: Temporary directory for checkpoints
            
        Returns:
            PatternMonitor: Monitor instance
        """
        return PatternMonitor(checkpoint_dir=str(tmp_path))
    
    @pytest.fixture
    def sample_interaction_data(self) -> Dict[str, Any]:
        """Create sample interaction data.
        
        Returns:
            Dict[str, Any]: Sample interaction data
        """
        return {
            "agent_id": "test_agent",
            "interaction_type": InteractionType.SEQUENTIAL,
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(seconds=1),
            "success": True,
            "token_usage": {
                "input": 100,
                "output": 50
            },
            "context_size": 1000,
            "compressed_size": 500
        }
    
    @pytest.fixture
    def sample_decision_data(self) -> Dict[str, Any]:
        """Create sample decision data.
        
        Returns:
            Dict[str, Any]: Sample decision data
        """
        return {
            "agent_id": "test_agent",
            "pattern": DecisionPattern.BRANCHING,
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(seconds=1),
            "branches": 3,
            "max_depth": 2,
            "success_rate": 0.8,
            "error_rate": 0.2,
            "optimization_score": 0.9
        }
    
    @pytest.fixture
    def sample_state(self) -> Dict[str, Any]:
        """Create sample agent state.
        
        Returns:
            Dict[str, Any]: Sample state
        """
        return {
            "current_task": "test_task",
            "progress": 0.5,
            "context": {
                "key1": "value1",
                "key2": "value2"
            }
        }
    
    @pytest.fixture
    def sample_tool_calls(self) -> List[Dict[str, Any]]:
        """Create sample tool calls.
        
        Returns:
            List[Dict[str, Any]]: Sample tool calls
        """
        return [
            {
                "tool": "test_tool",
                "args": {"arg1": "value1"},
                "result": "success"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_checkpoint_creation(
        self,
        monitor: PatternMonitor,
        sample_state: Dict[str, Any],
        sample_tool_calls: List[Dict[str, Any]]
    ):
        """Test checkpoint creation and restoration.
        
        Args:
            monitor (PatternMonitor): Monitor instance
            sample_state (Dict[str, Any]): Sample state
            sample_tool_calls (List[Dict[str, Any]]): Sample tool calls
        """
        # Create checkpoint
        checkpoint_id = await monitor.create_checkpoint(
            agent_id="test_agent",
            state=sample_state,
            context={"key": "value"},
            tool_calls=sample_tool_calls
        )
        
        # Verify checkpoint file exists
        checkpoint_path = os.path.join(monitor.checkpoint_dir, f"{checkpoint_id}.json")
        assert os.path.exists(checkpoint_path)
        
        # Restore checkpoint
        checkpoint = await monitor.restore_checkpoint(checkpoint_id)
        assert checkpoint is not None
        assert checkpoint.agent_id == "test_agent"
        assert checkpoint.state == sample_state
        assert checkpoint.tool_calls == sample_tool_calls
    
    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        monitor: PatternMonitor,
        sample_state: Dict[str, Any],
        sample_tool_calls: List[Dict[str, Any]]
    ):
        """Test error handling and recovery.
        
        Args:
            monitor (PatternMonitor): Monitor instance
            sample_state (Dict[str, Any]): Sample state
            sample_tool_calls (List[Dict[str, Any]]): Sample tool calls
        """
        # Create checkpoint
        await monitor.create_checkpoint(
            agent_id="test_agent",
            state=sample_state,
            context={"key": "value"},
            tool_calls=sample_tool_calls
        )
        
        # Handle error
        recovery_plan = await monitor.handle_error(
            agent_id="test_agent",
            error_type="test_error",
            severity=ErrorSeverity.HIGH,
            tool_name="test_tool",
            context={"error_context": "test"},
            stack_trace="test_trace"
        )
        
        # Verify recovery plan
        assert recovery_plan["error_context"]["error_type"] == "test_error"
        assert recovery_plan["error_context"]["severity"] == ErrorSeverity.HIGH.value
        assert recovery_plan["recovery_strategy"]["max_retries"] == 4
        assert recovery_plan["recovery_strategy"]["requires_rollback"] is True
        assert recovery_plan["latest_checkpoint"] is not None
    
    def test_error_tracking(
        self,
        monitor: PatternMonitor,
        sample_interaction_data: Dict[str, Any]
    ):
        """Test error pattern tracking.
        
        Args:
            monitor (PatternMonitor): Monitor instance
            sample_interaction_data (Dict[str, Any]): Sample interaction data
        """
        # Track error
        error_context = monitor.track_error(
            agent_id="test_agent",
            error_type="test_error",
            severity=ErrorSeverity.MEDIUM,
            tool_name="test_tool",
            context={"error_context": "test"},
            stack_trace="test_trace"
        )
        
        # Verify error context
        assert error_context.error_type == "test_error"
        assert error_context.severity == ErrorSeverity.MEDIUM
        assert error_context.tool_name == "test_tool"
        assert error_context.context == {"error_context": "test"}
        assert error_context.stack_trace == "test_trace"
        
        # Verify patterns
        patterns = monitor.get_agent_patterns("test_agent")
        assert patterns is not None
        assert len(patterns.error_history) == 1
        assert patterns.error_history[0] == error_context
    
    def test_recovery_strategy(
        self,
        monitor: PatternMonitor
    ):
        """Test recovery strategy selection.
        
        Args:
            monitor (PatternMonitor): Monitor instance
        """
        # Test default strategy
        strategy = monitor.get_recovery_strategy("unknown_error", ErrorSeverity.LOW)
        assert strategy.max_retries == 2
        assert strategy.backoff_factor == 1.2
        assert strategy.timeout == 15.0
        assert strategy.requires_rollback is False
        
        # Test high severity strategy
        strategy = monitor.get_recovery_strategy("critical_error", ErrorSeverity.HIGH)
        assert strategy.max_retries == 4
        assert strategy.backoff_factor == 1.8
        assert strategy.timeout == 45.0
        assert strategy.requires_rollback is True
        
        # Test critical severity strategy
        strategy = monitor.get_recovery_strategy("critical_error", ErrorSeverity.CRITICAL)
        assert strategy.max_retries == 5
        assert strategy.backoff_factor == 2.0
        assert strategy.timeout == 60.0
        assert strategy.requires_rollback is True
    
    def test_track_interaction(
        self,
        monitor: PatternMonitor,
        sample_interaction_data: Dict[str, Any]
    ):
        """Test tracking agent interactions.
        
        Args:
            monitor (PatternMonitor): Monitor instance
            sample_interaction_data (Dict[str, Any]): Sample interaction data
        """
        # Track interaction
        metrics = monitor.track_interaction(**sample_interaction_data)
        
        # Get patterns
        patterns = monitor.get_agent_patterns(sample_interaction_data["agent_id"])
        assert patterns is not None
        assert len(patterns.interaction_history) == 1
        
        # Verify metrics
        assert metrics.interaction_type == sample_interaction_data["interaction_type"]
        assert metrics.success == sample_interaction_data["success"]
        assert metrics.token_usage == sample_interaction_data["token_usage"]
        assert metrics.context_size == sample_interaction_data["context_size"]
        assert metrics.compressed_size == sample_interaction_data["compressed_size"]
        
        # Verify patterns
        interaction_patterns = monitor.get_interaction_patterns()
        assert interaction_patterns[sample_interaction_data["interaction_type"]] == 1
    
    def test_track_decision(
        self,
        monitor: PatternMonitor,
        sample_decision_data: Dict[str, Any]
    ):
        """Test tracking agent decisions.
        
        Args:
            monitor (PatternMonitor): Monitor instance
            sample_decision_data (Dict[str, Any]): Sample decision data
        """
        # Track decision
        metrics = monitor.track_decision(**sample_decision_data)
        
        # Get patterns
        patterns = monitor.get_agent_patterns(sample_decision_data["agent_id"])
        assert patterns is not None
        assert len(patterns.decision_history) == 1
        
        # Verify metrics
        assert metrics.pattern == sample_decision_data["pattern"]
        assert metrics.branches == sample_decision_data["branches"]
        assert metrics.max_depth == sample_decision_data["max_depth"]
        assert metrics.success_rate == sample_decision_data["success_rate"]
        assert metrics.error_rate == sample_decision_data["error_rate"]
        assert metrics.optimization_score == sample_decision_data["optimization_score"]
        
        # Verify patterns
        decision_patterns = monitor.get_decision_patterns()
        assert decision_patterns[sample_decision_data["pattern"]] == 1
    
    def test_token_usage_tracking(
        self,
        monitor: PatternMonitor,
        sample_interaction_data: Dict[str, Any]
    ):
        """Test token usage pattern tracking.
        
        Args:
            monitor (PatternMonitor): Monitor instance
            sample_interaction_data (Dict[str, Any]): Sample interaction data
        """
        # Track interaction
        monitor.track_interaction(**sample_interaction_data)
        
        # Verify token usage patterns
        token_patterns = monitor.get_token_usage_patterns()
        assert token_patterns["input"][sample_interaction_data["interaction_type"].value] == 100
        assert token_patterns["output"][sample_interaction_data["interaction_type"].value] == 50
    
    def test_context_pattern_tracking(
        self,
        monitor: PatternMonitor,
        sample_interaction_data: Dict[str, Any]
    ):
        """Test context pattern tracking.
        
        Args:
            monitor (PatternMonitor): Monitor instance
            sample_interaction_data (Dict[str, Any]): Sample interaction data
        """
        # Track interaction
        monitor.track_interaction(**sample_interaction_data)
        
        # Verify context patterns
        context_patterns = monitor.get_context_patterns()
        assert context_patterns[sample_interaction_data["interaction_type"].value]["original"] == 1000
        assert context_patterns[sample_interaction_data["interaction_type"].value]["compressed"] == 500
    
    def test_pattern_analysis(
        self,
        monitor: PatternMonitor,
        sample_interaction_data: Dict[str, Any],
        sample_decision_data: Dict[str, Any]
    ):
        """Test pattern analysis.
        
        Args:
            monitor (PatternMonitor): Monitor instance
            sample_interaction_data (Dict[str, Any]): Sample interaction data
            sample_decision_data (Dict[str, Any]): Sample decision data
        """
        # Track interactions and decisions
        monitor.track_interaction(**sample_interaction_data)
        monitor.track_decision(**sample_decision_data)
        
        # Get analysis
        analysis = monitor.analyze_patterns()
        
        # Verify analysis
        assert analysis["interaction_patterns"]["total"] == 1
        assert analysis["decision_patterns"]["total"] == 1
        assert analysis["token_usage"]["total"] == 150  # 100 input + 50 output
        assert analysis["context_compression"]["compression_ratio"] == 0.5  # 500/1000
        assert analysis["error_analysis"]["total_errors"] == 0 