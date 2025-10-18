"""Add properties, listing_history, property_confidential tables

Revision ID: 002_properties_and_related
Revises: 001_phase01_baseline
Create Date: 2025-09-23 08:57:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_properties_and_related"
down_revision: Union[str, None] = "001_phase01_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # properties table
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("property_type", sa.String(100), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Numeric(3, 1), nullable=True),
        sa.Column("area_sqft", sa.Integer(), nullable=True),
        sa.Column(
            "listing_status", sa.String(20), nullable=False, server_default="draft"
        ),
        sa.Column(
            "agent_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
    op.create_index("ix_properties_title", "properties", ["title"])
    op.create_index("ix_properties_location", "properties", ["location"])
    op.create_index("ix_properties_type", "properties", ["property_type"])
    op.create_index("ix_properties_price", "properties", ["price"])
    op.create_index("ix_properties_agent_id", "properties", ["agent_id"])

    # listing_history table
    op.create_table(
        "listing_history",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column(
            "changed_by_agent_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_listing_history_property_id", "listing_history", ["property_id"]
    )
    op.create_index("ix_listing_history_event_type", "listing_history", ["event_type"])

    # property_confidential table
    op.create_table(
        "property_confidential",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("unit_number", sa.String(100), nullable=True),
        sa.Column("plot_number", sa.String(100), nullable=True),
        sa.Column("floor", sa.String(50), nullable=True),
        sa.Column("owner_details", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_property_confidential_property_id", "property_confidential", ["property_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_property_confidential_property_id", table_name="property_confidential"
    )
    op.drop_table("property_confidential")

    op.drop_index("ix_listing_history_event_type", table_name="listing_history")
    op.drop_index("ix_listing_history_property_id", table_name="listing_history")
    op.drop_table("listing_history")

    op.drop_index("ix_properties_agent_id", table_name="properties")
    op.drop_index("ix_properties_price", table_name="properties")
    op.drop_index("ix_properties_type", table_name="properties")
    op.drop_index("ix_properties_location", table_name="properties")
    op.drop_index("ix_properties_title", table_name="properties")
    op.drop_table("properties")
