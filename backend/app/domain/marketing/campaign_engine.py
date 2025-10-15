"""
Marketing Campaign Engine
========================

AURA-style marketing automation engine that generates comprehensive marketing
campaigns including postcards, emails, social media content with approval workflows.

Features:
- Template-based content generation
- Multi-channel campaign creation
- Brand consistency enforcement
- Approval workflow management
- Asset generation (PDFs, images)
- Campaign distribution tracking
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session
from sqlalchemy import text
from pathlib import Path
import re

# Import AI orchestration for content generation
try:
    from domain.ai.task_orchestrator import (
        AITaskOrchestrator,
        AITaskRequest,
        TaskType,
        TaskPriority,
    )
    from domain.ai.ai_manager import get_social_media_prompt, get_email_prompt
except ImportError:
    AITaskOrchestrator = None
    get_social_media_prompt = None
    get_email_prompt = None

logger = logging.getLogger(__name__)


class MarketingTemplate:
    """Represents a marketing template with content generation capabilities"""

    def __init__(self, template_data: Dict[str, Any]):
        self.id = template_data["id"]
        self.name = template_data["name"]
        self.category = template_data["category"]
        self.type = template_data["type"]
        self.description = template_data.get("description", "")
        self.content_template = template_data["content_template"]
        self.design_config = template_data.get("design_config", {})
        self.dubai_specific = template_data.get("dubai_specific", True)
        self.is_active = template_data.get("is_active", True)

    def generate_content(
        self,
        property_data: Dict[str, Any],
        agent_data: Dict[str, Any],
        ai_content: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate marketing content from template using property and agent data"""
        try:
            # Create context for template variable substitution
            context = {
                **property_data,
                **agent_data,
                "ai_generated_description": ai_content.get("description", "")
                if ai_content
                else "",
                "ai_generated_highlights": ai_content.get("highlights", "")
                if ai_content
                else "",
                "hashtags": " ".join(ai_content.get("hashtags", []))
                if ai_content
                else "",
            }

            # Process template content
            processed_content = self._substitute_template_variables(
                self.content_template, context
            )

            return {
                "template_id": self.id,
                "template_name": self.name,
                "category": self.category,
                "type": self.type,
                "content": processed_content,
                "design_config": self.design_config,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to generate content for template {self.name}: {e}")
            raise

    def _substitute_template_variables(
        self, template: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Substitute template variables with actual values"""
        processed = {}

        for key, value in template.items():
            if isinstance(value, str):
                processed[key] = self._substitute_string(value, context)
            elif isinstance(value, list):
                processed[key] = [
                    self._substitute_string(item, context)
                    if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, dict):
                processed[key] = self._substitute_template_variables(value, context)
            else:
                processed[key] = value

        return processed

    def _substitute_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Substitute {{variable}} patterns in strings"""

        def replace_var(match):
            var_name = match.group(1).strip()
            return str(context.get(var_name, f"{{{{ {var_name} }}}}"))

        return re.sub(r"\{\{\s*([^}]+)\s*\}\}", replace_var, template_string)


class CampaignApprovalWorkflow:
    """Manages the approval workflow for marketing campaigns"""

    def __init__(self, db_session_factory: Callable[[], Session]):
        self.db_session_factory = db_session_factory

    async def create_approval_request(self, campaign_id: int, agent_id: int) -> str:
        """Create an approval request for a campaign"""
        try:
            approval_id = str(uuid.uuid4())

            with self.db_session_factory() as db:
                # Update campaign status to review
                db.execute(
                    text(
                        """
                    UPDATE marketing_campaigns 
                    SET status = 'review'
                    WHERE id = :campaign_id
                """
                    ),
                    {"campaign_id": campaign_id},
                )

                # Create approval workflow record (would be a separate table in production)
                # For now, we'll use the campaign's approved_by field

                db.commit()

            logger.info(f"Approval request created for campaign {campaign_id}")
            return approval_id

        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")
            raise

    async def approve_campaign(
        self,
        campaign_id: int,
        approver_id: int,
        approved_content: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Approve a marketing campaign"""
        try:
            with self.db_session_factory() as db:
                # Update campaign with approval
                update_data = {
                    "campaign_id": campaign_id,
                    "approved_by": approver_id,
                    "approved_at": datetime.utcnow(),
                    "status": "approved",
                }

                # If content was modified during approval, update it
                if approved_content:
                    update_data["content"] = json.dumps(approved_content)

                query = """
                    UPDATE marketing_campaigns 
                    SET status = :status, approved_by = :approved_by, approved_at = :approved_at
                """

                if approved_content:
                    query += ", content = :content"

                query += " WHERE id = :campaign_id"

                db.execute(text(query), update_data)
                db.commit()

            logger.info(f"Campaign {campaign_id} approved by user {approver_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to approve campaign: {e}")
            return False

    async def reject_campaign(
        self, campaign_id: int, approver_id: int, rejection_reason: str
    ) -> bool:
        """Reject a marketing campaign with feedback"""
        try:
            with self.db_session_factory() as db:
                # Update campaign status and add rejection feedback
                db.execute(
                    text(
                        """
                    UPDATE marketing_campaigns 
                    SET status = 'draft', 
                        content = jsonb_set(content, '{approval_feedback}', :feedback)
                    WHERE id = :campaign_id
                """
                    ),
                    {
                        "campaign_id": campaign_id,
                        "feedback": json.dumps(
                            {
                                "rejected_by": approver_id,
                                "rejected_at": datetime.utcnow().isoformat(),
                                "reason": rejection_reason,
                            }
                        ),
                    },
                )
                db.commit()

            logger.info(f"Campaign {campaign_id} rejected by user {approver_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reject campaign: {e}")
            return False


class MarketingCampaignEngine:
    """
    Main engine for AURA-style marketing automation.

    Capabilities:
    - Load and manage marketing templates
    - Generate multi-channel campaigns
    - Create postcards, emails, social media content
    - Manage approval workflows
    - Generate marketing assets
    """

    def __init__(
        self,
        db_session_factory: Callable[[], Session],
        orchestrator: Optional[AITaskOrchestrator] = None,
    ):
        self.db_session_factory = db_session_factory
        self.orchestrator = orchestrator
        self.approval_workflow = CampaignApprovalWorkflow(db_session_factory)
        self.template_cache: Dict[int, MarketingTemplate] = {}

    async def get_available_templates(
        self, category: Optional[str] = None, template_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get available marketing templates"""
        try:
            with self.db_session_factory() as db:
                query = """
                    SELECT id, name, category, type, description, dubai_specific
                    FROM marketing_templates 
                    WHERE is_active = true
                """
                params = {}

                if category:
                    query += " AND category = :category"
                    params["category"] = category

                if template_type:
                    query += " AND type = :type"
                    params["type"] = template_type

                query += " ORDER BY name ASC"

                result = db.execute(text(query), params)
                templates = []

                for row in result.fetchall():
                    templates.append(
                        {
                            "id": row.id,
                            "name": row.name,
                            "category": row.category,
                            "type": row.type,
                            "description": row.description,
                            "dubai_specific": row.dubai_specific,
                        }
                    )

                return templates

        except Exception as e:
            logger.error(f"Failed to get available templates: {e}")
            raise

    async def load_template(self, template_id: int) -> MarketingTemplate:
        """Load a marketing template from database"""
        # Check cache first
        if template_id in self.template_cache:
            return self.template_cache[template_id]

        try:
            with self.db_session_factory() as db:
                result = db.execute(
                    text(
                        """
                    SELECT id, name, category, type, description, content_template,
                           design_config, dubai_specific, is_active
                    FROM marketing_templates 
                    WHERE id = :template_id AND is_active = true
                """
                    ),
                    {"template_id": template_id},
                )

                row = result.fetchone()
                if not row:
                    raise ValueError(f"Template {template_id} not found or inactive")

                template_data = {
                    "id": row.id,
                    "name": row.name,
                    "category": row.category,
                    "type": row.type,
                    "description": row.description,
                    "content_template": json.loads(row.content_template),
                    "design_config": json.loads(row.design_config)
                    if row.design_config
                    else {},
                    "dubai_specific": row.dubai_specific,
                    "is_active": row.is_active,
                }

                template = MarketingTemplate(template_data)

                # Cache the template
                self.template_cache[template_id] = template
                return template

        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            raise

    async def create_campaign(
        self,
        property_id: int,
        agent_id: int,
        campaign_type: str,
        template_id: Optional[int] = None,
        custom_content: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Create a new marketing campaign.

        Args:
            property_id: Property to create campaign for
            agent_id: Agent creating the campaign
            campaign_type: Type of campaign (postcard, email_blast, social_campaign)
            template_id: Template to use (optional)
            custom_content: Custom content overrides (optional)

        Returns:
            campaign_id: ID of the created campaign
        """
        try:
            # Get property and agent data
            property_data = await self._get_property_data(property_id)
            agent_data = await self._get_agent_data(agent_id)

            # Generate AI content if using orchestrator
            ai_content = None
            if self.orchestrator:
                ai_content = await self._generate_ai_content(
                    property_data, agent_data, campaign_type
                )

            # Load and process template if specified
            campaign_content = {}
            if template_id:
                template = await self.load_template(template_id)
                campaign_content = template.generate_content(
                    property_data, agent_data, ai_content
                )

            # Apply custom content overrides
            if custom_content:
                campaign_content.update(custom_content)

            # Create campaign in database
            with self.db_session_factory() as db:
                result = db.execute(
                    text(
                        """
                    INSERT INTO marketing_campaigns 
                    (title, property_id, template_id, agent_id, brokerage_id, 
                     campaign_type, status, content, created_at, updated_at)
                    VALUES (:title, :property_id, :template_id, :agent_id, :brokerage_id,
                           :campaign_type, :status, :content, :created_at, :updated_at)
                    RETURNING id
                """
                    ),
                    {
                        "title": self._generate_campaign_title(
                            property_data, campaign_type
                        ),
                        "property_id": property_id,
                        "template_id": template_id,
                        "agent_id": agent_id,
                        "brokerage_id": agent_data["brokerage_id"],
                        "campaign_type": campaign_type,
                        "status": "draft",
                        "content": json.dumps(campaign_content),
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    },
                )

                campaign_id = result.fetchone().id
                db.commit()

            logger.info(
                f"Marketing campaign {campaign_id} created for property {property_id}"
            )
            return campaign_id

        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            raise

    async def create_full_marketing_package(
        self, property_id: int, agent_id: int
    ) -> Dict[str, Any]:
        """
        Create a complete AURA-style marketing package with multiple channels.

        Generates:
        - Just Listed postcard
        - Email announcement
        - Social media posts (Instagram, Facebook, LinkedIn)
        - Property flyer
        """
        try:
            campaigns = {}

            # Get available templates for different channels
            templates = await self.get_available_templates()

            # Create postcard campaign
            postcard_template = next(
                (
                    t
                    for t in templates
                    if t["category"] == "postcard" and t["type"] == "just_listed"
                ),
                None,
            )
            if postcard_template:
                campaigns["postcard"] = await self.create_campaign(
                    property_id, agent_id, "postcard", postcard_template["id"]
                )

            # Create email campaign
            email_template = next(
                (
                    t
                    for t in templates
                    if t["category"] == "email" and t["type"] == "just_listed"
                ),
                None,
            )
            if email_template:
                campaigns["email"] = await self.create_campaign(
                    property_id, agent_id, "email_blast", email_template["id"]
                )

            # Create social media campaigns
            social_template = next(
                (
                    t
                    for t in templates
                    if t["category"] == "social" and t["type"] == "just_listed"
                ),
                None,
            )
            if social_template:
                campaigns["social_instagram"] = await self.create_campaign(
                    property_id, agent_id, "social_campaign", social_template["id"]
                )

            return {
                "package_type": "full_marketing_package",
                "property_id": property_id,
                "campaigns": campaigns,
                "created_at": datetime.utcnow().isoformat(),
                "status": "draft",
            }

        except Exception as e:
            logger.error(f"Failed to create full marketing package: {e}")
            raise

    async def get_campaign_details(self, campaign_id: int) -> Dict[str, Any]:
        """Get detailed information about a campaign"""
        try:
            with self.db_session_factory() as db:
                result = db.execute(
                    text(
                        """
                    SELECT mc.id, mc.title, mc.property_id, mc.template_id, mc.agent_id,
                           mc.campaign_type, mc.status, mc.content, mc.approved_by,
                           mc.approved_at, mc.distributed_at, mc.created_at, mc.updated_at,
                           p.title as property_title, p.location as property_location,
                           u.first_name || ' ' || u.last_name as agent_name
                    FROM marketing_campaigns mc
                    LEFT JOIN properties p ON mc.property_id = p.id
                    LEFT JOIN users u ON mc.agent_id = u.id
                    WHERE mc.id = :campaign_id
                """
                    ),
                    {"campaign_id": campaign_id},
                )

                row = result.fetchone()
                if not row:
                    raise ValueError(f"Campaign {campaign_id} not found")

                # Get campaign assets
                assets_result = db.execute(
                    text(
                        """
                    SELECT asset_type, file_name, file_path, metadata, created_at
                    FROM campaign_assets
                    WHERE campaign_id = :campaign_id
                    ORDER BY created_at ASC
                """
                    ),
                    {"campaign_id": campaign_id},
                )

                assets = []
                for asset_row in assets_result.fetchall():
                    assets.append(
                        {
                            "asset_type": asset_row.asset_type,
                            "file_name": asset_row.file_name,
                            "file_path": asset_row.file_path,
                            "metadata": json.loads(asset_row.metadata)
                            if asset_row.metadata
                            else {},
                            "created_at": asset_row.created_at,
                        }
                    )

                return {
                    "id": row.id,
                    "title": row.title,
                    "property_id": row.property_id,
                    "property_title": row.property_title,
                    "property_location": row.property_location,
                    "template_id": row.template_id,
                    "agent_id": row.agent_id,
                    "agent_name": row.agent_name,
                    "campaign_type": row.campaign_type,
                    "status": row.status,
                    "content": json.loads(row.content),
                    "approved_by": row.approved_by,
                    "approved_at": row.approved_at,
                    "distributed_at": row.distributed_at,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                    "assets": assets,
                }

        except Exception as e:
            logger.error(f"Failed to get campaign details: {e}")
            raise

    async def generate_campaign_assets(self, campaign_id: int) -> List[Dict[str, Any]]:
        """Generate marketing assets (PDFs, images) for a campaign"""
        try:
            campaign = await self.get_campaign_details(campaign_id)
            generated_assets = []

            # Generate different assets based on campaign type
            if campaign["campaign_type"] == "postcard":
                pdf_asset = await self._generate_postcard_pdf(campaign)
                generated_assets.append(pdf_asset)

            elif campaign["campaign_type"] == "email_blast":
                html_asset = await self._generate_email_html(campaign)
                generated_assets.append(html_asset)

            elif campaign["campaign_type"] == "social_campaign":
                image_assets = await self._generate_social_images(campaign)
                generated_assets.extend(image_assets)

            # Save assets to database
            for asset in generated_assets:
                await self._save_campaign_asset(campaign_id, asset)

            return generated_assets

        except Exception as e:
            logger.error(f"Failed to generate campaign assets: {e}")
            raise

    # Helper methods

    async def _get_property_data(self, property_id: int) -> Dict[str, Any]:
        """Get property data for campaign generation"""
        with self.db_session_factory() as db:
            result = db.execute(
                text(
                    """
                SELECT title, description, price, location, property_type, 
                       bedrooms, bathrooms, area_sqft
                FROM properties 
                WHERE id = :property_id
            """
                ),
                {"property_id": property_id},
            )

            row = result.fetchone()
            if not row:
                raise ValueError(f"Property {property_id} not found")

            return {
                "property_id": property_id,
                "property_title": row.title,
                "property_description": row.description or "",
                "price": float(row.price) if row.price else 0,
                "location": row.location or "",
                "property_type": row.property_type or "",
                "bedrooms": row.bedrooms or 0,
                "bathrooms": float(row.bathrooms) if row.bathrooms else 0,
                "area_sqft": row.area_sqft or 0,
            }

    async def _get_agent_data(self, agent_id: int) -> Dict[str, Any]:
        """Get agent data for campaign generation"""
        with self.db_session_factory() as db:
            result = db.execute(
                text(
                    """
                SELECT u.first_name, u.last_name, u.email, u.brokerage_id,
                       b.name as brokerage_name, b.license_number as brokerage_license,
                       b.phone as brokerage_phone
                FROM users u
                LEFT JOIN brokerages b ON u.brokerage_id = b.id
                WHERE u.id = :agent_id
            """
                ),
                {"agent_id": agent_id},
            )

            row = result.fetchone()
            if not row:
                raise ValueError(f"Agent {agent_id} not found")

            return {
                "agent_id": agent_id,
                "agent_name": f"{row.first_name} {row.last_name}",
                "agent_email": row.email,
                "agent_phone": row.brokerage_phone or "",
                "brokerage_id": row.brokerage_id,
                "brokerage_name": row.brokerage_name or "PropertyPro Real Estate",
                "brokerage_license": row.brokerage_license or "",
            }

    async def _generate_ai_content(
        self,
        property_data: Dict[str, Any],
        agent_data: Dict[str, Any],
        campaign_type: str,
    ) -> Dict[str, Any]:
        """Generate AI content for the campaign"""
        if not self.orchestrator:
            return {}

        try:
            # Prepare context for AI generation
            context = {
                "property_details": property_data,
                "campaign_type": campaign_type,
                "location": property_data["location"],
                "price": property_data["price"],
                "property_type": property_data["property_type"],
            }

            # Submit AI task for content generation
            task_request = AITaskRequest(
                task_type=TaskType.CONTENT_GENERATION,
                user_id=agent_data["agent_id"],
                input_data={
                    "content_type": "marketing_campaign",
                    "campaign_type": campaign_type,
                    "context": context,
                },
                priority=TaskPriority.HIGH,
            )

            task_id = await self.orchestrator.submit_task(task_request)

            # Poll for completion (simplified for now)
            # In production, this would use proper async polling
            import asyncio

            await asyncio.sleep(2)  # Allow processing time

            task_result = await self.orchestrator.get_task_status(task_id)

            if task_result.output_data:
                return task_result.output_data

            return {}

        except Exception as e:
            logger.warning(f"AI content generation failed: {e}")
            return {}

    def _generate_campaign_title(
        self, property_data: Dict[str, Any], campaign_type: str
    ) -> str:
        """Generate a campaign title"""
        property_title = property_data.get("property_title", "Property")
        location = property_data.get("location", "")

        if campaign_type == "postcard":
            return f"Just Listed Postcard - {property_title}"
        elif campaign_type == "email_blast":
            return f"New Listing Email - {property_title}"
        elif campaign_type == "social_campaign":
            return f"Social Media Campaign - {property_title}"
        else:
            return f"Marketing Campaign - {property_title}"

    async def _generate_postcard_pdf(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PDF for postcard campaign (placeholder)"""
        # In production, this would use a PDF generation service
        return {
            "asset_type": "pdf",
            "file_name": f'postcard_{campaign["id"]}.pdf',
            "file_path": f'/assets/postcards/postcard_{campaign["id"]}.pdf',
            "metadata": {"generated_at": datetime.utcnow().isoformat()},
        }

    async def _generate_email_html(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Generate HTML for email campaign (placeholder)"""
        return {
            "asset_type": "html",
            "file_name": f'email_{campaign["id"]}.html',
            "file_path": f'/assets/emails/email_{campaign["id"]}.html',
            "metadata": {"generated_at": datetime.utcnow().isoformat()},
        }

    async def _generate_social_images(
        self, campaign: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate images for social media campaign (placeholder)"""
        return [
            {
                "asset_type": "image",
                "file_name": f'social_post_{campaign["id"]}.jpg',
                "file_path": f'/assets/social/social_post_{campaign["id"]}.jpg',
                "metadata": {
                    "platform": "instagram",
                    "generated_at": datetime.utcnow().isoformat(),
                },
            }
        ]

    async def _save_campaign_asset(self, campaign_id: int, asset: Dict[str, Any]):
        """Save generated asset to database"""
        try:
            with self.db_session_factory() as db:
                db.execute(
                    text(
                        """
                    INSERT INTO campaign_assets 
                    (campaign_id, asset_type, file_name, file_path, metadata, created_at)
                    VALUES (:campaign_id, :asset_type, :file_name, :file_path, :metadata, :created_at)
                """
                    ),
                    {
                        "campaign_id": campaign_id,
                        "asset_type": asset["asset_type"],
                        "file_name": asset["file_name"],
                        "file_path": asset["file_path"],
                        "metadata": json.dumps(asset["metadata"]),
                        "created_at": datetime.utcnow(),
                    },
                )
                db.commit()
        except Exception as e:
            logger.error(f"Failed to save campaign asset: {e}")
            raise
