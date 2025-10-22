"""Intelligence content storage

Revision ID: ae5d1c000101
Revises: ae5d1c000004
Create Date: 2024-10-11 10:18:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ae5d1c000101"
down_revision = "ae5d1c000004"
branch_labels = None
depends_on = None


def upgrade():
    """Create intelligence content storage table"""

    # Create intelligence_content table
    op.create_table(
        "intelligence_content",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "content_id", sa.String(255), unique=True, nullable=False, index=True
        ),
        sa.Column("task_id", sa.String(255), nullable=False, index=True),
        sa.Column("content_type", sa.String(50), nullable=False, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("enhanced", sa.Boolean, default=True, nullable=False),
        sa.Column("quality_scores", sa.JSON, nullable=False),
        sa.Column("memory_context", sa.JSON, nullable=False),
        sa.Column("generated_content", sa.JSON, nullable=False),
        sa.Column("metadata", sa.JSON, nullable=False),
        sa.Column("export_ready", sa.Boolean, default=True, nullable=False),
        sa.Column("version", sa.String(20), default="3.4", nullable=False),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        # Add indexes for common queries
        sa.Index("idx_intelligence_content_type", "content_type"),
        sa.Index("idx_intelligence_content_created", "created_at"),
        sa.Index("idx_intelligence_content_export_ready", "export_ready"),
        sa.Index("idx_intelligence_content_enhanced", "enhanced"),
    )

    # Create content refinement tracking table
    op.create_table(
        "content_refinements",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "refinement_id", sa.String(255), unique=True, nullable=False, index=True
        ),
        sa.Column("original_content_id", sa.String(255), nullable=False, index=True),
        sa.Column("refined_content_id", sa.String(255), nullable=False, index=True),
        sa.Column("refinement_prompt", sa.Text, nullable=False),
        sa.Column("improvements_made", sa.JSON, nullable=True),
        sa.Column("quality_improvement", sa.Float, nullable=True),
        sa.Column("user_id", sa.Integer, nullable=False, index=True),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        # Foreign key relationships
        sa.ForeignKeyConstraint(
            ["original_content_id"],
            ["intelligence_content.content_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["refined_content_id"],
            ["intelligence_content.content_id"],
            ondelete="CASCADE",
        ),
        # Add indexes
        sa.Index("idx_refinements_original", "original_content_id"),
        sa.Index("idx_refinements_user", "user_id"),
        sa.Index("idx_refinements_created", "created_at"),
    )

    # Create content usage tracking table
    op.create_table(
        "content_usage_analytics",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("content_id", sa.String(255), nullable=False, index=True),
        sa.Column("user_id", sa.Integer, nullable=False, index=True),
        sa.Column(
            "action_type", sa.String(50), nullable=False
        ),  # viewed, exported, shared, refined
        sa.Column("context_data", sa.JSON, nullable=True),
        sa.Column(
            "timestamp", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        # Foreign key relationship
        sa.ForeignKeyConstraint(
            ["content_id"], ["intelligence_content.content_id"], ondelete="CASCADE"
        ),
        # Add indexes for analytics queries
        sa.Index("idx_usage_content", "content_id"),
        sa.Index("idx_usage_user", "user_id"),
        sa.Index("idx_usage_action", "action_type"),
        sa.Index("idx_usage_timestamp", "timestamp"),
    )

    # Add intelligence content type enum constraint
    op.execute(
        """
        ALTER TABLE intelligence_content 
        ADD CONSTRAINT chk_content_type 
        CHECK (content_type IN (
            'CMA_REPORT', 'PITCH_DECK', 'SOCIAL_POST', 'MARKET_REPORT',
            'EMAIL_CAMPAIGN', 'PROPERTY_DESCRIPTION', 'LISTING_STRATEGY', 'GENERAL'
        ))
    """
    )

    # Add usage action type constraint
    op.execute(
        """
        ALTER TABLE content_usage_analytics 
        ADD CONSTRAINT chk_action_type 
        CHECK (action_type IN ('viewed', 'exported', 'shared', 'refined', 'copied'))
    """
    )


def downgrade():
    """Drop intelligence content storage tables"""

    # Drop tables in reverse order due to foreign key constraints
    op.drop_table("content_usage_analytics")
    op.drop_table("content_refinements")
    op.drop_table("intelligence_content")
