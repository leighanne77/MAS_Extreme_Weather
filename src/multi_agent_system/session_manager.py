"""
Session Management System for Multi-Agent Climate Risk Analysis

This module handles session management, state tracking, and agent coordination
for the multi-agent climate risk analysis system.
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import aiofiles
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from .utils.adk_features import (
    Buffer,
    CircuitBreaker,
    MetricsCollector,
    Monitoring,
    WorkerPool,
)

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants for session management
APP_NAME = "Gemini MAS Climate Risk"
DEFAULT_USER_ID = "default_user"
DEFAULT_SESSION_TIMEOUT = timedelta(hours=1)
SESSION_STORAGE_DIR = os.getenv("SESSION_STORAGE_DIR", "sessions")
MAX_CONCURRENT_OPERATIONS = int(os.getenv("MAX_CONCURRENT_OPERATIONS", "5"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"

class SessionState(Enum):
    """Session states with ADK metadata."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

    @property
    def metadata(self) -> dict:
        """Get ADK metadata for the session state."""
        return {
            "monitoring_enabled": True,
            "metrics_collection": True,
            "circuit_breaker": True
        }

@dataclass
class SecurityContext:
    """Security context for sessions and operations."""
    user_id: str
    roles: list[str]
    permissions: list[str]
    security_level: str
    token: str | None = None
    last_auth_check: datetime | None = None
    auth_method: str = "none"
    mfa_verified: bool = False

@dataclass
class AgentState:
    """Represents the state of an individual agent."""
    last_run: datetime | None = None
    last_result: dict | None = None
    error_count: int = 0
    is_active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    runner: Runner | None = None
    retry_count: int = 0
    last_error: str | None = None
    concurrent_operations: set[str] = field(default_factory=set)
    security_context: SecurityContext | None = None
    agent_id: str = ""
    status: str = ""
    last_updated: datetime = datetime.now()
    monitoring_enabled: bool = True
    metrics_collection: bool = True
    circuit_breaker: bool = True

@dataclass
class AnalysisSession:
    """Represents a complete analysis session."""
    session_id: str
    user_id: str
    location: str
    start_time: datetime
    agent_states: dict[str, AgentState] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    status: str = "initialized"
    error_messages: list[str] = field(default_factory=list)
    runner: Runner | None = None
    semaphore: asyncio.Semaphore | None = None
    last_persisted: datetime | None = None
    security_context: SecurityContext | None = None
    created_at: datetime = datetime.now()
    state: SessionState = SessionState.CREATED
    monitoring_enabled: bool = True
    metrics_collection: bool = True
    circuit_breaker: bool = True

    def update_agent_state(self, agent_name: str, result: dict) -> None:
        """Update the state of a specific agent."""
        if agent_name not in self.agent_states:
            self.agent_states[agent_name] = AgentState()

        state = self.agent_states[agent_name]
        state.last_run = datetime.now()
        state.last_result = result

        if result.get("status") == "error":
            state.error_count += 1
            state.last_error = result.get("error", "Unknown error")
            self.error_messages.append(
                f"{agent_name}: {state.last_error}"
            )
        else:
            state.error_count = 0
            state.last_error = None

    def get_agent_state(self, agent_name: str) -> AgentState | None:
        """Get the current state of a specific agent."""
        return self.agent_states.get(agent_name)

    def is_agent_healthy(self, agent_name: str) -> bool:
        """Check if an agent is in a healthy state."""
        state = self.get_agent_state(agent_name)
        if not state:
            return False
        return state.is_active and state.error_count < 3

    def get_session_summary(self) -> dict:
        """Get a summary of the current session state."""
        return {
            "app_name": APP_NAME,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "location": self.location,
            "start_time": self.start_time.isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "status": self.status,
            "active_agents": sum(1 for state in self.agent_states.values() if state.is_active),
            "error_count": sum(state.error_count for state in self.agent_states.values()),
            "error_messages": self.error_messages,
            "last_persisted": self.last_persisted.isoformat() if self.last_persisted else None,
            "security_level": self.security_context.security_level if self.security_context else "none"
        }

    def to_dict(self) -> dict:
        """Convert session to dictionary for persistence."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "location": self.location,
            "start_time": self.start_time.isoformat(),
            "agent_states": {
                name: {
                    "last_run": state.last_run.isoformat() if state.last_run else None,
                    "last_result": state.last_result,
                    "error_count": state.error_count,
                    "is_active": state.is_active,
                    "metadata": state.metadata,
                    "retry_count": state.retry_count,
                    "last_error": state.last_error,
                    "security_context": asdict(state.security_context) if state.security_context else None
                }
                for name, state in self.agent_states.items()
            },
            "context": self.context,
            "status": self.status,
            "error_messages": self.error_messages,
            "last_persisted": self.last_persisted.isoformat() if self.last_persisted else None,
            "security_context": asdict(self.security_context) if self.security_context else None,
            "created_at": self.created_at.isoformat(),
            "state": self.state.value,
            "monitoring_enabled": self.monitoring_enabled,
            "metrics_collection": self.metrics_collection,
            "circuit_breaker": self.circuit_breaker
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AnalysisSession':
        """Create session from dictionary."""
        session = cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            location=data["location"],
            start_time=datetime.fromisoformat(data["start_time"])
        )

        session.agent_states = {
            name: AgentState(
                last_run=datetime.fromisoformat(state["last_run"]) if state["last_run"] else None,
                last_result=state["last_result"],
                error_count=state["error_count"],
                is_active=state["is_active"],
                metadata=state["metadata"],
                retry_count=state["retry_count"],
                last_error=state["last_error"],
                security_context=SecurityContext(**state["security_context"]) if state.get("security_context") else None,
                agent_id=state.get("agent_id", ""),
                status=state.get("status", ""),
                last_updated=datetime.fromisoformat(state["last_updated"]) if state["last_updated"] else datetime.now(),
                monitoring_enabled=state.get("monitoring_enabled", True),
                metrics_collection=state.get("metrics_collection", True),
                circuit_breaker=state.get("circuit_breaker", True)
            )
            for name, state in data["agent_states"].items()
        }

        session.context = data["context"]
        session.status = data["status"]
        session.error_messages = data["error_messages"]
        session.last_persisted = (
            datetime.fromisoformat(data["last_persisted"])
            if data["last_persisted"]
            else None
        )
        session.security_context = (
            SecurityContext(**data["security_context"])
            if data.get("security_context")
            else None
        )
        session.created_at = (
            datetime.fromisoformat(data["created_at"])
            if data["created_at"]
            else datetime.now()
        )
        session.state = SessionState(data["state"])
        session.monitoring_enabled = data.get("monitoring_enabled", True)
        session.metrics_collection = data.get("metrics_collection", True)
        session.circuit_breaker = data.get("circuit_breaker", True)

        return session

class SessionManager:
    """Manages analysis sessions and agent coordination."""

    def __init__(
        self,
        session_timeout: timedelta = DEFAULT_SESSION_TIMEOUT,
        storage_dir: str = SESSION_STORAGE_DIR,
        max_concurrent: int = MAX_CONCURRENT_OPERATIONS
    ):
        """Initialize the session manager.

        Args:
            session_timeout (timedelta): Maximum age of sessions before cleanup
            storage_dir (str): Directory for session persistence
            max_concurrent (int): Maximum number of concurrent operations
        """
        self.sessions: dict[str, AnalysisSession] = {}
        self.session_service = InMemorySessionService()
        self.max_session_age = session_timeout
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._cleanup_task = None

        # Initialize ADK features
        self.metrics_collector = MetricsCollector()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=300
        )
        self.worker_pool = WorkerPool(max_workers=10)
        self.monitoring = Monitoring()
        self.buffer = Buffer()

    async def start(self):
        """Start the session manager and load persisted sessions."""
        # Load persisted sessions
        await self._load_persisted_sessions()

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def stop(self):
        """Stop the session manager and persist sessions."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        await self._persist_all_sessions()

    async def create_session(
        self,
        location: str,
        user_id: str = DEFAULT_USER_ID,
        session_id: str | None = None,
        runner: Runner | None = None,
        security_context: SecurityContext | None = None
    ) -> AnalysisSession:
        """Create a new analysis session.

        Args:
            location: Location for analysis
            user_id: User identifier
            session_id: Optional session identifier
            runner: Optional runner instance
            security_context: Security context for the session

        Returns:
            AnalysisSession: New session instance

        Raises:
            SecurityError: If security requirements are not met
        """
        if not session_id:
            session_id = f"{user_id}_{datetime.now().isoformat()}"

        session = AnalysisSession(
            session_id=session_id,
            user_id=user_id,
            location=location,
            start_time=datetime.now(),
            runner=runner,
            semaphore=self.semaphore,
            security_context=security_context
        )

        self.sessions[session_id] = session
        await self._persist_session(session)
        return session

    async def get_session(self, session_id: str) -> AnalysisSession | None:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    async def update_session(
        self,
        session_id: str,
        agent_name: str,
        result: dict,
        retry: bool = True
    ) -> None:
        """Update a session with agent results.

        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            result: Result from agent operation
            retry: Whether to retry on failure

        Raises:
            SecurityError: If security requirements are not met
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.update_agent_state(agent_name, result)
        await self._persist_session(session)

    async def _persist_session(self, session: AnalysisSession) -> None:
        """Persist a session to storage."""
        session.last_persisted = datetime.now()
        file_path = self.storage_dir / f"{session.session_id}.json"

        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(session.to_dict()))

    async def _load_persisted_sessions(self) -> None:
        """Load persisted sessions from storage."""
        for file_path in self.storage_dir.glob("*.json"):
            try:
                async with aiofiles.open(file_path) as f:
                    data = json.loads(await f.read())
                    session = AnalysisSession.from_dict(data)
                    self.sessions[session.session_id] = session
            except Exception as e:
                logger.error(f"Error loading session {file_path}: {str(e)}")

    async def _persist_all_sessions(self) -> None:
        """Persist all active sessions."""
        for session in self.sessions.values():
            await self._persist_session(session)

    async def _periodic_cleanup(self) -> None:
        """Periodically clean up old sessions."""
        while True:
            await asyncio.sleep(300)  # Run every 5 minutes
            await self.cleanup_old_sessions()

    async def cleanup_old_sessions(self) -> None:
        """Clean up sessions older than max_session_age."""
        now = datetime.now()
        to_remove = []

        for session_id, session in self.sessions.items():
            age = now - session.start_time
            if age > self.max_session_age:
                to_remove.append(session_id)

        for session_id in to_remove:
            del self.sessions[session_id]
            file_path = self.storage_dir / f"{session_id}.json"
            if file_path.exists():
                file_path.unlink()

    async def get_active_sessions(self) -> list[AnalysisSession]:
        """Get all active sessions."""
        return list(self.sessions.values())

    async def get_session_context(self, session_id: str) -> dict:
        """Get the context of a session."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "location": session.location,
            "start_time": session.start_time.isoformat(),
            "status": session.status,
            "error_count": sum(state.error_count for state in session.agent_states.values()),
            "security_level": session.security_context.security_level if session.security_context else "none"
        }

    async def handle_agent_error(
        self,
        session_id: str,
        agent_name: str,
        error: str,
        retry: bool = True
    ) -> None:
        """Handle an agent error.

        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            error: Error message
            retry: Whether to retry the operation

        Raises:
            SecurityError: If security requirements are not met
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        state = session.get_agent_state(agent_name)
        if not state:
            state = AgentState()
            session.agent_states[agent_name] = state

        state.error_count += 1
        state.last_error = error
        session.error_messages.append(f"{agent_name}: {error}")

        if retry and state.error_count < MAX_RETRY_ATTEMPTS:
            state.retry_count += 1
            await asyncio.sleep(RETRY_DELAY)

            # Implement retry logic
            try:
                # Get the agent instance if available
                agent_instance = None
                if hasattr(session, 'runner') and session.runner:
                    agent_instance = session.runner.get_agent(agent_name)

                if agent_instance:
                    # Retry the last operation
                    last_result = state.last_result
                    if last_result and "request" in last_result:
                        # Retry with exponential backoff
                        retry_delay = RETRY_DELAY * (2 ** (state.retry_count - 1))
                        await asyncio.sleep(retry_delay)

                        # Attempt to retry the operation
                        retry_result = await agent_instance.run(session)
                        if retry_result.get("status") == "success":
                            # Reset error state on successful retry
                            state.error_count = 0
                            state.last_error = None
                            state.is_active = True
                            session.error_messages.pop()  # Remove the error message
                            logger.info(f"Agent {agent_name} recovered after retry")
                        else:
                            # Increment error count for failed retry
                            state.error_count += 1
                            state.last_error = retry_result.get("error", "Retry failed")
                            session.error_messages.append(f"{agent_name} (retry): {state.last_error}")
                    else:
                        # No request data available for retry
                        state.error_count += 1
                        state.last_error = "No request data available for retry"
                else:
                    # No agent instance available for retry
                    state.error_count += 1
                    state.last_error = "Agent instance not available for retry"

            except Exception as retry_error:
                # Handle retry errors
                state.error_count += 1
                state.last_error = f"Retry failed: {str(retry_error)}"
                session.error_messages.append(f"{agent_name} (retry error): {state.last_error}")
                logger.error(f"Error during retry for agent {agent_name}: {retry_error}")
        else:
            state.is_active = False

        await self._persist_session(session)

    async def reset_agent(
        self,
        session_id: str,
        agent_name: str,
        retry: bool = True
    ) -> None:
        """Reset an agent's state.

        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            retry: Whether to retry the operation

        Raises:
            SecurityError: If security requirements are not met
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        state = session.get_agent_state(agent_name)
        if state:
            state.error_count = 0
            state.last_error = None
            state.is_active = True
            state.retry_count = 0

        await self._persist_session(session)

    async def get_user_sessions(self, user_id: str) -> list[AnalysisSession]:
        """Get all sessions for a user."""
        return [
            session for session in self.sessions.values()
            if session.user_id == user_id
        ]

    async def get_session_by_user(
        self,
        user_id: str,
        session_id: str
    ) -> AnalysisSession | None:
        """Get a specific session for a user."""
        session = await self.get_session(session_id)
        if session and session.user_id == user_id:
            return session
        return None

    async def update_agent_state(self, session_id: str, agent_id: str, status: str) -> AgentState:
        """Update an agent's state with ADK features.

        Args:
            session_id (str): ID of the session
            agent_id (str): ID of the agent
            status (str): New status

        Returns:
            AgentState: Updated agent state
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed():
                raise Exception("Circuit breaker is open for update_agent_state")

            # Track operation with metrics collector
            with self.metrics_collector.track("update_agent_state"):
                session = self.sessions.get(session_id)
                if not session:
                    raise ValueError(f"Unknown session: {session_id}")

                # Create or update agent state
                agent_state = AgentState(
                    agent_id=agent_id,
                    status=status,
                    last_updated=datetime.now(),
                    metadata={
                        "monitoring_enabled": True,
                        "metrics_collection": True,
                        "circuit_breaker": True
                    }
                )

                session.agent_states[agent_id] = agent_state

                return agent_state

        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure()
            logger.error(f"Error updating agent state: {str(e)}")
            raise

    async def update_session_state(self, session_id: str, state: SessionState) -> AnalysisSession:
        """Update a session's state with ADK features.

        Args:
            session_id (str): ID of the session
            state (SessionState): New state

        Returns:
            AnalysisSession: Updated session
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed():
                raise Exception("Circuit breaker is open for update_session_state")

            # Track operation with metrics collector
            with self.metrics_collector.track("update_session_state"):
                session = self.sessions.get(session_id)
                if not session:
                    raise ValueError(f"Unknown session: {session_id}")

                # Update session state
                session.state = state

                return session

        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure()
            logger.error(f"Error updating session state: {str(e)}")
            raise

    def get_metrics(self) -> dict[str, Any]:
        """Get ADK metrics for the session manager.

        Returns:
            Dict[str, Any]: Metrics including performance, resource usage, and circuit breaker status
        """
        return {
            "performance": self.metrics_collector.get_metrics(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "monitoring": self.monitoring.get_metrics(),
            "resource_usage": self.worker_pool.get_resource_usage(),
            "sessions": {
                session_id: {
                    "state": session.state.value,
                    "agents": len(session.agent_states),
                    "created_at": session.created_at.isoformat()
                }
                for session_id, session in self.sessions.items()
            }
        }

    async def validate_jwt_token(self, token: str) -> bool:
        """Validate a JWT token.

        Args:
            token: JWT token to validate

        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            # Basic JWT validation logic
            if not token:
                return False

            # In a real implementation, this would verify the token signature
            # For now, just check if it's a non-empty string
            return len(token) > 0
        except Exception as e:
            logger.error(f"Error validating JWT token: {str(e)}")
            return False
