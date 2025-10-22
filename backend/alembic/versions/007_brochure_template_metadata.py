"""Add preview and field metadata to brochure templates

Revision ID: ae5d1c000104
Revises: ae5d1c000103
Create Date: 2025-10-19 10:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ae5d1c000104"
down_revision = "ae5d1c000103"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("brochure_templates")}

    if "preview_url" not in columns:
        op.add_column(
            "brochure_templates",
            sa.Column("preview_url", sa.String(length=512), nullable=True),
        )
    if "fields_schema" not in columns:
        op.add_column(
            "brochure_templates",
            sa.Column("fields_schema", sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("brochure_templates")}

    if "fields_schema" in columns:
        op.drop_column("brochure_templates", "fields_schema")
    if "preview_url" in columns:
        op.drop_column("brochure_templates", "preview_url")
