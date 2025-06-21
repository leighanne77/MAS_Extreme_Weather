"""
Agent class for the multi-agent climate risk analysis system.

This module provides a simple Agent class that supports ADK features,
agent cards, and function-based tools.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Simple Agent class for climate risk analysis."""
    
    name: str
    description: str
    instruction: str = ""
    model: str = "gemini-2.0-flash"
    tools: List[Callable] = field(default_factory=list)
    agent_card: Optional[Dict[str, Any]] = None
    
    # ADK features
    metrics_collector: Optional[Any] = None
    circuit_breaker: Optional[Any] = None
    worker_pool: Optional[Any] = None
    monitoring: Optional[Any] = None
    buffer: Optional[Any] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.agent_card is None:
            # Create a basic agent card if none provided
            self.agent_card = {
                "name": self.name,
                "description": self.description,
                "url": f"/api/{self.name}",
                "version": "1.0.0",
                "provider": {
                    "name": "Climate Risk Analysis System",
                    "version": "1.0.0",
                    "description": "Multi-agent climate risk analysis platform"
                },
                "capabilities": {
                    "skills": [],
                    "extensions": {}
                },
                "defaultInputModes": ["text", "data"],
                "defaultOutputModes": ["text", "data"]
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request using the agent's tools and capabilities."""
        try:
            # Check circuit breaker if available
            if self.circuit_breaker and not self.circuit_breaker.is_allowed(self.name):
                raise Exception("Circuit breaker is open")
            
            # Track operation with metrics collector if available
            if self.metrics_collector:
                with self.metrics_collector.track_operation(f"{self.name}_request"):
                    return await self._process_request(request)
            else:
                return await self._process_request(request)
                
        except Exception as e:
            # Record failure in circuit breaker if available
            if self.circuit_breaker:
                self.circuit_breaker.record_failure(self.name)
            
            logger.error(f"Error in {self.name}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }
    
    async def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process the actual request."""
        # For now, return a simple response
        # In a real implementation, this would use the agent's tools and model
        return {
            "status": "success",
            "agent": self.name,
            "result": {
                "message": f"Request processed by {self.name}",
                "request": request
            }
        }
    
    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for handle_request for compatibility."""
        return await self.handle_request(request)
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Get the agent's card in ADK format."""
        return self.agent_card or {} 