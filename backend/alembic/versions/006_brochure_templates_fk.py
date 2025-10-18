"""Add brochure_templates and FKs on brochure_drafts

Revision ID: 006_brochure_templates_fk
Revises: 005_brochure_drafts
Create Date: 2025-10-17 12:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "006_brochure_templates_fk"
down_revision: Union[str, None] = "005_brochure_drafts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create brochure_templates
    op.create_table(
        "brochure_templates",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    # Add columns to brochure_drafts
    op.add_column("brochure_drafts", sa.Column("template_id", sa.String(length=36), nullable=True))
    op.add_column("brochure_drafts", sa.Column("contact_id", sa.Integer(), nullable=True))
    # Indexes
    op.create_index("ix_brochure_drafts_created_at", "brochure_drafts", ["created_at"]) 
    op.create_index("ix_brochure_drafts_template_id", "brochure_drafts", ["template_id"]) 
    op.create_index("ix_brochure_drafts_contact_id", "brochure_drafts", ["contact_id"]) 
    # FKs
    op.create_foreign_key(
        "fk_brochure_drafts_template",
        source_table="brochure_drafts",
        referent_table="brochure_templates",
        local_cols=["template_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )
    # Contacts table may or may not exist in all envs; wrap in try/except by deferring to DB to validate if exists
    try:
        op.create_foreign_key(
            "fk_brochure_drafts_contact",
            source_table="brochure_drafts",
            referent_table="contacts",
            local_cols=["contact_id"],
            remote_cols=["id"],
            ondelete="SET NULL",
        )
    except Exception:
        # In SQLite/no contacts env, skip FK creation gracefully
        pass


def downgrade() -> None:
    # Drop FKs and indexes
    with op.batch_alter_table("brochure_drafts") as batch_op:
        try:
            batch_op.drop_constraint("fk_brochure_drafts_contact", type_="foreignkey")
        except Exception:
            pass
        try:
            batch_op.drop_constraint("fk_brochure_drafts_template", type_="foreignkey")
        except Exception:
            pass
    op.drop_index("ix_brochure_drafts_contact_id", table_name="brochure_drafts")
    op.drop_index("ix_brochure_drafts_template_id", table_name="brochure_drafts")
    op.drop_index("ix_brochure_drafts_created_at", table_name="brochure_drafts")
    op.drop_column("brochure_drafts", "contact_id")
    op.drop_column("brochure_drafts", "template_id")
    op.drop_table("brochure_templates")

