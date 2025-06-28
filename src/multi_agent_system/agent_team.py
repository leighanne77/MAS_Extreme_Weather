"""
Multi-Agent System for Climate Risk Analysis

This module implements a coordinated multi-agent system for comprehensive climate risk analysis.
It defines specialized agents, their capabilities, and the orchestration of their interactions.

Key Components:
    - AgentCapability: Defines specific capabilities of agents
    - AgentTeam: Represents a team of specialized agents
    - AgentTeamManager: Manages the team and coordinates agent interactions

Agent Types:
    1. Root Orchestrator: Coordinates and delegates tasks to specialized agents
    2. Risk Analyzer: Analyzes current climate risks and conditions
    3. Historical Analyzer: Analyzes historical climate patterns
    4. News Monitor: Monitors real-time climate-related news
    5. Greeting Agent: Handles user interactions and session initialization
    6. Farewell Agent: Manages session conclusion and result compilation
    7. Validation Agent: Ensures data quality and consistency
    8. Recommendation Agent: Generates actionable recommendations

State Management:
    - Each agent maintains its own state
    - Shared state is managed through the session manager
    - State updates are coordinated through the team manager

Error Handling:
    - Agents implement retry mechanisms
    - Errors are logged and propagated appropriately
    - Failed operations can be retried based on configuration

Dependencies:
    - session_manager: For session and state management
    - weather_risks: For climate risk analysis
    - risk_definitions: For risk thresholds and definitions
    - agent: For base agent definition

Example Usage:
    ```python
    # Create and initialize the agent team
    team_manager = AgentTeamManager()

    # Create a new analysis session
    session = await team_manager.create_session(location="New York")

    # Run a comprehensive analysis
    result = await team_manager.run_analysis(session)
    ```

Configuration:
    - DEFAULT_MODEL: Default model for agent operations
    - LITE_MODEL: Lightweight model for simple tasks
    - MAX_CONCURRENT_AGENTS: Maximum number of concurrent agents
    - MAX_RETRY_ATTEMPTS: Maximum number of retry attempts
    - RETRY_DELAY: Delay between retry attempts
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from multi_agent_system.agents.base_agent import BaseAgent
from multi_agent_system.agents.farewell_agent import FarewellAgent
from multi_agent_system.agents.greeting_agent import GreetingAgent
from multi_agent_system.agents.historical_agent import HistoricalAnalyzerAgent
from multi_agent_system.agents.news_agent import NewsMonitoringAgent
from multi_agent_system.agents.recommendation_agent import RecommendationAgent
from multi_agent_system.agents.risk_agent import RiskAnalyzerAgent
from multi_agent_system.agents.validation_agent import ValidationAgent
from multi_agent_system.session_manager import AnalysisSession, SessionManager
from multi_agent_system.utils.adk_features import (
    Buffer,
    CircuitBreaker,
    MetricsCollector,
    Monitoring,
    WorkerPool,
)

# Load environment variables
load_dotenv()

# Constants
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
LITE_MODEL = os.getenv("LITE_MODEL", "gemini-2.0-flash")
MAX_CONCURRENT_AGENTS = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))

# --- Agent Definitions ---

@dataclass
class AgentCapability:
    """Represents a specific capability of an agent."""
    name: str
    description: str
    required_tools: list[str]
    required_model: str = DEFAULT_MODEL
    output_key: str | None = None  # Key for auto-saving agent response to session state

@dataclass
class AgentTeam:
    """Coordinates multiple agents for risk analysis with ADK features.

    This class manages a team of specialized agents that work together to analyze
    climate risks and provide recommendations. It includes ADK features for
    performance optimization, reliability, and monitoring.

    Attributes:
        session_manager (SessionManager): Manages analysis sessions
        metrics_collector (MetricsCollector): ADK metrics collector
        circuit_breaker (CircuitBreaker): ADK circuit breaker
        worker_pool (WorkerPool): ADK worker pool
        monitoring (Monitoring): ADK monitoring
        buffer (Buffer): ADK buffer
        agents (Dict[str, BaseAgent]): Dictionary of available agents
    """

    def __init__(self):
        """Initialize the agent team with ADK features."""
        self.session_manager = SessionManager()

        # Initialize ADK features
        self.metrics_collector = MetricsCollector()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=300
        )
        self.worker_pool = WorkerPool(max_workers=MAX_CONCURRENT_AGENTS)
        self.monitoring = Monitoring()
        self.buffer = Buffer()

        # Initialize agents
        self.agents = self._initialize_agents()

    def _initialize_agents(self) -> dict[str, BaseAgent]:
        """Initialize agents with ADK features and function-based tools."""
        return {
            "risk_analyzer": RiskAnalyzerAgent(),
            "historical_agent": HistoricalAnalyzerAgent(),
            "news_agent": NewsMonitoringAgent(),
            "recommendation_agent": RecommendationAgent(),
            "validation_agent": ValidationAgent(),
            "greeting_agent": GreetingAgent(),
            "farewell_agent": FarewellAgent()
        }

    async def analyze_risks(self, location: str, time_period: str) -> dict[str, Any]:
        """Analyze risks using the agent team with ADK features.

        Args:
            location (str): Location to analyze
            time_period (str): Time period for analysis

        Returns:
            Dict[str, Any]: Analysis results with ADK metrics
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("risk_analysis"):
                raise Exception("Circuit breaker is open")

            # Track operation with metrics collector
            with self.metrics_collector.track_operation("analyze_risks"):
                # Create new session
                await self.session_manager.create_session()

                # Use worker pool for parallel agent execution
                async def execute_agent(agent_name: str) -> dict[str, Any]:
                    agent = self.agents[agent_name]
                    return await agent.handle_request({
                        "location": location,
                        "time_period": time_period
                    })

                # Run agents in parallel
                agent_tasks = [
                    execute_agent(agent_name)
                    for agent_name in self.agents.keys()
                ]
                results = await self.worker_pool.execute_parallel(agent_tasks)

                # Combine results
                analysis_results = dict(zip(self.agents.keys(), results, strict=False))

                # Update monitoring
                self.monitoring.track_workflow("risk_analysis", {
                    "location": location,
                    "time_period": time_period,
                    "agents_executed": len(results),
                    "successful_agents": sum(1 for r in results if r.get("status") == "success")
                })

                # Get ADK metrics
                metrics = {
                    "performance": self.metrics_collector.get_metrics(),
                    "circuit_breaker": self.circuit_breaker.get_status(),
                    "monitoring": self.monitoring.get_metrics(),
                    "resource_usage": self.worker_pool.get_resource_usage()
                }

                return {
                    "status": "success",
                    "results": analysis_results,
                    "metrics": metrics
                }

        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("risk_analysis")
            logger.error(f"Error in risk analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "metrics": self.get_metrics()
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get ADK metrics for the agent team.

        Returns:
            Dict[str, Any]: Metrics including performance, resource usage, and circuit breaker status
        """
        return {
            "performance": self.metrics_collector.get_metrics(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "monitoring": self.monitoring.get_metrics(),
            "resource_usage": self.worker_pool.get_resource_usage(),
            "session_metrics": self.session_manager.get_metrics()
        }

    async def execute_workflow(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute a complete workflow using the agent team.

        Args:
            request: The workflow request containing location, risk_types, etc.

        Returns:
            Dict containing workflow results
        """
        try:
            location = request.get("location", "")
            risk_types = request.get("risk_types", [])
            time_horizon = request.get("time_horizon", "1y")

            # Create session
            session = await self.session_manager.create_session(
                location=location,
                user_id="test_user"
            )

            # Execute agents in parallel
            agent_tasks = []
            for agent_name, agent in self.agents.items():
                task = agent.handle_request({
                    "location": location,
                    "risk_types": risk_types,
                    "time_horizon": time_horizon,
                    "session_id": session.session_id
                })
                agent_tasks.append((agent_name, task))

            # Wait for all agents to complete
            results = {}
            for agent_name, task in agent_tasks:
                try:
                    result = await task
                    results[agent_name] = result
                except Exception as e:
                    results[agent_name] = {
                        "status": "error",
                        "error": str(e)
                    }

            return {
                "status": "success",
                "results": results,
                "session_id": session.session_id
            }

        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def check_permission(self, user_id: str, action: str) -> bool:
        """Check if user has permission for an action.

        Args:
            user_id: User identifier
            action: Action to check permission for

        Returns:
            bool: True if user has permission
        """
        # Basic permission check - in a real implementation this would check roles/permissions
        return True

    def get_agent_cards(self) -> list:
        """Return all agent cards in ADK format."""
        cards = []
        # self.team.agents may be a list or dict
        agents = self.team.agents.values() if hasattr(self.team.agents, 'values') else self.team.agents
        for agent in agents:
            if hasattr(agent, 'agent_card'):
                cards.append(agent.agent_card)
        return cards

    def get_registered_agents(self) -> list[dict[str, Any]]:
        """Get list of registered agents with basic info."""
        agents = []
        # self.team.agents may be a list or dict
        agent_list = self.team.agents.values() if hasattr(self.team.agents, 'values') else self.team.agents
        for agent in agent_list:
            agent_info = {
                "name": agent.name,
                "description": agent.description,
                "model": getattr(agent, 'model', 'unknown'),
                "tools_count": len(getattr(agent, 'tools', [])),
                "has_agent_card": hasattr(agent, 'agent_card') and agent.agent_card is not None
            }
            agents.append(agent_info)
        return agents

    def get_a2a_status(self) -> dict[str, Any]:
        """Get A2A protocol status and statistics."""
        return {
            "protocol_version": "1.0.0",
            "status": "active",
            "agents_registered": len(self.get_registered_agents()),
            "agent_cards_available": len(self.get_agent_cards()),
            "features": {
                "message_structure": True,
                "part_types": True,
                "artifact_generation": True,
                "task_management": True,
                "agent_discovery": True
            },
            "statistics": {
                "total_agents": len(self.get_registered_agents()),
                "agents_with_cards": len([a for a in self.get_registered_agents() if a["has_agent_card"]]),
                "active_sessions": len(self.session_manager.get_active_sessions()) if hasattr(self.session_manager, 'get_active_sessions') else 0
            }
        }

    async def route_a2a_message(self, sender: str, recipient: str, content: str, message_type: Any) -> dict[str, Any]:
        """Route an A2A message between agents."""
        try:
            # Find the recipient agent
            agent_list = self.team.agents.values() if hasattr(self.team.agents, 'values') else self.team.agents
            recipient_agent = None
            for agent in agent_list:
                if agent.name == recipient:
                    recipient_agent = agent
                    break

            if not recipient_agent:
                raise ValueError(f"Recipient agent '{recipient}' not found")

            # Process the message
            result = await recipient_agent.handle_request({
                "sender": sender,
                "content": content,
                "message_type": message_type.value if hasattr(message_type, 'value') else str(message_type)
            })

            return {
                "status": "success",
                "recipient": recipient,
                "result": result
            }

        except Exception as e:
            logger.error(f"Error routing A2A message: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def send_multipart_message(self, sender: str, recipient: str, parts: list[Any], message_type: Any) -> dict[str, Any]:
        """Send a multi-part A2A message."""
        try:
            # Find the recipient agent
            agent_list = self.team.agents.values() if hasattr(self.team.agents, 'values') else self.team.agents
            recipient_agent = None
            for agent in agent_list:
                if agent.name == recipient:
                    recipient_agent = agent
                    break

            if not recipient_agent:
                raise ValueError(f"Recipient agent '{recipient}' not found")

            # Process the multi-part message
            result = await recipient_agent.handle_request({
                "sender": sender,
                "parts": [part.to_dict() if hasattr(part, 'to_dict') else str(part) for part in parts],
                "message_type": message_type.value if hasattr(message_type, 'value') else str(message_type)
            })

            return {
                "status": "success",
                "recipient": recipient,
                "parts_processed": len(parts),
                "result": result
            }

        except Exception as e:
            logger.error(f"Error sending multi-part message: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

class AgentTeamManager:
    """Manages the team of specialized agents."""

    def __init__(self):
        """Initialize the agent team manager."""
        self.session_manager = SessionManager()
        self.team = self._create_agent_team()

    async def start(self):
        """Start the agent team manager."""
        logger.info("Agent team manager starting...")
        # Initialize any async resources here
        logger.info("Agent team manager started successfully")

    async def stop(self):
        """Stop the agent team manager."""
        logger.info("Agent team manager stopping...")
        # Clean up any async resources here
        logger.info("Agent team manager stopped successfully")

    def _create_agent_team(self) -> AgentTeam:
        """Create the agent team with specialized agents."""
        return AgentTeam(
            name="Climate Risk Analysis Team",
            description="A team of specialized agents for comprehensive climate risk analysis",
            capabilities=[
                AgentCapability(
                    name="risk_analysis",
                    description="Analyzes current climate risks and conditions",
                    required_tools=["analyze_current_risks", "get_risk_thresholds"],
                    output_key="risk_analysis_result"
                ),
                AgentCapability(
                    name="historical_analysis",
                    description="Analyzes historical climate patterns and trends",
                    required_tools=["get_historical_data", "analyze_trends"],
                    output_key="historical_analysis_result"
                ),
                AgentCapability(
                    name="news_monitoring",
                    description="Monitors real-time climate-related news and alerts",
                    required_tools=["search_risk_news", "get_weather_alerts"],
                    output_key="news_monitoring_result"
                ),
                AgentCapability(
                    name="user_interaction",
                    description="Handles user interactions and session management",
                    required_tools=["say_hello", "offer_assistance", "say_goodbye"],
                    output_key="user_interaction_result"
                ),
                AgentCapability(
                    name="data_validation",
                    description="Ensures data quality and consistency",
                    required_tools=["validate_location", "validate_risk_data"],
                    output_key="validation_result"
                ),
                AgentCapability(
                    name="recommendation",
                    description="Generates actionable recommendations",
                    required_tools=["generate_recommendations", "get_local_resources"],
                    output_key="recommendation_result"
                )
            ],
            agents=[
                root_agent,
                risk_analyzer,
                historical_analyzer,
                news_monitor,
                greeting_agent,
                farewell_agent,
                validation_agent,
                recommendation_agent
            ]
        )

    async def handle_request(
        self,
        request: dict[str, Any],
        session_id: str,
        user_id: str
    ) -> dict[str, Any]:
        """Handle a user request using the agent team."""
        # Get or create session
        try:
            session = self.session_manager.get_session(session_id)
        except ValueError:
            session = await self.session_manager.create_session(
                user_id=user_id,
                session_id=session_id,
                runner=self,
                initial_state={
                    "request_history": [],
                    "preferred_units": "metric",
                    "preferred_language": "en"
                }
            )

        # Update session state with new request
        await self.session_manager.add_to_history(session_id, {
            "type": "request",
            "content": request
        })

        # Determine required capabilities
        required_capabilities = self._determine_required_capabilities(request)

        # Run agents based on capabilities
        results = {}
        errors = {}

        for capability in required_capabilities:
            try:
                result = await self._run_capability(
                    capability=capability,
                    request=request,
                    session=session
                )
                results[capability.name] = result

                # Update session state with capability result
                if capability.output_key:
                    await self.session_manager.update_session_state(
                        session_id=session_id,
                        updates={capability.output_key: result}
                    )

            except Exception as e:
                errors[capability.name] = str(e)
                await self.session_manager.update_session_state(
                    session_id=session_id,
                    updates={f"{capability.name}_error": str(e)}
                )

        # Combine results
        final_result = self._combine_results(results, errors)

        # Update session state with final result
        await self.session_manager.add_to_history(session_id, {
            "type": "response",
            "content": final_result
        })

        return final_result

    def _determine_required_capabilities(
        self,
        request: dict[str, Any]
    ) -> list[AgentCapability]:
        """Determine which capabilities are required for the request."""
        required = []

        # Map request intents to capabilities
        intent = request.get("intent", "")
        parameters = request.get("parameters", {})

        if "risk" in intent.lower():
            required.append(self.team.capabilities[0])  # risk_analysis
            required.append(self.team.capabilities[4])  # data_validation

        if "historical" in intent.lower():
            required.append(self.team.capabilities[1])  # historical_analysis
            required.append(self.team.capabilities[4])  # data_validation

        if "news" in intent.lower() or "alert" in intent.lower():
            required.append(self.team.capabilities[2])  # news_monitoring

        if "recommend" in intent.lower():
            required.append(self.team.capabilities[5])  # recommendation

        # Always include user interaction for new sessions
        if not parameters.get("is_continuation", False):
            required.append(self.team.capabilities[3])  # user_interaction

        return required

    async def _run_capability(
        self,
        capability: AgentCapability,
        request: dict[str, Any],
        session: AnalysisSession
    ) -> dict[str, Any]:
        """Run a specific capability using appropriate agents."""
        # Get session context
        context = self.session_manager.get_session_context(session.session_id)

        # Find agents with required tools
        agents = [
            agent for agent in self.team.agents
            if all(tool in agent.tools for tool in capability.required_tools)
        ]

        if not agents:
            raise ValueError(f"No agents found for capability: {capability.name}")

        # Run agents in parallel
        async with session.semaphore:
            tasks = [
                self._run_agent(
                    agent=agent,
                    request=request,
                    context=context
                )
                for agent in agents
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results from all agents
        combined_result = {}
        for result in results:
            if isinstance(result, Exception):
                raise result
            combined_result.update(result)

        return combined_result

    async def _run_agent(
        self,
        agent: BaseAgent,
        request: dict[str, Any],
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Run a specific agent with retry logic."""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                # Add session context to request
                request_with_context = {
                    **request,
                    "session_context": context
                }

                result = await agent.run(request_with_context)
                return result

            except Exception as e:
                if attempt == MAX_RETRY_ATTEMPTS - 1:
                    raise e
                await asyncio.sleep(RETRY_DELAY)

    def _combine_results(
        self,
        results: dict[str, Any],
        errors: dict[str, Any]
    ) -> dict[str, Any]:
        """Combine results from multiple capabilities."""
        return {
            "status": "success" if not errors else "partial_success",
            "results": results,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }

    async def get_session_status(self, session_id: str) -> dict[str, Any]:
        """Get the current status of a session."""
        return self.session_manager.get_session_context(session_id)

    async def get_active_sessions(self) -> list[dict[str, Any]]:
        """Get all active sessions."""
        return [
            self.session_manager.get_session_context(session.session_id)
            for session in self.session_manager.sessions.values()
        ]

    async def reset_agent(
        self,
        session_id: str,
        agent_name: str
    ) -> None:
        """Reset a specific agent in a session."""
        session = self.session_manager.get_session(session_id)
        if agent_name in session.agents:
            session.agents[agent_name] = AgentState()
        await self.session_manager._persist_session(session)
