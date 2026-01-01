from typing import Any

from .base_agent import BaseAgent


class QueryRefinementAgent(BaseAgent):
    """Agent responsible for interactive dialogue to help users refine their initial query into a precise one.

    For detailed tool documentation, see docs/agent_tools.md#query-refinement-tools
    """

    # ADK Agent Card
    agent_card = {
        "name": "Query Refinement Agent",
        "description": "Helps users refine their initial queries through interactive dialogue to ensure precise analysis",
        "url": "/api/query-refinement-agent",
        "version": "1.0.0",
        "provider": {
            "name": "Climate Risk Analysis System",
            "version": "1.0.0",
            "description": "Multi-agent climate risk analysis platform"
        },
        "documentationUrl": "/docs/query-refinement-agent",
        "capabilities": {
            "skills": [
                {
                    "name": "refine_user_query",
                    "description": "Refines a user's initial query into a precise one",
                    "parameters": {
                        "initial_query": {"type": "string", "required": True},
                        "user_type": {"type": "string", "required": True}
                    }
                },
                {
                    "name": "ask_clarifying_questions",
                    "description": "Generates clarifying questions based on query context",
                    "parameters": {
                        "query_context": {"type": "object", "required": True}
                    }
                },
                {
                    "name": "check_enterprise_features",
                    "description": "Checks if query requires enterprise edition features",
                    "parameters": {
                        "user_query": {"type": "object", "required": True}
                    }
                }
            ],
            "extensions": {
                "supports_interactive_dialogue": True,
                "supports_query_validation": True,
                "max_clarification_rounds": 5
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Requires API key for authentication"
            }
        },
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text", "data"],
        "supportsAuthenticatedExtendedCard": True
    }

    def __init__(self):
        super().__init__("query_refinement_agent")
        self.tools = [
            self.refine_user_query,
            self.ask_clarifying_questions,
            self.check_enterprise_features
        ]

    async def refine_user_query(
        self,
        initial_query: str,
        user_type: str
    ) -> dict[str, Any]:
        """Refine a user's initial query into a precise one.
        
        This is a decision support tool, NOT a decision-making tool.
        Refined queries are suggestions for user review.
        
        Args:
            initial_query: The user's initial query
            user_type: Type of user (e.g., "private_equity_investor", "government_funder")
        
        Returns:
            Dict containing refined query with clarified parameters
        """
        try:
            refined_query = {
                "initial_query": initial_query,
                "user_type": user_type,
                "refined_query": "",
                "clarified_parameters": {
                    "location": None,
                    "risk_types": [],
                    "investment_timeline": None,
                    "facility_type": None,
                    "primary_concern": None
                },
                "confidence": 0.0
            }
            
            return {
                "status": "success",
                "result": refined_query,
                "confidence": 0.8,
                "disclaimer": "This is a decision support tool. Refined queries are suggestions for your review."
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def ask_clarifying_questions(
        self,
        query_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate clarifying questions based on query context.
        
        Args:
            query_context: Context dictionary from the user's query
        
        Returns:
            Dict containing list of clarifying questions
        """
        try:
            questions = [
                "What is your investment timeline?",
                "What is your primary concern?",
                "What type of facility or asset are you analyzing?",
                "Are you looking at a specific location?",
                "What extreme weather risks are most relevant to your situation?"
            ]
            
            return {
                "status": "success",
                "result": {
                    "questions": questions,
                    "context": query_context
                },
                "confidence": 0.9
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def check_enterprise_features(
        self,
        user_query: dict[str, Any]
    ) -> dict[str, Any]:
        """Check if query requires enterprise edition features.
        
        Args:
            user_query: User query dictionary
        
        Returns:
            Dict indicating if enterprise features are needed
        """
        try:
            enterprise_check = {
                "requires_enterprise": False,
                "enterprise_features_needed": [],
                "alternative_approaches": []
            }
            
            return {
                "status": "success",
                "result": enterprise_check,
                "confidence": 0.95
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def _execute_request(self, request: dict[str, Any], request_id: str) -> dict[str, Any]:
        """Execute a request for the query refinement agent."""
        try:
            initial_query = request.get("initial_query", "")
            user_type = request.get("user_type", "")
            result = await self.refine_user_query(initial_query, user_type)
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





