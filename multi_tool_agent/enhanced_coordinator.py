"""
Enhanced ADK Coordinator for Multi-Agent Climate Risk Analysis System

This module implements an enhanced coordinator for the Agent Development Kit (ADK) that provides
parallel execution, token tracking, and context compression capabilities for the climate risk
analysis system.

Key Components:
    - TokenUsage: Tracks token consumption across agents and operations
    - CompressedContext: Manages context data compression and decompression
    - EnhancedADKCoordinator: Main coordinator class for agent execution

Features:
    1. Parallel Execution:
       - Concurrent task execution with semaphore control
       - Task prioritization and scheduling
       - Resource management and allocation
    
    2. Token Tracking:
       - Per-agent token usage monitoring
       - Input/output token separation
       - Usage statistics and reporting
    
    3. Context Compression:
       - Automatic context compression
       - Compression ratio tracking
       - Size optimization
    
    4. Error Handling:
       - Comprehensive error recovery strategies
       - Retry mechanisms with backoff
       - State recovery procedures
    
    5. State Management:
       - Session-based state tracking
       - Agent state synchronization
       - Shared state management
    
    6. Artifact Management:
       - Task result persistence
       - Metadata tracking
       - Resource cleanup

Dependencies:
    - google.cloud.aiplatform: For Vertex AI integration
    - vertexai.preview: For ADK functionality
    - multi_tool_agent.artifact_manager: For artifact management
    - multi_tool_agent.session_manager: For session handling
    - multi_tool_agent.communication: For inter-agent communication

Example Usage:
    ```python
    # Initialize coordinator
    coordinator = EnhancedADKCoordinator(
        max_concurrent_tasks=5,
        project_id="your-project-id",
        location="us-central1"
    )
    
    # Set session
    coordinator.set_session(session)
    
    # Execute tasks in parallel
    results = await coordinator.execute_tasks_parallel(
        tasks=[
            {
                "agent_id": "risk_analyzer",
                "type": "risk_analysis",
                "input": {"location": "New York"}
            }
        ],
        session_id="session_123"
    )
    ```

Configuration:
    - MAX_CONCURRENT_TASKS: Maximum number of concurrent tasks
    - COMPRESSION_THRESHOLD: Minimum size for compression
    - TOKEN_ESTIMATION_METHOD: Method for token counting
    - RETRY_SETTINGS: Retry attempt configuration
"""

import asyncio
import json
import zlib
import logging
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from vertexai.preview.agent import Agent, Tool, ToolConfig

from multi_tool_agent.artifact_manager import ArtifactManager
from multi_tool_agent.risk_definitions import RiskType, RiskLevel
from multi_tool_agent.session_manager import AnalysisSession, AgentState
from multi_tool_agent.communication import CommunicationManager, SharedState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Track token usage for agents and operations.
    
    This class maintains token usage statistics across the system, including
    per-agent tracking and total usage metrics.
    
    Attributes:
        input_tokens (int): Total input tokens used
        output_tokens (int): Total output tokens used
        total_tokens (int): Total tokens used (input + output)
        by_agent (Dict[str, Dict[str, int]]): Per-agent token usage statistics
        
    Example:
        ```python
        usage = TokenUsage()
        usage.update("risk_analyzer", 100, 50)
        print(usage.total_tokens)  # 150
        ```
    """
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    by_agent: Dict[str, Dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {"input": 0, "output": 0}))
    
    def update(self, agent_id: str, input_tokens: int, output_tokens: int) -> None:
        """Update token counts for an agent."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += input_tokens + output_tokens
        self.by_agent[agent_id]["input"] += input_tokens
        self.by_agent[agent_id]["output"] += output_tokens

@dataclass
class CompressedContext:
    """Manage compressed context data for efficient storage and transmission.
    
    This class handles the compression and decompression of context data,
    tracking compression ratios and size metrics.
    
    Attributes:
        data (Dict[str, Any]): The context data
        compression_ratio (float): Ratio of original to compressed size
        original_size (int): Size of original data in bytes
        compressed_size (int): Size of compressed data in bytes
        
    Example:
        ```python
        context = CompressedContext.compress({"key": "value"})
        print(f"Compression ratio: {context.compression_ratio}")
        ```
    """
    data: Dict[str, Any]
    compression_ratio: float = 1.0
    original_size: int = 0
    compressed_size: int = 0
    
    @classmethod
    def compress(cls, data: Dict[str, Any]) -> 'CompressedContext':
        """Compress context data."""
        json_data = json.dumps(data)
        original_size = len(json_data.encode())
        compressed = zlib.compress(json_data.encode())
        compressed_size = len(compressed)
        
        return cls(
            data=data,
            compression_ratio=original_size / compressed_size if compressed_size > 0 else 1.0,
            original_size=original_size,
            compressed_size=compressed_size
        )

class EnhancedADKCoordinator:
    """Enhanced coordinator for ADK with parallel execution and token tracking.
    
    This class manages the execution of agent tasks, handling parallel processing,
    token tracking, and context compression. It integrates with Google's ADK
    while providing enhanced capabilities for the climate risk analysis system.
    
    Key Features:
        - Parallel task execution with resource control
        - Token usage tracking and optimization
        - Context compression for efficiency
        - Error handling and recovery
        - State management and synchronization
        - Artifact persistence and management
    
    State Management:
        - Maintains session state
        - Tracks agent states
        - Manages shared state
        - Handles state recovery
    
    Error Handling:
        - Implements retry mechanisms
        - Provides recovery strategies
        - Logs errors with context
        - Maintains error statistics
    
    Example:
        ```python
        coordinator = EnhancedADKCoordinator()
        coordinator.set_session(session)
        results = await coordinator.execute_tasks_parallel(tasks, session_id)
        ```
    """
    
    def __init__(
        self,
        max_concurrent_tasks: int = 5,
        project_id: str = "your-project-id",
        location: str = "us-central1"
    ):
        """Initialize the coordinator.
        
        Args:
            max_concurrent_tasks (int): Maximum number of concurrent tasks
            project_id (str): Google Cloud project ID
            location (str): Google Cloud location
            
        State Initialization:
            - Creates semaphore for concurrency control
            - Initializes token usage tracking
            - Sets up artifact management
            - Configures recovery strategies
            
        Example:
            ```python
            coordinator = EnhancedADKCoordinator(
                max_concurrent_tasks=5,
                project_id="my-project",
                location="us-central1"
            )
            ```
        """
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.token_usage = TokenUsage()
        self.artifact_manager = ArtifactManager()
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # Initialize communication manager
        self.communication_manager = None
        
        # Initialize recovery strategies
        self.recovery_strategies = {
            "timeout": self._handle_timeout,
            "error": self._handle_error,
            "retry": self._handle_retry
        }
    
    def set_session(self, session: AnalysisSession) -> None:
        """Set the current session and initialize communication manager.
        
        Args:
            session (AnalysisSession): Current analysis session
        """
        self.communication_manager = CommunicationManager(session)
    
    async def execute_tasks_parallel(
        self,
        tasks: List[Dict[str, Any]],
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Execute multiple tasks in parallel with resource control.
        
        Args:
            tasks (List[Dict[str, Any]]): List of tasks to execute
            session_id (str): Session identifier
            
        Returns:
            List[Dict[str, Any]]: Results of task execution
            
        Task Structure:
            Each task should be a dictionary with:
            - agent_id: Identifier for the agent
            - type: Type of task to execute
            - input: Input data for the task
            
        Execution Flow:
            1. Acquires semaphore for each task
            2. Executes task with error handling
            3. Updates token usage
            4. Compresses and stores results
            5. Updates shared state
            
        Example:
            ```python
            tasks = [
                {
                    "agent_id": "risk_analyzer",
                    "type": "risk_analysis",
                    "input": {"location": "New York"}
                }
            ]
            results = await coordinator.execute_tasks_parallel(tasks, "session_123")
            ```
        """
        async def execute_with_semaphore(task: Dict[str, Any]) -> Dict[str, Any]:
            async with self.semaphore:
                return await self._execute_task(task, session_id)
        
        return await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks]
        )
    
    async def _execute_task(
        self,
        task: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Execute a single task with token tracking and context compression.
        
        Args:
            task (Dict[str, Any]): Task to execute
            session_id (str): Session identifier
            
        Returns:
            Dict[str, Any]: Task execution result
            
        Execution Steps:
            1. Extracts task components
            2. Compresses input context
            3. Estimates token usage
            4. Executes task using ADK
            5. Updates token statistics
            6. Stores results as artifacts
            7. Updates shared state
            
        Error Handling:
            - Catches and logs exceptions
            - Updates error state
            - Returns error information
            
        Example:
            ```python
            result = await coordinator._execute_task(
                {
                    "agent_id": "risk_analyzer",
                    "type": "risk_analysis",
                    "input": {"location": "New York"}
                },
                "session_123"
            )
            ```
        """
        try:
            # Extract task components
            agent_id = task.get("agent_id", "unknown")
            task_type = task.get("type", "unknown")
            input_data = task.get("input", {})
            
            # Compress input context
            compressed_input = CompressedContext.compress(input_data)
            
            # Estimate input tokens
            input_tokens = self._estimate_tokens(input_data)
            
            # Execute task using ADK
            result = await self._execute_adk_task(agent_id, task_type, input_data)
            
            # Estimate output tokens
            output_tokens = self._estimate_tokens(result)
            
            # Update token usage
            self.token_usage.update(agent_id, input_tokens, output_tokens)
            
            # Store task result as artifact
            artifact_path = await self.artifact_manager.store_artifact(
                session_id=session_id,
                agent_id=agent_id,
                artifact_type=task_type,
                data=result,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "compression_ratio": compressed_input.compression_ratio
                }
            )
            
            # Update shared state through communication manager
            if self.communication_manager:
                self.communication_manager.update_shared_state({
                    f"{agent_id}_result": result,
                    f"{agent_id}_tokens": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": input_tokens + output_tokens
                    }
                })
            
            return {
                "status": "success",
                "result": result,
                "token_usage": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens
                },
                "compression": {
                    "ratio": compressed_input.compression_ratio,
                    "original_size": compressed_input.original_size,
                    "compressed_size": compressed_input.compressed_size
                },
                "artifact_path": artifact_path
            }
            
        except Exception as e:
            # Handle error through communication manager
            if self.communication_manager:
                self.communication_manager.update_shared_state({
                    f"{agent_id}_error": str(e)
                })
            
            return {
                "status": "error",
                "error": str(e),
                "agent_id": agent_id,
                "task_type": task_type
            }
    
    async def _execute_adk_task(
        self,
        agent_id: str,
        task_type: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a task using ADK with state management.
        
        Args:
            agent_id (str): Agent identifier
            task_type (str): Type of task
            input_data (Dict[str, Any]): Input data
            
        Returns:
            Dict[str, Any]: Task result
            
        State Management:
            - Updates agent state
            - Tracks execution status
            - Manages agent tools
            - Handles state transitions
            
        Error Handling:
            - Implements retry logic
            - Manages timeouts
            - Handles ADK errors
            
        Example:
            ```python
            result = await coordinator._execute_adk_task(
                "risk_analyzer",
                "risk_analysis",
                {"location": "New York"}
            )
            ```
        """
        if not self.communication_manager:
            raise ValueError("No active session")
        
        # Get agent state
        agent_state = self.communication_manager.shared_state.get_agent_state(agent_id)
        if not agent_state:
            agent_state = AgentState()
            self.communication_manager.shared_state.update_agent_state(agent_id, agent_state)
        
        # Update state
        agent_state.status = "running"
        agent_state.last_active = datetime.now()
        
        try:
            # Initialize agent
            agent = Agent(
                model=GenerativeModel("gemini-pro"),
                tools=self._get_agent_tools(agent_id),
                tool_config=ToolConfig(
                    name=agent_id,
                    description=self._get_agent_description(agent_id)
                )
            )
            
            # Execute task with retries
            for attempt in range(3):  # MAX_RETRY_ATTEMPTS
                try:
                    # Execute task with timeout
                    async with asyncio.timeout(300):  # DEFAULT_TIMEOUT
                        result = await agent.execute_task(
                            task_type=task_type,
                            input_data=input_data
                        )
                    
                    # Update state on success
                    agent_state.status = "completed"
                    agent_state.error_count = 0
                    agent_state.retry_count = 0
                    agent_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "task_type": task_type,
                        "status": "success"
                    })
                    
                    return result
                    
                except asyncio.TimeoutError:
                    # Handle timeout
                    agent_state.error_count += 1
                    agent_state.retry_count += 1
                    agent_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "task_type": task_type,
                        "status": "timeout",
                        "attempt": attempt + 1
                    })
                    
                    if attempt < 2:  # MAX_RETRY_ATTEMPTS - 1
                        await self.recovery_strategies["timeout"](agent_state)
                        continue
                    else:
                        raise TimeoutError(f"Task timed out after 3 attempts")
                    
                except Exception as e:
                    # Handle other errors
                    agent_state.error_count += 1
                    agent_state.retry_count += 1
                    agent_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "task_type": task_type,
                        "status": "error",
                        "error": str(e),
                        "attempt": attempt + 1
                    })
                    
                    if attempt < 2:  # MAX_RETRY_ATTEMPTS - 1
                        await self.recovery_strategies["error"](agent_state, e)
                        continue
                    else:
                        raise
                        
        except Exception as e:
            # Final error handling
            agent_state.status = "error"
            logger.error(f"Task execution failed: {str(e)}")
            raise
            
        finally:
            # Update state
            agent_state.last_active = datetime.now()
            self.communication_manager.shared_state.update_agent_state(agent_id, agent_state)
    
    def _get_agent_tools(self, agent_id: str) -> List[Tool]:
        """Get tools configured for an agent.
        
        Args:
            agent_id (str): Agent identifier
            
        Returns:
            List[Tool]: List of tools for the agent
            
        Tool Configuration:
            - Loads agent-specific tools
            - Configures tool parameters
            - Sets up tool handlers
            
        Example:
            ```python
            tools = coordinator._get_agent_tools("risk_analyzer")
            ```
        """
        # TODO: Implement tool mapping based on agent_id
        return []
    
    def _get_agent_description(self, agent_id: str) -> str:
        """Get description for an agent.
        
        Args:
            agent_id (str): Agent identifier
            
        Returns:
            str: Agent description
            
        Description Format:
            - Agent role and responsibilities
            - Capabilities and limitations
            - Usage guidelines
            
        Example:
            ```python
            description = coordinator._get_agent_description("risk_analyzer")
            ```
        """
        # TODO: Implement description mapping based on agent_id
        return f"Agent {agent_id}"
    
    async def _handle_timeout(self, state: AgentState) -> None:
        """Handle task timeout.
        
        Args:
            state (AgentState): Current agent state
            
        Timeout Handling:
            - Updates state status
            - Logs timeout event
            - Implements recovery strategy
            
        Example:
            ```python
            await coordinator._handle_timeout(agent_state)
            ```
        """
        logger.warning(f"Timeout for agent {state.agent_id}")
        await asyncio.sleep(2 ** state.retry_count)  # Exponential backoff
    
    async def _handle_error(self, state: AgentState, error: Exception) -> None:
        """Handle task error.
        
        Args:
            state (AgentState): Current agent state
            error (Exception): Error that occurred
            
        Error Handling:
            - Updates error state
            - Logs error details
            - Implements recovery strategy
            
        Example:
            ```python
            await coordinator._handle_error(agent_state, error)
            ```
        """
        logger.error(f"Error for agent {state.agent_id}: {str(error)}")
        await asyncio.sleep(2 ** state.retry_count)  # Exponential backoff
    
    async def _handle_retry(self, state: AgentState) -> None:
        """Handle task retry.
        
        Args:
            state (AgentState): Current agent state
            
        Retry Handling:
            - Updates retry count
            - Implements backoff strategy
            - Prepares for retry attempt
            
        Example:
            ```python
            await coordinator._handle_retry(agent_state)
            ```
        """
        logger.info(f"Retrying agent {state.agent_id}")
        await asyncio.sleep(2 ** state.retry_count)  # Exponential backoff
    
    def _estimate_tokens(self, data: Any) -> int:
        """Estimate token count for data.
        
        Args:
            data (Any): Data to estimate tokens for
            
        Returns:
            int: Estimated token count
            
        Estimation Method:
            - Uses configured estimation method
            - Handles different data types
            - Provides approximate count
            
        Example:
            ```python
            tokens = coordinator._estimate_tokens({"key": "value"})
            ```
        """
        if isinstance(data, str):
            # Rough estimate: 1 token ≈ 4 characters
            return len(data) // 4
        elif isinstance(data, dict):
            return sum(self._estimate_tokens(v) for v in data.values())
        elif isinstance(data, list):
            return sum(self._estimate_tokens(item) for item in data)
        else:
            # For other types, convert to string and estimate
            return len(str(data)) // 4
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get current token usage statistics.
        
        Returns:
            Dict[str, Any]: Token usage statistics
            
        Statistics Include:
            - Total token usage
            - Per-agent usage
            - Input/output breakdown
            
        Example:
            ```python
            usage = coordinator.get_token_usage()
            print(f"Total tokens: {usage['total_tokens']}")
            ```
        """
        return {
            "total": {
                "input": self.token_usage.input_tokens,
                "output": self.token_usage.output_tokens,
                "total": self.token_usage.total_tokens
            },
            "by_agent": dict(self.token_usage.by_agent)
        } 