"""Add activity-related indexes and columns

Revision ID: ae5d1c000109
Revises: ae5d1c000108
Create Date: 2025-10-18 01:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "ae5d1c000109"
down_revision = "ae5d1c000108"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Clients: last_activity_at column + index
    op.add_column(
        "clients",
        sa.Column("last_activity_at", sa.DateTime(), nullable=True),
    )
    op.execute(
        """
        UPDATE clients
        SET last_activity_at = sub.last_activity
        FROM (
            SELECT contact_id, MAX(occurred_at) AS last_activity
            FROM activities
            GROUP BY contact_id
        ) sub
        WHERE clients.id = sub.contact_id
        """
    )
    op.create_index(
        "idx_clients_last_activity_desc",
        "clients",
        [sa.text("last_activity_at DESC")],
    )

    # Activities: ensure composite index for ordering
    op.create_index(
        "idx_activities_contact_occurred_desc",
        "activities",
        ["contact_id", sa.text("occurred_at DESC")],
    )

    # Followups: due_at index and uniqueness
    op.create_index("idx_followups_due_at", "followups", ["due_at"])
    op.create_unique_constraint(
        "uq_followups_contact_due_channel",
        "followups",
        ["contact_id", "due_at", "channel"],
    )

    # Audit logs: contact tracking columns and index
    op.add_column(
        "audit_logs",
        sa.Column("contact_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "audit_logs",
        sa.Column(
            "occurred_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_foreign_key(
        "fk_audit_logs_contact_id",
        "audit_logs",
        "clients",
        ["contact_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        "UPDATE audit_logs SET occurred_at = COALESCE(occurred_at, created_at, CURRENT_TIMESTAMP)"
    )
    op.alter_column("audit_logs", "occurred_at", server_default=None, nullable=False)
    op.create_index(
        "idx_audit_logs_contact_occurred_desc",
        "audit_logs",
        ["contact_id", sa.text("occurred_at DESC")],
    )


def downgrade() -> None:
    op.drop_index("idx_audit_logs_contact_occurred_desc", table_name="audit_logs")
    op.drop_constraint("fk_audit_logs_contact_id", "audit_logs", type_="foreignkey")
    op.drop_column("audit_logs", "occurred_at")
    op.drop_column("audit_logs", "contact_id")

    op.drop_constraint(
        "uq_followups_contact_due_channel", "followups", type_="unique"
    )
    op.drop_index("idx_followups_due_at", table_name="followups")

    op.drop_index("idx_activities_contact_occurred_desc", table_name="activities")

    op.drop_index("idx_clients_last_activity_desc", table_name="clients")
    op.drop_column("clients", "last_activity_at")
