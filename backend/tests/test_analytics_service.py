"""Regression tests for analytics service."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.analytics import UsageQuota
from backend.app.models.user import User
from backend.app.schemas.analytics import (
    MetricEventCreate,
    MetricEventResponse,
    PerformanceMetricCreate,
    PerformanceMetricResponse,
    UsageQuotaResponse,
    UsageStatistics,
)
from backend.app.services.analytics_service import AnalyticsService


def create_user(db_session: Session) -> User:
    """Persist and return a test user."""

    user = User(
        email="test@example.com",
        username="tester",
        hashed_password="hashed",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_create_metric_event_with_metadata(db_session: Session) -> None:
    """Metric events must persist client-provided metadata."""

    user = create_user(db_session)
    service = AnalyticsService(db_session)
    metric = MetricEventCreate(
        user_id=user.id,
        metric_type="api_call",
        metric_name="chat_request",
        value=1.0,
        unit="count",
        metadata={"source": "test"},
    )

    saved = service.create_metric_event(metric)

    assert saved.extra_metadata == {"source": "test"}
    response = MetricEventResponse.model_validate(saved)
    assert response.extra_metadata == {"source": "test"}


def test_create_performance_metric_with_metadata(db_session: Session) -> None:
    """Performance metrics must accept optional metadata payloads."""

    service = AnalyticsService(db_session)
    metric = PerformanceMetricCreate(
        operation="GET /api/health",
        duration_ms=123.4,
        status="success",
        metadata={"trace_id": "abc123"},
    )

    saved = service.create_performance_metric(metric)

    assert saved.extra_metadata == {"trace_id": "abc123"}
    response = PerformanceMetricResponse.model_validate(saved)
    assert response.extra_metadata == {"trace_id": "abc123"}


def test_usage_statistics_returns_all_user_quotas(db_session: Session) -> None:
    """Users can own multiple quota records of different types."""

    user = create_user(db_session)
    now = datetime.now(timezone.utc)
    quota_values = [
        ("api_calls", 100.0),
        ("tokens", 1000.0),
    ]
    for quota_type, limit in quota_values:
        quota = UsageQuota(
            user_id=user.id,
            quota_type=quota_type,
            limit=limit,
            used=0.0,
            reset_period="day",
            last_reset=now,
            next_reset=now + timedelta(days=1),
        )
        db_session.add(quota)
    db_session.commit()

    service = AnalyticsService(db_session)
    stats = service.get_usage_statistics(
        user.id,
        now - timedelta(days=1),
        now + timedelta(days=1),
    )

    assert len(stats.quotas) == 2
    quota_types = sorted(quota.quota_type for quota in stats.quotas)
    assert quota_types == ["api_calls", "tokens"]


def test_usage_statistics_default_list_isolated() -> None:
    """Usage statistics should not share mutable defaults across instances."""

    now = datetime.now(timezone.utc)
    stats_a = UsageStatistics(
        user_id=uuid4(),
        total_api_calls=0,
        total_tokens=0,
        total_cost=0.0,
        avg_response_time_ms=0.0,
        error_rate=0.0,
        period_start=now,
        period_end=now,
    )
    stats_a.quotas.append(
        UsageQuotaResponse(
            id=uuid4(),
            user_id=uuid4(),
            quota_type="api_calls",
            limit=10.0,
            used=0.0,
            reset_period="day",
            last_reset=now,
            next_reset=now,
            extra_metadata=None,
            created_at=now,
            updated_at=now,
        )
    )

    stats_b = UsageStatistics(
        user_id=uuid4(),
        total_api_calls=0,
        total_tokens=0,
        total_cost=0.0,
        avg_response_time_ms=0.0,
        error_rate=0.0,
        period_start=now,
        period_end=now,
    )

    assert stats_b.quotas == []
