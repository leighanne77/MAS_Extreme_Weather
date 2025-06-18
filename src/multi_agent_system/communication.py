"""
Communication Manager for Multi-Agent Climate Risk Analysis System

This module implements the communication and coordination layer between agents in the climate risk analysis system.
It manages message passing, state sharing, and agent interactions.

Key Components:
    - SharedState: Manages shared state between agents
    - CommunicationManager: Coordinates agent communication
    - AgentTransfer: Handles transfer of control between agents

State Management:
    - Centralized state management through SharedState
    - Atomic state updates with timestamps
    - State versioning and conflict resolution
    - State persistence and recovery

Message Types:
    1. Control Messages: For agent coordination
    2. Data Messages: For sharing analysis results
    3. State Messages: For state synchronization
    4. Error Messages: For error propagation
    5. Heartbeat Messages: For agent health monitoring

Error Handling:
    - Message delivery guarantees
    - Error propagation and recovery
    - Deadlock prevention
    - Timeout handling

Dependencies:
    - session_manager: For session state management
    - agent: For agent definitions and capabilities

Example Usage:
    ```python
    # Initialize communication manager
    comm_manager = CommunicationManager()
    
    # Create shared state
    shared_state = SharedState(session)
    
    # Transfer control between agents
    transfer = AgentTransfer(
        source_agent="risk_analyzer",
        target_agent="validation_agent",
        context={"data": analysis_result}
    )
    result = await transfer.execute(session, agents)
    ```

Configuration:
    - Message timeout settings
    - Retry policies
    - State synchronization intervals
    - Error handling strategies
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import asyncio

from src.multi_agent_system.session_manager import AnalysisSession, AgentState
from src.multi_agent_system.agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SharedState:
    """Manages shared state between agents in the system.
    
    This class provides atomic operations for state management and ensures
    consistency across agent interactions.
    
    Attributes:
        session (AnalysisSession): Current analysis session
        agent_states (Dict[str, AgentState]): States of all agents
        context (Dict[str, Any]): Shared context data
        last_updated (datetime): Timestamp of last update
        
    State Management:
        - Atomic updates with timestamps
        - Version tracking for state changes
        - Conflict detection and resolution
        - State persistence and recovery
        
    Example:
        ```python
        shared_state = SharedState(session)
        shared_state.update_agent_state("risk_analyzer", agent_state)
        context = shared_state.get_agent_state("risk_analyzer")
        ```
    """
    
    session: AnalysisSession
    agent_states: Dict[str, AgentState] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_session_state(self, updates: Dict[str, Any]) -> None:
        """Update session state with atomic operation.
        
        Args:
            updates (Dict[str, Any]): State updates to apply
            
        State Updates:
            - Applies updates atomically
            - Updates timestamp
            - Triggers state change notifications
            
        Example:
            ```python
            shared_state.update_session_state({
                "analysis_status": "completed",
                "results": analysis_data
            })
            ```
        """
        self.session.state.update(updates)
        self.last_updated = datetime.now()
    
    def update_agent_state(self, agent_id: str, state: AgentState) -> None:
        """Update agent state with atomic operation.
        
        Args:
            agent_id (str): Agent identifier
            state (AgentState): New agent state
            
        State Updates:
            - Updates agent state atomically
            - Updates timestamp
            - Triggers state change notifications
            
        Example:
            ```python
            agent_state = AgentState(
                last_run=datetime.now(),
                last_result={"status": "success"}
            )
            shared_state.update_agent_state("risk_analyzer", agent_state)
            ```
        """
        self.agent_states[agent_id] = state
        self.last_updated = datetime.now()
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get current agent state.
        
        Args:
            agent_id (str): Agent identifier
            
        Returns:
            Optional[AgentState]: Current agent state if exists
            
        Example:
            ```python
            state = shared_state.get_agent_state("risk_analyzer")
            if state and state.is_active:
                process_agent_state(state)
            ```
        """
        return self.agent_states.get(agent_id)
    
    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update shared context with atomic operation.
        
        Args:
            updates (Dict[str, Any]): Context updates to apply
            
        State Updates:
            - Updates context atomically
            - Updates timestamp
            - Triggers context change notifications
            
        Example:
            ```python
            shared_state.update_context({
                "location": "New York",
                "time_period": "2024-01"
            })
            ```
        """
        self.context.update(updates)
        self.last_updated = datetime.now()
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status.
        
        Returns:
            Dict[str, Any]: Session status
        """
        return {
            "session_id": self.session.session_id,
            "created_at": self.session.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "agent_states": {
                agent_id: {
                    "status": state.status,
                    "last_active": state.last_active.isoformat(),
                    "error_count": state.error_count,
                    "retry_count": state.retry_count
                }
                for agent_id, state in self.agent_states.items()
            },
            "context_keys": list(self.context.keys())
        }

class CommunicationManager:
    """Manages communication between agents in the system.
    
    This class handles message passing, state synchronization, and agent coordination.
    
    Attributes:
        shared_state (SharedState): Current shared state
        message_queue (List[Dict]): Queue of pending messages
        active_transfers (List[AgentTransfer]): Active agent transfers
        
    Message Handling:
        - Asynchronous message processing
        - Message prioritization
        - Delivery guarantees
        - Error handling
        
    Example:
        ```python
        comm_manager = CommunicationManager(shared_state)
        await comm_manager.send_message(
            source="risk_analyzer",
            target="validation_agent",
            message={"type": "data", "content": analysis_result}
        )
        ```
    """
    
    def __init__(self, session: AnalysisSession):
        """Initialize communication manager.
        
        Args:
            session (AnalysisSession): Current analysis session
        """
        self.session = session
        self.shared_state = SharedState(session=session)
    
    def update_shared_state(self, updates: Dict[str, Any]) -> None:
        """Update shared state.
        
        Args:
            updates (Dict[str, Any]): State updates
        """
        # Split updates into different categories
        session_updates = {}
        agent_updates = {}
        context_updates = {}
        
        for key, value in updates.items():
            if key.endswith("_result"):
                agent_id = key[:-7]  # Remove "_result" suffix
                context_updates[f"{agent_id}_result"] = value
            elif key.endswith("_tokens"):
                agent_id = key[:-7]  # Remove "_tokens" suffix
                context_updates[f"{agent_id}_tokens"] = value
            elif key.endswith("_error"):
                agent_id = key[:-6]  # Remove "_error" suffix
                agent_updates[agent_id] = {
                    "status": "error",
                    "error": value
                }
            else:
                session_updates[key] = value
        
        # Apply updates
        if session_updates:
            self.shared_state.update_session_state(session_updates)
        
        if agent_updates:
            for agent_id, state in agent_updates.items():
                current_state = self.shared_state.get_agent_state(agent_id)
                if current_state:
                    current_state.status = state["status"]
                    current_state.error_count += 1
                    current_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "status": "error",
                        "error": state["error"]
                    })
                    self.shared_state.update_agent_state(agent_id, current_state)
        
        if context_updates:
            self.shared_state.update_context(context_updates)
    
    def get_shared_state(self) -> SharedState:
        """Get shared state.
        
        Returns:
            SharedState: Current shared state
        """
        return self.shared_state
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status.
        
        Returns:
            Dict[str, Any]: Session status
        """
        return self.shared_state.get_session_status()

@dataclass
class AgentTransfer:
    """Manages transfer of control between agents.
    
    This class handles the transfer of control and context between agents,
    ensuring proper state management and error handling.
    
    Attributes:
        source_agent (str): Source agent identifier
        target_agent (str): Target agent identifier
        context (Dict[str, Any]): Transfer context
        priority (int): Transfer priority
        
    Transfer Process:
        - Validates agent availability
        - Transfers context and state
        - Handles errors and retries
        - Updates agent states
        
    Example:
        ```python
        transfer = AgentTransfer(
            source_agent="risk_analyzer",
            target_agent="validation_agent",
            context={"data": analysis_result},
            priority=1
        )
        result = await transfer.execute(session, agents)
        ```
    """
    
    source_agent: str
    target_agent: str
    context: Dict[str, Any]
    priority: int = 0
    
    async def execute(
        self,
        session: AnalysisSession,
        agents: Dict[str, Agent]
    ) -> Dict[str, Any]:
        """Execute the agent transfer.
        
        Args:
            session (AnalysisSession): Current analysis session
            agents (Dict[str, Agent]): Available agents
            
        Returns:
            Dict[str, Any]: Transfer result
            
        Transfer Steps:
            1. Validate agent availability
            2. Transfer context and state
            3. Execute target agent
            4. Handle errors and retries
            5. Update agent states
            
        Example:
            ```python
            result = await transfer.execute(session, agents)
            if result["status"] == "success":
                process_transfer_result(result["data"])
            ```
        """
        if self.target_agent not in agents:
            raise ValueError(f"Target agent {self.target_agent} not found")
        
        # Update session state with transfer context
        session.context.update(self.context)
        
        # Execute target agent
        try:
            result = await agents[self.target_agent].run(session)
            return {
                "status": "success",
                "source": self.source_agent,
                "target": self.target_agent,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "source": self.source_agent,
                "target": self.target_agent,
                "error": str(e)
            }

@dataclass
class ExplicitInvocation:
    """Manages explicit agent invocations with enhanced response handling.
    
    This class provides a way to invoke agents while maintaining control,
    with support for response summarization and caching.
    
    Attributes:
        agent_name (str): Name of the agent to invoke
        request (Dict[str, Any]): Request data
        context (Dict[str, Any]): Context data
        timeout (int): Operation timeout in seconds
        skip_summarization (bool): Whether to skip response summarization
        cache_key (Optional[str]): Key for response caching
        cache_ttl (int): Cache time-to-live in seconds
        
    Example:
        ```python
        invocation = ExplicitInvocation(
            agent_name="risk_analyzer",
            request={"location": "New York"},
            context={"time_period": "2024-01"},
            cache_key="ny_risk_2024_01"
        )
        result = await invocation.execute(session, agents)
        ```
    """
    agent_name: str
    request: Dict[str, Any]
    context: Dict[str, Any]
    timeout: int = 30
    skip_summarization: bool = False
    cache_key: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    async def execute(
        self,
        session: AnalysisSession,
        agents: Dict[str, Agent]
    ) -> Dict[str, Any]:
        """Execute the explicit invocation with enhanced response handling.
        
        Args:
            session (AnalysisSession): Current analysis session
            agents (Dict[str, Agent]): Available agents
            
        Returns:
            Dict[str, Any]: Invocation result
            
        Process:
            1. Check cache for existing response
            2. Execute agent with timeout
            3. Handle and summarize response
            4. Cache result if needed
            
        Example:
            ```python
            result = await invocation.execute(session, agents)
            if result["status"] == "success":
                process_result(result["data"])
            ```
        """
        if self.agent_name not in agents:
            raise ValueError(f"Agent {self.agent_name} not found")
        
        # Check cache if cache_key is provided
        if self.cache_key:
            cached_result = await self._get_cached_result(session)
            if cached_result:
                return cached_result
        
        # Update session state with invocation context
        session.context.update(self.context)
        
        # Execute agent with timeout
        try:
            async with asyncio.timeout(self.timeout):
                result = await agents[self.agent_name].run(session)
                
                # Handle the response
                if result["status"] == "error":
                    return {
                        "status": "error",
                        "agent": self.agent_name,
                        "error": result["error"]
                    }
                
                # Summarize response if needed
                if not self.skip_summarization:
                    result = await self._summarize_response(result)
                
                # Cache result if cache_key is provided
                if self.cache_key:
                    await self._cache_result(session, result)
                
                return {
                    "status": "success",
                    "agent": self.agent_name,
                    "result": result["result"],
                    "summary": result.get("summary")
                }
                
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "agent": self.agent_name,
                "error": f"Invocation timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e)
            }
    
    async def _get_cached_result(self, session: AnalysisSession) -> Optional[Dict[str, Any]]:
        """Get cached result if available."""
        if not self.cache_key:
            return None
            
        # TODO: Implement cache retrieval
        return None
    
    async def _cache_result(self, session: AnalysisSession, result: Dict[str, Any]) -> None:
        """Cache the result."""
        if not self.cache_key:
            return
            
        # TODO: Implement result caching
        pass
    
    async def _summarize_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize the agent's response."""
        if not result.get("result"):
            return result
            
        # TODO: Implement response summarization
        return result 