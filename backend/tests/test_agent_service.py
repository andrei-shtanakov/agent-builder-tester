"""Tests for agent service."""

from backend.app import schemas
from backend.app.services import agent_service


def test_create_agent(db_session):
    """Test agent creation."""
    agent_data = schemas.AgentCreate(
        name="Test Agent",
        description="A test agent",
        type="assistant",
        initial_config={"model": "gpt-4"},
    )
    agent = agent_service.create_agent(db_session, agent_data)

    assert agent.id is not None
    assert agent.name == "Test Agent"
    assert agent.type == "assistant"
    assert agent.status == "draft"


def test_list_agents(db_session):
    """Test listing agents."""
    # Create test agents
    for i in range(3):
        agent_data = schemas.AgentCreate(
            name=f"Agent {i}",
            description=f"Description {i}",
            type="assistant",
        )
        agent_service.create_agent(db_session, agent_data)

    agents = agent_service.list_agents(db_session)
    assert len(agents) == 3


def test_get_agent(db_session):
    """Test getting agent by ID."""
    agent_data = schemas.AgentCreate(
        name="Test Agent",
        type="assistant",
    )
    created_agent = agent_service.create_agent(db_session, agent_data)

    agent = agent_service.get_agent(db_session, created_agent.id)
    assert agent is not None
    assert agent.id == created_agent.id
    assert agent.name == "Test Agent"


def test_update_agent(db_session):
    """Test updating agent."""
    agent_data = schemas.AgentCreate(
        name="Test Agent",
        type="assistant",
    )
    created_agent = agent_service.create_agent(db_session, agent_data)

    update_data = schemas.AgentUpdate(name="Updated Agent", status="active")
    updated_agent = agent_service.update_agent(
        db_session, created_agent.id, update_data
    )

    assert updated_agent is not None
    assert updated_agent.name == "Updated Agent"
    assert updated_agent.status == "active"


def test_delete_agent(db_session):
    """Test deleting agent."""
    agent_data = schemas.AgentCreate(
        name="Test Agent",
        type="assistant",
    )
    created_agent = agent_service.create_agent(db_session, agent_data)

    success = agent_service.delete_agent(db_session, created_agent.id)
    assert success is True

    agent = agent_service.get_agent(db_session, created_agent.id)
    assert agent is None
