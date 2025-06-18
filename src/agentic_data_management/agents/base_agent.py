"""
Base Agent Module

This module provides the foundation for all data management agents in the system.
"""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging
from pydantic import BaseModel

class AgentState(BaseModel):
    """Represents the current state of an agent."""
    agent_id: str
    status: str
    last_active: datetime
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    """Base class for all data management agents."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.state = AgentState(
            agent_id=agent_id,
            status="initialized",
            last_active=datetime.now()
        )
        self.logger = logging.getLogger(f"agent.{agent_id}")
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main logic.
        
        Args:
            context: Execution context containing necessary information
            
        Returns:
            Dictionary containing execution results
        """
        pass
    
    async def update_state(self, status: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update the agent's state.
        
        Args:
            status: New status
            metadata: Optional metadata to update
        """
        self.state.status = status
        self.state.last_active = datetime.now()
        if metadata:
            self.state.metadata.update(metadata)
    
    async def get_state(self) -> AgentState:
        """Get the current state of the agent.
        
        Returns:
            Current agent state
        """
        return self.state
    
    async def validate_config(self) -> bool:
        """Validate the agent's configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return True
    
    async def handle_error(self, error: Exception) -> None:
        """Handle errors that occur during agent execution.
        
        Args:
            error: The exception that occurred
        """
        self.logger.error(f"Error in agent {self.agent_id}: {str(error)}")
        await self.update_state("error", {"last_error": str(error)})
    
    async def cleanup(self) -> None:
        """Perform cleanup operations when the agent is shutting down."""
        await self.update_state("shutdown") 