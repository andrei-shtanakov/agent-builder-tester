"""AutoGen group chat orchestration manager."""

from typing import Any, cast
from uuid import UUID

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import ChatAgent, TaskResult
from autogen_agentchat.teams import (
    RoundRobinGroupChat,
    SelectorGroupChat,
)
from autogen_core.models import ChatCompletionClient
from sqlalchemy.orm import Session

from backend.app import models


class GroupChatManager:
    """Manager for AutoGen group chat orchestration."""

    def __init__(
        self,
        db: Session,
        group_chat: models.GroupChat,
        model_client: ChatCompletionClient | None = None,
    ):
        """
        Initialize group chat manager.

        Args:
            db: Database session
            group_chat: Group chat model
            model_client: Optional model client for agents
        """
        self.db = db
        self.group_chat = group_chat
        self.model_client = model_client
        self.agents: list[AssistantAgent] = []

    def _create_agent_from_model(
        self, agent_model: models.Agent, config: dict[str, Any]
    ) -> AssistantAgent:
        """
        Create AutoGen agent from database model.

        Args:
            agent_model: Agent database model
            config: Agent configuration

        Returns:
            AutoGen AssistantAgent
        """
        system_message = config.get("system_message", "You are a helpful assistant.")

        if self.model_client is None:
            msg = "Model client is required to create agents"
            raise ValueError(msg)

        agent = AssistantAgent(
            name=agent_model.name,
            description=agent_model.description or "",
            model_client=self.model_client,
            system_message=system_message,
        )
        return agent

    def load_participants(self) -> None:
        """Load and initialize agents from group chat participants."""
        participants = (
            self.db.query(models.GroupChatParticipant)
            .filter(models.GroupChatParticipant.group_chat_id == self.group_chat.id)
            .order_by(models.GroupChatParticipant.speaking_order)
            .all()
        )

        for participant in participants:
            agent_model = (
                self.db.query(models.Agent)
                .filter(models.Agent.id == participant.agent_id)
                .first()
            )

            if not agent_model:
                continue

            if participant.agent_version_id:
                version = (
                    self.db.query(models.AgentVersion)
                    .filter(models.AgentVersion.id == participant.agent_version_id)
                    .first()
                )
                config = version.config if version else {}
            elif agent_model.current_version:
                config = agent_model.current_version.config
            else:
                config = {}

            agent = self._create_agent_from_model(agent_model, config)
            self.agents.append(agent)

    async def run_conversation(
        self, initial_message: str, conversation_id: UUID
    ) -> TaskResult:
        """
        Run group chat conversation.

        Args:
            initial_message: Initial message to start conversation
            conversation_id: Conversation ID for logging

        Returns:
            Task result from group chat
        """
        if not self.agents:
            msg = "No agents loaded. Call load_participants() first."
            raise ValueError(msg)

        if self.model_client is None:
            msg = "Model client is required to run group chat"
            raise ValueError(msg)

        chat_agents = cast(list[ChatAgent], self.agents)

        if self.group_chat.selection_strategy == "round_robin":
            team = RoundRobinGroupChat(
                participants=chat_agents,  # type: ignore[arg-type]
                max_turns=self.group_chat.max_rounds,
            )
        elif self.group_chat.selection_strategy == "selector":
            team = SelectorGroupChat(
                participants=chat_agents,  # type: ignore[arg-type]
                model_client=self.model_client,
                max_turns=self.group_chat.max_rounds,
                allow_repeated_speaker=self.group_chat.allow_repeated_speaker,
            )
        else:
            msg = (
                f"Unsupported selection strategy: {self.group_chat.selection_strategy}"
            )
            raise ValueError(msg)

        result = await team.run(task=initial_message)

        self._save_conversation_messages(result, conversation_id)

        return result

    def _save_conversation_messages(
        self, result: TaskResult, conversation_id: UUID
    ) -> None:
        """
        Save conversation messages to database.

        Args:
            result: Task result containing messages
            conversation_id: Conversation ID
        """
        for message in result.messages:
            content = getattr(message, "content", str(message))
            source = getattr(message, "source", "assistant")

            msg_record = models.Message(
                conversation_id=conversation_id,
                role=source,
                content=str(content),
                extra_data={
                    "agent_name": source,
                    "message_type": type(message).__name__,
                },
            )
            self.db.add(msg_record)

        self.db.commit()


async def run_group_chat(
    db: Session,
    group_chat_id: UUID,
    initial_message: str,
    conversation_id: UUID,
    model_client: ChatCompletionClient | None = None,
) -> TaskResult:
    """
    Run a group chat conversation.

    Args:
        db: Database session
        group_chat_id: Group chat ID
        initial_message: Initial message
        conversation_id: Conversation ID for logging
        model_client: Optional model client

    Returns:
        Task result from conversation
    """
    group_chat = (
        db.query(models.GroupChat).filter(models.GroupChat.id == group_chat_id).first()
    )

    if not group_chat:
        msg = f"Group chat {group_chat_id} not found"
        raise ValueError(msg)

    manager = GroupChatManager(db, group_chat, model_client)
    manager.load_participants()
    result = await manager.run_conversation(initial_message, conversation_id)

    return result
