"""Tests for group chat functionality."""

import uuid

import pytest
from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.main import app
from backend.app.services import group_chat_service
from backend.app.database import get_db


@pytest.fixture
def api_client(db_session: Session) -> Iterator[TestClient]:
    """Provide TestClient with database dependency override."""

    def _override_get_db() -> Iterator[Session]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def sample_agents(db_session: Session) -> list[models.Agent]:
    """Create sample agents for testing."""
    agents = []
    for i in range(3):
        agent = models.Agent(
            name=f"Test Agent {i+1}",
            description=f"Test agent {i+1} description",
            type="assistant",
            status="active",
        )
        db_session.add(agent)
        db_session.flush()

        version = models.AgentVersion(
            agent_id=agent.id,
            version="1.0.0",
            config={
                "system_message": f"You are test agent {i+1}",
                "model": "gpt-4",
            },
            is_current=True,
        )
        db_session.add(version)
        agent.current_version_id = version.id
        agents.append(agent)

    db_session.commit()
    return agents


@pytest.fixture
def sample_group_chat(
    db_session: Session, sample_agents: list[models.Agent]
) -> models.GroupChat:
    """Create sample group chat for testing."""
    group_chat_data = schemas.GroupChatCreate(
        title="Test Group Chat",
        description="A test group chat",
        selection_strategy="round_robin",
        max_rounds=5,
        allow_repeated_speaker=False,
        participant_agent_ids=[agent.id for agent in sample_agents[:2]],
    )

    group_chat = group_chat_service.create_group_chat(db_session, group_chat_data)
    return group_chat


@pytest.fixture
def group_chat_conversation(
    db_session: Session,
    sample_group_chat: models.GroupChat,
    sample_agents: list[models.Agent],
) -> models.Conversation:
    """Create a conversation with messages linked to a group chat."""
    conversation = models.Conversation(
        agent_id=sample_agents[0].id,
        agent_version_id=None,
        title="Group Chat Conversation",
        extra_data={"group_chat_id": str(sample_group_chat.id)},
    )
    db_session.add(conversation)
    db_session.flush()

    link = models.GroupChatConversation(
        group_chat_id=sample_group_chat.id,
        conversation_id=conversation.id,
        round_number=1,
    )
    db_session.add(link)

    initial_message = models.Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello team",
        extra_data={"agent_name": "User"},
    )
    reply_message = models.Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Response from agent",
        extra_data={"agent_name": sample_agents[0].name},
    )
    db_session.add_all([initial_message, reply_message])
    db_session.commit()

    return conversation


def test_create_group_chat(
    db_session: Session, sample_agents: list[models.Agent]
) -> None:
    """Test creating a group chat."""
    group_chat_data = schemas.GroupChatCreate(
        title="Test Group",
        description="Test description",
        selection_strategy="selector",
        max_rounds=10,
        allow_repeated_speaker=True,
        participant_agent_ids=[agent.id for agent in sample_agents],
    )

    group_chat = group_chat_service.create_group_chat(db_session, group_chat_data)

    assert group_chat.title == "Test Group"
    assert group_chat.selection_strategy == "selector"
    assert group_chat.max_rounds == 10
    assert group_chat.allow_repeated_speaker is True
    assert len(group_chat.participants) == 3


def test_list_group_chats(
    db_session: Session, sample_group_chat: models.GroupChat
) -> None:
    """Test listing group chats."""
    group_chats = group_chat_service.list_group_chats(db_session)
    assert len(group_chats) >= 1
    assert any(gc.id == sample_group_chat.id for gc in group_chats)


def test_get_group_chat(
    db_session: Session, sample_group_chat: models.GroupChat
) -> None:
    """Test getting a group chat by ID."""
    group_chat = group_chat_service.get_group_chat(db_session, sample_group_chat.id)
    assert group_chat is not None
    assert group_chat.id == sample_group_chat.id
    assert group_chat.title == sample_group_chat.title


def test_get_nonexistent_group_chat(db_session: Session) -> None:
    """Test getting a non-existent group chat."""
    fake_id = uuid.uuid4()
    group_chat = group_chat_service.get_group_chat(db_session, fake_id)
    assert group_chat is None


def test_update_group_chat(
    db_session: Session, sample_group_chat: models.GroupChat
) -> None:
    """Test updating a group chat."""
    update_data = schemas.GroupChatUpdate(
        title="Updated Title",
        max_rounds=15,
        selection_strategy="selector",
    )

    updated = group_chat_service.update_group_chat(
        db_session, sample_group_chat.id, update_data
    )

    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.max_rounds == 15
    assert updated.selection_strategy == "selector"


def test_delete_group_chat(
    db_session: Session, sample_group_chat: models.GroupChat
) -> None:
    """Test deleting a group chat."""
    success = group_chat_service.delete_group_chat(db_session, sample_group_chat.id)
    assert success is True

    group_chat = group_chat_service.get_group_chat(db_session, sample_group_chat.id)
    assert group_chat is None


def test_add_participant(
    db_session: Session,
    sample_group_chat: models.GroupChat,
    sample_agents: list[models.Agent],
) -> None:
    """Test adding a participant to group chat."""
    new_agent = sample_agents[2]
    participant_data = schemas.GroupChatParticipantCreate(
        agent_id=new_agent.id,
        speaking_order=3,
    )

    participant = group_chat_service.add_participant(
        db_session, sample_group_chat.id, participant_data
    )

    assert participant is not None
    assert participant.agent_id == new_agent.id
    assert participant.speaking_order == 3


def test_remove_participant(
    db_session: Session,
    sample_group_chat: models.GroupChat,
    sample_agents: list[models.Agent],
) -> None:
    """Test removing a participant from group chat."""
    agent_to_remove = sample_agents[0]

    success = group_chat_service.remove_participant(
        db_session, sample_group_chat.id, agent_to_remove.id
    )

    assert success is True

    participants = group_chat_service.list_participants(
        db_session, sample_group_chat.id
    )
    assert not any(p.agent_id == agent_to_remove.id for p in participants)


def test_list_participants(
    db_session: Session, sample_group_chat: models.GroupChat
) -> None:
    """Test listing participants in a group chat."""
    participants = group_chat_service.list_participants(
        db_session, sample_group_chat.id
    )

    assert len(participants) == 2
    assert all(p.group_chat_id == sample_group_chat.id for p in participants)


def test_list_group_chat_messages(
    db_session: Session,
    sample_group_chat: models.GroupChat,
    group_chat_conversation: models.Conversation,
) -> None:
    """Test listing messages associated with a group chat."""
    messages = group_chat_service.list_group_chat_messages(
        db_session, sample_group_chat.id
    )

    assert len(messages) == 2
    assert [message.role for message in messages] == ["user", "assistant"]


def test_api_create_group_chat(
    api_client: TestClient, sample_agents: list[models.Agent]
) -> None:
    """Test creating group chat via API."""
    response = api_client.post(
        "/api/group-chats",
        json={
            "title": "API Test Group",
            "description": "Created via API",
            "selection_strategy": "round_robin",
            "max_rounds": 5,
            "allow_repeated_speaker": False,
            "participant_agent_ids": [str(agent.id) for agent in sample_agents[:2]],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Test Group"
    assert data["selection_strategy"] == "round_robin"


def test_api_list_group_chats(api_client: TestClient) -> None:
    """Test listing group chats via API."""
    response = api_client.get("/api/group-chats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_get_group_chat(
    api_client: TestClient, sample_group_chat: models.GroupChat
) -> None:
    """Test getting group chat via API."""
    response = api_client.get(f"/api/group-chats/{sample_group_chat.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_group_chat.id)
    assert data["title"] == sample_group_chat.title


def test_api_update_group_chat(
    api_client: TestClient, sample_group_chat: models.GroupChat
) -> None:
    """Test updating group chat via API."""
    response = api_client.put(
        f"/api/group-chats/{sample_group_chat.id}",
        json={"title": "Updated via API", "max_rounds": 20},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated via API"
    assert data["max_rounds"] == 20


def test_api_delete_group_chat(
    api_client: TestClient, sample_group_chat: models.GroupChat
) -> None:
    """Test deleting group chat via API."""
    response = api_client.delete(f"/api/group-chats/{sample_group_chat.id}")
    assert response.status_code == 204


def test_api_add_participant(
    api_client: TestClient,
    sample_group_chat: models.GroupChat,
    sample_agents: list[models.Agent],
) -> None:
    """Test adding participant via API."""
    response = api_client.post(
        f"/api/group-chats/{sample_group_chat.id}/participants",
        json={
            "agent_id": str(sample_agents[2].id),
            "speaking_order": 3,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["agent_id"] == str(sample_agents[2].id)


def test_api_remove_participant(
    api_client: TestClient,
    sample_group_chat: models.GroupChat,
    sample_agents: list[models.Agent],
) -> None:
    """Test removing participant via API."""
    response = api_client.delete(
        f"/api/group-chats/{sample_group_chat.id}/participants/"
        f"{sample_agents[0].id}"
    )
    assert response.status_code == 204


def test_api_list_participants(
    api_client: TestClient, sample_group_chat: models.GroupChat
) -> None:
    """Test listing participants via API."""
    response = api_client.get(
        f"/api/group-chats/{sample_group_chat.id}/participants"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_api_list_group_chat_messages(
    api_client: TestClient,
    sample_group_chat: models.GroupChat,
    group_chat_conversation: models.Conversation,
) -> None:
    """Test listing group chat messages via API."""
    response = api_client.get(f"/api/group-chats/{sample_group_chat.id}/messages")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["conversation_id"] == str(group_chat_conversation.id)
