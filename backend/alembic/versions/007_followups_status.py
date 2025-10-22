"""Add status to followups

Revision ID: ae5d1c000108
Revises: ae5d1c000107
Create Date: 2025-10-18 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "ae5d1c000108"
down_revision = "ae5d1c000107"
branch_labels = None
depends_on = None


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
