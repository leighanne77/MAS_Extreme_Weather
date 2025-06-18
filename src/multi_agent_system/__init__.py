"""
Multi-Agent System for Climate Risk Analysis.

This package implements a multi-agent system for analyzing climate risks using
Google's ADK and A2A SDK, with support for various data sources and analysis tools.
"""

from .agents import (
    BaseAgent,
    GreetingAgent,
    FarewellAgent,
    RecommendationAgent,
    ValidationAgent,
    HistoricalAgent,
    RiskAgent,
    NewsAgent
)

from .data import (
    NOAAWeatherData,
    get_weather_data,
    DataSource,
    DataSourceManager
)

from .utils import (
    Tool,
    AgentTools
)

from .workflows import (
    RiskAnalysisWorkflow,
    HistoricalAnalysisWorkflow,
    NewsAnalysisWorkflow,
    RecommendationWorkflow
)

from .coordinator import CoordinatorAgent
from .communication import CommunicationManager
from .session_manager import AnalysisSession, AgentState
from .agent_team import AgentTeam
from .adk_integration import ADKIntegration
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
    'HistoricalAgent',
    'RiskAgent',
    'NewsAgent',
    
    # Data
    'NOAAWeatherData',
    'get_weather_data',
    'DataSource',
    'DataSourceManager',
    
    # Utils
    'Tool',
    'AgentTools',
    
    # Workflows
    'RiskAnalysisWorkflow',
    'HistoricalAnalysisWorkflow',
    'NewsAnalysisWorkflow',
    'RecommendationWorkflow',
    
    # Core Components
    'CoordinatorAgent',
    'CommunicationManager',
    'AnalysisSession',
    'AgentState',
    'AgentTeam',
    'ADKIntegration',
    'ObservabilityManager',
    'RiskType',
    'RiskLevel',
    'get_consensus_thresholds',
    'ArtifactManager',
    'ClimateRiskAnalyzer'
]