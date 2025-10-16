"""Tests for agent test endpoint."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app

client = TestClient(app)


def test_test_agent_success(db: Session) -> None:
    """Test testing an agent with valid configuration."""
    # Create an agent
    agent_data = {
        "name": "Test Agent",
        "description": "Test",
        "type": "assistant",
        "initial_config": {
            "system_message": "You are a helpful assistant",
            "temperature": 0.7,
        },
    }

    agent_response = client.post("/api/v1/agents/", json=agent_data)
    agent_id = agent_response.json()["id"]

    # Test the agent
    test_data = {"test_input": "Hello, how are you?"}

    response = client.post(f"/api/v1/agents/{agent_id}/test", json=test_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "response" in data
    assert data["config_valid"] is True
    assert data["system_message_length"] > 0


def test_test_agent_no_system_message(db: Session) -> None:
    """Test testing an agent with no system message."""
    # Create an agent without system message
    agent_data = {
        "name": "Test Agent",
        "description": "Test",
        "type": "assistant",
        "initial_config": {"temperature": 0.7},
    }

    agent_response = client.post("/api/v1/agents/", json=agent_data)
    agent_id = agent_response.json()["id"]

    # Test the agent
    test_data = {"test_input": "Hello"}

    response = client.post(f"/api/v1/agents/{agent_id}/test", json=test_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert "system message" in data["error"].lower()


def test_test_nonexistent_agent(db: Session) -> None:
    """Test testing a non-existent agent."""
    import uuid

    fake_id = uuid.uuid4()
    test_data = {"test_input": "Hello"}

    response = client.post(f"/api/v1/agents/{fake_id}/test", json=test_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["error"].lower()


def test_test_agent_no_version(db: Session) -> None:
    """Test testing an agent with no active version."""
    # Create an agent without initial config
    agent_data = {
        "name": "Test Agent",
        "description": "Test",
        "type": "assistant",
    }

    agent_response = client.post("/api/v1/agents/", json=agent_data)
    agent_id = agent_response.json()["id"]

    # Test the agent
    test_data = {"test_input": "Hello"}

    response = client.post(f"/api/v1/agents/{agent_id}/test", json=test_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "version" in data["error"].lower()
