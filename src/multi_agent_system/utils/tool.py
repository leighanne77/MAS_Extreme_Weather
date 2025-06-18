from typing import Any, Callable, Dict
from dataclasses import dataclass

@dataclass
class Tool:
    """Class representing a tool available to an agent."""
    
    name: str
    func: Callable
    description: str
    
    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool function.
        
        Args:
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Dictionary containing the function results
        """
        return self.func(*args, **kwargs) 