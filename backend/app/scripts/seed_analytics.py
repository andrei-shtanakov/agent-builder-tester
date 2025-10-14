"""Seed the database with demo analytics data for dashboards."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.database import SessionLocal
from backend.app.models import (
    Agent,
    AgentVersion,
    Conversation,
    MetricEvent,
    PerformanceMetric,
    UsageQuota,
    User,
)

SEED_EMAIL = "analytics@example.com"
SEED_USERNAME = "analytics-demo"
SEED_PASSWORD = "AnalyticsDemo!123"
SEED_AGENT_NAME = "Analytics Demo Agent"
SEED_CONVERSATION_TITLE = "Analytics Demo Conversation"
SEED_OPERATION = "agent.run"
SEED_METADATA_TAG = {"seed": "analytics-demo"}


def seed_demo_analytics() -> None:
    """Populate the database with demo analytics entities and metrics."""
    with SessionLocal() as session:
        user = _get_or_create_user(session)
        agent = _get_or_create_agent(session, user)
        conversation = _get_or_create_conversation(session, agent)

        created_any = False
        created_any |= _seed_metric_events(session, user, agent, conversation)
        created_any |= _seed_performance_metrics(session, agent, conversation)
        created_any |= _seed_usage_quotas(session, user)

        if created_any:
            session.commit()
        else:
            session.rollback()


def _get_or_create_user(session: Session) -> User:
    user = session.query(User).filter(User.email == SEED_EMAIL).first()
    if user is not None:
        return user

    hashed_password = get_password_hash(SEED_PASSWORD)
    user = User(
        email=SEED_EMAIL,
        username=SEED_USERNAME,
        hashed_password=hashed_password,
        full_name="Analytics Demo User",
        is_superuser=True,
    )
    session.add(user)
    session.flush()
    return user


def _get_or_create_agent(session: Session, owner: User) -> Agent:
    agent = session.query(Agent).filter(Agent.name == SEED_AGENT_NAME).first()
    if agent is not None:
        if agent.current_version_id is None and agent.versions:
            latest_version = agent.versions[-1]
            agent.current_version_id = latest_version.id
        return agent

    agent = Agent(
        name=SEED_AGENT_NAME,
        description="Demo agent used for seeded analytics visualisations",
        type="assistant",
        status="active",
        tags={"category": "demo", "owner": owner.username},
    )
    session.add(agent)
    session.flush()

    version = AgentVersion(
        agent_id=agent.id,
        version="1.0.0",
        config={
            "model": "gpt-4o-mini",
            "system_message": "You are an analytics demonstration agent.",
        },
        changelog="Initial demo configuration",
        created_by=owner.full_name or owner.username,
        is_current=True,
    )
    session.add(version)
    session.flush()

    agent.current_version_id = version.id
    return agent


def _get_or_create_conversation(session: Session, agent: Agent) -> Conversation:
    conversation = (
        session.query(Conversation)
        .filter(Conversation.title == SEED_CONVERSATION_TITLE)
        .first()
    )
    if conversation is not None:
        return conversation

    now = datetime.now(timezone.utc)
    conversation = Conversation(
        agent_id=agent.id,
        agent_version_id=agent.current_version_id,
        title=SEED_CONVERSATION_TITLE,
        status="completed",
        started_at=now - timedelta(days=3),
        ended_at=now - timedelta(days=3) + timedelta(minutes=15),
        extra_data={"seed": "analytics-demo"},
    )
    session.add(conversation)
    session.flush()
    return conversation


def _seed_metric_events(
    session: Session, user: User, agent: Agent, conversation: Conversation
) -> bool:
    existing = (
        session.query(MetricEvent)
        .filter(MetricEvent.metric_name == "demo.cost")
        .limit(1)
        .first()
    )
    if existing is not None:
        return False

    now = datetime.now(timezone.utc)
    events: list[MetricEvent] = []
    for days_back in range(7):
        timestamp = (now - timedelta(days=days_back)).replace(
            hour=15, minute=30, second=0, microsecond=0
        )
        cost_value = round(4.25 + days_back * 0.35, 2)
        token_value = float(4200 + days_back * 180)
        api_calls_value = float(45 + days_back * 3)

        events.extend(
            _build_metric_triplet(
                user_id=user.id,
                agent_id=agent.id,
                conversation_id=conversation.id,
                timestamp=timestamp,
                cost=cost_value,
                tokens=token_value,
                api_calls=api_calls_value,
            )
        )

    session.add_all(events)
    return True


def _build_metric_triplet(
    *,
    user_id: UUID,
    agent_id: UUID,
    conversation_id: UUID,
    timestamp: datetime,
    cost: float,
    tokens: float,
    api_calls: float,
) -> Tuple[MetricEvent, MetricEvent, MetricEvent]:
    return (
        MetricEvent(
            user_id=user_id,
            agent_id=agent_id,
            conversation_id=conversation_id,
            metric_type="cost",
            metric_name="demo.cost",
            value=cost,
            unit="USD",
            extra_metadata=SEED_METADATA_TAG,
            timestamp=timestamp,
        ),
        MetricEvent(
            user_id=user_id,
            agent_id=agent_id,
            conversation_id=conversation_id,
            metric_type="token_usage",
            metric_name="demo.tokens",
            value=tokens,
            unit="tokens",
            extra_metadata=SEED_METADATA_TAG,
            timestamp=timestamp + timedelta(minutes=1),
        ),
        MetricEvent(
            user_id=user_id,
            agent_id=agent_id,
            conversation_id=conversation_id,
            metric_type="api_call",
            metric_name="demo.calls",
            value=api_calls,
            unit="calls",
            extra_metadata=SEED_METADATA_TAG,
            timestamp=timestamp + timedelta(minutes=2),
        ),
    )


def _seed_performance_metrics(
    session: Session, agent: Agent, conversation: Conversation
) -> bool:
    existing = (
        session.query(PerformanceMetric)
        .filter(PerformanceMetric.operation == SEED_OPERATION)
        .limit(1)
        .first()
    )
    if existing is not None:
        return False

    now = datetime.now(timezone.utc)
    metrics: list[PerformanceMetric] = []
    for index in range(20):
        timestamp = now - timedelta(hours=index)
        status = "error" if index % 5 == 0 else "success"
        duration = 180 + index * 7
        metric = PerformanceMetric(
            agent_id=agent.id,
            conversation_id=conversation.id,
            operation=SEED_OPERATION,
            duration_ms=float(duration),
            status=status,
            error_message="Upstream timeout" if status == "error" else None,
            extra_metadata=SEED_METADATA_TAG,
            timestamp=timestamp,
        )
        metrics.append(metric)

    session.add_all(metrics)
    return True


def _seed_usage_quotas(session: Session, user: User) -> bool:
    now = datetime.now(timezone.utc)
    created_any = False
    quota_configs = {
        "api_call": (12000.0, 480.0),
        "token_usage": (250_000.0, 32_000.0),
        "cost": (500.0, 78.0),
    }

    for quota_type, (limit, used) in quota_configs.items():
        quota = (
            session.query(UsageQuota)
            .filter(UsageQuota.user_id == user.id, UsageQuota.quota_type == quota_type)
            .first()
        )
        if quota is not None:
            continue

        quota = UsageQuota(
            user_id=user.id,
            quota_type=quota_type,
            limit=limit,
            used=used,
            reset_period="month",
            last_reset=now - timedelta(days=10),
            next_reset=now + timedelta(days=20),
            extra_metadata=SEED_METADATA_TAG,
        )
        session.add(quota)
        created_any = True

    return created_any


def main() -> None:
    """CLI entrypoint for the seeding script."""
    seed_demo_analytics()


if __name__ == "__main__":
    main()
