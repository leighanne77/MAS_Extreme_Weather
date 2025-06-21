"""
ADK Integration System for Multi-Agent Climate Risk Analysis

This module implements the integration with the ADK (Agent Development Kit) system,
providing a bridge between the multi-agent climate risk analysis system and ADK services.

Key Components:
    - ADKClient: Main client for ADK service interaction
    - ADKResponse: Response data structure
    - ADKError: Error handling and reporting
    - ADKConfig: Configuration management
    - ADKAgentCard: Compliant agent card implementation

Features:
    1. Service Integration:
       - ADK service communication
       - Response handling
       - Error management
       - Configuration control
    
    2. Response Processing:
       - Data validation
       - Error detection
       - Response parsing
       - Status tracking
    
    3. Error Handling:
       - Error classification
       - Recovery strategies
       - Error reporting
       - Status monitoring
    
    4. Configuration Management:
       - Service settings
       - Timeout control
       - Retry policies
       - Logging configuration

    5. Tool Implementation:
       - Function-based tools
       - Automatic tool wrapping
       - Parameter validation
       - Response formatting

    6. Agent Card Implementation:
       - A2A-compliant agent cards
       - TypeScript interface compliance
       - Security scheme support
       - Capability discovery

Tool Implementation:
    Tools in ADK are implemented as regular Python functions, which the framework automatically
    wraps when added to an agent's tools list. This approach provides flexibility and quick
    integration of custom logic.

    Key aspects of tool implementation:
    1. Function Definition:
       - Use standard JSON-serializable types for parameters
       - Avoid default parameter values
       - Return dictionary for structured responses
       - Include comprehensive docstrings

    2. Automatic Wrapping:
       - Functions are automatically wrapped as FunctionTools
       - Parameter types are inferred
       - Return values are structured
       - Documentation is extracted

    3. Best Practices:
       - Return descriptive dictionaries
       - Include status indicators
       - Provide clear error messages
       - Document parameters thoroughly

Example Tool Implementation:
    ```python
    def analyze_climate_risk(location: str, time_period: str) -> Dict[str, Any]:
        \"\"\"
        Analyzes climate risks for a specific location and time period.

        Args:
            location (str): The location to analyze
            time_period (str): The time period for analysis

        Returns:
            Dict[str, Any]: Analysis results with status and data
        \"\"\"
        try:
            # Analysis logic here
            return {
                "status": "success",
                "data": {
                    "location": location,
                    "time_period": time_period,
                    "risks": [...]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }
    ```

Dependencies:
    - aiohttp: For async HTTP requests
    - json: For data serialization
    - logging: For system logging
    - typing: For type hints

Example Usage:
    ```python
    # Initialize ADK client
    client = ADKClient(
        base_url="https://adk-service.example.com",
        api_key="your-api-key"
    )
    
    # Make request to ADK service
    response = await client.request(
        endpoint="analyze",
        data={"location": "New York"}
    )
    
    # Handle response
    if response.is_success:
        result = response.data
    else:
        error = response.error
    ```

Configuration:
    - BASE_URL: ADK service base URL
    - API_KEY: Authentication key
    - TIMEOUT: Request timeout
    - MAX_RETRIES: Maximum retry attempts
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import zlib
from collections import defaultdict
from dataclasses import dataclass, field

from google.adk.agents import Agent
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel

from .session_manager import SessionManager, AnalysisSession
from .weather_risks import ClimateRiskAnalyzer
from .risk_definitions import severity_levels, RiskSource, RiskThreshold, RiskType, RiskLevel
from .coordinator import CoordinatorAgent, TokenUsage
from .communication import CommunicationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentProvider:
    """Agent provider information following ADK TypeScript interface."""
    name: str
    version: str
    description: str

@dataclass
class AgentCapabilities:
    """Agent capabilities following ADK TypeScript interface."""
    skills: List[Dict[str, Any]]
    extensions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityScheme:
    """Security scheme following ADK TypeScript interface."""
    type: str
    description: str
    scheme: str = "bearer"

@dataclass
class ADKAgentCard:
    """A2A-compliant agent card following ADK TypeScript interface exactly."""
    name: str
    description: str
    url: str
    version: str
    capabilities: AgentCapabilities
    iconUrl: Optional[str] = None
    provider: Optional[AgentProvider] = None
    documentationUrl: Optional[str] = None
    securitySchemes: Optional[Dict[str, SecurityScheme]] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    defaultInputModes: List[str] = field(default_factory=lambda: ["text", "data"])
    defaultOutputModes: List[str] = field(default_factory=lambda: ["text", "data"])
    skills: List[Dict[str, Any]] = field(default_factory=list)
    supportsAuthenticatedExtendedCard: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for A2A protocol."""
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "capabilities": {
                "skills": self.capabilities.skills,
                "extensions": self.capabilities.extensions
            },
            "iconUrl": self.iconUrl,
            "provider": {
                "name": self.provider.name,
                "version": self.provider.version,
                "description": self.provider.description
            } if self.provider else None,
            "documentationUrl": self.documentationUrl,
            "securitySchemes": {
                name: {
                    "type": scheme.type,
                    "description": scheme.description,
                    "scheme": scheme.scheme
                }
                for name, scheme in (self.securitySchemes or {}).items()
            },
            "security": self.security,
            "defaultInputModes": self.defaultInputModes,
            "defaultOutputModes": self.defaultOutputModes,
            "skills": self.skills,
            "supportsAuthenticatedExtendedCard": self.supportsAuthenticatedExtendedCard
        }

class ADKAgentCardManager:
    """Manages ADK agent cards for A2A protocol compliance."""
    
    def __init__(self):
        self.agent_cards: Dict[str, ADKAgentCard] = {}
        self._initialize_agent_cards()
    
    def _initialize_agent_cards(self):
        """Initialize agent cards for all system agents."""
        
        # Climate Risk Analysis Agent Card
        self.agent_cards["climate_risk_analyzer"] = ADKAgentCard(
            name="Climate Risk Analysis Agent",
            description="Specialized agent for analyzing climate risks and providing recommendations",
            url="/api/climate-risk-analyzer",
            version="1.0.0",
            provider=AgentProvider(
                name="Climate Risk Analysis System",
                version="1.0.0",
                description="Multi-agent climate risk analysis platform"
            ),
            documentationUrl="/docs/climate-risk-analyzer",
            capabilities=AgentCapabilities(
                skills=[
                    {
                        "name": "analyze_climate_risk",
                        "description": "Analyzes climate risks for a specific location",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "timeframe": {"type": "string", "required": True},
                            "risk_types": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    {
                        "name": "get_weather_data",
                        "description": "Retrieves weather data for analysis",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "data_sources": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    {
                        "name": "generate_recommendations",
                        "description": "Generates climate resilience recommendations",
                        "parameters": {
                            "risk_analysis": {"type": "object", "required": True},
                            "location": {"type": "string", "required": True},
                            "solution_types": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                ],
                extensions={
                    "supports_streaming": True,
                    "supports_file_attachments": True,
                    "max_message_size": "10MB",
                    "supports_nature_based_solutions": True,
                    "supports_cost_benefit_analysis": True
                }
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Requires API key for authentication"
                )
            },
            defaultInputModes=["text", "data", "file"],
            defaultOutputModes=["text", "data", "file"],
            supportsAuthenticatedExtendedCard=True
        )
        
        # Nature-Based Solutions Agent Card
        self.agent_cards["nbs_agent"] = ADKAgentCard(
            name="Nature-Based Solutions Agent",
            description="Specialized agent for nature-based climate resilience solutions",
            url="/api/nbs-agent",
            version="1.0.0",
            provider=AgentProvider(
                name="Climate Risk Analysis System",
                version="1.0.0",
                description="Multi-agent climate risk analysis platform"
            ),
            capabilities=AgentCapabilities(
                skills=[
                    {
                        "name": "get_nbs_solutions",
                        "description": "Retrieves nature-based solutions for climate resilience",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "risk_types": {"type": "array", "items": {"type": "string"}},
                            "solution_scale": {"type": "string", "enum": ["property", "community", "regional"]}
                        }
                    },
                    {
                        "name": "calculate_cost_benefit",
                        "description": "Calculates cost-benefit analysis for solutions",
                        "parameters": {
                            "solution_id": {"type": "string", "required": True},
                            "property_value": {"type": "number"},
                            "timeframe": {"type": "string", "default": "10_years"}
                        }
                    }
                ],
                extensions={
                    "supports_streaming": True,
                    "supports_file_attachments": True,
                    "max_message_size": "10MB",
                    "supports_financial_analysis": True
                }
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Requires API key for authentication"
                )
            },
            defaultInputModes=["text", "data"],
            defaultOutputModes=["text", "data", "file"]
        )
        
        # Historical Agent Card
        self.agent_cards["historical_agent"] = ADKAgentCard(
            name="Historical Climate Data Agent",
            description="Analyzes historical climate data and identifies patterns, trends, and anomalies",
            url="/api/historical-agent",
            version="1.0.0",
            provider=AgentProvider(
                name="Climate Risk Analysis System",
                version="1.0.0",
                description="Multi-agent climate risk analysis platform"
            ),
            documentationUrl="/docs/historical-agent",
            capabilities=AgentCapabilities(
                skills=[
                    {
                        "name": "get_weather_data",
                        "description": "Retrieves historical weather data for analysis",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "data_sources": {"type": "array", "items": {"type": "string"}},
                            "time_range": {"type": "object", "properties": {"start": "string", "end": "string"}}
                        }
                    },
                    {
                        "name": "analyze_historical_patterns",
                        "description": "Analyzes historical climate patterns and trends",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "analysis_type": {"type": "string", "enum": ["trends", "anomalies", "patterns"]},
                            "time_period": {"type": "string", "required": True}
                        }
                    },
                    {
                        "name": "identify_climate_anomalies",
                        "description": "Identifies climate anomalies and extreme events",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "anomaly_type": {"type": "string", "enum": ["temperature", "precipitation", "wind", "all"]},
                            "severity_threshold": {"type": "number", "default": 0.95}
                        }
                    }
                ],
                extensions={
                    "supports_streaming": True,
                    "supports_file_attachments": True,
                    "max_message_size": "10MB",
                    "supports_long_term_analysis": True,
                    "supports_data_visualization": True
                }
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Requires API key for authentication"
                )
            },
            defaultInputModes=["text", "data"],
            defaultOutputModes=["text", "data", "file"],
            supportsAuthenticatedExtendedCard=True
        )
        
        # News Agent Card
        self.agent_cards["news_agent"] = ADKAgentCard(
            name="Climate News and Alert Agent",
            description="Monitors and analyzes climate-related news, alerts, and emergency information",
            url="/api/news-agent",
            version="1.0.0",
            provider=AgentProvider(
                name="Climate Risk Analysis System",
                version="1.0.0",
                description="Multi-agent climate risk analysis platform"
            ),
            documentationUrl="/docs/news-agent",
            capabilities=AgentCapabilities(
                skills=[
                    {
                        "name": "monitor_climate_news",
                        "description": "Monitors climate-related news and alerts",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "news_sources": {"type": "array", "items": {"type": "string"}},
                            "alert_types": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    {
                        "name": "analyze_emergency_alerts",
                        "description": "Analyzes emergency information and warnings",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "alert_severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                            "include_historical": {"type": "boolean", "default": True}
                        }
                    },
                    {
                        "name": "assess_event_impacts",
                        "description": "Assesses potential impacts of climate events",
                        "parameters": {
                            "event_type": {"type": "string", "required": True},
                            "location": {"type": "string", "required": True},
                            "impact_areas": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                ],
                extensions={
                    "supports_streaming": True,
                    "supports_push_notifications": True,
                    "max_message_size": "10MB",
                    "supports_real_time_monitoring": True,
                    "supports_alert_prioritization": True
                }
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Requires API key for authentication"
                )
            },
            defaultInputModes=["text", "data"],
            defaultOutputModes=["text", "data"],
            supportsAuthenticatedExtendedCard=True
        )
        
        # Recommendation Agent Card
        self.agent_cards["recommendation_agent"] = ADKAgentCard(
            name="Climate Resilience Recommendation Agent",
            description="Generates comprehensive climate resilience recommendations with cost-benefit analysis",
            url="/api/recommendation-agent",
            version="1.0.0",
            provider=AgentProvider(
                name="Climate Risk Analysis System",
                version="1.0.0",
                description="Multi-agent climate risk analysis platform"
            ),
            documentationUrl="/docs/recommendation-agent",
            capabilities=AgentCapabilities(
                skills=[
                    {
                        "name": "get_nbs_solutions",
                        "description": "Retrieves nature-based solutions for climate resilience",
                        "parameters": {
                            "location": {"type": "string", "required": True},
                            "risk_types": {"type": "array", "items": {"type": "string"}},
                            "solution_scale": {"type": "string", "enum": ["property", "community", "regional"]}
                        }
                    },
                    {
                        "name": "calculate_cost_benefit",
                        "description": "Calculates cost-benefit analysis for solutions",
                        "parameters": {
                            "solution_id": {"type": "string", "required": True},
                            "property_value": {"type": "number"},
                            "timeframe_years": {"type": "number", "default": 10}
                        }
                    },
                    {
                        "name": "generate_recommendations",
                        "description": "Generates comprehensive climate resilience recommendations",
                        "parameters": {
                            "risk_analysis": {"type": "object", "required": True},
                            "location": {"type": "string", "required": True},
                            "solution_types": {"type": "array", "items": {"type": "string"}},
                            "priority_focus": {"type": "string", "enum": ["nature_based", "structural", "emergency"]}
                        }
                    }
                ],
                extensions={
                    "supports_streaming": True,
                    "supports_file_attachments": True,
                    "max_message_size": "10MB",
                    "supports_financial_analysis": True,
                    "supports_implementation_planning": True
                }
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Requires API key for authentication"
                )
            },
            defaultInputModes=["text", "data"],
            defaultOutputModes=["text", "data", "file"],
            supportsAuthenticatedExtendedCard=True
        )
        
        # Validation Agent Card
        self.agent_cards["validation_agent"] = ADKAgentCard(
            name="Data Validation and Quality Agent",
            description="Validates and quality-checks all data, analysis results, and recommendations",
            url="/api/validation-agent",
            version="1.0.0",
            provider=AgentProvider(
                name="Climate Risk Analysis System",
                version="1.0.0",
                description="Multi-agent climate risk analysis platform"
            ),
            documentationUrl="/docs/validation-agent",
            capabilities=AgentCapabilities(
                skills=[
                    {
                        "name": "validate_and_geocode",
                        "description": "Validates and geocodes addresses for analysis",
                        "parameters": {
                            "address": {"type": "string", "required": True},
                            "validation_level": {"type": "string", "enum": ["basic", "strict"]},
                            "include_metadata": {"type": "boolean", "default": True}
                        }
                    },
                    {
                        "name": "validate_risk_analysis",
                        "description": "Quality-checks risk analysis results",
                        "parameters": {
                            "risk_analysis": {"type": "object", "required": True},
                            "validation_criteria": {"type": "array", "items": {"type": "string"}},
                            "confidence_threshold": {"type": "number", "default": 0.8}
                        }
                    },
                    {
                        "name": "verify_recommendations",
                        "description": "Verifies recommendation accuracy and feasibility",
                        "parameters": {
                            "recommendations": {"type": "object", "required": True},
                            "location": {"type": "string", "required": True},
                            "verification_level": {"type": "string", "enum": ["basic", "comprehensive"]}
                        }
                    }
                ],
                extensions={
                    "supports_streaming": True,
                    "supports_file_attachments": True,
                    "max_message_size": "10MB",
                    "supports_data_quality_scoring": True,
                    "supports_consistency_checks": True
                }
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Requires API key for authentication"
                )
            },
            defaultInputModes=["text", "data"],
            defaultOutputModes=["text", "data"],
            supportsAuthenticatedExtendedCard=True
        )
        
        # Greeting Agent Card
        self.agent_cards["greeting_agent"] = ADKAgentCard(
            name="User Interaction and Guidance Agent",
            description="Handles initial user interactions, explains system capabilities, and guides users through analysis",
            url="/api/greeting-agent",
            version="1.0.0",
            provider=AgentProvider(
                name="Climate Risk Analysis System",
                version="1.0.0",
                description="Multi-agent climate risk analysis platform"
            ),
            documentationUrl="/docs/greeting-agent",
            capabilities=AgentCapabilities(
                skills=[
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
                extensions={
                    "supports_streaming": True,
                    "supports_interactive_guidance": True,
                    "max_message_size": "10MB",
                    "supports_user_onboarding": True,
                    "supports_context_awareness": True
                }
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Requires API key for authentication"
                )
            },
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            supportsAuthenticatedExtendedCard=True
        )
        
        # Farewell Agent Card
        self.agent_cards["farewell_agent"] = ADKAgentCard(
            name="Session Completion and Summary Agent",
            description="Handles user session completion, provides summary of results, and offers next steps",
            url="/api/farewell-agent",
            version="1.0.0",
            provider=AgentProvider(
                name="Climate Risk Analysis System",
                version="1.0.0",
                description="Multi-agent climate risk analysis platform"
            ),
            documentationUrl="/docs/farewell-agent",
            capabilities=AgentCapabilities(
                skills=[
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
                extensions={
                    "supports_streaming": True,
                    "supports_file_generation": True,
                    "max_message_size": "10MB",
                    "supports_session_archiving": True,
                    "supports_followup_scheduling": True
                }
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Requires API key for authentication"
                )
            },
            defaultInputModes=["text", "data"],
            defaultOutputModes=["text", "data", "file"],
            supportsAuthenticatedExtendedCard=True
        )
    
    def get_agent_card(self, agent_name: str) -> Optional[ADKAgentCard]:
        """Get agent card by name."""
        return self.agent_cards.get(agent_name)
    
    def list_agent_cards(self) -> List[Dict[str, Any]]:
        """List all agent cards for discovery."""
        return [card.to_dict() for card in self.agent_cards.values()]
    
    def validate_agent_card(self, agent_name: str) -> bool:
        """Validate agent card against ADK schema."""
        card = self.get_agent_card(agent_name)
        if not card:
            return False
        
        # Validate required fields
        required_fields = ["name", "description", "url", "version", "capabilities"]
        for field in required_fields:
            if not getattr(card, field, None):
                return False
        
        return True

class ADKAgentCoordinator:
    """Coordinate agents using ADK while maintaining custom components."""
    
    def __init__(
        self,
        project_id: str = "your-project-id",
        location: str = "us-central1",
        max_concurrent_tasks: int = 5
    ):
        """Initialize the coordinator.
        
        Args:
            project_id (str): Google Cloud project ID
            location (str): Google Cloud location
            max_concurrent_tasks (int): Maximum number of concurrent tasks
        """
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # Initialize coordinator
        self.coordinator = CoordinatorAgent(
            max_concurrent_tasks=max_concurrent_tasks,
            project_id=project_id,
            location=location
        )
        
        # Initialize communication manager
        self.communication_manager = None
    
    def set_session(self, session: AnalysisSession) -> None:
        """Set the current session.
        
        Args:
            session (AnalysisSession): Current analysis session
        """
        self.communication_manager = CommunicationManager(session)
        self.coordinator.set_session(session)
    
    async def handle_request(
        self,
        request: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Handle a user request.
        
        Args:
            request (Dict[str, Any]): User request
            session_id (str): Session identifier
            
        Returns:
            Dict[str, Any]: Response to request
        """
        try:
            # Create or get session
            if not self.communication_manager:
                session = AnalysisSession(
                    session_id=session_id,
                    created_at=datetime.now()
                )
                self.set_session(session)
            
            # Prepare tasks for parallel execution
            tasks = self._prepare_tasks(request)
            
            # Execute tasks in parallel
            results = await self.coordinator.execute_tasks_parallel(
                tasks=tasks,
                session_id=session_id
            )
            
            # Get token usage statistics
            token_usage = self.coordinator.get_token_usage()
            
            # Get artifact statistics
            artifact_stats = await self.coordinator.artifact_manager.get_artifact_stats(
                session_id=session_id
            )
            
            # Get session status
            session_status = self.communication_manager.shared_state.get_session_status()
            
            return {
                "status": "success",
                "results": results,
                "token_usage": token_usage,
                "artifact_stats": artifact_stats,
                "session_status": session_status
            }
            
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _prepare_tasks(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare tasks for parallel execution.
        
        Args:
            request (Dict[str, Any]): User request
            
        Returns:
            List[Dict[str, Any]]: List of tasks to execute
        """
        tasks = []
        
        # Add risk analysis task
        if "location" in request:
            tasks.append({
                "agent_id": "risk_analyzer",
                "type": "analyze_risk",
                "input": {
                    "location": request["location"],
                    "risk_type": request.get("risk_type", "all"),
                    "timeframe": request.get("timeframe", "current")
                }
            })
        
        # Add recommendation task
        if "generate_recommendations" in request:
            tasks.append({
                "agent_id": "recommendation",
                "type": "generate_recommendations",
                "input": {
                    "risk_analysis": request.get("risk_analysis", {}),
                    "location": request.get("location", "")
                }
            })
        
        return tasks
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get current token usage statistics.
        
        Returns:
            Dict[str, Any]: Token usage statistics
        """
        return self.coordinator.get_token_usage()
    
    async def get_artifact_stats(self, session_id: str) -> Dict[str, Any]:
        """Get artifact statistics for a session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            Dict[str, Any]: Artifact statistics
        """
        return await self.coordinator.artifact_manager.get_artifact_stats(
            session_id=session_id
        )
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status.
        
        Returns:
            Dict[str, Any]: Session status
        """
        if not self.communication_manager:
            return {"status": "no_session"}
        
        return self.communication_manager.shared_state.get_session_status()
    
    async def get_session_status_by_id(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a session."""
        return await self.session_manager.get_session_context(session_id)
    
    async def reset_agent(self, session_id: str, agent_name: str) -> None:
        """Reset a specific agent in a session."""
        await self.session_manager.reset_agent(session_id, agent_name)
        
    async def get_token_usage_by_id(self, session_id: str) -> Dict[str, TokenUsage]:
        """Get token usage statistics for a session."""
        return {
            task_id: usage
            for task_id, usage in self.coordinator.token_usage.items()
            if task_id.startswith(session_id)
        }
        
    async def get_context_stats(self, session_id: str) -> Dict[str, Any]:
        """Get context compression statistics for a session."""
        context = self.coordinator.context_cache.get(session_id)
        if not context:
            return {}
            
        return {
            "original_size": context.original_size,
            "compressed_size": context.compressed_size,
            "compression_ratio": context.compression_ratio,
            "last_compressed": context.last_compressed.isoformat()
        }

class ADKClient:
    """Client for interacting with the ADK service.
    
    This class provides a comprehensive interface for communicating with
    the ADK service, handling responses, and managing errors.
    
    Key Features:
        - Async HTTP communication
        - Response processing
        - Error handling
        - Configuration management
    
    State Management:
        - Maintains session state
        - Tracks request status
        - Manages error states
        - Handles configuration
    
    Example:
        ```python
        client = ADKClient(
            base_url="https://adk-service.example.com",
            api_key="your-api-key"
        )
        
        # Make analysis request
        response = await client.request(
            endpoint="analyze",
            data={"location": "New York"}
        )
        ```
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize the ADK client.
        
        Args:
            base_url (str): Base URL for ADK service
            api_key (str): API key for authentication
            timeout (int): Request timeout in seconds
            max_retries (int): Maximum retry attempts
            
        Initialization:
            - Sets up HTTP session
            - Configures timeouts
            - Initializes retry policy
            - Sets up logging
            
        Example:
            ```python
            client = ADKClient(
                base_url="https://adk-service.example.com",
                api_key="your-api-key",
                timeout=30,
                max_retries=3
            )
            ```
        """
        # ... existing code ...

    async def request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        method: str = "POST"
    ) -> "ADKResponse":
        """Make a request to the ADK service.
        
        Args:
            endpoint (str): Service endpoint
            data (Dict[str, Any], optional): Request data
            method (str): HTTP method
            
        Returns:
            ADKResponse: Service response
            
        Request Process:
            1. Validates request
            2. Prepares headers
            3. Makes HTTP request
            4. Processes response
            5. Returns result
            
        Example:
            ```python
            response = await client.request(
                endpoint="analyze",
                data={"location": "New York"},
                method="POST"
            )
            ```
        """
        # ... existing code ...

    async def close(self) -> None:
        """Close the ADK client session.
        
        Cleanup Process:
            1. Closes HTTP session
            2. Cleans up resources
            3. Resets state
            
        Example:
            ```python
            await client.close()
            ```
        """
        # ... existing code ...

class ADKResponse:
    """Response from the ADK service.
    
    This class represents a response from the ADK service,
    including success status, data, and error information.
    
    Attributes:
        is_success (bool): Whether the request was successful
        data (Dict[str, Any]): Response data
        error (Optional[ADKError]): Error information
        
    Example:
        ```python
        response = ADKResponse(
            is_success=True,
            data={"result": "success"}
        )
        ```
    """
    
    def __init__(
        self,
        is_success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional["ADKError"] = None
    ):
        """Initialize the ADK response.
        
        Args:
            is_success (bool): Success status
            data (Dict[str, Any], optional): Response data
            error (ADKError, optional): Error information
            
        Example:
            ```python
            response = ADKResponse(
                is_success=True,
                data={"result": "success"}
            )
            ```
        """
        # ... existing code ...

class ADKError:
    """Error from the ADK service.
    
    This class represents an error from the ADK service,
    including error code, message, and details.
    
    Attributes:
        code (str): Error code
        message (str): Error message
        details (Optional[Dict[str, Any]]): Additional details
        
    Example:
        ```python
        error = ADKError(
            code="INVALID_REQUEST",
            message="Invalid request parameters"
        )
        ```
    """
    
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the ADK error.
        
        Args:
            code (str): Error code
            message (str): Error message
            details (Dict[str, Any], optional): Additional details
            
        Example:
            ```python
            error = ADKError(
                code="INVALID_REQUEST",
                message="Invalid request parameters"
            )
            ```        """
        # ... existing code ... 

# Define custom function tools
def analyze_climate_risk(location: str, time_period: str):
    """
    Analyzes climate risks for a given location and time period.

    Args:
        location (str): The location to analyze (e.g., "New York", "London")
        time_period (str): The time period for analysis (e.g., "2024-2025", "next 5 years")

    Returns:
        dict: Analysis results including risk levels and recommendations
    """
    try:
        # Implementation here
        return {
            "status": "success",
            "location": location,
            "time_period": time_period,
            "risks": [],
            "recommendations": []
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }

def get_weather_data(location: str):
    """
    Retrieves weather data for a given location.

    Args:
        location (str): The location to get weather data for

    Returns:
        dict: Weather data including temperature, precipitation, etc.
    """
    try:
        # Implementation here
        return {
            "status": "success",
            "location": location,
            "temperature": 0,
            "precipitation": 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }

# Create the agent with our custom tools
climate_agent = Agent(
    model='gemini-2.0-flash',
    name='climate_agent',
    instruction='You are an expert climate risk analyst. Use the provided tools to analyze climate risks and provide recommendations.',
    description='Agent for analyzing climate risks and providing recommendations',
    tools=[analyze_climate_risk, get_weather_data]  # Add our functions directly to tools list
)
