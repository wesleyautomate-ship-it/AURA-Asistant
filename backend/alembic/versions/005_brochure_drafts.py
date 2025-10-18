"""Create brochure_drafts table

Revision ID: 005_brochure_drafts
Revises: 004_aura_core_entities
Create Date: 2025-10-17 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "005_brochure_drafts"
down_revision: Union[str, None] = "004_aura_core_entities"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "brochure_drafts",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("download_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_brochure_drafts_status", "brochure_drafts", ["status"])
    op.create_index("ix_brochure_drafts_id", "brochure_drafts", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_brochure_drafts_id", table_name="brochure_drafts")
    op.drop_index("ix_brochure_drafts_status", table_name="brochure_drafts")
    op.drop_table("brochure_drafts")

