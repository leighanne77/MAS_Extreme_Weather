"""
A2A Task Management System

Implements task lifecycle management for the A2A protocol, including
task creation, state tracking, and artifact management.
"""

import asyncio
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from .message import A2AMessage, A2AMessagePart, PartType

logger = logging.getLogger(__name__)

class TaskState(Enum):
    """A2A Task States following protocol specifications"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

@dataclass
class Task:
    """A2A Task following protocol specifications"""
    task_id: str
    description: str
    state: TaskState = TaskState.CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    result: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int | None = None
    priority: int = 1

    def __post_init__(self):
        """Post-initialization setup."""
        if isinstance(self.state, str):
            self.state = TaskState(self.state)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

    def update_state(self, state: TaskState, error: str | None = None):
        """Update task state with timestamp."""
        self.state = state
        self.updated_at = datetime.now(UTC)
        if error:
            self.error = error

    def add_artifact(self, artifact: dict[str, Any]):
        """Add artifact to task."""
        self.artifacts.append(artifact)
        self.updated_at = datetime.now(UTC)

    def set_result(self, result: dict[str, Any]):
        """Set task result and mark as completed."""
        self.result = result
        self.state = TaskState.COMPLETED
        self.updated_at = datetime.now(UTC)

    def is_expired(self) -> bool:
        """Check if task has expired based on timeout."""
        if not self.timeout_seconds:
            return False
        elapsed = (datetime.now(UTC) - self.created_at).total_seconds()
        return elapsed > self.timeout_seconds

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary following A2A protocol."""
        return {
            "id": self.task_id,
            "description": self.description,
            "status": {
                "state": self.state.value,
                "createdAt": self.created_at.isoformat(),
                "updatedAt": self.updated_at.isoformat()
            },
            "artifacts": self.artifacts,
            "error": self.error,
            "result": self.result,
            "metadata": self.metadata,
            "timeoutSeconds": self.timeout_seconds,
            "priority": self.priority,
            "kind": "task"
        }

    def to_a2a_message(self) -> A2AMessage:
        """Convert task to A2A message for communication."""
        data_part = A2AMessagePart(
            kind=PartType.DATA,
            data=self.to_dict()
        )

        return A2AMessage(
            role="system",
            parts=[data_part],
            message_id=str(uuid.uuid4())
        )

class TaskManager:
    """Manages A2A tasks with lifecycle tracking and cleanup."""

    def __init__(self, max_tasks: int = 1000, cleanup_interval_hours: int = 1):
        self.tasks: dict[str, Task] = {}
        self.max_tasks = max_tasks
        self.cleanup_interval_hours = cleanup_interval_hours
        self._cleanup_task: asyncio.Task | None = None
        self._task_handlers: dict[str, Callable] = {}

        logger.info("A2A Task Manager initialized")

    async def create_task(
        self,
        description: str,
        timeout_seconds: int | None = None,
        priority: int = 1,
        metadata: dict[str, Any] | None = None
    ) -> Task:
        """Create a new A2A task."""
        task_id = str(uuid.uuid4())

        # Check if we're at capacity
        if len(self.tasks) >= self.max_tasks:
            # Remove oldest completed/failed tasks
            await self._cleanup_old_tasks(force=True)

        task = Task(
            task_id=task_id,
            description=description,
            timeout_seconds=timeout_seconds,
            priority=priority,
            metadata=metadata or {}
        )

        self.tasks[task_id] = task
        logger.info(f"Created task: {task_id} - {description}")

        return task

    async def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        task = self.tasks.get(task_id)

        # Check if task has expired
        if task and task.is_expired():
            task.update_state(TaskState.TIMEOUT, "Task timed out")

        return task

    async def update_task_state(
        self,
        task_id: str,
        state: TaskState,
        error: str | None = None
    ) -> bool:
        """Update task state."""
        task = self.tasks.get(task_id)
        if task:
            task.update_state(state, error)
            logger.info(f"Updated task {task_id} to state: {state.value}")
            return True
        return False

    async def add_task_artifact(self, task_id: str, artifact: dict[str, Any]) -> bool:
        """Add artifact to task."""
        task = self.tasks.get(task_id)
        if task:
            task.add_artifact(artifact)
            return True
        return False

    async def set_task_result(self, task_id: str, result: dict[str, Any]) -> bool:
        """Set task result."""
        task = self.tasks.get(task_id)
        if task:
            task.set_result(result)
            return True
        return False

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        task = self.tasks.get(task_id)
        if task and task.state in [TaskState.CREATED, TaskState.RUNNING]:
            task.update_state(TaskState.CANCELLED)
            logger.info(f"Cancelled task: {task_id}")
            return True
        return False

    async def list_tasks(
        self,
        state_filter: TaskState | None = None,
        limit: int | None = None
    ) -> list[Task]:
        """List tasks with optional filtering."""
        tasks = list(self.tasks.values())

        # Apply state filter
        if state_filter:
            tasks = [task for task in tasks if task.state == state_filter]

        # Sort by priority and creation time
        tasks.sort(key=lambda t: (t.priority, t.created_at), reverse=True)

        # Apply limit
        if limit:
            tasks = tasks[:limit]

        return tasks

    async def get_task_stats(self) -> dict[str, Any]:
        """Get task statistics."""
        total_tasks = len(self.tasks)
        state_counts = {}

        for state in TaskState:
            state_counts[state.value] = len([
                task for task in self.tasks.values()
                if task.state == state
            ])

        return {
            "total_tasks": total_tasks,
            "state_counts": state_counts,
            "max_tasks": self.max_tasks,
            "available_slots": self.max_tasks - total_tasks
        }

    async def cleanup_old_tasks(self, max_age_hours: int = 24, force: bool = False):
        """Clean up old completed/failed/cancelled tasks."""
        cutoff_time = datetime.now(UTC).timestamp() - (max_age_hours * 3600)
        tasks_to_remove = []

        for task_id, task in self.tasks.items():
            if (task.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED, TaskState.TIMEOUT] and
                task.updated_at.timestamp() < cutoff_time):
                tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            logger.info(f"Cleaned up old task: {task_id}")

        return len(tasks_to_remove)

    async def _cleanup_old_tasks(self, force: bool = False):
        """Internal cleanup method."""
        await self.cleanup_old_tasks(force=force)

    async def start_cleanup_scheduler(self):
        """Start periodic cleanup of old tasks."""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.cleanup_interval_hours * 3600)
                    await self._cleanup_old_tasks()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in cleanup loop: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info("Started task cleanup scheduler")

    async def stop_cleanup_scheduler(self):
        """Stop the cleanup scheduler."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped task cleanup scheduler")

    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a handler for a specific task type."""
        self._task_handlers[task_type] = handler
        logger.info(f"Registered task handler for type: {task_type}")

    async def process_task(self, task: Task) -> bool:
        """Process a task using registered handlers."""
        try:
            # Update task state to running
            task.update_state(TaskState.RUNNING)

            # Get task type from metadata
            task_type = task.metadata.get("type", "default")
            handler = self._task_handlers.get(task_type)

            if not handler:
                task.update_state(TaskState.FAILED, f"No handler registered for task type: {task_type}")
                return False

            # Execute handler
            result = await handler(task)

            if result:
                task.set_result(result)
                return True
            else:
                task.update_state(TaskState.FAILED, "Task handler returned no result")
                return False

        except Exception as e:
            task.update_state(TaskState.FAILED, str(e))
            logger.error(f"Error processing task {task.task_id}: {e}")
            return False

    async def create_task_from_message(self, message: A2AMessage) -> Task:
        """Create a task from an A2A message."""
        # Extract task information from message parts
        description = ""
        metadata = {}

        for part in message.parts:
            if part.kind == PartType.TEXT:
                description = part.text or ""
            elif part.kind == PartType.DATA:
                data = part.data or {}
                description = data.get("description", description)
                metadata.update(data.get("metadata", {}))

        if not description:
            description = f"Task from message {message.message_id}"

        return await self.create_task(
            description=description,
            metadata=metadata
        )

    async def _execute_task(self, task: Task) -> Task:
        """Execute a task and update its state."""
        try:
            # Update task state to running
            task.state = TaskState.RUNNING
            task.updated_at = datetime.now(UTC)

            # Execute the task function if provided
            if task.function:
                result = await task.function(task.metadata)
                task.result = result
                task.state = TaskState.COMPLETED
            else:
                # No function provided, mark as completed
                task.state = TaskState.COMPLETED
                task.result = {"status": "completed", "message": "No execution function provided"}

            task.updated_at = datetime.now(UTC)
            return task

        except Exception as e:
            # Handle task execution errors
            task.state = TaskState.FAILED
            task.error = str(e)
            task.updated_at = datetime.now(UTC)
            logger.error(f"Task {task.task_id} failed: {e}")
            return task

# Global task manager instance
task_manager = TaskManager()
