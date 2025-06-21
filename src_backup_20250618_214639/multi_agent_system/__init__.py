"""
Multi-Agent System for Climate Risk Analysis.

This package implements a multi-agent system for analyzing climate risks using
Google's ADK and A2A SDK, with support for various data sources and analysis tools.
"""

from .agents.base_agent import BaseAgent
from .agents import (
    GreetingAgent,
    FarewellAgent,
    RecommendationAgent,
    ValidationAgent,
    HistoricalAnalyzerAgent,
    RiskAnalyzerAgent,
    NewsMonitoringAgent
)

from .data import (
    NOAAWeatherData,
    get_weather_data,
    DataSource,
    DataSourceManager
)

from .workflows import (
    SequentialWorkflow,
    ParallelWorkflow,
    LoopWorkflow,
    WorkflowManager,
    WorkflowStep,
    WorkflowState,
    WorkflowContext
)

from .coordinator import CoordinatorAgent
from .communication import CommunicationManager
from .session_manager import AnalysisSession, AgentState
from .agent_team import AgentTeam
from .adk_integration import ADKAgentCardManager, ADKAgentCoordinator, ADKClient
from .observability import ObservabilityManager
from .risk_definitions import RiskType, RiskLevel, get_consensus_thresholds
from .artifact_manager import ArtifactManager
from .weather_risks import ClimateRiskAnalyzer

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