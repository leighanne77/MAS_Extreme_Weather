"""
Tests for agent tools functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from src.multi_agent_system.agent_tools import (
    get_cached_result,
    update_cache,
    handle_tool_error,
    execute_with_concurrency_limit,
    CACHE_DURATIONS,
    STATE_KEYS
)
from src.multi_agent_system.session_manager import AgentState

def mock_tool_context():
    """Create a mock context for function-based tools for testing."""
    return type('MockContext', (), {'state': {}})()

def test_get_cached_result(mock_tool_context):
    """Test getting cached results."""
    # Test with no cache
    assert get_cached_result(mock_tool_context, "test_key", 3600) is None
    
    # Test with expired cache
    mock_tool_context.state["test_key"] = {
        "timestamp": (datetime.now().timestamp() - 7200),
        "result": {"test": "data"}
    }
    assert get_cached_result(mock_tool_context, "test_key", 3600) is None
    
    # Test with valid cache
    mock_tool_context.state["test_key"] = {
        "timestamp": datetime.now().isoformat(),
        "result": {"test": "data"}
    }
    result = get_cached_result(mock_tool_context, "test_key", 3600)
    assert result == {"test": "data"}

def test_update_cache(mock_tool_context):
    """Test updating cache."""
    test_data = {"test": "data"}
    update_cache(mock_tool_context, "test_key", test_data)
    
    assert "test_key" in mock_tool_context.state
    assert "timestamp" in mock_tool_context.state["test_key"]
    assert mock_tool_context.state["test_key"]["result"] == test_data

@pytest.mark.asyncio
async def test_handle_tool_error(mock_tool_context):
    """Test handling tool errors."""
    error = "Test error"
    agent_name = "test_agent"
    
    result = await handle_tool_error(mock_tool_context, error, agent_name)
    
    assert result["status"] == "error"
    assert result["error"] == error
    assert result["agent"] == agent_name
    assert "timestamp" in result
    
    # Verify agent state was updated
    agent_state = mock_tool_context.state[STATE_KEYS["agent_state"]][agent_name]
    assert isinstance(agent_state, AgentState)
    assert agent_state.error_count == 1
    assert agent_state.last_error == error

@pytest.mark.asyncio
async def test_execute_with_concurrency_limit(mock_tool_context):
    """Test executing with concurrency limits."""
    async def test_func(*args, **kwargs):
        return {"status": "success"}
    
    # Test successful execution
    result = await execute_with_concurrency_limit(
        mock_tool_context,
        test_func,
        "test_agent"
    )
    assert result["status"] == "success"
    
    # Test error handling
    async def error_func(*args, **kwargs):
        raise Exception("Test error")
    
    result = await execute_with_concurrency_limit(
        mock_tool_context,
        error_func,
        "test_agent"
    )
    assert result["status"] == "error"
    assert "Test error" in result["error"]

@pytest.mark.asyncio
async def test_concurrency_limit(mock_tool_context):
    """Test concurrency limit enforcement."""
    mock_tool_context.state["max_concurrent"] = 2
    mock_tool_context.state[STATE_KEYS["concurrent_ops"]] = {"op1", "op2"}
    
    async def test_func(*args, **kwargs):
        return {"status": "success"}
    
    result = await execute_with_concurrency_limit(
        mock_tool_context,
        test_func,
        "test_agent"
    )
    assert result["status"] == "error"
    assert "Concurrency limit reached" in result["error"]

def say_hello(name: str) -> str:
    return f"Hello, {name}!"

def test_function_tool_wrapping():
    from google.adk.agents import Agent
    agent = Agent(
        model="gemini-2.0-flash",
        name="test_agent",
        instruction="Use the provided tools to greet users.",
        tools=[say_hello]
    )
    result = agent.tools[0]("World")
    assert result == "Hello, World!" 