"""Analytics and metrics database models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class MetricEvent(Base):
    """Model for storing individual metric events.

    Captures granular metrics like API calls, token usage, costs, etc.
    """

    __tablename__ = "metric_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    metric_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 'api_call', 'token_usage', 'cost', 'latency', 'error'
    metric_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # Specific metric name
    value: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # Numeric value of the metric
    unit: Mapped[str] = mapped_column(String(20), nullable=True)  # 'tokens', 'ms', '$'
    extra_metadata: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Additional context
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("idx_metric_user_timestamp", "user_id", "timestamp"),
        Index("idx_metric_agent_timestamp", "agent_id", "timestamp"),
        Index("idx_metric_type_timestamp", "metric_type", "timestamp"),
        Index("idx_metric_name_timestamp", "metric_name", "timestamp"),
        Index("idx_metric_conversation_timestamp", "conversation_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"<MetricEvent(id={self.id}, "
            f"metric_type={self.metric_type}, value={self.value})>"
        )


class AggregatedMetric(Base):
    """Model for storing pre-aggregated metrics.

    Stores hourly/daily/monthly rollups for faster queries.
    """

    __tablename__ = "aggregated_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    aggregation_period: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # 'hour', 'day', 'week', 'month'
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sum: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit: Mapped[str] = mapped_column(String(20), nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Composite indexes
    __table_args__ = (
        Index(
            "idx_agg_user_period_timestamp", "user_id", "aggregation_period", "period_start"
        ),
        Index(
            "idx_agg_agent_period_timestamp",
            "agent_id",
            "aggregation_period",
            "period_start",
        ),
        Index(
            "idx_agg_metric_period_timestamp",
            "metric_type",
            "aggregation_period",
            "period_start",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AggregatedMetric(id={self.id}, "
            f"metric_type={self.metric_type}, period={self.aggregation_period})>"
        )


class UsageQuota(Base):
    """Model for tracking user usage quotas and limits."""

    __tablename__ = "usage_quotas"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    quota_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'api_calls', 'tokens', 'cost'
    limit: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # Maximum allowed value
    used: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Current
    reset_period: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'hour', 'day', 'month'
    last_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    next_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("idx_quota_user_type", "user_id", "quota_type"),
        UniqueConstraint("user_id", "quota_type", name="uq_usage_quota_user_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<UsageQuota(id={self.id}, "
            f"user_id={self.user_id}, used={self.used}/{self.limit})>"
        )


class PerformanceMetric(Base):
    """Model for tracking system and agent performance metrics."""

    __tablename__ = "performance_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    operation: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # API endpoint or operation name
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'success', 'error'
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Request/response details
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    __table_args__ = (
        Index("idx_perf_operation_timestamp", "operation", "timestamp"),
        Index("idx_perf_agent_operation", "agent_id", "operation"),
        Index("idx_perf_status_timestamp", "status", "timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"<PerformanceMetric(id={self.id}, "
            f"operation={self.operation}, duration={self.duration_ms}ms)>"
        )
