"""
Tests for communication mechanisms.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from src.multi_agent_system.communication import (
    SharedState,
    AgentTransfer,
    ExplicitInvocation,
    CommunicationManager
)
from src.multi_agent_system.session_manager import AnalysisSession, AgentState
from src.multi_agent_system.agent_team import Agent

@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    session = Mock(spec=AnalysisSession)
    session.context = {}
    session.agent_states = {}
    session.agents = {}
    return session

@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock(spec=Agent)
    async def async_run(*args, **kwargs):
        return {"result": "test"}
    agent.run = async_run
    return agent

def test_shared_state_updates():
    """Test SharedState update methods."""
    state = SharedState(
        session_state={},
        agent_states={},
        context={}
    )
    
    # Test session state updates
    state.update_session_state({"key": "value"})
    assert state.session_state["key"] == "value"
    
    # Test agent state updates
    agent_state = AgentState(
        last_run=datetime.now(),
        last_result={"foo": "bar"},
        error_count=0,
        is_active=True,
        metadata={},
        retry_count=0,
        last_error=None
    )
    state.update_agent_state("test_agent", agent_state)
    assert state.get_agent_state("test_agent") == agent_state
    
    # Test context updates
    state.update_context({"context_key": "context_value"})
    assert state.context["context_key"] == "context_value"

@pytest.mark.asyncio
async def test_agent_transfer(mock_session, mock_agent):
    """Test AgentTransfer execution."""
    mock_session.agents["target_agent"] = mock_agent
    
    transfer = AgentTransfer(
        source_agent="source_agent",
        target_agent="target_agent",
        context={"transfer_key": "transfer_value"}
    )
    
    result = await transfer.execute(mock_session, mock_session.agents)
    
    assert result["status"] == "success"
    assert result["source"] == "source_agent"
    assert result["target"] == "target_agent"
    assert result["result"] == {"result": "test"}
    assert mock_session.context["transfer_key"] == "transfer_value"

@pytest.mark.asyncio
async def test_agent_transfer_error(mock_session):
    """Test AgentTransfer error handling."""
    transfer = AgentTransfer(
        source_agent="source_agent",
        target_agent="nonexistent_agent",
        context={}
    )
    with pytest.raises(ValueError, match="Target agent nonexistent_agent not found"):
        await transfer.execute(mock_session, mock_session.agents)

@pytest.mark.asyncio
async def test_explicit_invocation(mock_session, mock_agent):
    """Test ExplicitInvocation execution."""
    mock_session.agents["test_agent"] = mock_agent
    
    invocation = ExplicitInvocation(
        agent_name="test_agent",
        request={"request_key": "request_value"},
        context={"invocation_key": "invocation_value"}
    )
    
    result = await invocation.execute(mock_session, mock_session.agents)
    
    assert result["status"] == "success"
    assert result["agent"] == "test_agent"
    assert result["result"] == {"result": "test"}
    assert mock_session.context["invocation_key"] == "invocation_value"

@pytest.mark.asyncio
async def test_explicit_invocation_timeout(mock_session, mock_agent):
    """Test ExplicitInvocation timeout handling."""
    async def slow_run(*args, **kwargs):
        await asyncio.sleep(2)
        return {"result": "test"}
    
    mock_agent.run = slow_run
    mock_session.agents["test_agent"] = mock_agent
    
    invocation = ExplicitInvocation(
        agent_name="test_agent",
        request={},
        context={},
        timeout=1
    )
    
    result = await invocation.execute(mock_session, mock_session.agents)
    
    assert result["status"] == "error"
    assert "Invocation timed out after 1 seconds" in result["error"]

@pytest.mark.asyncio
async def test_communication_manager(mock_session, mock_agent):
    """Test CommunicationManager methods."""
    mock_session.agents["test_agent"] = mock_agent
    
    manager = CommunicationManager(mock_session)
    
    # Test state updates
    manager.update_shared_state({"manager_key": "manager_value"})
    assert manager.shared_state.session_state["manager_key"] == "manager_value"
    
    # Test agent transfer
    transfer_result = await manager.transfer_control(
        "source_agent",
        "test_agent",
        {"transfer_key": "transfer_value"}
    )
    assert transfer_result["status"] == "success"
    
    # Test explicit invocation
    invocation_result = await manager.invoke_agent(
        "test_agent",
        {"request_key": "request_value"},
        {"invocation_key": "invocation_value"}
    )
    assert invocation_result["status"] == "success" 