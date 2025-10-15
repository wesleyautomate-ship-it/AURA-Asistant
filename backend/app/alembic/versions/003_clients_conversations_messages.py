"""Add clients, conversations, messages tables

Revision ID: 003_clients_conversations_messages
Revises: 002_properties_and_related
Create Date: 2025-09-23 09:27:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003_clients_conversations_messages"
down_revision: Union[str, None] = "002_properties_and_related"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # clients table
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("budget_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("budget_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("preferred_location", sa.String(255), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_clients_name", "clients", ["name"])
    op.create_index("ix_clients_email", "clients", ["email"], unique=False)

    # conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.String(255), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("role", sa.String(50), nullable=False, server_default="client"),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
    )
    op.create_index("ix_conversations_session_id", "conversations", ["session_id"])
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])

    # messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "conversation_id",
            sa.Integer(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("message_type", sa.String(50), nullable=False, server_default="text"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_timestamp", "messages", ["timestamp"])


def downgrade() -> None:
    op.drop_index("ix_messages_timestamp", table_name="messages")
    op.drop_index("ix_messages_conversation_id", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_conversations_user_id", table_name="conversations")
    op.drop_index("ix_conversations_session_id", table_name="conversations")
    op.drop_table("conversations")

    op.drop_index("ix_clients_email", table_name="clients")
    op.drop_index("ix_clients_name", table_name="clients")
    op.drop_table("clients")
