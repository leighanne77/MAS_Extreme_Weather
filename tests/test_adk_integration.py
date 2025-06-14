"""
Tests for ADK Integration with our custom components.
"""

import pytest
import asyncio
from datetime import datetime
from multi_tool_agent.adk_integration import ADKAgentCoordinator

@pytest.fixture
async def coordinator():
    """Create a coordinator instance for testing."""
    return ADKAgentCoordinator()

@pytest.mark.asyncio
async def test_risk_analysis_workflow(coordinator):
    """Test the risk analysis workflow using ADK."""
    # Create a test request
    request = {
        "user_id": "test_user",
        "location": "New York",
        "type": "risk_analysis"
    }
    
    # Handle the request
    result = await coordinator.handle_request(request)
    
    # Verify the result
    assert result["status"] == "success"
    assert "session_id" in result
    assert "result" in result
    assert "timestamp" in result
    
    # Verify session state
    session_status = await coordinator.get_session_status(result["session_id"])
    assert "risk_analysis" in session_status
    assert "recommendations" in session_status

@pytest.mark.asyncio
async def test_agent_reset(coordinator):
    """Test resetting an agent."""
    # Create a test request
    request = {
        "user_id": "test_user",
        "location": "New York",
        "type": "risk_analysis"
    }
    
    # Handle the request
    result = await coordinator.handle_request(request)
    session_id = result["session_id"]
    
    # Reset the risk analyzer agent
    await coordinator.reset_agent(session_id, "RiskAnalyzer")
    
    # Verify the agent was reset
    session_status = await coordinator.get_session_status(session_id)
    assert session_status["agent_states"]["RiskAnalyzer"]["error_count"] == 0

@pytest.mark.asyncio
async def test_concurrent_requests(coordinator):
    """Test handling multiple concurrent requests."""
    # Create multiple test requests
    requests = [
        {
            "user_id": f"test_user_{i}",
            "location": "New York",
            "type": "risk_analysis"
        }
        for i in range(3)
    ]
    
    # Handle requests concurrently
    tasks = [
        coordinator.handle_request(request)
        for request in requests
    ]
    results = await asyncio.gather(*tasks)
    
    # Verify all requests were handled successfully
    for result in results:
        assert result["status"] == "success"
        assert "session_id" in result
        assert "result" in result 