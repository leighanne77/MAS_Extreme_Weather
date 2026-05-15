from typing import Any

from .base_agent import BaseAgent


class ProgressDisplayAgent(BaseAgent):
    """Agent responsible for showing MAS's working process (active agents, data sources, progress stages).

    For detailed tool documentation, see docs/agent_tools.md#progress-display-tools
    """

    # ADK Agent Card
    agent_card = {
        "name": "Progress Display Agent",
        "description": "Shows MAS's working process including active agents, data sources, and progress stages",
        "url": "/api/progress-display-agent",
        "version": "1.0.0",
        "provider": {
            "name": "Climate Risk Analysis System",
            "version": "1.0.0",
            "description": "Multi-agent climate risk analysis platform"
        },
        "documentationUrl": "/docs/progress-display-agent",
        "capabilities": {
            "skills": [
                {
                    "name": "get_analysis_progress",
                    "description": "Gets current analysis progress for a session",
                    "parameters": {
                        "session_id": {"type": "string", "required": True}
                    }
                },
                {
                    "name": "get_active_agents",
                    "description": "Gets list of currently active agents",
                    "parameters": {
                        "session_id": {"type": "string", "required": True}
                    }
                },
                {
                    "name": "get_data_source_status",
                    "description": "Gets status of data sources being used",
                    "parameters": {
                        "session_id": {"type": "string", "required": True}
                    }
                },
                {
                    "name": "get_progress_stages",
                    "description": "Gets progress stages for the analysis",
                    "parameters": {
                        "session_id": {"type": "string", "required": True}
                    }
                }
            ],
            "extensions": {
                "supports_real_time_updates": True,
                "supports_progress_tracking": True,
                "max_concurrent_sessions": 100
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Requires API key for authentication"
            }
        },
        "defaultInputModes": ["text", "data"],
        "defaultOutputModes": ["text", "data"],
        "supportsAuthenticatedExtendedCard": True
    }

    def __init__(self):
        super().__init__("progress_display_agent")
        self.tools = [
            self.get_analysis_progress,
            self.get_active_agents,
            self.get_data_source_status,
            self.get_progress_stages
        ]

    async def get_analysis_progress(self, session_id: str) -> dict[str, Any]:
        """Get current analysis progress for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict containing progress information
        """
        try:
            progress = {
                "session_id": session_id,
                "overall_progress": 0.0,  # 0.0 to 1.0
                "current_stage": "initializing",
                "stages_completed": [],
                "stages_remaining": [],
                "estimated_time_remaining": None
            }
            
            return {
                "status": "success",
                "result": progress,
                "confidence": 0.95
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def get_active_agents(self, session_id: str) -> dict[str, Any]:
        """Get list of currently active agents.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict containing list of active agents
        """
        try:
            active_agents = {
                "session_id": session_id,
                "active_agents": [
                    # Example: "EnvironmentalDataAgent", "InfrastructureDataAgent", etc.
                ],
                "agent_status": {}
            }
            
            return {
                "status": "success",
                "result": active_agents,
                "confidence": 0.95
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def get_data_source_status(self, session_id: str) -> dict[str, Any]:
        """Get status of data sources being used.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict containing data source status information
        """
        try:
            data_sources = {
                "session_id": session_id,
                "data_sources": {
                    "google_data": {
                        "status": "active",
                        "description": "Best in Class Climate Risk Modeling + Weather Forecasting, Data, and AI Models"
                    },
                    "local_data": {
                        "status": "active",
                        "description": "Local Data, Shipbuilding Industry Experts, Local Bioregional Experts, Scientists, NGOs"
                    }
                },
                "data_quality": "high",
                "last_updated": None
            }
            
            return {
                "status": "success",
                "result": data_sources,
                "confidence": 0.95
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def get_progress_stages(self, session_id: str) -> dict[str, Any]:
        """Get progress stages for the analysis.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict containing progress stages information
        """
        try:
            stages = {
                "session_id": session_id,
                "stages": [
                    {
                        "name": "query_refinement",
                        "status": "completed",
                        "progress": 1.0
                    },
                    {
                        "name": "data_collection",
                        "status": "in_progress",
                        "progress": 0.5
                    },
                    {
                        "name": "risk_analysis",
                        "status": "pending",
                        "progress": 0.0
                    },
                    {
                        "name": "recommendations",
                        "status": "pending",
                        "progress": 0.0
                    },
                    {
                        "name": "ballpark_roi",
                        "status": "pending",
                        "progress": 0.0
                    }
                ]
            }
            
            return {
                "status": "success",
                "result": stages,
                "confidence": 0.95
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def _execute_request(self, request: dict[str, Any], request_id: str) -> dict[str, Any]:
        """Execute a request for the progress display agent."""
        try:
            session_id = request.get("session_id", "")
            result = await self.get_analysis_progress(session_id)
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





