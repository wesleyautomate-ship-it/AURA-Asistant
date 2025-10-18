"""Add status to followups

Revision ID: 007_followups_status
Revises: 006_contacts_crm
Create Date: 2025-10-18 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "007_followups_status"
down_revision: Union[str, None] = "006_contacts_crm"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "followups",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="scheduled",
        ),
    )
    op.execute(
        sa.text("UPDATE followups SET status = COALESCE(status, 'scheduled')")
    )
    op.alter_column("followups", "status", server_default=None)


def downgrade() -> None:
    op.drop_column("followups", "status")

