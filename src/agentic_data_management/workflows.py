"""
Workflow Management Module

This module provides workflow management for data processing tasks.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import ConfigManager
from .integrations.google_cloud import GoogleCloudIntegration

logger = logging.getLogger(__name__)

class WorkflowStep:
    """Represents a single step in a workflow."""

    def __init__(
        self,
        name: str,
        action: str,
        parameters: dict[str, Any],
        next_step: str | None = None,
        error_step: str | None = None
    ):
        """Initialize workflow step.

        Args:
            name: Step name
            action: Action to perform
            parameters: Action parameters
            next_step: Next step name
            error_step: Error handling step name
        """
        self.name = name
        self.action = action
        self.parameters = parameters
        self.next_step = next_step
        self.error_step = error_step

class Workflow:
    """Represents a data processing workflow."""

    def __init__(
        self,
        name: str,
        description: str,
        steps: list[WorkflowStep],
        schedule: str | None = None
    ):
        """Initialize workflow.

        Args:
            name: Workflow name
            description: Workflow description
            steps: List of workflow steps
            schedule: Cron schedule expression
        """
        self.name = name
        self.description = description
        self.steps = steps
        self.schedule = schedule
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at

class WorkflowManager:
    """Manages data processing workflows."""

    def __init__(
        self,
        config: ConfigManager,
        google_cloud: GoogleCloudIntegration
    ):
        """Initialize workflow manager.

        Args:
            config: Configuration manager
            google_cloud: Google Cloud integration
        """
        self.config = config
        self.google_cloud = google_cloud
        self.workflow_dir = Path(config.get_system_config().workflow_dir)
        self.workflow_dir.mkdir(parents=True, exist_ok=True)

    def create_workflow(
        self,
        name: str,
        description: str,
        steps: list[dict[str, Any]],
        schedule: str | None = None
    ) -> Workflow:
        """Create a new workflow.

        Args:
            name: Workflow name
            description: Workflow description
            steps: List of step definitions
            schedule: Cron schedule expression

        Returns:
            Created workflow
        """
        # Convert step definitions to WorkflowStep objects
        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(
                name=step_def["name"],
                action=step_def["action"],
                parameters=step_def["parameters"],
                next_step=step_def.get("next_step"),
                error_step=step_def.get("error_step")
            )
            workflow_steps.append(step)

        # Create workflow
        workflow = Workflow(
            name=name,
            description=description,
            steps=workflow_steps,
            schedule=schedule
        )

        # Save workflow
        self._save_workflow(workflow)

        # Publish workflow creation event
        self.google_cloud.publish_event(
            "workflow_created",
            {
                "workflow_name": name,
                "description": description,
                "step_count": len(steps),
                "schedule": schedule
            }
        )

        return workflow

    def get_workflow(self, name: str) -> Workflow | None:
        """Get workflow by name.

        Args:
            name: Workflow name

        Returns:
            Workflow if found, None otherwise
        """
        workflow_path = self.workflow_dir / f"{name}.json"
        if not workflow_path.exists():
            return None

        with open(workflow_path) as f:
            data = json.load(f)

        # Convert step data to WorkflowStep objects
        steps = []
        for step_data in data["steps"]:
            step = WorkflowStep(
                name=step_data["name"],
                action=step_data["action"],
                parameters=step_data["parameters"],
                next_step=step_data.get("next_step"),
                error_step=step_data.get("error_step")
            )
            steps.append(step)

        return Workflow(
            name=data["name"],
            description=data["description"],
            steps=steps,
            schedule=data.get("schedule")
        )

    def list_workflows(self) -> list[Workflow]:
        """List all workflows.

        Returns:
            List of workflows
        """
        workflows = []
        for path in self.workflow_dir.glob("*.json"):
            workflow = self.get_workflow(path.stem)
            if workflow:
                workflows.append(workflow)
        return workflows

    def update_workflow(
        self,
        name: str,
        description: str | None = None,
        steps: list[dict[str, Any]] | None = None,
        schedule: str | None = None
    ) -> Workflow | None:
        """Update workflow.

        Args:
            name: Workflow name
            description: New description
            steps: New step definitions
            schedule: New schedule

        Returns:
            Updated workflow if found, None otherwise
        """
        workflow = self.get_workflow(name)
        if not workflow:
            return None

        if description:
            workflow.description = description

        if steps:
            workflow_steps = []
            for step_def in steps:
                step = WorkflowStep(
                    name=step_def["name"],
                    action=step_def["action"],
                    parameters=step_def["parameters"],
                    next_step=step_def.get("next_step"),
                    error_step=step_def.get("error_step")
                )
                workflow_steps.append(step)
            workflow.steps = workflow_steps

        if schedule:
            workflow.schedule = schedule

        workflow.updated_at = datetime.utcnow()

        # Save updated workflow
        self._save_workflow(workflow)

        # Publish workflow update event
        self.google_cloud.publish_event(
            "workflow_updated",
            {
                "workflow_name": name,
                "description": workflow.description,
                "step_count": len(workflow.steps),
                "schedule": workflow.schedule
            }
        )

        return workflow

    def delete_workflow(self, name: str) -> bool:
        """Delete workflow.

        Args:
            name: Workflow name

        Returns:
            True if deleted, False if not found
        """
        workflow_path = self.workflow_dir / f"{name}.json"
        if not workflow_path.exists():
            return False

        workflow_path.unlink()

        # Publish workflow deletion event
        self.google_cloud.publish_event(
            "workflow_deleted",
            {"workflow_name": name}
        )

        return True

    def _save_workflow(self, workflow: Workflow) -> None:
        """Save workflow to file.

        Args:
            workflow: Workflow to save
        """
        workflow_path = self.workflow_dir / f"{workflow.name}.json"

        # Convert workflow to dictionary
        data = {
            "name": workflow.name,
            "description": workflow.description,
            "steps": [
                {
                    "name": step.name,
                    "action": step.action,
                    "parameters": step.parameters,
                    "next_step": step.next_step,
                    "error_step": step.error_step
                }
                for step in workflow.steps
            ],
            "schedule": workflow.schedule,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat()
        }

        with open(workflow_path, 'w') as f:
            json.dump(data, f, indent=2)
