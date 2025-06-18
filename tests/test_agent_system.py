"""
Test Agent System Module

This module contains tests for the agent system components.
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
import json
import shutil
from src.agentic_data_management.agents.base_agent import BaseAgent, AgentState
from src.agentic_data_management.agents.data_agent import DataAgent
from src.agentic_data_management.agents.quality_agent import DataQualityAgent
from src.agentic_data_management.agents.security_agent import SecurityAgent
from src.agentic_data_management.agents.lifecycle_agent import LifecycleAgent
from src.agentic_data_management.coordinator import AgentCoordinator, Workflow, WorkflowStep

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path

@pytest.fixture
async def coordinator(temp_dir):
    """Create a test coordinator instance."""
    coordinator = AgentCoordinator(
        workflow_dir=str(temp_dir / "workflows"),
        config={
            "data_agent": {"test_mode": True},
            "quality_agent": {"test_mode": True},
            "security_agent": {"test_mode": True},
            "lifecycle_agent": {"test_mode": True}
        }
    )
    yield coordinator
    # Cleanup
    if (temp_dir / "workflows").exists():
        shutil.rmtree(temp_dir / "workflows")

@pytest.mark.asyncio
async def test_data_agent(coordinator):
    """Test the data agent functionality."""
    agent = coordinator.agents["data"]
    
    # Test import
    result = await agent.execute({
        "operation": "import",
        "data": {"test": "data"},
        "source": "test_source"
    })
    
    assert result["status"] == "success"
    assert "imported_data" in result
    
    # Test export
    result = await agent.execute({
        "operation": "export",
        "data": {"test": "data"},
        "destination": "test_destination"
    })
    
    assert result["status"] == "success"
    assert "exported_data" in result

@pytest.mark.asyncio
async def test_quality_agent(coordinator):
    """Test the quality agent functionality."""
    agent = coordinator.agents["quality"]
    
    # Test quality check
    result = await agent.execute({
        "data": {"test": "data"},
        "data_source": "test_source",
        "rules": []
    })
    
    assert result["quality_report"] is not None
    assert result["validation_results"] is not None
    assert "quality_score" in result

@pytest.mark.asyncio
async def test_security_agent(coordinator):
    """Test the security agent functionality."""
    agent = coordinator.agents["security"]
    
    # Test authentication
    result = await agent.execute({
        "operation": "authenticate",
        "credentials": {
            "username": "test_user",
            "password": "test_pass"
        }
    })
    
    assert result["status"] == "success"
    assert "token" in result
    
    # Test authorization
    result = await agent.execute({
        "operation": "authorize",
        "token": "test_token",
        "resource": "test_resource",
        "action": "read"
    })
    
    assert result["status"] == "success"
    assert "authorized" in result

@pytest.mark.asyncio
async def test_lifecycle_agent(coordinator):
    """Test the lifecycle agent functionality."""
    agent = coordinator.agents["lifecycle"]
    
    # Test retention policy
    result = await agent.execute({
        "operation": "define_retention_policy",
        "policy_id": "test_policy",
        "policy": {
            "retention_period": "30d",
            "conditions": []
        }
    })
    
    assert result["status"] == "success"
    
    # Test versioning
    result = await agent.execute({
        "operation": "create_version",
        "data_id": "test_data",
        "version_data": {"test": "data"}
    })
    
    assert result["status"] == "success"
    assert "version" in result

@pytest.mark.asyncio
async def test_workflow_execution(coordinator):
    """Test workflow execution."""
    # Create a test workflow
    workflow = await coordinator.create_workflow(
        name="Test Workflow",
        description="Test workflow for data and quality operations",
        steps=[
            {
                "step_id": "data_import",
                "agent_id": "data",
                "operation": "import",
                "context": {
                    "data": {"test": "data"},
                    "source": "test_source"
                }
            },
            {
                "step_id": "quality_check",
                "agent_id": "quality",
                "operation": "check",
                "context": {
                    "data": {"test": "data"},
                    "data_source": "test_source"
                },
                "dependencies": ["data_import"]
            }
        ]
    )
    
    # Execute workflow
    result = await coordinator.execute_workflow(workflow.workflow_id)
    
    assert result["status"] == "completed"
    assert "results" in result
    assert "data_import" in result["results"]
    assert "quality_check" in result["results"]

@pytest.mark.asyncio
async def test_workflow_dependencies(coordinator):
    """Test workflow dependency handling."""
    # Create a workflow with dependencies
    workflow = await coordinator.create_workflow(
        name="Dependency Test",
        description="Test workflow with dependencies",
        steps=[
            {
                "step_id": "data_import",
                "agent_id": "data",
                "operation": "import",
                "context": {"data": {"test": "data"}}
            },
            {
                "step_id": "quality_check",
                "agent_id": "quality",
                "operation": "check",
                "context": {"data": {"test": "data"}},
                "dependencies": ["data_import"]
            },
            {
                "step_id": "security_check",
                "agent_id": "security",
                "operation": "authorize",
                "context": {"resource": "test_resource"},
                "dependencies": ["quality_check"]
            }
        ]
    )
    
    # Execute workflow
    result = await coordinator.execute_workflow(workflow.workflow_id)
    
    assert result["status"] == "completed"
    assert len(result["results"]) == 3
    assert all(step_id in result["results"] for step_id in ["data_import", "quality_check", "security_check"])

@pytest.mark.asyncio
async def test_workflow_error_handling(coordinator):
    """Test workflow error handling."""
    # Create a workflow with an invalid step
    workflow = await coordinator.create_workflow(
        name="Error Test",
        description="Test workflow error handling",
        steps=[
            {
                "step_id": "error_step",
                "agent_id": "data",
                "operation": "invalid_operation",
                "context": {}
            }
        ]
    )
    
    # Execute workflow and expect error
    with pytest.raises(Exception):
        await coordinator.execute_workflow(workflow.workflow_id)
    
    # Verify workflow status
    workflow = await coordinator.get_workflow(workflow.workflow_id)
    assert workflow.status == "failed"
    assert workflow.steps[0].status == "failed" 