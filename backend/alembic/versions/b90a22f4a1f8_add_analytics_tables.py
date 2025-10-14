"""Add analytics tables

Revision ID: b90a22f4a1f8
Revises: aee3db5aee50
Create Date: 2025-10-14 08:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b90a22f4a1f8"
down_revision: Union[str, Sequence[str], None] = "aee3db5aee50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "metric_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("agent_id", sa.Uuid(), nullable=True),
        sa.Column("conversation_id", sa.Uuid(), nullable=True),
        sa.Column("metric_type", sa.String(length=50), nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_metric_events_id"), "metric_events", ["id"], unique=False)
    op.create_index(
        "idx_metric_user_timestamp", "metric_events", ["user_id", "timestamp"], unique=False
    )
    op.create_index(
        "idx_metric_agent_timestamp",
        "metric_events",
        ["agent_id", "timestamp"],
        unique=False,
    )
    op.create_index(
        "idx_metric_conversation_timestamp",
        "metric_events",
        ["conversation_id", "timestamp"],
        unique=False,
    )
    op.create_index(
        "idx_metric_type_timestamp",
        "metric_events",
        ["metric_type", "timestamp"],
        unique=False,
    )
    op.create_index(
        "idx_metric_name_timestamp",
        "metric_events",
        ["metric_name", "timestamp"],
        unique=False,
    )

    op.create_table(
        "aggregated_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("agent_id", sa.Uuid(), nullable=True),
        sa.Column("metric_type", sa.String(length=50), nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=False),
        sa.Column("aggregation_period", sa.String(length=20), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("sum", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("avg", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("min", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("max", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_aggregated_metrics_id"), "aggregated_metrics", ["id"], unique=False)
    op.create_index(
        "idx_agg_user_period_timestamp",
        "aggregated_metrics",
        ["user_id", "aggregation_period", "period_start"],
        unique=False,
    )
    op.create_index(
        "idx_agg_agent_period_timestamp",
        "aggregated_metrics",
        ["agent_id", "aggregation_period", "period_start"],
        unique=False,
    )
    op.create_index(
        "idx_agg_metric_period_timestamp",
        "aggregated_metrics",
        ["metric_type", "aggregation_period", "period_start"],
        unique=False,
    )

    op.create_table(
        "usage_quotas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("quota_type", sa.String(length=50), nullable=False),
        sa.Column("limit", sa.Float(), nullable=False),
        sa.Column("used", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("reset_period", sa.String(length=20), nullable=False),
        sa.Column(
            "last_reset",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.Column("next_reset", sa.DateTime(timezone=True), nullable=False),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "quota_type", name="uq_usage_quota_user_type"),
    )
    op.create_index(
        "idx_quota_user_type", "usage_quotas", ["user_id", "quota_type"], unique=False
    )

    op.create_table(
        "performance_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("agent_id", sa.Uuid(), nullable=True),
        sa.Column("conversation_id", sa.Uuid(), nullable=True),
        sa.Column("operation", sa.String(length=100), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_performance_metrics_id"), "performance_metrics", ["id"], unique=False)
    op.create_index(
        "idx_perf_operation_timestamp",
        "performance_metrics",
        ["operation", "timestamp"],
        unique=False,
    )
    op.create_index(
        "idx_perf_agent_operation",
        "performance_metrics",
        ["agent_id", "operation"],
        unique=False,
    )
    op.create_index(
        "idx_perf_status_timestamp",
        "performance_metrics",
        ["status", "timestamp"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_perf_status_timestamp", table_name="performance_metrics")
    op.drop_index("idx_perf_agent_operation", table_name="performance_metrics")
    op.drop_index("idx_perf_operation_timestamp", table_name="performance_metrics")
    op.drop_index(op.f("ix_performance_metrics_id"), table_name="performance_metrics")
    op.drop_table("performance_metrics")

    op.drop_index("idx_quota_user_type", table_name="usage_quotas")
    op.drop_table("usage_quotas")

    op.drop_index("idx_agg_metric_period_timestamp", table_name="aggregated_metrics")
    op.drop_index("idx_agg_agent_period_timestamp", table_name="aggregated_metrics")
    op.drop_index("idx_agg_user_period_timestamp", table_name="aggregated_metrics")
    op.drop_index(op.f("ix_aggregated_metrics_id"), table_name="aggregated_metrics")
    op.drop_table("aggregated_metrics")

    op.drop_index("idx_metric_name_timestamp", table_name="metric_events")
    op.drop_index("idx_metric_type_timestamp", table_name="metric_events")
    op.drop_index("idx_metric_conversation_timestamp", table_name="metric_events")
    op.drop_index("idx_metric_agent_timestamp", table_name="metric_events")
    op.drop_index("idx_metric_user_timestamp", table_name="metric_events")
    op.drop_index(op.f("ix_metric_events_id"), table_name="metric_events")
    op.drop_table("metric_events")
