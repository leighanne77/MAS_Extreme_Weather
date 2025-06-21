from typing import Dict, Any, List
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        self.name = name
        self.tools: List[Any] = []
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary containing processing results
        """
        pass
        
    def get_tools(self) -> List[Any]:
        """Get list of tools available to this agent.
        
        Returns:
            List of tools
        """
        return self.tools 