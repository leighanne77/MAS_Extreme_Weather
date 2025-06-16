"""
Multi-Agent System for Climate Risk Analysis

This package provides a comprehensive system for analyzing climate risks
using multiple specialized agents working together.

Key Components:
    - AgentTeam: Coordinates multiple agents
    - SessionManager: Manages analysis sessions
    - EnhancedADKCoordinator: Coordinates ADK interactions
    - ArtifactManager: Manages analysis artifacts
    - Observability: System monitoring and logging
    - RiskDefinitions: Risk assessment definitions

Example Usage:
    ```python
    from src.multi_agent_system.agent_team import AgentTeam
    from google.adk.agents import Agent

    # Create agent team
    team = AgentTeam([
        Agent(
            model='gemini-2.0-flash',
            name='climate_agent',
            instruction='You are an expert climate risk analyst.',
            description='Agent for analyzing climate risks'
        )
    ])

    # Execute analysis
    result = team.execute_analysis(
        location="New York",
        time_period="2024-2025"
    )
    ```
"""

from .agent_team import AgentTeam
from .session_manager import SessionManager, AnalysisSession
from .enhanced_coordinator import EnhancedADKCoordinator
from .artifact_manager import ArtifactManager
from .observability import ObservabilityManager
from .risk_definitions import (
    RiskSource,
    RiskThreshold,
    RiskType,
    RiskLevel,
    severity_levels
)

__all__ = [
    'AgentTeam',
    'SessionManager',
    'AnalysisSession',
    'EnhancedADKCoordinator',
    'ArtifactManager',
    'ObservabilityManager',
    'RiskSource',
    'RiskThreshold',
    'RiskType',
    'RiskLevel',
    'severity_levels'
]