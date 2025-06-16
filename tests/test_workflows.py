"""
End-to-end workflow tests for the Climate Risk Analysis System.
"""

import pytest
from fastapi.testclient import TestClient
from app import app
from src.multi_agent_system.agent_team import Agent
from src.multi_agent_system.session_manager import SessionManager

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.mark.asyncio
async def test_complete_risk_analysis_workflow(client, mock_session_manager, mock_agent):
    """Test the complete risk analysis workflow from request to response."""
    # 1. Submit analysis request
    response = client.post(
        "/analyze",
        json={"location": "2038 Forest Club Drive, Orlando, FL 32804"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # 2. Verify session creation
    session_id = data.get("session_id")
    assert session_id is not None
    assert session_id in mock_session_manager.sessions
    
    # 3. Verify agent execution
    mock_agent.run.assert_called_once()
    
    # 4. Verify result structure
    result = data["result"]
    assert "temperature" in result
    assert "precipitation" in result
    assert "wind" in result
    assert "humidity" in result
    assert "air_quality" in result
    
    # 5. Verify risk levels
    for risk_type, risk_data in result.items():
        assert "value" in risk_data
        assert "unit" in risk_data
        assert "risk_level" in risk_data
        assert risk_data["risk_level"] in ["low", "moderate", "high", "extreme"]

@pytest.mark.asyncio
async def test_error_recovery_workflow(client, mock_session_manager, mock_agent):
    """Test error recovery workflow."""
    # 1. Simulate initial error
    mock_agent.run.side_effect = Exception("Initial error")
    
    # 2. Submit request
    response = client.post(
        "/analyze",
        json={"location": "Invalid Location"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    
    # 3. Verify error handling
    assert "error" in data
    assert "retry_count" in data
    
    # 4. Simulate successful retry
    mock_agent.run.side_effect = None
    mock_agent.run.return_value = {
        "status": "success",
        "result": {
            "temperature": {"value": 25.5, "unit": "celsius", "risk_level": "low"}
        }
    }
    
    # 5. Retry request
    response = client.post(
        "/analyze",
        json={"location": "2038 Forest Club Drive, Orlando, FL 32804"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

@pytest.mark.asyncio
async def test_concurrent_analysis_workflow(client, mock_session_manager, mock_agent):
    """Test concurrent analysis workflow."""
    import asyncio
    
    # 1. Set up concurrent requests
    locations = [
        "2038 Forest Club Drive, Orlando, FL 32804",
        "123 Main St, New York, NY 10001",
        "456 Market St, San Francisco, CA 94105"
    ]
    
    # 2. Submit concurrent requests
    async def make_request(location):
        return client.post("/analyze", json={"location": location})
    
    responses = await asyncio.gather(
        *[make_request(loc) for loc in locations]
    )
    
    # 3. Verify all requests were handled
    assert all(r.status_code == 200 for r in responses)
    
    # 4. Verify session management
    assert len(mock_session_manager.sessions) == 3
    
    # 5. Verify agent execution
    assert mock_agent.run.call_count == 3

@pytest.mark.asyncio
async def test_cache_workflow(client, mock_session_manager, mock_agent):
    """Test caching workflow."""
    location = "2038 Forest Club Drive, Orlando, FL 32804"
    
    # 1. First request (cache miss)
    response = client.post("/analyze", json={"location": location})
    assert response.status_code == 200
    first_data = response.json()
    assert first_data["status"] == "success"
    
    # 2. Second request (cache hit)
    response = client.post("/analyze", json={"location": location})
    assert response.status_code == 200
    second_data = response.json()
    assert second_data["status"] == "success"
    
    # 3. Verify cache was used
    assert mock_agent.run.call_count == 1
    
    # 4. Verify results are consistent
    assert first_data["result"] == second_data["result"] 