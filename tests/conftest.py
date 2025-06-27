"""
Common test fixtures and configurations.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from dataclasses import dataclass
from enum import Enum

from src.multi_agent_system.agent_team import AgentTeam
from src.multi_agent_system.session_manager import SessionManager
from src.multi_agent_system.coordinator import CoordinatorAgent
from src.multi_agent_system.artifact_manager import ArtifactManager
from src.multi_agent_system.observability import (
    ObservabilityManager,
    InteractionType,
    DecisionPattern,
    ErrorSeverity
)
from src.multi_agent_system.risk_definitions import RiskType, RiskLevel, RiskThreshold

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
def mock_agent() -> AgentTeam:
    """Create a mock agent with standard configuration.
    
    Returns:
        AgentTeam: Mock agent instance
    """
    agent = Mock(spec=AgentTeam)
    agent.name = "test_agent"
    agent.description = "Test agent"
    agent.instructions = "Test instructions"
    agent.model = "Gemini 2.0 Flash"
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
def mock_observability_manager():
    """Create a mock ObservabilityManager for testing.
    
    Returns:
        Mock: Mocked ObservabilityManager instance
    """
    manager = Mock(spec=ObservabilityManager)
    
    # Mock checkpoint methods
    manager.create_checkpoint.return_value = "test_checkpoint_id"
    manager.restore_checkpoint.return_value = Mock(
        agent_id="test_agent",
        state={"status": "running"},
        context={"location": "test"},
        tool_calls=[{"tool": "test_tool"}],
        recovery_point="test_point",
        metadata={"test": "metadata"}
    )
    manager.list_checkpoints.return_value = [
        {
            "id": "test_checkpoint_id",
            "agent_id": "test_agent",
            "timestamp": datetime.now().isoformat(),
            "state": {"status": "running"},
            "context": {"location": "test"},
            "tool_calls": [{"tool": "test_tool"}],
            "recovery_point": "test_point",
            "metadata": {"test": "metadata"}
        }
    ]
    manager.delete_checkpoint.return_value = True
    manager.cleanup_old_checkpoints.return_value = 1
    
    # Mock pattern methods
    manager.get_agent_patterns.return_value = Mock(
        interaction_history=[],
        decision_history=[],
        error_history=[],
        checkpoints=[]
    )
    manager.get_interaction_patterns.return_value = {}
    manager.get_decision_patterns.return_value = {}
    manager.get_error_patterns.return_value = {}
    manager.get_retry_patterns.return_value = {}
    manager.get_token_usage_patterns.return_value = {}
    manager.get_context_patterns.return_value = {}
    manager.analyze_patterns.return_value = {}
    
    return manager

@pytest.fixture
def enhanced_coordinator() -> CoordinatorAgent:
    """Create an enhanced coordinator instance.
    
    Returns:
        CoordinatorAgent: Coordinator instance
    """
    return CoordinatorAgent()

# Fixtures for Test Data
@pytest.fixture
def sample_risk_definition() -> dict:
    """Create a sample risk definition for testing using RiskType, RiskLevel, and RiskThreshold."""
    return {
        "risk_type": RiskType.TEMPERATURE,
        "description": "Temperature risk",
        "thresholds": [
            RiskThreshold(value=30, unit="celsius", sources=[], metadata={}, monitoring_enabled=True, metrics_collection=True, circuit_breaker=True),
            RiskThreshold(value=40, unit="celsius", sources=[], metadata={}, monitoring_enabled=True, metrics_collection=True, circuit_breaker=True),
            RiskThreshold(value=50, unit="celsius", sources=[], metadata={}, monitoring_enabled=True, metrics_collection=True, circuit_breaker=True)
        ],
        "levels": [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.EXTREME]
    }

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
    from A2A_app import app
    return TestClient(app)

# Security fixtures
@pytest.fixture
def mock_jwt_token():
    return "test.jwt.token"

@pytest.fixture
def mock_api_key():
    return "api-key-123"

@pytest.fixture
def mock_user():
    return {"username": "test_user", "roles": ["admin", "user"]}

# Performance fixtures
@pytest.fixture
def performance_metrics():
    return {
        "response_time": 120.5,
        "cpu_percent": 15.0,
        "memory_mb": 256.0,
        "token_usage": {"input": 100, "output": 50, "total": 150}
    }

# Observability fixtures
@pytest.fixture
def mock_observability_manager():
    manager = Mock()
    manager.log_event = Mock(return_value=True)
    manager.send_alert = Mock(return_value=True)
    return manager

# Error scenario fixtures
@pytest.fixture
def error_scenario():
    return {"type": "timeout", "message": "Request timed out"}

# Test markers (pytest.ini or pyproject.toml should be updated accordingly)
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "performance: mark a test as a performance test")
    config.addinivalue_line("markers", "security: mark a test as a security test")

# Update comments to clarify that tools are functions, not Tool objects 