"""
Multi-Agent Climate Risk Analysis System

This package implements a comprehensive multi-agent system for climate risk analysis,
combining specialized agents, workflow management, and advanced coordination capabilities.

Key Components:
    - Agent Team: Core agent coordination and execution
    - Enhanced Coordinator: Advanced task orchestration
    - Communication Manager: Inter-agent communication
    - Artifact Manager: Output storage and management
    - Workflow Manager: Process orchestration
    - Observability System: Monitoring and metrics
    - ADK Integration: External service integration

Features:
    1. Multi-Agent Architecture:
       - Specialized agent roles
       - Coordinated execution
       - State management
       - Error handling
    
    2. Workflow Management:
       - Process orchestration
       - State tracking
       - Error recovery
       - Progress monitoring
    
    3. Communication System:
       - Inter-agent messaging
       - State synchronization
       - Error propagation
       - Heartbeat monitoring
    
    4. Artifact Management:
       - Output storage
       - Version control
       - Cleanup policies
       - Access control
    
    5. Observability:
       - Performance metrics
       - Error tracking
       - Pattern analysis
       - System health monitoring

Dependencies:
    - asyncio: For async operations
    - aiohttp: For HTTP requests
    - logging: For system logging
    - typing: For type hints
    - json: For data serialization

Example Usage:
    ```python
    from multi_tool_agent import AgentTeam, EnhancedADKCoordinator
    
    # Initialize agent team
    team = AgentTeam(
        agents=[
            RiskAnalyzer(),
            DataCollector(),
            ReportGenerator()
        ]
    )
    
    # Create coordinator
    coordinator = EnhancedADKCoordinator(team)
    
    # Execute analysis
    result = await coordinator.execute_analysis(
        location="New York",
        time_period="2024-2025"
    )
    ```

Configuration:
    - AGENT_CONFIG: Agent-specific settings
    - COORDINATOR_CONFIG: Coordinator settings
    - COMMUNICATION_CONFIG: Communication settings
    - STORAGE_CONFIG: Storage settings
    - LOGGING_CONFIG: Logging settings

Version: 1.0.0
"""

from .agent_team import AgentTeam, Agent
from .enhanced_coordinator import EnhancedADKCoordinator
from .communication import CommunicationManager, SharedState
from .artifact_manager import ArtifactManager
from .workflows import WorkflowManager, WorkflowStep
from .observability import PatternMonitor, InteractionMetrics
from .adk_integration import ADKClient, ADKResponse

__version__ = "1.0.0"
__all__ = [
    "AgentTeam",
    "Agent",
    "EnhancedADKCoordinator",
    "CommunicationManager",
    "SharedState",
    "ArtifactManager",
    "WorkflowManager",
    "WorkflowStep",
    "PatternMonitor",
    "InteractionMetrics",
    "ADKClient",
    "ADKResponse"
]
