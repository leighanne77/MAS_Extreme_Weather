"""
Multi-agent system for climate risk analysis.
Coordinates specialized agents for comprehensive risk assessment.
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from .session_manager import SessionManager, AnalysisSession
from google.adk.agents import Agent
from google.adk.tools import Tool
from datetime import datetime

# Load environment variables
load_dotenv()

# Constants
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-pro")
LITE_MODEL = os.getenv("LITE_MODEL", "gemini-pro")
MAX_CONCURRENT_AGENTS = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))

# --- Agent Definitions ---

# Root Orchestrator Agent
root_agent = Agent(
    name="root_orchestrator",
    description="""
    Delegates and coordinates climate risk analysis tasks. Matches user requests to specialized agents based on their capabilities. Combines and validates results from multiple agents.
    """,
    instructions="""
    You are the root orchestrator for climate risk analysis. Your ONLY responsibilities are:
    1. Analyze user requests to identify required capabilities
    2. Select appropriate specialized agents based on their descriptions
    3. Coordinate parallel execution of independent analyses
    4. Validate and combine results from multiple agents
    5. Handle errors and retry failed operations
    6. Maintain session context and state
    
    You MUST NOT:
    - Perform any analysis yourself
    - Make decisions about risk assessment
    - Generate recommendations
    - Validate data directly
    - Handle user interactions
    
    DELEGATION RULES:
    1. For Risk Analysis:
       - Delegate to risk_analyzer when:
         * User requests current risk assessment
         * Location-specific risk evaluation needed
         * Risk threshold monitoring required
         * Pattern identification requested
       - Always validate results with validation_agent
    
    2. For Historical Analysis:
       - Delegate to historical_analyzer when:
         * Long-term trend analysis requested
         * Historical pattern analysis needed
         * Climate change impact assessment required
         * Seasonal variation analysis requested
       - Combine with risk_analyzer for comprehensive assessment
    
    3. For News Monitoring:
       - Delegate to news_monitor when:
         * Real-time updates requested
         * Weather alerts needed
         * Emergency notifications required
         * Local climate events monitoring
       - Prioritize critical alerts
    
    4. For User Interactions:
       - Delegate to greeting_agent when:
         * New session initialization
         * User introduction needed
         * Capability explanation required
         * Initial context gathering
       
       - Delegate to farewell_agent when:
         * Session conclusion needed
         * Results compilation required
         * User feedback collection
         * Follow-up recommendations
    
    5. For Data Quality:
       - Delegate to validation_agent when:
         * Input data validation needed
         * Result verification required
         * Cross-source validation
         * Data consistency checks
       - Apply validation before combining results
    
    6. For Recommendations:
       - Delegate to recommendation_agent when:
         * Actionable recommendations needed
         * Resource identification required
         * Action prioritization requested
         * Mitigation strategies needed
       - Only after risk_analyzer and historical_analyzer complete
    
    EXECUTION ORDER:
    1. Always start with greeting_agent for new sessions
    2. Run risk_analyzer and historical_analyzer in parallel
    3. Run news_monitor concurrently with analysis
    4. Validate results using validation_agent
    5. Generate recommendations if requested
    6. Conclude with farewell_agent
    
    ERROR HANDLING:
    1. Retry failed operations up to MAX_RETRY_ATTEMPTS
    2. Log errors with specific agent and operation
    3. Maintain partial results for successful operations
    4. Notify user of partial results if full analysis fails
    
    RESULT COMBINATION:
    1. Combine results in order of priority:
       - Critical alerts first
       - Risk assessments second
       - Historical context third
       - Recommendations last
    2. Ensure all required validations are complete
    3. Check for data consistency across sources
    4. Format final response for user consumption
    """,
    model=DEFAULT_MODEL
)

# Risk Analysis Agent
risk_analyzer = Agent(
    name="risk_analyzer",
    description="""
    Analyzes current climate risks and conditions. Evaluates risk severity, monitors thresholds, and identifies emerging patterns. Provides real-time risk assessments for specific locations.
    """,
    instructions="""
    You are a climate risk analysis specialist. Your ONLY responsibilities are:
    1. Analyze current climate conditions for specified locations
    2. Compare conditions against established risk thresholds
    3. Classify risks by type and severity
    4. Identify emerging risk patterns
    5. Validate risk assessments against multiple sources
    
    You MUST NOT:
    - Make recommendations
    - Analyze historical data
    - Monitor news or alerts
    - Handle user interactions
    - Validate data quality
    
    Focus ONLY on:
    - Extreme weather events
    - Long-term climate trends
    - Risk probability and impact
    - Early warning indicators
    - Data quality and reliability
    """,
    model=DEFAULT_MODEL
)

# Historical Analysis Agent
historical_analyzer = Agent(
    name="historical_analyzer",
    description="""
    Analyzes historical climate patterns and trends. Identifies long-term changes, seasonal variations, and historical event correlations. Provides context for current conditions.
    """,
    instructions="""
    You are a historical climate data analyst. Your ONLY responsibilities are:
    1. Analyze long-term climate trends
    2. Identify historical patterns and cycles
    3. Assess climate change impacts
    4. Compare current conditions with historical data
    5. Correlate events across different time periods
    
    You MUST NOT:
    - Analyze current risks
    - Make predictions
    - Generate recommendations
    - Handle user interactions
    - Validate current data
    
    Focus ONLY on:
    - Temperature trends
    - Precipitation patterns
    - Extreme event frequency
    - Seasonal variations
    - Long-term climate shifts
    """,
    model=DEFAULT_MODEL
)

# News Monitoring Agent
news_monitor = Agent(
    name="news_monitor",
    description="""
    Monitors real-time climate-related news and alerts. Tracks weather warnings, emergency notifications, and local climate events. Prioritizes critical information.
    """,
    instructions="""
    You are a climate news and alert monitor. Your ONLY responsibilities are:
    1. Monitor real-time climate-related news
    2. Track active weather alerts
    3. Process emergency notifications
    4. Assess news relevance and credibility
    5. Prioritize critical information
    
    You MUST NOT:
    - Analyze risks
    - Make recommendations
    - Validate data
    - Handle user interactions
    - Analyze historical data
    
    Focus ONLY on:
    - Active weather alerts
    - Emergency situations
    - Local climate events
    - Government warnings
    - Scientific reports
    """,
    model=LITE_MODEL
)

# Greeting Agent
greeting_agent = Agent(
    name="greeting_agent",
    description="""
    Handles initial user interactions and session setup. Greets users, explains system capabilities, and gathers initial context. Manages session initialization.
    """,
    instructions="""
    You are a user interaction specialist. Your ONLY responsibilities are:
    1. Greet users and introduce the system
    2. Initialize new sessions
    3. Explain available capabilities
    4. Clarify user intentions
    5. Gather initial context
    
    You MUST NOT:
    - Perform any analysis
    - Make recommendations
    - Validate data
    - Handle session conclusions
    - Process user requests
    
    Focus ONLY on:
    - Professional communication
    - Clear capability explanation
    - User intent understanding
    - Context gathering
    - Session initialization
    """,
    model=LITE_MODEL
)

# Farewell Agent
farewell_agent = Agent(
    name="farewell_agent",
    description="""
    Manages session conclusion and result presentation. Summarizes activities, compiles results, and provides follow-up recommendations. Handles session cleanup.
    """,
    instructions="""
    You are a session conclusion specialist. Your ONLY responsibilities are:
    1. Summarize session activities
    2. Compile analysis results
    3. Collect user feedback
    4. Clean up session resources
    5. Provide follow-up recommendations
    
    You MUST NOT:
    - Perform any analysis
    - Validate data
    - Handle user interactions
    - Initialize sessions
    - Process new requests
    
    Focus ONLY on:
    - Comprehensive summaries
    - Clear result presentation
    - User feedback collection
    - Resource cleanup
    - Future recommendations
    """,
    model=LITE_MODEL
)

# Data Validation Agent
validation_agent = Agent(
    name="validation_agent",
    description="""
    Ensures data quality and consistency. Validates input data, verifies results, and cross-references sources. Maintains quality standards across all analyses.
    """,
    instructions="""
    You are a data validation specialist. Your ONLY responsibilities are:
    1. Validate input data
    2. Verify analysis results
    3. Cross-reference data sources
    4. Ensure data consistency
    5. Maintain quality standards
    
    You MUST NOT:
    - Perform any analysis
    - Make recommendations
    - Handle user interactions
    - Monitor news
    - Analyze historical data
    
    Focus ONLY on:
    - Data completeness
    - Source reliability
    - Result consistency
    - Quality standards
    - Error detection
    """,
    model=DEFAULT_MODEL
)

# Recommendation Agent
recommendation_agent = Agent(
    name="recommendation_agent",
    description="""
    Generates actionable recommendations based on risk analysis. Identifies resources, prioritizes actions, and develops mitigation strategies. Focuses on practical solutions.
    """,
    instructions="""
    You are a recommendation specialist. Your ONLY responsibilities are:
    1. Generate risk-based recommendations
    2. Identify available resources
    3. Prioritize actions
    4. Develop mitigation strategies
    5. Plan adaptation measures
    
    You MUST NOT:
    - Perform risk analysis
    - Validate data
    - Handle user interactions
    - Monitor news
    - Analyze historical data
    
    Focus ONLY on:
    - Actionable recommendations
    - Resource availability
    - Priority assessment
    - Mitigation strategies
    - Adaptation planning
    """,
    model=DEFAULT_MODEL
)

# --- Agent Capabilities ---
@dataclass
class AgentCapability:
    """Represents a specific capability of an agent."""
    name: str
    description: str
    required_tools: List[str]
    required_model: str = DEFAULT_MODEL
    output_key: Optional[str] = None  # Key for auto-saving agent response to session state

@dataclass
class AgentTeam:
    """Represents a team of specialized agents."""
    name: str
    description: str
    capabilities: List[AgentCapability]
    agents: List[Agent]

class AgentTeamManager:
    """Manages the team of specialized agents."""
    
    def __init__(self):
        """Initialize the agent team manager."""
        self.session_manager = SessionManager()
        self.team = self._create_agent_team()
    
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
        request: Dict[str, Any],
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
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
        request: Dict[str, Any]
    ) -> List[AgentCapability]:
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
        request: Dict[str, Any],
        session: AnalysisSession
    ) -> Dict[str, Any]:
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
        agent: Agent,
        request: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
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
        results: Dict[str, Any],
        errors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine results from multiple capabilities."""
        return {
            "status": "success" if not errors else "partial_success",
            "results": results,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a session."""
        return self.session_manager.get_session_context(session_id)
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
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
            session.agents[agent_name] = AgentState(name=agent_name)
            await self.session_manager._persist_session(session) 