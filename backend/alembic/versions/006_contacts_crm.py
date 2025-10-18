"""Add contacts-related tables: contact_notes, activities, followups

Revision ID: 006_contacts_crm
Revises: 0eb8185a636d_consolidate_models
Create Date: 2025-10-17 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "006_contacts_crm"
down_revision: Union[str, None] = "0eb8185a636d_consolidate_models"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # contact_notes
    op.create_table(
        "contact_notes",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("contact_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_contact_notes_contact_id", "contact_notes", ["contact_id"])
    op.create_index("ix_contact_notes_created_at", "contact_notes", ["created_at"])

    # activities
    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("contact_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.CheckConstraint("kind in ('call','email','whatsapp','meeting','ai')", name="ck_activities_kind"),
    )
    op.create_index("ix_activities_contact_id", "activities", ["contact_id"])
    op.create_index("ix_activities_occurred_at", "activities", ["occurred_at"])
    op.create_index("idx_activities_contact_time", "activities", ["contact_id", sa.text("occurred_at DESC")])

    # followups
    op.create_table(
        "followups",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("contact_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("due_at", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("channel in ('call','email','whatsapp','meeting')", name="ck_followups_channel"),
    )
    op.create_index("ix_followups_contact_id", "followups", ["contact_id"])
    op.create_index("ix_followups_due_at", "followups", ["due_at"])
    op.create_index("idx_followups_contact_due", "followups", ["contact_id", "due_at"])


def downgrade() -> None:
    op.drop_index("idx_followups_contact_due", table_name="followups")
    op.drop_index("ix_followups_due_at", table_name="followups")
    op.drop_index("ix_followups_contact_id", table_name="followups")
    op.drop_table("followups")

    op.drop_index("idx_activities_contact_time", table_name="activities")
    op.drop_index("ix_activities_occurred_at", table_name="activities")
    op.drop_index("ix_activities_contact_id", table_name="activities")
    op.drop_table("activities")

    op.drop_index("ix_contact_notes_created_at", table_name="contact_notes")
    op.drop_index("ix_contact_notes_contact_id", table_name="contact_notes")
    op.drop_table("contact_notes")

