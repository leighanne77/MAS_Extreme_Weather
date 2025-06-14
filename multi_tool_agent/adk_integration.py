"""
ADK Integration System for Multi-Agent Climate Risk Analysis

This module implements the integration with the ADK (Agent Development Kit) system,
providing a bridge between the multi-agent climate risk analysis system and ADK services.

Key Components:
    - ADKClient: Main client for ADK service interaction
    - ADKResponse: Response data structure
    - ADKError: Error handling and reporting
    - ADKConfig: Configuration management

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
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import zlib
from collections import defaultdict

from google.adk import Tool
from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from vertexai.preview.agent import ToolConfig

from .session_manager import SessionManager, AnalysisSession
from .weather_risks import ClimateRiskAnalyzer
from .risk_definitions import severity_levels, RiskSource, RiskThreshold, RiskType, RiskLevel
from .enhanced_coordinator import EnhancedADKCoordinator, TokenUsage, CompressedContext
from .communication import CommunicationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Initialize enhanced coordinator
        self.coordinator = EnhancedADKCoordinator(
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
    ) -> ADKResponse:
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
        error: Optional[ADKError] = None
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
            ```
        """
        # ... existing code ... 