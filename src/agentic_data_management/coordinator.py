"""
Agent Coordinator Module

This module provides coordination and orchestration of data management agents.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel, Field

from .agents.base_agent import BaseAgent
from .agents.data_agent import DataAgent
from .agents.lifecycle_agent import LifecycleAgent
from .agents.quality_agent import DataQualityAgent
from .agents.security_agent import SecurityAgent


class WorkflowStep(BaseModel):
    """Represents a step in a data management workflow."""
    step_id: str
    agent_id: str
    operation: str
    context: dict[str, Any]
    dependencies: list[str] = []
    status: str = "pending"
    result: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None

class Workflow(BaseModel):
    """Represents a complete data management workflow."""
    workflow_id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    metadata: dict[str, Any] = {}

class AgentCoordinator:
    """Coordinates and orchestrates data management agents."""

    def __init__(
        self,
        workflow_dir: str = "workflows",
        config: dict[str, Any] | None = None
    ):
        """Initialize the agent coordinator.

        Args:
            workflow_dir: Directory for storing workflow definitions
            config: Optional configuration dictionary
        """
        self.workflow_dir = Path(workflow_dir)
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or {}
        self.logger = logging.getLogger("agent_coordinator")

        # Initialize agents
        self.agents: dict[str, BaseAgent] = {}
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize the available agents."""
        # Data agent
        self.agents["data"] = DataAgent(
            agent_id="data_agent",
            config=self.config.get("data_agent", {})
        )

        # Quality agent
        self.agents["quality"] = DataQualityAgent(
            agent_id="quality_agent",
            config=self.config.get("quality_agent", {})
        )

        # Security agent
        self.agents["security"] = SecurityAgent(
            agent_id="security_agent",
            config=self.config.get("security_agent", {})
        )

        # Lifecycle agent
        self.agents["lifecycle"] = LifecycleAgent(
            agent_id="lifecycle_agent",
            config=self.config.get("lifecycle_agent", {})
        )

    async def create_workflow(
        self,
        name: str,
        description: str,
        steps: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None
    ) -> Workflow:
        """Create a new workflow.

        Args:
            name: Workflow name
            description: Workflow description
            steps: List of workflow steps
            metadata: Optional workflow metadata

        Returns:
            Created workflow
        """
        workflow = Workflow(
            workflow_id=f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=name,
            description=description,
            steps=[WorkflowStep(**step) for step in steps],
            metadata=metadata or {}
        )

        # Save workflow definition
        workflow_path = self.workflow_dir / f"{workflow.workflow_id}.json"
        async with aiofiles.open(workflow_path, 'w') as f:
            await f.write(workflow.json(indent=2))

        return workflow

    async def execute_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Execute a workflow.

        Args:
            workflow_id: ID of the workflow to execute

        Returns:
            Workflow execution results
        """
        # Load workflow
        workflow_path = self.workflow_dir / f"{workflow_id}.json"
        if not workflow_path.exists():
            raise ValueError(f"Workflow not found: {workflow_id}")

        async with aiofiles.open(workflow_path) as f:
            workflow_data = json.loads(await f.read())
            workflow = Workflow(**workflow_data)

        # Update workflow status
        workflow.status = "running"
        await self._save_workflow(workflow)

        try:
            # Execute steps in dependency order
            results = {}
            for step in workflow.steps:
                if step.status == "pending":
                    # Check dependencies
                    if not all(
                        workflow.steps[i].status == "completed"
                        for i in step.dependencies
                    ):
                        continue

                    # Execute step
                    step.status = "running"
                    await self._save_workflow(workflow)

                    try:
                        agent = self.agents.get(step.agent_id)
                        if not agent:
                            raise ValueError(f"Agent not found: {step.agent_id}")

                        result = await agent.execute(step.context)
                        step.result = result
                        step.status = "completed"
                        step.completed_at = datetime.now()
                        results[step.step_id] = result

                    except Exception as e:
                        step.status = "failed"
                        step.result = {"error": str(e)}
                        self.logger.error(f"Step {step.step_id} failed: {str(e)}")
                        raise

                    await self._save_workflow(workflow)

            # Update workflow status
            workflow.status = "completed"
            workflow.completed_at = datetime.now()
            await self._save_workflow(workflow)

            return {
                "workflow_id": workflow.workflow_id,
                "status": "completed",
                "results": results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception:
            workflow.status = "failed"
            await self._save_workflow(workflow)
            raise

    async def _save_workflow(self, workflow: Workflow) -> None:
        """Save workflow state.

        Args:
            workflow: Workflow to save
        """
        workflow_path = self.workflow_dir / f"{workflow.workflow_id}.json"
        async with aiofiles.open(workflow_path, 'w') as f:
            await f.write(workflow.json(indent=2))

    async def get_workflow(self, workflow_id: str) -> Workflow:
        """Get workflow definition.

        Args:
            workflow_id: ID of the workflow to get

        Returns:
            Workflow definition
        """
        workflow_path = self.workflow_dir / f"{workflow_id}.json"
        if not workflow_path.exists():
            raise ValueError(f"Workflow not found: {workflow_id}")

        async with aiofiles.open(workflow_path) as f:
            workflow_data = json.loads(await f.read())
            return Workflow(**workflow_data)

    async def list_workflows(self) -> list[dict[str, Any]]:
        """List all available workflows.

        Returns:
            List of workflow definitions
        """
        workflows = []
        for workflow_path in self.workflow_dir.glob("workflow_*.json"):
            async with aiofiles.open(workflow_path) as f:
                workflow_data = json.loads(await f.read())
                workflows.append(workflow_data)
        return workflows
