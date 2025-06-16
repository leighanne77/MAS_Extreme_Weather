"""
Session Management System for Multi-Agent Climate Risk Analysis

This module handles session management, state tracking, and agent coordination
for the multi-agent climate risk analysis system.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import aiofiles
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

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

@dataclass
class AgentState:
    """Represents the state of an individual agent."""
    last_run: Optional[datetime] = None
    last_result: Optional[Dict] = None
    error_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    runner: Optional[Runner] = None
    retry_count: int = 0
    last_error: Optional[str] = None
    concurrent_operations: Set[str] = field(default_factory=set)

@dataclass
class AnalysisSession:
    """Represents a complete analysis session."""
    session_id: str
    user_id: str
    location: str
    start_time: datetime
    agent_states: Dict[str, AgentState] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "initialized"
    error_messages: List[str] = field(default_factory=list)
    runner: Optional[Runner] = None
    semaphore: Optional[asyncio.Semaphore] = None
    last_persisted: Optional[datetime] = None
    
    def update_agent_state(self, agent_name: str, result: Dict) -> None:
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
            
    def get_agent_state(self, agent_name: str) -> Optional[AgentState]:
        """Get the current state of a specific agent."""
        return self.agent_states.get(agent_name)
        
    def is_agent_healthy(self, agent_name: str) -> bool:
        """Check if an agent is in a healthy state."""
        state = self.get_agent_state(agent_name)
        if not state:
            return False
        return state.is_active and state.error_count < 3
        
    def get_session_summary(self) -> Dict:
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
            "last_persisted": self.last_persisted.isoformat() if self.last_persisted else None
        }
        
    def to_dict(self) -> Dict:
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
                    "last_error": state.last_error
                }
                for name, state in self.agent_states.items()
            },
            "context": self.context,
            "status": self.status,
            "error_messages": self.error_messages,
            "last_persisted": self.last_persisted.isoformat() if self.last_persisted else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisSession':
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
                last_error=state["last_error"]
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
        self.sessions: Dict[str, AnalysisSession] = {}
        self.session_service = InMemorySessionService()
        self.max_session_age = session_timeout
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._cleanup_task = None
        
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
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        # Persist all sessions
        await self._persist_all_sessions()
        
    async def create_session(
        self,
        location: str,
        user_id: str = DEFAULT_USER_ID,
        session_id: Optional[str] = None,
        runner: Optional[Runner] = None
    ) -> AnalysisSession:
        """Create a new analysis session.
        
        Args:
            location (str): Location to analyze
            user_id (str): User identifier
            session_id (Optional[str]): Custom session ID
            runner (Optional[Runner]): Runner instance for agent orchestration
            
        Returns:
            AnalysisSession: New session instance
        """
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        # Create session in the session service
        await self.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create our session object
        session = AnalysisSession(
            session_id=session_id,
            user_id=user_id,
            location=location,
            start_time=datetime.now(),
            runner=runner,
            semaphore=self.semaphore
        )
        
        self.sessions[session_id] = session
        await self._persist_session(session)
        return session
        
    async def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Get an existing session by ID."""
        return self.sessions.get(session_id)
        
    async def update_session(
        self,
        session_id: str,
        agent_name: str,
        result: Dict,
        retry: bool = True
    ) -> None:
        """Update a session with new agent results.
        
        Args:
            session_id (str): Session identifier
            agent_name (str): Name of the agent
            result (Dict): Result to update
            retry (bool): Whether to retry on failure
        """
        session = await self.get_session(session_id)
        if not session:
            return
            
        async with session.semaphore:
            try:
                session.update_agent_state(agent_name, result)
                
                # Update session service with new context
                await self.session_service.update_session(
                    app_name=APP_NAME,
                    user_id=session.user_id,
                    session_id=session_id,
                    context={
                        "agent_states": {
                            name: {
                                "last_run": state.last_run.isoformat() if state.last_run else None,
                                "error_count": state.error_count,
                                "is_active": state.is_active
                            }
                            for name, state in session.agent_states.items()
                        },
                        "status": session.status
                    }
                )
                
                # Persist session
                await self._persist_session(session)
                
            except Exception as e:
                if retry and session.agent_states[agent_name].retry_count < MAX_RETRY_ATTEMPTS:
                    session.agent_states[agent_name].retry_count += 1
                    await asyncio.sleep(RETRY_DELAY)
                    await self.update_session(session_id, agent_name, result, retry=True)
                else:
                    await self.handle_agent_error(session_id, agent_name, str(e))
                    
    async def _persist_session(self, session: AnalysisSession) -> None:
        """Persist a session to disk.
        
        Args:
            session (AnalysisSession): Session to persist
        """
        try:
            session.last_persisted = datetime.now()
            file_path = self.storage_dir / f"{session.session_id}.json"
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(session.to_dict(), indent=2))
                
        except Exception as e:
            print(f"Error persisting session {session.session_id}: {e}")
            
    async def _load_persisted_sessions(self) -> None:
        """Load all persisted sessions from disk."""
        try:
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    async with aiofiles.open(file_path, 'r') as f:
                        data = json.loads(await f.read())
                        session = AnalysisSession.from_dict(data)
                        self.sessions[session.session_id] = session
                except Exception as e:
                    print(f"Error loading session from {file_path}: {e}")
                    
        except Exception as e:
            print(f"Error loading persisted sessions: {e}")
            
    async def _persist_all_sessions(self) -> None:
        """Persist all active sessions to disk."""
        tasks = [
            self._persist_session(session)
            for session in self.sessions.values()
        ]
        await asyncio.gather(*tasks)
            
    async def _periodic_cleanup(self) -> None:
        """Periodically clean up old sessions."""
        while True:
            try:
                await self.cleanup_old_sessions()
                await asyncio.sleep(300)  # Run every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in periodic cleanup: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
                
    async def cleanup_old_sessions(self) -> None:
        """Remove sessions older than max_session_age."""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session.start_time > self.max_session_age
        ]
        
        for session_id in expired_sessions:
            session = self.sessions[session_id]
            # Clean up session in session service
            await self.session_service.delete_session(
                app_name=APP_NAME,
                user_id=session.user_id,
                session_id=session_id
            )
            
            # Remove persisted file
            file_path = self.storage_dir / f"{session_id}.json"
            if file_path.exists():
                file_path.unlink()
                
            del self.sessions[session_id]
            
    async def get_active_sessions(self) -> List[AnalysisSession]:
        """Get all active sessions."""
        await self.cleanup_old_sessions()
        return list(self.sessions.values())
        
    async def get_session_context(self, session_id: str) -> Dict:
        """Get the current context for a session."""
        session = await self.get_session(session_id)
        if not session:
            return {}
            
        # Get context from session service
        service_context = await self.session_service.get_session(
            app_name=APP_NAME,
            user_id=session.user_id,
            session_id=session_id
        )
        
        return {
            "app_name": APP_NAME,
            "session_id": session.session_id,
            "user_id": session.user_id,
            "location": session.location,
            "start_time": session.start_time.isoformat(),
            "agent_states": {
                name: {
                    "last_run": state.last_run.isoformat() if state.last_run else None,
                    "error_count": state.error_count,
                    "is_active": state.is_active,
                    "retry_count": state.retry_count,
                    "last_error": state.last_error
                }
                for name, state in session.agent_states.items()
            },
            "status": session.status,
            "error_messages": session.error_messages,
            "service_context": service_context,
            "last_persisted": session.last_persisted.isoformat() if session.last_persisted else None
        }
        
    async def handle_agent_error(
        self,
        session_id: str,
        agent_name: str,
        error: str,
        retry: bool = True
    ) -> None:
        """Handle an error from an agent.
        
        Args:
            session_id (str): Session identifier
            agent_name (str): Name of the agent
            error (str): Error message
            retry (bool): Whether to retry the operation
        """
        session = await self.get_session(session_id)
        if not session:
            return
            
        async with session.semaphore:
            try:
                session.update_agent_state(agent_name, {
                    "status": "error",
                    "error": error
                })
                
                # If too many errors, mark agent as inactive
                state = session.get_agent_state(agent_name)
                if state and state.error_count >= 3:
                    state.is_active = False
                    session.status = "degraded"
                    
                # Update session service
                await self.session_service.update_session(
                    app_name=APP_NAME,
                    user_id=session.user_id,
                    session_id=session_id,
                    context={
                        "status": "error",
                        "error": error,
                        "agent": agent_name
                    }
                )
                
                # Persist session
                await self._persist_session(session)
                
            except Exception as e:
                if retry and session.agent_states[agent_name].retry_count < MAX_RETRY_ATTEMPTS:
                    session.agent_states[agent_name].retry_count += 1
                    await asyncio.sleep(RETRY_DELAY)
                    await self.handle_agent_error(session_id, agent_name, error, retry=True)
                else:
                    print(f"Error handling agent error: {e}")
                    
    async def reset_agent(
        self,
        session_id: str,
        agent_name: str,
        retry: bool = True
    ) -> None:
        """Reset an agent's state in a session.
        
        Args:
            session_id (str): Session identifier
            agent_name (str): Name of the agent
            retry (bool): Whether to retry on failure
        """
        session = await self.get_session(session_id)
        if not session:
            return
            
        async with session.semaphore:
            try:
                session.agent_states[agent_name] = AgentState()
                await self.update_session(session_id, agent_name, {
                    "status": "reset",
                    "message": "Agent state has been reset"
                })
                
            except Exception as e:
                if retry and session.agent_states[agent_name].retry_count < MAX_RETRY_ATTEMPTS:
                    session.agent_states[agent_name].retry_count += 1
                    await asyncio.sleep(RETRY_DELAY)
                    await self.reset_agent(session_id, agent_name, retry=True)
                else:
                    await self.handle_agent_error(session_id, agent_name, str(e))
                    
    async def get_user_sessions(self, user_id: str) -> List[AnalysisSession]:
        """Get all sessions for a specific user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            List[AnalysisSession]: List of user's sessions
        """
        return [
            session for session in self.sessions.values()
            if session.user_id == user_id
        ]
        
    async def get_session_by_user(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[AnalysisSession]:
        """Get a specific session for a user.
        
        Args:
            user_id (str): User identifier
            session_id (str): Session identifier
            
        Returns:
            Optional[AnalysisSession]: Session if found and belongs to user
        """
        session = await self.get_session(session_id)
        if session and session.user_id == user_id:
            return session
        return None 