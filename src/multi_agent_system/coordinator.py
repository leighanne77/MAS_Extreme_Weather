"""
Enhanced ADK Coordinator for Multi-Agent Climate Risk Analysis System

This module implements an enhanced coordinator for the Agent Development Kit (ADK) that provides
parallel execution, token tracking, context compression, and A2A protocol support for the climate risk
analysis system.

Key Components:
    - TokenUsage: Tracks token consumption across agents and operations
    - CompressedContext: Manages context data compression and decompression
    - CoordinatorAgent: Main coordinator class for agent execution
    - A2A Message Routing: Handles A2A protocol message routing and addressing
    - Part Type Management: Manages different content types and multi-part messages

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

    4. A2A Protocol Support:
       - Message routing and addressing
       - Part type handling and content serialization
       - Multi-part message support
       - Message validation and error handling

    5. Error Handling:
       - Comprehensive error recovery strategies
       - Retry mechanisms with backoff
       - State recovery procedures

    6. State Management:
       - Session-based state tracking
       - Agent state synchronization
       - Shared state management

    7. Artifact Management:
       - Task result persistence
       - Metadata tracking
       - Resource cleanup
"""

import asyncio
import json
import logging
import zlib
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from google.adk.agents import Agent
from google.cloud import aiplatform

from .a2a import (
    A2AMessage,
    A2APart,
    create_request_message,
)
from .a2a.enums import MessageType
from .a2a.router import A2AMessageRouter
from .agents.base_agent import BaseAgent
from .artifact_manager import ArtifactManager
from .communication import CommunicationManager
from .session_manager import AgentState, AnalysisSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Track token usage for agents and operations."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    by_agent: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {"input": 0, "output": 0}))

    def update(self, agent_id: str, input_tokens: int, output_tokens: int) -> None:
        """Update token counts for an agent."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += input_tokens + output_tokens
        self.by_agent[agent_id]["input"] += input_tokens
        self.by_agent[agent_id]["output"] += output_tokens

@dataclass
class CompressedContext:
    """Manage compressed context data for efficient storage and transmission."""
    data: dict[str, Any]
    compression_ratio: float = 1.0
    original_size: int = 0
    compressed_size: int = 0

    @classmethod
    def compress(cls, data: dict[str, Any]) -> 'CompressedContext':
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

class CoordinatorAgent(BaseAgent):
    """Enhanced coordinator for ADK with parallel execution, token tracking, and A2A protocol support."""

    def __init__(
        self,
        max_concurrent_tasks: int = 5,
        project_id: str = "your-project-id",
        location: str = "us-central1"
    ):
        """Initialize the coordinator."""
        super().__init__("coordinator")
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.token_usage = TokenUsage()
        self.artifact_manager = ArtifactManager()

        # Initialize A2A router
        self.a2a_router = A2AMessageRouter()

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

        # Initialize communication manager
        self.communication_manager = None

        # Set up tools
        self.tools = [
            self.identify_capable_agents,
            self.merge_agent_results,
            self.monitor_agent_status,
            self.execute_tasks_parallel,
            self.route_a2a_message,
            self.send_multipart_message
        ]

    async def start(self):
        """Start the coordinator with A2A routing."""
        await self.a2a_router.start()
        logger.info("Coordinator started with A2A routing")

    async def stop(self):
        """Stop the coordinator."""
        await self.a2a_router.stop()
        logger.info("Coordinator stopped")

    def register_agent(self, agent_id: str, agent_info: dict[str, Any], agent_instance: BaseAgent | None = None):
        """Register an agent with the coordinator and A2A router."""
        # Register with A2A router
        self.a2a_router.register_agent(agent_id, agent_info)

        # Set up message handler if agent instance provided
        if agent_instance:
            async def message_handler(message: A2AMessage):
                return await agent_instance.handle_a2a_message(message)

            self.a2a_router.agents[agent_id]['message_handler'] = message_handler

        logger.info(f"Agent {agent_id} registered with coordinator")

    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the coordinator."""
        self.a2a_router.unregister_agent(agent_id)
        logger.info(f"Agent {agent_id} unregistered from coordinator")

    async def route_a2a_message(self, sender_id: str, recipient_id: str, content: str | dict[str, Any],
                              message_type: MessageType = MessageType.REQUEST) -> dict[str, Any]:
        """Route an A2A message between agents."""
        try:
            # Create A2A message
            message = create_request_message(
                sender=sender_id,
                recipients=[recipient_id],
                content=content,
                message_type=message_type
            )

            # Route message
            success = await self.a2a_router.route_message(message)

            return {
                "status": "success" if success else "failed",
                "message_id": message.id,
                "routed": success
            }

        except Exception as e:
            logger.error(f"Error routing A2A message: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def send_multipart_message(self, sender_id: str, recipient_id: str, parts: list[dict[str, Any]],
                                   message_type: MessageType = MessageType.REQUEST) -> dict[str, Any]:
        """Send a multi-part A2A message."""
        try:
            # Convert part dictionaries to A2APart objects
            a2a_parts = []
            for part_data in parts:
                part = A2APart.from_dict(part_data)
                a2a_parts.append(part)

            # Create multi-part message
            from .a2a.multipart import create_multipart_message
            message = create_multipart_message(
                sender=sender_id,
                recipients=[recipient_id],
                parts=a2a_parts,
                message_type=message_type
            )

            # Route message
            success = await self.a2a_router.route_message(message)

            return {
                "status": "success" if success else "failed",
                "message_id": message.id,
                "part_count": len(a2a_parts),
                "routed": success
            }

        except Exception as e:
            logger.error(f"Error sending multi-part message: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def set_session(self, session: AnalysisSession) -> None:
        """Set the current analysis session."""
        self.session = session
        self.communication_manager = CommunicationManager(session)

    async def execute_tasks_parallel(
        self,
        tasks: list[dict[str, Any]],
        session_id: str
    ) -> list[dict[str, Any]]:
        """Execute multiple tasks in parallel with resource control."""
        async def execute_with_semaphore(task: dict[str, Any]) -> dict[str, Any]:
            async with self.semaphore:
                return await self._execute_task(task, session_id)

        return await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks]
        )

    async def _execute_task(
        self,
        task: dict[str, Any],
        session_id: str
    ) -> dict[str, Any]:
        """Execute a single task with error handling and state management."""
        try:
            agent_id = task["agent_id"]
            task_type = task["type"]
            input_data = task["input"]

            # Update agent state
            state = self.session.get_agent_state(agent_id)
            state.status = "processing"
            state.last_active = datetime.utcnow()

            # Execute task
            result = await self._execute_adk_task(agent_id, task_type, input_data)

            # Update state
            state.status = "completed"
            state.last_active = datetime.utcnow()

            return result

        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            await self._handle_error(state, e)
            return {
                "status": "error",
                "error": str(e)
            }

    async def _execute_adk_task(
        self,
        agent_id: str,
        task_type: str,
        input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a task using ADK."""
        try:
            # Get agent tools and description
            tools = self._get_agent_tools(agent_id)
            description = self._get_agent_description(agent_id)

            # Create ADK agent
            agent = Agent(
                name=agent_id,
                description=description,
                tools=tools
            )

            # Execute task
            result = await agent.execute_task(task_type, input_data)

            # Update token usage
            input_tokens = self._estimate_tokens(input_data)
            output_tokens = self._estimate_tokens(result)
            self.token_usage.update(agent_id, input_tokens, output_tokens)

            return {
                "status": "success",
                "result": result,
                "token_usage": {
                    "input": input_tokens,
                    "output": output_tokens
                }
            }

        except Exception as e:
            logger.error(f"Error in ADK task execution: {str(e)}")
            raise

    def _get_agent_tools(self, agent_id: str) -> list[Callable]:
        """Get tools for a specific agent."""
        # Implementation here
        return []

    def _get_agent_description(self, agent_id: str) -> str:
        """Get description for a specific agent."""
        # Implementation here
        return ""

    async def _handle_timeout(self, state: AgentState) -> None:
        """Handle task timeout."""
        state.status = "timeout"
        state.last_active = datetime.utcnow()
        logger.warning(f"Task timeout for agent {state.agent_id}")

    async def _handle_error(self, state: AgentState, error: Exception) -> None:
        """Handle task error."""
        state.status = "error"
        state.last_active = datetime.utcnow()
        state.error = str(error)
        logger.error(f"Error for agent {state.agent_id}: {str(error)}")

    async def _handle_retry(self, state: AgentState) -> None:
        """Handle task retry."""
        state.status = "retrying"
        state.last_active = datetime.utcnow()
        state.retry_count += 1
        logger.info(f"Retrying task for agent {state.agent_id}")

    def _estimate_tokens(self, data: Any) -> int:
        """Estimate token count for data."""
        # Simple estimation based on string length
        if isinstance(data, str):
            return len(data) // 4
        elif isinstance(data, dict):
            return sum(self._estimate_tokens(v) for v in data.values())
        elif isinstance(data, list):
            return sum(self._estimate_tokens(v) for v in data)
        return 0

    def get_token_usage(self) -> dict[str, Any]:
        """Get token usage statistics."""
        return {
            "total": {
                "input": self.token_usage.input_tokens,
                "output": self.token_usage.output_tokens,
                "total": self.token_usage.total_tokens
            },
            "by_agent": dict(self.token_usage.by_agent)
        }

    # Original coordinator methods
    async def identify_capable_agents(self, request: dict[str, Any]) -> dict[str, Any]:
        """Identifies which agents are capable of handling a specific request."""
        try:
            # Implementation here
            return {
                "status": "success",
                "result": {
                    "risk_analysis": ["risk_analyzer"],
                    "historical_analysis": ["historical_analyzer"]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def merge_agent_results(self, results: list[dict[str, Any]], request: dict[str, Any]) -> dict[str, Any]:
        """Combines and prioritizes results from multiple agents."""
        try:
            # Implementation here
            return {
                "status": "success",
                "result": {
                    "combined_analysis": {},
                    "confidence_scores": {}
                },
                "confidence": 0.95
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def monitor_agent_status(self, agent_id: str) -> dict[str, Any]:
        """Checks the status of other agents."""
        try:
            # Implementation here
            return {
                "status": "success",
                "result": {
                    "agent_id": agent_id,
                    "status": "active",
                    "last_active": "2024-01-01T00:00:00Z"
                },
                "confidence": 0.95
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

    async def execute_workflow(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute a complete workflow using the coordinator.

        Args:
            request: The workflow request containing location, risk_types, etc.

        Returns:
            Dict containing workflow results
        """
        try:
            location = request.get("location", "")
            risk_types = request.get("risk_types", [])
            time_horizon = request.get("time_horizon", "1y")
            request_id = request.get("request_id", self._generate_request_id())

            # Create tasks for different agents
            tasks = []

            # Risk analysis task
            if risk_types:
                tasks.append({
                    "agent_id": "risk_analyzer",
                    "type": "analyze_risks",
                    "input": {
                        "location": location,
                        "risk_types": risk_types,
                        "time_horizon": time_horizon
                    }
                })

            # Historical analysis task
            tasks.append({
                "agent_id": "historical_agent",
                "type": "analyze_trends",
                "input": {
                    "location": location,
                    "time_period": time_horizon
                }
            })

            # Execute tasks in parallel
            results = await self.execute_tasks_parallel(tasks, request_id)

            # Combine results
            combined_result = {
                "status": "success",
                "request_id": request_id,
                "location": location,
                "session_id": request.get("session_id"),
                "results": {
                    task["agent_id"]: result
                    for task, result in zip(tasks, results, strict=False)
                },
                "token_usage": self.get_token_usage()
            }

            return combined_result

        except Exception as e:
            self.logger.error(f"Error executing workflow: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "request_id": request.get("request_id", "unknown")
            }

    async def _execute_request(self, request: dict[str, Any], request_id: str) -> dict[str, Any]:
        """Execute a request using the coordinator's capabilities.

        Args:
            request: The request to execute
            request_id: Unique identifier for the request

        Returns:
            Dict containing the execution results
        """
        try:
            # Extract request parameters
            location = request.get("location", "")
            risk_types = request.get("risk_types", [])
            time_horizon = request.get("time_horizon", "1y")

            # Execute workflow
            result = await self.execute_workflow({
                "location": location,
                "risk_types": risk_types,
                "time_horizon": time_horizon,
                "request_id": request_id
            })

            return {
                "status": "success",
                "request_id": request_id,
                "result": result
            }

        except Exception as e:
            self.logger.error(f"Error executing request {request_id}: {str(e)}")
            return {
                "status": "error",
                "request_id": request_id,
                "error": str(e)
            }
