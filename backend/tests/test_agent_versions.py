"""Tests for agent version endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app

client = TestClient(app)


def test_create_agent_version(db: Session) -> None:
    """Test creating a new version for an agent."""
    # Create an agent first
    agent_data = {
        "name": "Test Agent",
        "description": "Test description",
        "type": "assistant",
        "status": "draft",
        "initial_config": {
            "system_message": "You are a helpful assistant",
            "temperature": 0.7,
        },
    }

    agent_response = client.post("/api/v1/agents/", json=agent_data)
    assert agent_response.status_code == 201
    agent = agent_response.json()
    agent_id = agent["id"]

    # Create a new version
    version_data = {
        "version": "2.0.0",
        "config": {
            "system_message": "You are an improved helpful assistant",
            "temperature": 0.8,
            "max_tokens": 2000,
        },
        "changelog": "Improved system message and increased max tokens",
        "created_by": "test_user",
    }

    response = client.post(f"/api/v1/agents/{agent_id}/versions", json=version_data)

    assert response.status_code == 201
    data = response.json()
    assert data["version"] == version_data["version"]
    assert data["config"] == version_data["config"]
    assert data["changelog"] == version_data["changelog"]
    assert data["agent_id"] == agent_id
    assert data["is_current"] is True


def test_create_version_for_nonexistent_agent(db: Session) -> None:
    """Test creating a version for a non-existent agent."""
    import uuid

    fake_id = uuid.uuid4()
    version_data = {
        "version": "2.0.0",
        "config": {"system_message": "Test"},
        "changelog": "Test",
    }

    response = client.post(f"/api/v1/agents/{fake_id}/versions", json=version_data)

    assert response.status_code == 404


def test_version_becomes_current(db: Session) -> None:
    """Test that new version becomes current and old one is not."""
    # Create an agent
    agent_data = {
        "name": "Test Agent",
        "description": "Test",
        "type": "assistant",
        "initial_config": {"system_message": "V1"},
    }

    agent_response = client.post("/api/v1/agents/", json=agent_data)
    agent_id = agent_response.json()["id"]

    # Create version 2
    version2_data = {
        "version": "2.0.0",
        "config": {"system_message": "V2"},
        "changelog": "Version 2",
    }

    v2_response = client.post(f"/api/v1/agents/{agent_id}/versions", json=version2_data)
    assert v2_response.status_code == 201

    # Get agent and check versions
    agent_response = client.get(f"/api/v1/agents/{agent_id}")
    agent = agent_response.json()

    # Check that only the latest version is current
    current_versions = [v for v in agent["versions"] if v["is_current"]]
    assert len(current_versions) == 1
    assert current_versions[0]["version"] == "2.0.0"
