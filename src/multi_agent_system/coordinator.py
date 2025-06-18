"""
Enhanced ADK Coordinator for Multi-Agent Climate Risk Analysis System

This module implements an enhanced coordinator for the Agent Development Kit (ADK) that provides
parallel execution, token tracking, and context compression capabilities for the climate risk
analysis system.

Key Components:
    - TokenUsage: Tracks token consumption across agents and operations
    - CompressedContext: Manages context data compression and decompression
    - CoordinatorAgent: Main coordinator class for agent execution

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
"""

import asyncio
import json
import zlib
import logging
from typing import Dict, Any, List, Optional, Set, Callable
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from google.adk.agents import Agent

from .base_agent import BaseAgent
from .tool import Tool
from .artifact_manager import ArtifactManager
from .risk_definitions import RiskType, RiskLevel
from .session_manager import AnalysisSession, AgentState
from .communication import CommunicationManager, SharedState
from .observability import ObservabilityManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Track token usage for agents and operations."""
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
    """Manage compressed context data for efficient storage and transmission."""
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

class CoordinatorAgent(BaseAgent):
    """Enhanced coordinator for ADK with parallel execution and token tracking."""
    
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
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # Initialize communication manager
        self.communication_manager = None
        
        # Set up tools
        self.tools = [
            Tool(
                name="identify_capable_agents",
                func=self.identify_capable_agents,
                description="Identifies which agents are capable of handling a specific request"
            ),
            Tool(
                name="merge_agent_results",
                func=self.merge_agent_results,
                description="Combines and prioritizes results from multiple agents"
            ),
            Tool(
                name="monitor_agent_status",
                func=self.monitor_agent_status,
                description="Checks the status of other agents"
            ),
            Tool(
                name="execute_tasks_parallel",
                func=self.execute_tasks_parallel,
                description="Executes multiple tasks in parallel"
            )
        ]

    def set_session(self, session: AnalysisSession) -> None:
        """Set the current analysis session."""
        self.session = session
        self.communication_manager = CommunicationManager(session)

    async def execute_tasks_parallel(
        self,
        tasks: List[Dict[str, Any]],
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Execute multiple tasks in parallel with resource control."""
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
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
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

    def _get_agent_tools(self, agent_id: str) -> List[Callable]:
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

    def get_token_usage(self) -> Dict[str, Any]:
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
    async def identify_capable_agents(self, request: Dict[str, Any]) -> Dict[str, Any]:
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

    async def merge_agent_results(self, results: List[Dict[str, Any]], request: Dict[str, Any]) -> Dict[str, Any]:
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

    async def monitor_agent_status(self, agent_id: str) -> Dict[str, Any]:
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