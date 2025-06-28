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

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from google.adk.agents import Agent
from google.cloud import aiplatform

from .a2a import A2AMessage, A2AMessagePart, PartType
from .communication import CommunicationManager
from .coordinator import CoordinatorAgent, TokenUsage
from .session_manager import AnalysisSession, SessionManager

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
    skills: list[dict[str, Any]]
    extensions: dict[str, Any] = field(default_factory=dict)

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
    iconUrl: str | None = None
    provider: AgentProvider | None = None
    documentationUrl: str | None = None
    securitySchemes: dict[str, SecurityScheme] | None = None
    security: list[dict[str, list[str]]] | None = None
    defaultInputModes: list[str] = field(default_factory=lambda: ["text", "data"])
    defaultOutputModes: list[str] = field(default_factory=lambda: ["text", "data"])
    skills: list[dict[str, Any]] = field(default_factory=list)
    supportsAuthenticatedExtendedCard: bool = False

    def to_dict(self) -> dict[str, Any]:
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

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

class ADKAgentCardManager:
    """Manages ADK agent cards for A2A protocol compliance."""

    def __init__(self):
        self.cards: dict[str, ADKAgentCard] = {}
        self._initialize_agent_cards()

    def _initialize_agent_cards(self):
        """Initialize default agent cards."""
        # Climate Risk Analyzer Agent Card
        climate_risk_card = ADKAgentCard(
            name="climate_risk_analyzer",
            description="Specialized agent for comprehensive extreme weather risk analysis and assessment",
            url="https://api.tool.com/agents/climate_risk_analyzer",
            version="1.0.0",
            capabilities=AgentCapabilities(
                skills=[
                    {
                        "name": "analyze_weather_risks",
                        "description": "Analyzes extreme weather risks for a specific location and time period",
                        "parameters": {
                            "location": {"type": "string", "description": "Geographic location identifier"},
                            "time_period": {"type": "string", "description": "Time period for analysis"},
                            "risk_types": {"type": "array", "items": {"type": "string"}, "description": "Types of risks to analyze"}
                        }
                    },
                    {
                        "name": "get_risk_thresholds",
                        "description": "Retrieves risk thresholds for a location",
                        "parameters": {
                            "location": {"type": "string", "description": "Geographic location identifier"},
                            "risk_type": {"type": "string", "description": "Type of risk threshold to retrieve"}
                        }
                    }
                ],
                extensions={
                    "supports_streaming": True,
                    "supports_file_attachments": True,
                    "max_message_size": "10MB"
                }
            ),
            provider=AgentProvider(
                name="Tool Climate Risk Analysis Team",
                version="1.0.0",
                description="Specialized team for extreme weather risk analysis"
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Bearer token authentication"
                )
            }
        )

        # Nature-Based Solutions Agent Card
        nbs_card = ADKAgentCard(
            name="nature_based_solutions_agent",
            description="Agent for retrieving and analyzing nature-based solutions for extreme weather resilience",
            url="https://api.tool.com/agents/nature_based_solutions",
            version="1.0.0",
            capabilities=AgentCapabilities(
                skills=[
                    {
                        "name": "get_nbs_solutions",
                        "description": "Retrieves nature-based solutions for specific risks and locations",
                        "parameters": {
                            "location": {"type": "string", "description": "Geographic location"},
                            "risk_types": {"type": "array", "items": {"type": "string"}, "description": "Types of risks"},
                            "solution_scale": {"type": "string", "description": "Scale of solution needed"}
                        }
                    },
                    {
                        "name": "calculate_cost_benefit",
                        "description": "Calculates cost-benefit analysis for nature-based solutions",
                        "parameters": {
                            "solution_id": {"type": "string", "description": "Solution identifier"},
                            "property_value": {"type": "number", "description": "Property value for ROI calculation"},
                            "timeframe_years": {"type": "number", "description": "Analysis timeframe in years"}
                        }
                    }
                ],
                extensions={
                    "supports_streaming": True,
                    "supports_file_attachments": False,
                    "max_message_size": "5MB"
                }
            ),
            provider=AgentProvider(
                name="Tool Nature-Based Solutions Team",
                version="1.0.0",
                description="Specialized team for nature-based solutions analysis"
            ),
            securitySchemes={
                "bearer": SecurityScheme(
                    type="bearer",
                    description="Bearer token authentication"
                )
            }
        )

        # Register the cards
        self.register_card(climate_risk_card)
        self.register_card(nbs_card)

    def register_card(self, card: ADKAgentCard):
        """Register an agent card."""
        self.cards[card.name] = card
        logger.info(f"Registered agent card: {card.name}")

    def get_agent_card(self, agent_name: str) -> ADKAgentCard | None:
        """Get agent card by name."""
        return self.cards.get(agent_name)

    def list_agent_cards(self) -> list[dict[str, Any]]:
        """List all agent cards as dictionaries."""
        return [card.to_dict() for card in self.cards.values()]

    def validate_agent_card(self, agent_name: str) -> bool:
        """Validate agent card against A2A protocol requirements."""
        card = self.cards.get(agent_name)
        if not card:
            return False

        # Check required fields
        required_fields = ["name", "description", "url", "version", "capabilities"]
        for field in required_fields:
            if not getattr(card, field, None):
                logger.error(f"Agent card {agent_name} missing required field: {field}")
                return False

        return True

class ADKAgentCoordinator:
    """Coordinates ADK agents for multi-agent climate risk analysis."""

    def __init__(
        self,
        project_id: str = "your-project-id",
        location: str = "us-central1",
        max_concurrent_tasks: int = 5
    ):
        self.project_id = project_id
        self.location = location
        self.max_concurrent_tasks = max_concurrent_tasks
        self.session_manager = SessionManager()
        self.coordinator = CoordinatorAgent()
        self.communication_manager = CommunicationManager()
        self.card_manager = ADKAgentCardManager()

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

        # Performance tracking
        self.token_usage = TokenUsage()
        self.performance_metrics = defaultdict(list)

        logger.info(f"ADK Agent Coordinator initialized for project: {project_id}")

    def set_session(self, session: AnalysisSession) -> None:
        """Set the current analysis session."""
        self.session_manager.set_session(session)
        logger.info(f"Session set: {session.session_id}")

    async def handle_request(
        self,
        request: dict[str, Any],
        session_id: str
    ) -> dict[str, Any]:
        """Handle incoming requests using ADK agents."""
        start_time = datetime.now()

        try:
            # Validate session
            if not self.session_manager.validate_session(session_id):
                return {
                    "status": "error",
                    "error": "Invalid session",
                    "session_id": session_id
                }

            # Extract request parameters
            location = request.get("location", "")
            time_period = request.get("time_period", "7_years")
            risk_types = request.get("risk_types", ["all"])
            user_type = request.get("user_type", "general")

            # Create A2A message for processing
            text_part = A2AMessagePart(
                kind=PartType.TEXT,
                text=f"Analyze extreme weather risks for {location} over {time_period}"
            )
            data_part = A2AMessagePart(
                kind=PartType.DATA,
                data={
                    "location": location,
                    "time_period": time_period,
                    "risk_types": risk_types,
                    "user_type": user_type,
                    "session_id": session_id
                }
            )

            message = A2AMessage(
                role="user",
                parts=[text_part, data_part]
            )

            # Process with coordinator
            result = await self.coordinator.process_request(message)

            # Track performance
            processing_time = (datetime.now() - start_time).total_seconds()
            self.performance_metrics["request_processing_time"].append(processing_time)

            # Update session
            self.session_manager.update_session_activity(session_id)

            return {
                "status": "success",
                "result": result,
                "session_id": session_id,
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id
            }

    def _prepare_tasks(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        """Prepare tasks for ADK agents."""
        tasks = []

        # Weather risk analysis task
        if "location" in request:
            tasks.append({
                "agent": "climate_risk_analyzer",
                "task": "analyze_weather_risks",
                "parameters": {
                    "location": request["location"],
                    "time_period": request.get("time_period", "7_years"),
                    "risk_types": request.get("risk_types", ["all"])
                }
            })

        # Nature-based solutions task
        if "risk_types" in request:
            tasks.append({
                "agent": "nature_based_solutions_agent",
                "task": "get_nbs_solutions",
                "parameters": {
                    "location": request.get("location", ""),
                    "risk_types": request["risk_types"],
                    "solution_scale": request.get("solution_scale", "medium")
                }
            })

        return tasks

    def get_token_usage(self) -> dict[str, Any]:
        """Get current token usage statistics."""
        return {
            "total_tokens": self.token_usage.total_tokens,
            "prompt_tokens": self.token_usage.prompt_tokens,
            "completion_tokens": self.token_usage.completion_tokens,
            "cost_estimate": self.token_usage.cost_estimate
        }

    async def get_artifact_stats(self, session_id: str) -> dict[str, Any]:
        """Get artifact statistics for a session."""
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            artifacts = session.get_artifacts()
            return {
                "session_id": session_id,
                "total_artifacts": len(artifacts),
                "artifact_types": list({artifact.type for artifact in artifacts}),
                "total_size": sum(artifact.size for artifact in artifacts)
            }
        except Exception as e:
            logger.error(f"Error getting artifact stats: {e}")
            return {"error": str(e)}

    def get_session_status(self) -> dict[str, Any]:
        """Get current session status."""
        return self.session_manager.get_session_status()

    async def get_session_status_by_id(self, session_id: str) -> dict[str, Any]:
        """Get session status by ID."""
        return self.session_manager.get_session_status_by_id(session_id)

    async def reset_agent(self, session_id: str, agent_name: str) -> None:
        """Reset a specific agent for a session."""
        self.coordinator.reset_agent(agent_name)
        logger.info(f"Reset agent {agent_name} for session {session_id}")

    async def get_token_usage_by_id(self, session_id: str) -> dict[str, TokenUsage]:
        """Get token usage for a specific session."""
        session = self.session_manager.get_session(session_id)
        if session:
            return session.get_token_usage()
        return {}

    async def get_context_stats(self, session_id: str) -> dict[str, Any]:
        """Get context statistics for a session."""
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            context = session.get_context()
            return {
                "session_id": session_id,
                "context_size": len(context),
                "context_tokens": sum(len(str(item).split()) for item in context),
                "context_types": list({type(item).__name__ for item in context})
            }
        except Exception as e:
            logger.error(f"Error getting context stats: {e}")
            return {"error": str(e)}

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
        data: dict[str, Any] | None = None,
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
        data: dict[str, Any] | None = None,
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
        details: dict[str, Any] | None = None
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
