"""Add AURA core entities: Marketing, Analytics, Packages, Social Media, Transactions

Revision ID: ae5d1c000004
Revises: ae5d1c000003
Create Date: 2025-09-24 13:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "ae5d1c000004"
down_revision = "ae5d1c000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =============================================================================
    # BROKERAGES TABLE (Referenced by other entities)
    # =============================================================================
    op.create_table(
        "brokerages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("license_number", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column(
            "rera_registered",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("brand_settings", sa.JSON(), nullable=True),  # Colors, fonts, logos
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
    op.create_index("ix_brokerages_name", "brokerages", ["name"])
    op.create_index("ix_brokerages_license_number", "brokerages", ["license_number"])

    # Add brokerage_id to users table
    op.add_column(
        "users",
        sa.Column(
            "brokerage_id",
            sa.Integer(),
            sa.ForeignKey("brokerages.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_users_brokerage_id", "users", ["brokerage_id"])

    # =============================================================================
    # MARKETING AUTOMATION ENTITIES
    # =============================================================================

    # Templates for marketing materials
    op.create_table(
        "marketing_templates",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "category", sa.String(100), nullable=False
        ),  # postcard, email, social, flyer
        sa.Column(
            "type", sa.String(100), nullable=False
        ),  # just_listed, open_house, price_reduction, sold
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "content_template", sa.JSON(), nullable=False
        ),  # Template structure with placeholders
        sa.Column("design_config", sa.JSON(), nullable=True),  # Colors, fonts, layout
        sa.Column(
            "dubai_specific",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_by",
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
    op.create_index(
        "ix_marketing_templates_category", "marketing_templates", ["category"]
    )
    op.create_index("ix_marketing_templates_type", "marketing_templates", ["type"])

    # Marketing campaigns
    op.create_table(
        "marketing_campaigns",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "template_id",
            sa.Integer(),
            sa.ForeignKey("marketing_templates.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "agent_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "brokerage_id",
            sa.Integer(),
            sa.ForeignKey("brokerages.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "campaign_type", sa.String(100), nullable=False
        ),  # postcard, email_blast, social_campaign
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="draft"
        ),  # draft, review, approved, distributed, archived
        sa.Column("content", sa.JSON(), nullable=False),  # Generated content
        sa.Column("target_audience", sa.JSON(), nullable=True),  # Targeting criteria
        sa.Column(
            "distribution_settings", sa.JSON(), nullable=True
        ),  # Email lists, print quantities, etc.
        sa.Column(
            "approved_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("distributed_at", sa.DateTime(), nullable=True),
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
    op.create_index(
        "ix_marketing_campaigns_property_id", "marketing_campaigns", ["property_id"]
    )
    op.create_index(
        "ix_marketing_campaigns_agent_id", "marketing_campaigns", ["agent_id"]
    )
    op.create_index("ix_marketing_campaigns_status", "marketing_campaigns", ["status"])
    op.create_index(
        "ix_marketing_campaigns_campaign_type", "marketing_campaigns", ["campaign_type"]
    )

    # Campaign assets (PDFs, images, etc.)
    op.create_table(
        "campaign_assets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "campaign_id",
            sa.Integer(),
            sa.ForeignKey("marketing_campaigns.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "asset_type", sa.String(50), nullable=False
        ),  # pdf, image, video, html
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_campaign_assets_campaign_id", "campaign_assets", ["campaign_id"]
    )
    op.create_index("ix_campaign_assets_asset_type", "campaign_assets", ["asset_type"])

    # =============================================================================
    # DATA & ANALYTICS ENTITIES
    # =============================================================================

    # CMA Reports
    op.create_table(
        "cma_reports",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "report_data", sa.JSON(), nullable=False
        ),  # Comparable properties, analysis
        sa.Column(
            "price_recommendation", sa.JSON(), nullable=False
        ),  # Aggressive, standard, conservative
        sa.Column(
            "market_conditions", sa.JSON(), nullable=True
        ),  # Market trends, seasonality
        sa.Column("pdf_file_path", sa.String(500), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True),  # 0.00-1.00
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=True),  # CMA validity period
    )
    op.create_index("ix_cma_reports_property_id", "cma_reports", ["property_id"])
    op.create_index("ix_cma_reports_agent_id", "cma_reports", ["agent_id"])
    op.create_index("ix_cma_reports_created_at", "cma_reports", ["created_at"])

    # Market snapshots for Dubai areas
    op.create_table(
        "market_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "area", sa.String(255), nullable=False
        ),  # Dubai Marina, Downtown, Palm Jumeirah
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column(
            "property_type", sa.String(100), nullable=True
        ),  # apartment, villa, townhouse
        sa.Column(
            "metrics", sa.JSON(), nullable=False
        ),  # Price per sqft, sales volume, inventory
        sa.Column(
            "trend_analysis", sa.JSON(), nullable=True
        ),  # Price trends, market velocity
        sa.Column("data_source", sa.String(100), nullable=True),  # dubizzle, bayut, pf
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_market_snapshots_area", "market_snapshots", ["area"])
    op.create_index("ix_market_snapshots_date", "market_snapshots", ["snapshot_date"])
    op.create_index(
        "ix_market_snapshots_area_type", "market_snapshots", ["area", "property_type"]
    )

    # =============================================================================
    # SOCIAL MEDIA MANAGEMENT ENTITIES
    # =============================================================================

    # Brand assets (logos, images, templates)
    op.create_table(
        "brand_assets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "brokerage_id",
            sa.Integer(),
            sa.ForeignKey("brokerages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "asset_type", sa.String(100), nullable=False
        ),  # logo, background, template, font
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("usage_guidelines", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),  # Dimensions, colors, etc.
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_brand_assets_brokerage_id", "brand_assets", ["brokerage_id"])
    op.create_index("ix_brand_assets_asset_type", "brand_assets", ["asset_type"])

    # Social media posts
    op.create_table(
        "social_media_posts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "campaign_id",
            sa.Integer(),
            sa.ForeignKey("marketing_campaigns.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "agent_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "platform", sa.String(50), nullable=False
        ),  # instagram, facebook, linkedin, tiktok
        sa.Column(
            "post_type", sa.String(100), nullable=False
        ),  # just_listed, open_house, sold, testimonial
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_urls", sa.JSON(), nullable=True),  # Array of image URLs
        sa.Column("hashtags", sa.JSON(), nullable=True),  # Array of hashtags
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="draft"
        ),  # draft, scheduled, published, failed
        sa.Column("scheduled_for", sa.DateTime(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column(
            "external_post_id", sa.String(255), nullable=True
        ),  # Platform-specific ID
        sa.Column(
            "engagement_metrics", sa.JSON(), nullable=True
        ),  # Likes, comments, shares
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_social_posts_campaign_id", "social_media_posts", ["campaign_id"]
    )
    op.create_index("ix_social_posts_agent_id", "social_media_posts", ["agent_id"])
    op.create_index("ix_social_posts_platform", "social_media_posts", ["platform"])
    op.create_index("ix_social_posts_status", "social_media_posts", ["status"])
    op.create_index(
        "ix_social_posts_scheduled_for", "social_media_posts", ["scheduled_for"]
    )

    # =============================================================================
    # AI PACKAGES WORKFLOW ENGINE
    # =============================================================================

    # Workflow package definitions
    op.create_table(
        "workflow_packages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category", sa.String(100), nullable=False
        ),  # listing, nurturing, onboarding, custom
        sa.Column(
            "steps", sa.JSON(), nullable=False
        ),  # Ordered array of step definitions
        sa.Column("estimated_duration", sa.Integer(), nullable=True),  # Minutes
        sa.Column(
            "is_template", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "brokerage_id",
            sa.Integer(),
            sa.ForeignKey("brokerages.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
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
    op.create_index("ix_workflow_packages_category", "workflow_packages", ["category"])
    op.create_index(
        "ix_workflow_packages_is_template", "workflow_packages", ["is_template"]
    )

    # Package executions (running instances)
    op.create_table(
        "package_executions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "package_id",
            sa.Integer(),
            sa.ForeignKey("workflow_packages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "client_id",
            sa.Integer(),
            sa.ForeignKey("clients.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="queued"
        ),  # queued, running, completed, failed, cancelled
        sa.Column(
            "progress", sa.Integer(), nullable=False, server_default="0"
        ),  # 0-100
        sa.Column(
            "context_data", sa.JSON(), nullable=True
        ),  # Variables passed between steps
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_package_executions_package_id", "package_executions", ["package_id"]
    )
    op.create_index("ix_package_executions_user_id", "package_executions", ["user_id"])
    op.create_index("ix_package_executions_status", "package_executions", ["status"])

    # Individual package steps (execution tracking)
    op.create_table(
        "package_steps",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "execution_id",
            sa.Integer(),
            sa.ForeignKey("package_executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_name", sa.String(255), nullable=False),
        sa.Column(
            "step_type", sa.String(100), nullable=False
        ),  # ai_task, human_review, api_call, notification
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="pending"
        ),  # pending, running, completed, failed, skipped
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("input_data", sa.JSON(), nullable=True),
        sa.Column("output_data", sa.JSON(), nullable=True),
        sa.Column(
            "ai_task_id", sa.String(255), nullable=True
        ),  # Reference to AI processing task
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_package_steps_execution_id", "package_steps", ["execution_id"])
    op.create_index("ix_package_steps_status", "package_steps", ["status"])
    op.create_index("ix_package_steps_step_type", "package_steps", ["step_type"])

    # =============================================================================
    # STRATEGY & ADVISORY ENTITIES
    # =============================================================================

    # Listing strategies
    op.create_table(
        "listing_strategies",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column(
            "target_audience", sa.JSON(), nullable=True
        ),  # Demographics, preferences
        sa.Column("key_selling_points", sa.JSON(), nullable=True),  # Array of USPs
        sa.Column(
            "marketing_timeline", sa.JSON(), nullable=True
        ),  # Phased marketing plan
        sa.Column(
            "pricing_strategy", sa.JSON(), nullable=True
        ),  # Initial price, reduction schedule
        sa.Column("staging_recommendations", sa.Text(), nullable=True),
        sa.Column(
            "document_content", sa.Text(), nullable=False
        ),  # Full strategy document
        sa.Column("pdf_file_path", sa.String(500), nullable=True),
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
    op.create_index(
        "ix_listing_strategies_property_id", "listing_strategies", ["property_id"]
    )
    op.create_index(
        "ix_listing_strategies_agent_id", "listing_strategies", ["agent_id"]
    )

    # =============================================================================
    # TRANSACTIONS & COMPLIANCE ENTITIES
    # =============================================================================

    # Transaction timelines
    op.create_table(
        "transaction_timelines",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "client_id",
            sa.Integer(),
            sa.ForeignKey("clients.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "transaction_type", sa.String(100), nullable=False
        ),  # sale, lease, off_plan
        sa.Column("contract_date", sa.Date(), nullable=False),
        sa.Column("expected_completion", sa.Date(), nullable=True),
        sa.Column(
            "milestones", sa.JSON(), nullable=False
        ),  # Array of milestone definitions
        sa.Column(
            "notifications", sa.JSON(), nullable=True
        ),  # Notification preferences
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="active"
        ),  # active, completed, cancelled
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
    op.create_index(
        "ix_transaction_timelines_property_id", "transaction_timelines", ["property_id"]
    )
    op.create_index(
        "ix_transaction_timelines_agent_id", "transaction_timelines", ["agent_id"]
    )
    op.create_index(
        "ix_transaction_timelines_contract_date",
        "transaction_timelines",
        ["contract_date"],
    )

    # RERA compliance checks
    op.create_table(
        "compliance_checks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "transaction_id",
            sa.Integer(),
            sa.ForeignKey("transaction_timelines.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "property_id",
            sa.Integer(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "agent_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "rule_type", sa.String(100), nullable=False
        ),  # listing_disclosure, noc_required, etc.
        sa.Column("rule_description", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(50), nullable=False
        ),  # compliant, non_compliant, pending, na
        sa.Column("details", sa.JSON(), nullable=True),  # Evidence, notes, documents
        sa.Column(
            "checked_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("next_check_due", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_compliance_checks_transaction_id", "compliance_checks", ["transaction_id"]
    )
    op.create_index(
        "ix_compliance_checks_property_id", "compliance_checks", ["property_id"]
    )
    op.create_index("ix_compliance_checks_status", "compliance_checks", ["status"])

    # Communication templates
    op.create_table(
        "communication_templates",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "brokerage_id",
            sa.Integer(),
            sa.ForeignKey("brokerages.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),  # email, sms, whatsapp
        sa.Column(
            "trigger_event", sa.String(100), nullable=False
        ),  # inspection_scheduled, offer_received, etc.
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "variables", sa.JSON(), nullable=True
        ),  # Available template variables
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_by",
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
    op.create_index(
        "ix_communication_templates_category", "communication_templates", ["category"]
    )
    op.create_index(
        "ix_communication_templates_trigger",
        "communication_templates",
        ["trigger_event"],
    )

    # =============================================================================
    # AI ORCHESTRATION ENTITIES
    # =============================================================================

    # AI task queue (for async processing)
    op.create_table(
        "ai_tasks",
        sa.Column("id", sa.String(255), primary_key=True, nullable=False),  # UUID
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "task_type", sa.String(100), nullable=False
        ),  # content_generation, cma_analysis, etc.
        sa.Column("input_data", sa.JSON(), nullable=False),
        sa.Column("output_data", sa.JSON(), nullable=True),
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="queued"
        ),  # queued, processing, completed, failed
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),  # 1-10
        sa.Column(
            "progress", sa.Integer(), nullable=False, server_default="0"
        ),  # 0-100
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("worker_id", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_ai_tasks_user_id", "ai_tasks", ["user_id"])
    op.create_index("ix_ai_tasks_status", "ai_tasks", ["status"])
    op.create_index("ix_ai_tasks_task_type", "ai_tasks", ["task_type"])
    op.create_index("ix_ai_tasks_priority", "ai_tasks", ["priority"])

    # AI context store (for RAG and conversation memory)
    op.create_table(
        "ai_contexts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "context_type", sa.String(100), nullable=False
        ),  # property, client, market, conversation
        sa.Column(
            "reference_id", sa.String(255), nullable=True
        ),  # ID of related entity
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embeddings", sa.JSON(), nullable=True),  # Vector embeddings for RAG
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("last_accessed", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_ai_contexts_user_id", "ai_contexts", ["user_id"])
    op.create_index("ix_ai_contexts_context_type", "ai_contexts", ["context_type"])
    op.create_index("ix_ai_contexts_reference_id", "ai_contexts", ["reference_id"])


def downgrade() -> None:
    # Drop AI orchestration tables
    op.drop_table("ai_contexts")
    op.drop_table("ai_tasks")

    # Drop communication templates
    op.drop_table("communication_templates")

    # Drop compliance tables
    op.drop_table("compliance_checks")
    op.drop_table("transaction_timelines")

    # Drop strategy tables
    op.drop_table("listing_strategies")

    # Drop package workflow tables
    op.drop_table("package_steps")
    op.drop_table("package_executions")
    op.drop_table("workflow_packages")

    # Drop social media tables
    op.drop_table("social_media_posts")
    op.drop_table("brand_assets")

    # Drop analytics tables
    op.drop_table("market_snapshots")
    op.drop_table("cma_reports")

    # Drop marketing tables
    op.drop_table("campaign_assets")
    op.drop_table("marketing_campaigns")
    op.drop_table("marketing_templates")

    # Remove brokerage_id from users
    op.drop_index("ix_users_brokerage_id", table_name="users")
    op.drop_column("users", "brokerage_id")

    # Drop brokerages table
    op.drop_table("brokerages")
