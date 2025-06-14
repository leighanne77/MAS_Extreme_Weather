"""
Tests for FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app import app

def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_session(client: TestClient, mock_session_manager):
    """Test session creation endpoint."""
    with patch("app.session_manager", mock_session_manager):
        response = client.post("/sessions")
        assert response.status_code == 201
        assert "session_id" in response.json()

def test_get_session(client: TestClient, mock_session_manager, mock_session):
    """Test session retrieval endpoint."""
    mock_session_manager.get_session.return_value = mock_session
    with patch("app.session_manager", mock_session_manager):
        response = client.get(f"/sessions/{mock_session.id}")
        assert response.status_code == 200
        assert response.json()["id"] == mock_session.id

def test_execute_task(client: TestClient, mock_session_manager, mock_session):
    """Test task execution endpoint."""
    mock_session_manager.get_session.return_value = mock_session
    with patch("app.session_manager", mock_session_manager):
        response = client.post(
            f"/sessions/{mock_session.id}/tasks",
            json={"task": "test_task"}
        )
        assert response.status_code == 200
        assert "result" in response.json()

def test_get_artifacts(client: TestClient, mock_session_manager, mock_session):
    """Test artifact retrieval endpoint."""
    mock_session_manager.get_session.return_value = mock_session
    with patch("app.session_manager", mock_session_manager):
        response = client.get(f"/sessions/{mock_session.id}/artifacts")
        assert response.status_code == 200
        assert isinstance(response.json(), list) 