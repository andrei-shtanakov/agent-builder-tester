"""Add content column to execution_logs."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20241014_add_content_to_execution_logs"
down_revision = "b90a22f4a1f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add content column."""
    with op.batch_alter_table("execution_logs") as batch_op:
        batch_op.add_column(sa.Column("content", sa.Text(), nullable=True))

    op.execute("UPDATE execution_logs SET content = '' WHERE content IS NULL")

    with op.batch_alter_table("execution_logs", recreate="always") as batch_op:
        batch_op.alter_column(
            "content",
            existing_type=sa.Text(),
            nullable=False,
        )


def downgrade() -> None:
    """Drop content column."""
    op.drop_column("execution_logs", "content")
