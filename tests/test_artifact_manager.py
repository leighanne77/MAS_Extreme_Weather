"""
Tests for the artifact manager.
"""

import pytest
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from src.multi_agent_system.artifact_manager import ArtifactManager

@pytest.fixture
async def artifact_manager(tmp_path):
    """Create an artifact manager instance."""
    manager = ArtifactManager(base_dir=str(tmp_path))
    yield manager
    # Cleanup
    if os.path.exists(manager.base_dir):
        for root, dirs, files in os.walk(manager.base_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

@pytest.mark.asyncio
async def test_store_and_retrieve_artifact(artifact_manager):
    """Test storing and retrieving an artifact."""
    # Store artifact
    session_id = "test_session"
    agent_id = "test_agent"
    artifact_type = "test_type"
    data = {"key": "value"}
    metadata = {"meta": "data"}
    
    artifact_path = await artifact_manager.store_artifact(
        session_id=session_id,
        agent_id=agent_id,
        artifact_type=artifact_type,
        data=data,
        metadata=metadata
    )
    
    # Verify artifact was stored
    assert os.path.exists(artifact_path)
    
    # Retrieve artifact
    artifact = await artifact_manager.get_artifact(artifact_path)
    
    # Verify artifact contents
    assert artifact["data"] == data
    assert artifact["metadata"] == metadata
    assert artifact["session_id"] == session_id
    assert artifact["agent_id"] == agent_id
    assert artifact["type"] == artifact_type
    assert "timestamp" in artifact

@pytest.mark.asyncio
async def test_list_artifacts(artifact_manager):
    """Test listing artifacts with filters."""
    # Store multiple artifacts
    session_id = "test_session"
    agent_ids = ["agent1", "agent2"]
    artifact_types = ["type1", "type2"]
    
    for agent_id in agent_ids:
        for artifact_type in artifact_types:
            await artifact_manager.store_artifact(
                session_id=session_id,
                agent_id=agent_id,
                artifact_type=artifact_type,
                data={"test": "data"}
            )
    
    # Test listing all artifacts
    all_artifacts = await artifact_manager.list_artifacts()
    assert len(all_artifacts) == 4
    
    # Test filtering by session
    session_artifacts = await artifact_manager.list_artifacts(session_id=session_id)
    assert len(session_artifacts) == 4
    
    # Test filtering by agent
    agent_artifacts = await artifact_manager.list_artifacts(agent_id="agent1")
    assert len(agent_artifacts) == 2
    
    # Test filtering by type
    type_artifacts = await artifact_manager.list_artifacts(artifact_type="type1")
    assert len(type_artifacts) == 2
    
    # Test combined filters
    filtered_artifacts = await artifact_manager.list_artifacts(
        session_id=session_id,
        agent_id="agent1",
        artifact_type="type1"
    )
    assert len(filtered_artifacts) == 1

@pytest.mark.asyncio
async def test_cleanup_session(artifact_manager):
    """Test cleaning up session artifacts."""
    # Store artifacts for multiple sessions
    sessions = ["session1", "session2"]
    for session_id in sessions:
        await artifact_manager.store_artifact(
            session_id=session_id,
            agent_id="test_agent",
            artifact_type="test_type",
            data={"test": "data"}
        )
    
    # Clean up one session
    await artifact_manager.cleanup_session("session1")
    
    # Verify cleanup
    session1_artifacts = await artifact_manager.list_artifacts(session_id="session1")
    assert len(session1_artifacts) == 0
    
    session2_artifacts = await artifact_manager.list_artifacts(session_id="session2")
    assert len(session2_artifacts) == 1

@pytest.mark.asyncio
async def test_cleanup_old_artifacts(artifact_manager):
    """Test cleaning up old artifacts."""
    # Store artifacts with different timestamps
    session_id = "test_session"
    agent_id = "test_agent"
    
    # Create an old artifact
    old_timestamp = (datetime.now() - timedelta(days=8)).strftime("%Y%m%d_%H%M%S")
    old_path = artifact_manager.base_dir / session_id / agent_id / f"test_{old_timestamp}.json"
    old_path.parent.mkdir(parents=True, exist_ok=True)
    with open(old_path, 'w') as f:
        json.dump({
            "data": {"test": "old"},
            "timestamp": old_timestamp
        }, f)
    
    # Create a new artifact
    await artifact_manager.store_artifact(
        session_id=session_id,
        agent_id=agent_id,
        artifact_type="test_type",
        data={"test": "new"}
    )
    
    # Clean up old artifacts
    await artifact_manager.cleanup_old_artifacts(max_age_days=7)
    
    # Verify cleanup
    artifacts = await artifact_manager.list_artifacts(session_id=session_id)
    assert len(artifacts) == 1
    assert "old" not in str(artifacts[0]["path"])

@pytest.mark.asyncio
async def test_get_artifact_stats(artifact_manager):
    """Test getting artifact statistics."""
    # Store artifacts for different agents and types
    session_id = "test_session"
    agents = ["agent1", "agent2"]
    types = ["type1", "type2"]
    
    for agent_id in agents:
        for artifact_type in types:
            await artifact_manager.store_artifact(
                session_id=session_id,
                agent_id=agent_id,
                artifact_type=artifact_type,
                data={"test": "data"}
            )
    
    # Get stats
    stats = await artifact_manager.get_artifact_stats(session_id)
    
    # Verify stats
    assert stats["total_artifacts"] == 4
    assert stats["total_size"] > 0
    assert len(stats["by_agent"]) == 2
    assert len(stats["by_type"]) == 2
    
    # Verify agent stats
    for agent_id in agents:
        assert agent_id in stats["by_agent"]
        assert stats["by_agent"][agent_id]["count"] == 2
        assert stats["by_agent"][agent_id]["size"] > 0
    
    # Verify type stats
    for artifact_type in types:
        assert artifact_type in stats["by_type"]
        assert stats["by_type"][artifact_type]["count"] == 2
        assert stats["by_type"][artifact_type]["size"] > 0 