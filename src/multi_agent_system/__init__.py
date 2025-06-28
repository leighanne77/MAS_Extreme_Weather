"""
Multi-Agent System for Climate Risk Analysis.

This package implements a multi-agent system for analyzing climate risks using
Google's ADK and A2A SDK, with support for various data sources and analysis tools.
"""

from .adk_integration import ADKAgentCardManager, ADKAgentCoordinator, ADKClient
from .agent_team import AgentTeam
from .agents import (
    FarewellAgent,
    GreetingAgent,
    HistoricalAnalyzerAgent,
    NewsMonitoringAgent,
    RecommendationAgent,
    RiskAnalyzerAgent,
    ValidationAgent,
)
from .agents.base_agent import BaseAgent
from .artifact_manager import ArtifactManager
from .communication import CommunicationManager
from .coordinator import CoordinatorAgent
from .data import DataSource, DataSourceManager, NOAAWeatherData, get_weather_data
from .observability import ObservabilityManager
from .risk_definitions import RiskLevel, RiskType, get_consensus_thresholds
from .session_manager import AgentState, AnalysisSession
from .weather_risks import ClimateRiskAnalyzer
from .workflows import (
    LoopWorkflow,
    ParallelWorkflow,
    SequentialWorkflow,
    WorkflowContext,
    WorkflowManager,
    WorkflowState,
    WorkflowStep,
)

__all__ = [
    # Agents
    'BaseAgent',
    'GreetingAgent',
    'FarewellAgent',
    'RecommendationAgent',
    'ValidationAgent',
    'HistoricalAnalyzerAgent',
    'RiskAnalyzerAgent',
    'NewsMonitoringAgent',

    # Data
    'NOAAWeatherData',
    'get_weather_data',
    'DataSource',
    'DataSourceManager',

    # Workflows
    'SequentialWorkflow',
    'ParallelWorkflow',
    'LoopWorkflow',
    'WorkflowManager',
    'WorkflowStep',
    'WorkflowState',
    'WorkflowContext',

    # Core Components
    'CoordinatorAgent',
    'CommunicationManager',
    'AnalysisSession',
    'AgentState',
    'AgentTeam',
    'ADKAgentCardManager',
    'ADKAgentCoordinator',
    'ADKClient',
    'ObservabilityManager',
    'RiskType',
    'RiskLevel',
    'get_consensus_thresholds',
    'ArtifactManager',
    'ClimateRiskAnalyzer'
]
