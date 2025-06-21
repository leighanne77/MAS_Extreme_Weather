"""
A2A Task Manager

Manages A2A-compliant agent tasks, assignments, and tracking.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class A2ATask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    created_by: str = ""
    assigned_to: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['status'] = self.status.value
        d['priority'] = self.priority.value
        d['created_at'] = self.created_at.isoformat()
        d['updated_at'] = self.updated_at.isoformat()
        d['due_at'] = self.due_at.isoformat() if self.due_at else None
        d['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2ATask':
        data = dict(data)
        data['status'] = TaskStatus(data['status'])
        data['priority'] = TaskPriority(data['priority'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('due_at'):
            data['due_at'] = datetime.fromisoformat(data['due_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)

class A2ATaskManager:
    def __init__(self):
        self.tasks: Dict[str, A2ATask] = {}

    def create_task(self, title: str, description: str, created_by: str, assigned_to: Optional[List[str]] = None, priority: TaskPriority = TaskPriority.NORMAL, due_at: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None) -> A2ATask:
        task = A2ATask(
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=assigned_to or [],
            priority=priority,
            due_at=due_at,
            metadata=metadata or {}
        )
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Optional[A2ATask]:
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, **updates) -> Optional[A2ATask]:
        task = self.tasks.get(task_id)
        if not task:
            return None
        for k, v in updates.items():
            if hasattr(task, k):
                setattr(task, k, v)
        task.updated_at = datetime.utcnow()
        return task

    def complete_task(self, task_id: str, result: Any = None) -> Optional[A2ATask]:
        task = self.tasks.get(task_id)
        if not task:
            return None
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = result
        task.updated_at = datetime.utcnow()
        return task

    def list_tasks(self, status: Optional[TaskStatus] = None, assigned_to: Optional[str] = None) -> List[A2ATask]:
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        if assigned_to:
            tasks = [t for t in tasks if assigned_to in t.assigned_to]
        return tasks

# Global instance
task_manager = A2ATaskManager() 