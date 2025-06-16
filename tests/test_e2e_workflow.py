"""
End-to-end tests for the complete system workflow.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import json

from src.multi_agent_system.agent_team import Agent
from src.multi_agent_system.session_manager import SessionManager
from src.multi_agent_system.enhanced_coordinator import EnhancedADKCoordinator
from src.multi_agent_system.artifact_manager import ArtifactManager
from src.multi_agent_system.observability import PatternMonitor
from src.multi_agent_system.risk_definitions import RiskDefinition, RiskType, RiskLevel

@pytest.fixture
def e2e_test_data() -> Dict[str, Any]:
    """Create test data for end-to-end testing.
    
    Returns:
        Dict[str, Any]: Test data including location, time range, and expected results
    """
    return {
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "name": "San Francisco"
        },
        "time_range": {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-12-31T23:59:59Z"
        },
        "expected_risks": [
            RiskType.TEMPERATURE,
            RiskType.PRECIPITATION,
            RiskType.WIND
        ]
    }

@pytest.mark.asyncio
async def test_complete_workflow(
    test_client,
    mock_agent,
    mock_session_manager,
    mock_artifact_manager,
    mock_pattern_monitor,
    enhanced_coordinator,
    e2e_test_data
):
    """Test the complete system workflow from data collection to risk analysis."""
    
    # 1. Initialize session
    session_response = await test_client.post(
        "/api/sessions",
        json={"location": e2e_test_data["location"]}
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["session_id"]
    
    # 2. Start data collection
    collection_response = await test_client.post(
        f"/api/sessions/{session_id}/collect",
        json={"time_range": e2e_test_data["time_range"]}
    )
    assert collection_response.status_code == 200
    
    # 3. Verify data collection progress
    progress_response = await test_client.get(
        f"/api/sessions/{session_id}/progress"
    )
    assert progress_response.status_code == 200
    progress = progress_response.json()
    assert "status" in progress
    assert "completed_steps" in progress
    
    # 4. Start risk analysis
    analysis_response = await test_client.post(
        f"/api/sessions/{session_id}/analyze"
    )
    assert analysis_response.status_code == 200
    
    # 5. Get analysis results
    results_response = await test_client.get(
        f"/api/sessions/{session_id}/results"
    )
    assert results_response.status_code == 200
    results = results_response.json()
    
    # 6. Verify results structure
    assert "risks" in results
    assert "recommendations" in results
    assert "confidence" in results
    
    # 7. Verify risk types
    risk_types = [risk["type"] for risk in results["risks"]]
    for expected_risk in e2e_test_data["expected_risks"]:
        assert expected_risk in risk_types
    
    # 8. Verify recommendations
    assert len(results["recommendations"]) > 0
    for rec in results["recommendations"]:
        assert "action" in rec
        assert "priority" in rec
        assert "description" in rec

@pytest.mark.asyncio
async def test_error_recovery(
    test_client,
    mock_agent,
    mock_session_manager,
    mock_artifact_manager,
    mock_pattern_monitor,
    enhanced_coordinator,
    e2e_test_data
):
    """Test system's ability to recover from errors during workflow."""
    
    # 1. Initialize session with invalid location
    invalid_location = e2e_test_data["location"].copy()
    invalid_location["latitude"] = 200  # Invalid latitude
    
    session_response = await test_client.post(
        "/api/sessions",
        json={"location": invalid_location}
    )
    assert session_response.status_code == 400
    
    # 2. Initialize session with valid location
    session_response = await test_client.post(
        "/api/sessions",
        json={"location": e2e_test_data["location"]}
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["session_id"]
    
    # 3. Start data collection with invalid time range
    invalid_time_range = e2e_test_data["time_range"].copy()
    invalid_time_range["start"] = "invalid_date"
    
    collection_response = await test_client.post(
        f"/api/sessions/{session_id}/collect",
        json={"time_range": invalid_time_range}
    )
    assert collection_response.status_code == 400
    
    # 4. Retry with valid time range
    collection_response = await test_client.post(
        f"/api/sessions/{session_id}/collect",
        json={"time_range": e2e_test_data["time_range"]}
    )
    assert collection_response.status_code == 200
    
    # 5. Verify error recovery
    progress_response = await test_client.get(
        f"/api/sessions/{session_id}/progress"
    )
    assert progress_response.status_code == 200
    progress = progress_response.json()
    assert progress["status"] == "in_progress"
    assert "error_count" in progress
    assert progress["error_count"] == 0

@pytest.mark.asyncio
async def test_performance_metrics(
    test_client,
    mock_agent,
    mock_session_manager,
    mock_artifact_manager,
    mock_pattern_monitor,
    enhanced_coordinator,
    e2e_test_data
):
    """Test system performance metrics during workflow execution."""
    
    # 1. Initialize session
    start_time = datetime.now()
    
    session_response = await test_client.post(
        "/api/sessions",
        json={"location": e2e_test_data["location"]}
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["session_id"]
    
    # 2. Start data collection
    collection_response = await test_client.post(
        f"/api/sessions/{session_id}/collect",
        json={"time_range": e2e_test_data["time_range"]}
    )
    assert collection_response.status_code == 200
    
    # 3. Get performance metrics
    metrics_response = await test_client.get(
        f"/api/sessions/{session_id}/metrics"
    )
    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    
    # 4. Verify performance metrics
    assert "response_times" in metrics
    assert "resource_usage" in metrics
    assert "error_rates" in metrics
    
    # 5. Verify response times are within acceptable range
    for endpoint, time in metrics["response_times"].items():
        assert time < 5.0  # Response time should be under 5 seconds
    
    # 6. Verify resource usage
    assert metrics["resource_usage"]["cpu_percent"] < 80
    assert metrics["resource_usage"]["memory_percent"] < 80
    
    # 7. Verify error rates
    assert metrics["error_rates"]["total"] == 0
    assert metrics["error_rates"]["recovered"] == 0

@pytest.mark.asyncio
async def test_data_persistence(
    test_client,
    mock_agent,
    mock_session_manager,
    mock_artifact_manager,
    mock_pattern_monitor,
    enhanced_coordinator,
    e2e_test_data
):
    """Test data persistence and retrieval during workflow."""
    
    # 1. Initialize session
    session_response = await test_client.post(
        "/api/sessions",
        json={"location": e2e_test_data["location"]}
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["session_id"]
    
    # 2. Start data collection
    collection_response = await test_client.post(
        f"/api/sessions/{session_id}/collect",
        json={"time_range": e2e_test_data["time_range"]}
    )
    assert collection_response.status_code == 200
    
    # 3. Get collected data
    data_response = await test_client.get(
        f"/api/sessions/{session_id}/data"
    )
    assert data_response.status_code == 200
    data = data_response.json()
    
    # 4. Verify data structure
    assert "weather_data" in data
    assert "risk_data" in data
    assert "metadata" in data
    
    # 5. Verify data persistence
    # Simulate system restart by creating new session manager
    new_session_manager = SessionManager()
    
    # 6. Retrieve data after "restart"
    restored_data_response = await test_client.get(
        f"/api/sessions/{session_id}/data"
    )
    assert restored_data_response.status_code == 200
    restored_data = restored_data_response.json()
    
    # 7. Verify data integrity
    assert restored_data == data
    assert "weather_data" in restored_data
    assert "risk_data" in restored_data
    assert "metadata" in restored_data 