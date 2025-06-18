from typing import Dict, Any
from .base_agent import BaseAgent
from .tool import Tool

class GreetingAgent(BaseAgent):
    """Agent responsible for welcoming users and listing available capabilities.
    
    For detailed tool documentation, see docs/agent_tools.md#5-greeting-tools
    """
    
    def __init__(self):
        super().__init__("greeting_agent")
        self.tools = [
            Tool(
                name="generate_welcome_message",
                func=self.generate_welcome_message,
                description="Generates a personalized welcome message"
            ),
            Tool(
                name="list_available_capabilities",
                func=self.list_available_capabilities,
                description="Lists available system capabilities"
            )
        ]

    async def generate_welcome_message(self, user_id: str) -> Dict[str, Any]:
        """Generates a personalized welcome message.
        
        See docs/agent_tools.md#generate_welcome_message for detailed documentation.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            A dictionary containing:
                - status: str - 'success' or 'error'
                - result: Dict[str, str] - Welcome message
                - user_preferences: Dict[str, Any] - User preferences
                - error: str - Error message if status is 'error'
        """
        try:
            # Implementation here
            return {
                "status": "success",
                "result": {
                    "message": f"Welcome, user {user_id}!",
                    "user_preferences": {}
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def list_available_capabilities(self) -> Dict[str, Any]:
        """Lists available system capabilities.
        
        See docs/agent_tools.md#list_available_capabilities for detailed documentation.
        
        Returns:
            A dictionary containing:
                - status: str - 'success' or 'error'
                - result: List[Dict[str, Any]] - Available capabilities
                - examples: List[str] - Usage examples
                - error: str - Error message if status is 'error'
        """
        try:
            # Implementation here
            return {
                "status": "success",
                "result": [
                    {"capability": "risk analysis"},
                    {"capability": "historical data analysis"}
                ],
                "examples": [
                    "Analyze current risks for New York, NY",
                    "Show historical temperature trends for California"
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 