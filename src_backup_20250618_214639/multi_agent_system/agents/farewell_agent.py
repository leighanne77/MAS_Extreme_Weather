from typing import Dict, Any
from .base_agent import BaseAgent

class FarewellAgent(BaseAgent):
    """Agent responsible for generating session summaries and farewell messages.
    
    For detailed tool documentation, see docs/agent_tools.md#6-farewell-tools
    """
    
    # ADK Agent Card
    agent_card = {
        "name": "Session Completion and Summary Agent",
        "description": "Handles user session completion, provides summary of results, and offers next steps",
        "url": "/api/farewell-agent",
        "version": "1.0.0",
        "provider": {
            "name": "Climate Risk Analysis System",
            "version": "1.0.0",
            "description": "Multi-agent climate risk analysis platform"
        },
        "documentationUrl": "/docs/farewell-agent",
        "capabilities": {
            "skills": [
                {
                    "name": "summarize_analysis_results",
                    "description": "Summarizes analysis results and key findings",
                    "parameters": {
                        "analysis_results": {"type": "object", "required": True},
                        "summary_level": {"type": "string", "enum": ["brief", "detailed", "executive"]},
                        "include_recommendations": {"type": "boolean", "default": True}
                    }
                },
                {
                    "name": "provide_next_steps",
                    "description": "Provides clear next steps and recommendations",
                    "parameters": {
                        "user_type": {"type": "string", "enum": ["investor", "property_owner", "planner"]},
                        "priority_level": {"type": "string", "enum": ["immediate", "short_term", "long_term"]},
                        "include_timeline": {"type": "boolean", "default": True}
                    }
                },
                {
                    "name": "offer_followup_options",
                    "description": "Offers follow-up options and resources",
                    "parameters": {
                        "followup_type": {"type": "string", "enum": ["detailed_report", "consultation", "monitoring"]},
                        "contact_preferences": {"type": "object", "properties": {"email": "boolean", "phone": "boolean"}}
                    }
                }
            ],
            "extensions": {
                "supports_streaming": True,
                "supports_file_generation": True,
                "max_message_size": "10MB",
                "supports_session_archiving": True,
                "supports_followup_scheduling": True
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Requires API key for authentication"
            }
        },
        "defaultInputModes": ["text", "data"],
        "defaultOutputModes": ["text", "data", "file"],
        "supportsAuthenticatedExtendedCard": True
    }
    
    def __init__(self):
        super().__init__("farewell_agent")
        self.tools = [
            self.generate_session_summary,
            self.generate_farewell_message
        ]

    async def generate_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Generates a summary of the current session.
        
        See docs/agent_tools.md#generate_session_summary for detailed documentation.
        
        Args:
            session_id: ID of the session to summarize
            
        Returns:
            A dictionary containing:
                - status: str - 'success' or 'error'
                - result: Dict[str, Any] - Session summary
                - recommendations: List[str] - Follow-up actions
                - error: str - Error message if status is 'error'
        """
        try:
            # Implementation here
            return {
                "status": "success",
                "result": {
                    "session_id": session_id,
                    "summary": "Session summary goes here.",
                    "recommendations": []
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def generate_farewell_message(self, user_name: str) -> Dict[str, Any]:
        """Generates a farewell message for the user.
        
        See docs/agent_tools.md#generate_farewell_message for detailed documentation.
        
        Args:
            user_name: The name of the user to bid farewell
            
        Returns:
            A dictionary containing:
                - status: str - 'success' or 'error'
                - result: Dict[str, Any] - Farewell message
                - error: str - Error message if status is 'error'
        """
        try:
            # Implementation here
            return {
                "status": "success",
                "result": {
                    "message": f"Goodbye, {user_name}! Thank you for using our service."
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def _execute_request(self, request: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Execute a request for the farewell agent."""
        try:
            session_id = request.get("session_id", "")
            result = await self.generate_session_summary(session_id)
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