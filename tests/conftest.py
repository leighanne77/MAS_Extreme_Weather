"""
Common test fixtures and configurations.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from dataclasses import dataclass
from enum import Enum

from multi_tool_agent.agent_team import Agent
from multi_tool_agent.session_manager import SessionManager
from multi_tool_agent.enhanced_coordinator import EnhancedADKCoordinator
from multi_tool_agent.artifact_manager import ArtifactManager
from multi_tool_agent.observability import PatternMonitor
from multi_tool_agent.risk_definitions import RiskDefinition, RiskType, RiskLevel, RiskThreshold

class TestCategory(Enum):
    """Test categories."""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    E2E = "e2e"

@dataclass
class TestConfig:
    """Base test configuration."""
    category: TestCategory
    timeout: float
    max_retries: int
    cleanup: bool

# Fixtures for Common Objects
@pytest.fixture
def mock_agent() -> Agent:
    """Create a mock agent with standard configuration.
    
    Returns:
        Agent: Mock agent instance
    """
    agent = Mock(spec=Agent)
    agent.name = "test_agent"
    agent.description = "Test agent"
    agent.instructions = "Test instructions"
    agent.model = "gpt-4"
    agent.tools = []
    return agent

@pytest.fixture
def mock_session() -> Mock:
    """Create a mock session with standard configuration.
    
    Returns:
        Mock: Mock session instance
    """
    session = Mock()
    session.state = {}
    session.id = "test_session"
    session.created_at = datetime.now()
    return session

@pytest.fixture
def mock_session_manager() -> SessionManager:
    """Create a mock session manager with standard configuration.
    
    Returns:
        SessionManager: Mock session manager instance
    """
    manager = Mock(spec=SessionManager)
    manager.sessions = {}
    return manager

@pytest.fixture
def mock_artifact_manager() -> ArtifactManager:
    """Create a mock artifact manager.
    
    Returns:
        ArtifactManager: Mock artifact manager instance
    """
    manager = Mock(spec=ArtifactManager)
    manager.artifacts = {}
    return manager

@pytest.fixture
def mock_pattern_monitor() -> PatternMonitor:
    """Create a mock pattern monitor.
    
    Returns:
        PatternMonitor: Mock pattern monitor instance
    """
    monitor = Mock(spec=PatternMonitor)
    monitor.agent_patterns = {}
    return monitor

@pytest.fixture
def enhanced_coordinator() -> EnhancedADKCoordinator:
    """Create an enhanced coordinator instance.
    
    Returns:
        EnhancedADKCoordinator: Coordinator instance
    """
    return EnhancedADKCoordinator()

# Fixtures for Test Data
@pytest.fixture
def sample_risk_definition() -> RiskDefinition:
    """Create a sample risk definition for testing.
    
    Returns:
        RiskDefinition: Sample risk definition
    """
    return RiskDefinition(
        risk_type=RiskType.TEMPERATURE,
        description="Temperature risk",
        thresholds=[
            RiskThreshold(0, 30, "celsius", RiskLevel.LOW),
            RiskThreshold(30, 40, "celsius", RiskLevel.MODERATE),
            RiskThreshold(40, 50, "celsius", RiskLevel.HIGH),
            RiskThreshold(50, float("inf"), "celsius", RiskLevel.EXTREME)
        ]
    )

@pytest.fixture
def sample_weather_data() -> Dict[str, Any]:
    """Create sample weather data for testing.
    
    Returns:
        Dict[str, Any]: Sample weather data
    """
    return {
        "temperature": 35.0,
        "humidity": 0.6,
        "wind_speed": 10.0,
        "precipitation": 0.0,
        "timestamp": datetime.now().isoformat()
    }

@pytest.fixture
def sample_risk_analysis_result() -> Dict[str, Any]:
    """Create sample risk analysis result.
    
    Returns:
        Dict[str, Any]: Sample analysis result
    """
    return {
        "risk_level": RiskLevel.MODERATE,
        "confidence": 0.85,
        "factors": ["temperature", "humidity"],
        "recommendations": ["monitor", "alert"]
    }

# Fixtures for Test Configuration
@pytest.fixture
def unit_test_config() -> TestConfig:
    """Create unit test configuration.
    
    Returns:
        TestConfig: Unit test configuration
    """
    return TestConfig(
        category=TestCategory.UNIT,
        timeout=5.0,
        max_retries=1,
        cleanup=True
    )

@pytest.fixture
def integration_test_config() -> TestConfig:
    """Create integration test configuration.
    
    Returns:
        TestConfig: Integration test configuration
    """
    return TestConfig(
        category=TestCategory.INTEGRATION,
        timeout=30.0,
        max_retries=3,
        cleanup=True
    )

@pytest.fixture
def performance_test_config() -> TestConfig:
    """Create performance test configuration.
    
    Returns:
        TestConfig: Performance test configuration
    """
    return TestConfig(
        category=TestCategory.PERFORMANCE,
        timeout=60.0,
        max_retries=1,
        cleanup=False
    )

@pytest.fixture
def e2e_test_config() -> TestConfig:
    """Create end-to-end test configuration.
    
    Returns:
        TestConfig: E2E test configuration
    """
    return TestConfig(
        category=TestCategory.E2E,
        timeout=120.0,
        max_retries=3,
        cleanup=True
    )

# Fixtures for Async Testing
@pytest.fixture
def event_loop():
    """Create an event loop for async testing.
    
    Returns:
        asyncio.AbstractEventLoop: Event loop instance
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Fixtures for API Testing
@pytest.fixture
def test_client():
    """Create a test client for API testing.
    
    Returns:
        TestClient: FastAPI test client
    """
    from fastapi.testclient import TestClient
    from app import app
    return TestClient(app) 