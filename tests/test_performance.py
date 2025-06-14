"""
Performance tests for the Climate Risk Analysis System.
"""

import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from app import app
from multi_tool_agent.session_manager import SessionManager

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

def test_response_time(client):
    """Test response time for analysis requests."""
    location = "2038 Forest Club Drive, Orlando, FL 32804"
    
    # Measure response time
    start_time = time.time()
    response = client.post("/analyze", json={"location": location})
    end_time = time.time()
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Check response time
    response_time = end_time - start_time
    assert response_time < 5.0  # Should respond within 5 seconds

@pytest.mark.asyncio
async def test_concurrent_performance(client):
    """Test performance under concurrent load."""
    locations = [
        "2038 Forest Club Drive, Orlando, FL 32804",
        "123 Main St, New York, NY 10001",
        "456 Market St, San Francisco, CA 94105",
        "789 State St, Chicago, IL 60601",
        "321 Market St, Seattle, WA 98101"
    ]
    
    # Measure concurrent performance
    start_time = time.time()
    
    async def make_request(location):
        return client.post("/analyze", json={"location": location})
    
    responses = await asyncio.gather(
        *[make_request(loc) for loc in locations]
    )
    
    end_time = time.time()
    
    # Verify responses
    assert all(r.status_code == 200 for r in responses)
    assert all(r.json()["status"] == "success" for r in responses)
    
    # Check total time
    total_time = end_time - start_time
    assert total_time < 10.0  # Should handle 5 concurrent requests within 10 seconds

def test_memory_usage(client):
    """Test memory usage during analysis."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform analysis
    response = client.post(
        "/analyze",
        json={"location": "2038 Forest Club Drive, Orlando, FL 32804"}
    )
    assert response.status_code == 200
    
    # Check memory usage
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable (less than 100MB)
    assert memory_increase < 100 * 1024 * 1024

def test_cache_performance(client):
    """Test cache performance."""
    location = "2038 Forest Club Drive, Orlando, FL 32804"
    
    # First request (cache miss)
    start_time = time.time()
    response = client.post("/analyze", json={"location": location})
    first_time = time.time() - start_time
    
    # Second request (cache hit)
    start_time = time.time()
    response = client.post("/analyze", json={"location": location})
    second_time = time.time() - start_time
    
    # Cache hit should be significantly faster
    assert second_time < first_time * 0.5  # At least 50% faster

def test_session_cleanup_performance():
    """Test session cleanup performance."""
    manager = SessionManager()
    
    # Create multiple sessions
    for _ in range(100):
        asyncio.run(manager.create_session())
    
    # Measure cleanup time
    start_time = time.time()
    asyncio.run(manager.cleanup_inactive_sessions())
    cleanup_time = time.time() - start_time
    
    # Cleanup should be fast
    assert cleanup_time < 1.0  # Should clean up within 1 second 