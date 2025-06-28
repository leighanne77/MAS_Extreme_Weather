from typing import Any

from .base_agent import BaseAgent


class GreetingAgent(BaseAgent):
    """Agent responsible for welcoming users and listing available capabilities.

    For detailed tool documentation, see docs/agent_tools.md#5-greeting-tools
    """

    # ADK Agent Card
    agent_card = {
        "name": "User Interaction and Guidance Agent",
        "description": "Handles initial user interactions, explains system capabilities, and guides users through analysis",
        "url": "/api/greeting-agent",
        "version": "1.0.0",
        "provider": {
            "name": "Climate Risk Analysis System",
            "version": "1.0.0",
            "description": "Multi-agent climate risk analysis platform"
        },
        "documentationUrl": "/docs/greeting-agent",
        "capabilities": {
            "skills": [
                {
                    "name": "welcome_user",
                    "description": "Welcomes users and explains system capabilities",
                    "parameters": {
                        "user_context": {"type": "object", "properties": {"experience_level": "string", "use_case": "string"}},
                        "include_examples": {"type": "boolean", "default": True}
                    }
                },
                {
                    "name": "guide_analysis_process",
                    "description": "Guides users through the analysis process",
                    "parameters": {
                        "analysis_type": {"type": "string", "enum": ["basic", "comprehensive", "investment"]},
                        "user_preferences": {"type": "object", "properties": {"location": "string", "focus_areas": "array"}}
                    }
                },
                {
                    "name": "collect_analysis_requirements",
                    "description": "Collects necessary information for analysis",
                    "parameters": {
                        "required_fields": {"type": "array", "items": {"type": "string"}},
                        "optional_fields": {"type": "array", "items": {"type": "string"}},
                        "validation_rules": {"type": "object"}
                    }
                }
            ],
            "extensions": {
                "supports_streaming": True,
                "supports_interactive_guidance": True,
                "max_message_size": "10MB",
                "supports_user_onboarding": True,
                "supports_context_awareness": True
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Requires API key for authentication"
            }
        },
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "supportsAuthenticatedExtendedCard": True
    }

    def __init__(self):
        super().__init__("greeting_agent")
        self.tools = [
            self.generate_welcome_message,
            self.list_available_capabilities
        ]

    async def generate_welcome_message(self, user_id: str) -> dict[str, Any]:
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

    async def list_available_capabilities(self) -> dict[str, Any]:
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

    async def _execute_request(self, request: dict[str, Any], request_id: str) -> dict[str, Any]:
        """Execute a request for the greeting agent."""
        try:
            user_id = request.get("user_id", "anonymous")
            result = await self.generate_welcome_message(user_id)
            return {
                "status": "success",
                "result": result,
                "request_id": request_id,
                "agent": self.name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "request_id": request_id,
                "agent": self.name
            }
