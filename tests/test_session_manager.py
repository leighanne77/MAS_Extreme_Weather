"""
Tests for session management functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from multi_tool_agent.session_manager import (
    SessionManager,
    AgentState,
    SessionState,
    STATE_KEYS
)

@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    session = Mock()
    session.state = {}
    return session

@pytest.fixture
def session_manager():
    """Create a session manager instance for testing."""
    return SessionManager()

def test_agent_state_initialization():
    """Test AgentState initialization."""
    state = AgentState()
    assert state.last_run is None
    assert state.last_result is None
    assert state.error_count == 0
    assert state.is_active is True
    assert state.metadata == {}
    assert state.retry_count == 0
    assert state.last_error is None
    assert state.concurrent_operations == 0

def test_session_state_initialization():
    """Test SessionState initialization."""
    state = SessionState()
    assert state.agents == {}
    assert state.shared_data == {}
    assert state.last_update is None
    assert state.is_active is True
    assert state.metadata == {}

def test_create_session(session_manager: SessionManager):
    """Test session creation."""
    session = session_manager.create_session()
    assert session is not None
    assert session.id is not None
    assert session.created_at is not None
    assert session.state == {}

def test_get_session(session_manager: SessionManager, mock_session):
    """Test session retrieval."""
    session_manager.sessions[mock_session.id] = mock_session
    retrieved = session_manager.get_session(mock_session.id)
    assert retrieved == mock_session

def test_update_session_state(session_manager: SessionManager, mock_session):
    """Test session state updates."""
    session_manager.sessions[mock_session.id] = mock_session
    new_state = {"key": "value"}
    session_manager.update_session_state(mock_session.id, new_state)
    assert mock_session.state == new_state

def test_get_agent_state(session_manager: SessionManager, mock_session):
    """Test agent state retrieval."""
    session_manager.sessions[mock_session.id] = mock_session
    mock_session.state[STATE_KEYS.AGENT_STATE] = {"agent1": {"status": "active"}}
    state = session_manager.get_agent_state(mock_session.id, "agent1")
    assert state == {"status": "active"}

def test_update_agent_state(session_manager: SessionManager, mock_session):
    """Test agent state updates."""
    session_manager.sessions[mock_session.id] = mock_session
    new_state = {"status": "active"}
    session_manager.update_agent_state(mock_session.id, "agent1", new_state)
    assert mock_session.state[STATE_KEYS.AGENT_STATE]["agent1"] == new_state

def test_get_context(session_manager: SessionManager, mock_session):
    """Test context retrieval."""
    session_manager.sessions[mock_session.id] = mock_session
    mock_session.state[STATE_KEYS.CONTEXT] = {"key": "value"}
    context = session_manager.get_context(mock_session.id)
    assert context == {"key": "value"}

def test_update_context(session_manager: SessionManager, mock_session):
    """Test context updates."""
    session_manager.sessions[mock_session.id] = mock_session
    new_context = {"key": "value"}
    session_manager.update_context(mock_session.id, new_context)
    assert mock_session.state[STATE_KEYS.CONTEXT] == new_context

def test_cleanup_old_sessions(session_manager: SessionManager):
    """Test cleanup of old sessions."""
    # Create old session
    old_session = session_manager.create_session()
    old_session.created_at = datetime.now() - timedelta(days=2)
    
    # Create new session
    new_session = session_manager.create_session()
    
    # Cleanup old sessions
    session_manager.cleanup_old_sessions(max_age_days=1)
    
    # Verify old session was removed
    assert old_session.id not in session_manager.sessions
    assert new_session.id in session_manager.sessions

@pytest.mark.asyncio
async def test_update_shared_data(session_manager):
    """Test updating shared data."""
    session_id = await session_manager.create_session()
    key = "test_key"
    value = {"test": "data"}
    
    # Update shared data
    await session_manager.update_shared_data(session_id, key, value)
    
    # Verify data was updated
    session = await session_manager.get_session(session_id)
    assert key in session.shared_data
    assert session.shared_data[key] == value

@pytest.mark.asyncio
async def test_cleanup_inactive_sessions(session_manager):
    """Test cleaning up inactive sessions."""
    # Create multiple sessions
    session_ids = []
    for _ in range(3):
        session_id = await session_manager.create_session()
        session_ids.append(session_id)
    
    # Mark one session as inactive
    session = await session_manager.get_session(session_ids[0])
    session.is_active = False
    
    # Clean up inactive sessions
    await session_manager.cleanup_inactive_sessions()
    
    # Verify inactive session was removed
    assert session_ids[0] not in session_manager.sessions
    assert session_ids[1] in session_manager.sessions
    assert session_ids[2] in session_manager.sessions 