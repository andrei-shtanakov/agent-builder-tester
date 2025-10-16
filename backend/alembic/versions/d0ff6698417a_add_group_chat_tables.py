"""Add group chat tables

Revision ID: d0ff6698417a
Revises: 627fe3ff9cdf
Create Date: 2025-10-14 06:15:19.428014

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d0ff6698417a"
down_revision: Union[str, Sequence[str], None] = "627fe3ff9cdf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "group_chats",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "selection_strategy",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'selector'"),
        ),
        sa.Column(
            "max_rounds",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("10"),
        ),
        sa.Column(
            "allow_repeated_speaker",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("termination_config", sa.JSON(), nullable=True),
        sa.Column("extra_data", sa.JSON(), nullable=True),
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
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_chats_id"), "group_chats", ["id"], unique=False)

    op.create_table(
        "group_chat_participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group_chat_id", sa.Uuid(), nullable=False),
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("agent_version_id", sa.Uuid(), nullable=True),
        sa.Column("speaking_order", sa.Integer(), nullable=True),
        sa.Column("constraints", sa.JSON(), nullable=True),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["agent_version_id"], ["agent_versions.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["group_chat_id"], ["group_chats.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_group_chat_participants_agent_id"),
        "group_chat_participants",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_group_chat_participants_group_chat_id"),
        "group_chat_participants",
        ["group_chat_id"],
        unique=False,
    )

    op.create_table(
        "group_chat_conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group_chat_id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column(
            "round_number",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("current_speaker_agent_id", sa.Uuid(), nullable=True),
        sa.Column("extra_data", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["group_chat_id"], ["group_chats.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["current_speaker_agent_id"], ["agents.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_group_chat_conversations_conversation_id"),
        "group_chat_conversations",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_group_chat_conversations_group_chat_id"),
        "group_chat_conversations",
        ["group_chat_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_group_chat_conversations_group_chat_id"),
        table_name="group_chat_conversations",
    )
    op.drop_index(
        op.f("ix_group_chat_conversations_conversation_id"),
        table_name="group_chat_conversations",
    )
    op.drop_table("group_chat_conversations")

    op.drop_index(
        op.f("ix_group_chat_participants_group_chat_id"),
        table_name="group_chat_participants",
    )
    op.drop_index(
        op.f("ix_group_chat_participants_agent_id"),
        table_name="group_chat_participants",
    )
    op.drop_table("group_chat_participants")

    op.drop_index(op.f("ix_group_chats_id"), table_name="group_chats")
    op.drop_table("group_chats")
