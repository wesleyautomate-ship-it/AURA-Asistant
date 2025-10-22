"""Seed AURA data: Templates, Dubai market data, workflow packages

Revision ID: ae5d1c000105
Revises: ae5d1c000104
Create Date: 2025-09-24 13:45:00

"""
from typing import Sequence, Union
import json
from datetime import datetime, date

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "ae5d1c000105"
down_revision = "ae5d1c000104"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =============================================================================
    # SEED BROKERAGE DATA
    # =============================================================================

    # Create sample brokerage
    op.execute(
        f"""
        INSERT INTO brokerages (name, license_number, email, phone, address, website, rera_registered, brand_settings) VALUES 
        (
            'PropertyPro Real Estate',
            'RERA-12345',
            'info@propertypro.ae',
            '+971-4-123-4567',
            'Business Bay, Dubai, UAE',
            'https://propertypro.ae',
            true,
            '{json.dumps({
                "primary_color": "#1E3A8A",
                "secondary_color": "#F59E0B", 
                "logo_url": "/assets/logo.png",
                "font_family": "Inter",
                "brand_guidelines": "Professional, modern, Dubai-focused"
            })}'
        )
    """
    )

    # =============================================================================
    # SEED MARKETING TEMPLATES
    # =============================================================================

    # Just Listed Postcard Template
    op.execute(
        f"""
        INSERT INTO marketing_templates (name, category, type, description, content_template, design_config, dubai_specific, created_by) VALUES 
        (
            'Dubai Just Listed - Luxury Postcard',
            'postcard',
            'just_listed',
            'Professional postcard template for new luxury listings in Dubai',
            '{json.dumps({
                "title": "JUST LISTED - {{property_title}}",
                "headline": "Exclusive {{property_type}} in {{location}}",
                "features": ["{{bedrooms}} Bedrooms", "{{bathrooms}} Bathrooms", "{{area_sqft}} Sq Ft", "{{key_features}}"],
                "description": "{{ai_generated_description}}",
                "price": "AED {{price}}",
                "contact": "{{agent_name}} - {{agent_phone}}",
                "call_to_action": "Schedule your exclusive viewing today!",
                "disclaimers": ["RERA License: {{brokerage_license}}", "Prices subject to change"]
            })}',
            '{json.dumps({
                "background_color": "#FFFFFF",
                "primary_color": "#1E3A8A", 
                "accent_color": "#F59E0B",
                "font_primary": "Inter Bold",
                "font_body": "Inter Regular",
                "layout": "image_top_content_bottom",
                "image_dimensions": "600x400"
            })}',
            true,
            1
        )
    """
    )

    # Open House Email Template
    op.execute(
        f"""
        INSERT INTO marketing_templates (name, category, type, description, content_template, design_config, dubai_specific, created_by) VALUES 
        (
            'Dubai Open House - Email Invitation',
            'email',
            'open_house',
            'Professional email template for open house events in Dubai',
            '{json.dumps({
                "subject": "Exclusive Open House: {{property_title}} - {{date}}",
                "greeting": "Dear {{recipient_name}},",
                "intro": "You are cordially invited to an exclusive open house viewing of this stunning {{property_type}} in {{location}}.",
                "property_highlights": "{{ai_generated_highlights}}",
                "event_details": {
                    "date": "{{open_house_date}}",
                    "time": "{{open_house_time}}",
                    "duration": "2 hours",
                    "address": "{{property_address}}",
                    "parking": "Valet parking available"
                },
                "rsvp_info": "Please RSVP by {{rsvp_date}} to {{agent_email}} or {{agent_phone}}",
                "signature": "{{agent_name}}<br>{{brokerage_name}}<br>RERA License: {{brokerage_license}}"
            })}',
            '{json.dumps({
                "template_style": "professional",
                "color_scheme": "dubai_luxury",
                "include_property_images": true,
                "max_images": 3
            })}',
            true,
            1
        )
    """
    )

    # Social Media - Just Listed Template
    social_content_template = json.dumps(
        {
            "caption": "✨ JUST LISTED ✨\\n\\n📍 {{location}}\\n🏠 {{property_type}}\\n🛏️ {{bedrooms}} BR | 🛁 {{bathrooms}} BA\\n📏 {{area_sqft}} sq ft\\n💰 AED {{price}}\\n\\n{{ai_generated_description}}\\n\\n{{hashtags}}\\n\\n#DubaiRealEstate #{{location}}Properties #LuxuryLiving #PropertyPro",
            "story_text": "New Listing Alert!\\n{{property_title}}\\nAED {{price}}",
            "carousel_slides": [
                {"type": "property_image", "overlay": "JUST LISTED"},
                {"type": "property_details", "layout": "specs"},
                {"type": "location_map", "style": "satellite"},
            ],
        }
    )
    social_design_config = json.dumps(
        {
            "aspect_ratio": "1:1",
            "brand_overlay": True,
            "include_agent_info": True,
            "story_duration": 24,
            "suggested_hashtags": [
                "#DubaiRealEstate",
                "#PropertyForSale",
                "#LuxuryLiving",
                "#DubaiProperties",
                "#RealEstateInvestment",
                "#PropertyPro",
            ],
        }
    )
    op.execute(
        f"""
        INSERT INTO marketing_templates (name, category, type, description, content_template, design_config, dubai_specific, created_by) VALUES 
        (
            'Instagram Just Listed - Dubai',
            'social',
            'just_listed',
            'Instagram-optimized template for new Dubai listings',
            '{social_content_template}',
            '{social_design_config}',
            true,
            1
        )
    """
    )

    # =============================================================================
    # SEED WORKFLOW PACKAGES
    # =============================================================================

    # New Listing Package
    op.execute(
        f"""
        INSERT INTO workflow_packages (name, description, category, steps, estimated_duration, is_template, created_by) VALUES 
        (
            'New Listing Package',
            'Complete AURA-style workflow for launching a new property listing',
            'listing',
            '{json.dumps([
                {
                    "step_name": "Generate CMA Report",
                    "step_type": "ai_task",
                    "description": "Create comparative market analysis with pricing recommendations",
                    "ai_task_type": "cma_generation",
                    "estimated_duration": 5,
                    "inputs": ["property_address", "property_details"],
                    "outputs": ["cma_report", "price_recommendations"]
                },
                {
                    "step_name": "Create Listing Strategy",
                    "step_type": "ai_task", 
                    "description": "Develop comprehensive listing strategy document",
                    "ai_task_type": "strategy_generation",
                    "estimated_duration": 8,
                    "inputs": ["property_details", "cma_data", "market_conditions"],
                    "outputs": ["listing_strategy", "marketing_timeline"]
                },
                {
                    "step_name": "Generate Marketing Campaign",
                    "step_type": "ai_task",
                    "description": "Create postcard, email, and social media content",
                    "ai_task_type": "content_generation",
                    "estimated_duration": 10,
                    "inputs": ["property_details", "listing_strategy", "brand_assets"],
                    "outputs": ["marketing_campaign", "social_posts", "email_templates"]
                },
                {
                    "step_name": "Agent Review & Approval",
                    "step_type": "human_review",
                    "description": "Agent reviews and approves all generated content",
                    "estimated_duration": 15,
                    "inputs": ["all_generated_content"],
                    "outputs": ["approved_campaign", "revision_requests"]
                },
                {
                    "step_name": "Launch Marketing Campaign",
                    "step_type": "api_call",
                    "description": "Distribute approved marketing materials",
                    "estimated_duration": 2,
                    "inputs": ["approved_campaign"],
                    "outputs": ["campaign_metrics", "distribution_report"]
                }
            ])}',
            40,
            true,
            1
        )
    """
    )

    # Lead Nurturing Package
    op.execute(
        f"""
        INSERT INTO workflow_packages (name, description, category, steps, estimated_duration, is_template, created_by) VALUES 
        (
            'Lead Nurturing Package',
            'Automated lead nurturing sequence with personalized touchpoints',
            'nurturing',
            '{json.dumps([
                {
                    "step_name": "Lead Qualification Analysis",
                    "step_type": "ai_task",
                    "description": "Analyze lead profile and investment potential",
                    "ai_task_type": "lead_scoring",
                    "estimated_duration": 3,
                    "inputs": ["client_profile", "budget", "preferences"],
                    "outputs": ["lead_score", "persona_category"]
                },
                {
                    "step_name": "Personalized Welcome Email",
                    "step_type": "ai_task",
                    "description": "Generate personalized welcome email based on lead profile",
                    "ai_task_type": "email_generation",
                    "estimated_duration": 5,
                    "inputs": ["client_profile", "persona_category"],
                    "outputs": ["welcome_email", "follow_up_schedule"]
                },
                {
                    "step_name": "Property Recommendations",
                    "step_type": "ai_task",
                    "description": "Generate curated property recommendations",
                    "ai_task_type": "property_matching",
                    "estimated_duration": 7,
                    "inputs": ["client_preferences", "current_listings"],
                    "outputs": ["property_list", "matching_explanations"]
                },
                {
                    "step_name": "Schedule Follow-up Tasks",
                    "step_type": "notification",
                    "description": "Set up automated follow-up reminders for agent",
                    "estimated_duration": 1,
                    "inputs": ["follow_up_schedule"],
                    "outputs": ["scheduled_tasks", "reminder_notifications"]
                }
            ])}',
            16,
            true,
            1
        )
    """
    )

    # Client Onboarding Package
    op.execute(
        f"""
        INSERT INTO workflow_packages (name, description, category, steps, estimated_duration, is_template, created_by) VALUES 
        (
            'Client Onboarding Package',
            'Complete client onboarding with welcome materials and CRM setup',
            'onboarding',
            '{json.dumps([
                {
                    "step_name": "Create Client Profile",
                    "step_type": "api_call",
                    "description": "Set up comprehensive client profile in CRM",
                    "estimated_duration": 2,
                    "inputs": ["client_details", "preferences", "documents"],
                    "outputs": ["crm_profile", "client_id"]
                },
                {
                    "step_name": "Generate Welcome Package",
                    "step_type": "ai_task",
                    "description": "Create personalized welcome materials and market guide",
                    "ai_task_type": "content_generation",
                    "estimated_duration": 10,
                    "inputs": ["client_profile", "market_data", "services_overview"],
                    "outputs": ["welcome_packet", "market_guide", "service_brochure"]
                },
                {
                    "step_name": "Schedule Initial Meeting",
                    "step_type": "notification",
                    "description": "Send meeting invitation and preparation materials",
                    "estimated_duration": 3,
                    "inputs": ["client_contact", "agent_calendar"],
                    "outputs": ["meeting_invite", "prep_materials"]
                },
                {
                    "step_name": "Send Welcome Communication",
                    "step_type": "api_call",
                    "description": "Deliver welcome packet and meeting details to client",
                    "estimated_duration": 1,
                    "inputs": ["welcome_materials", "client_contact"],
                    "outputs": ["delivery_confirmation", "tracking_info"]
                }
            ])}',
            16,
            true,
            1
        )
    """
    )

    # =============================================================================
    # SEED DUBAI MARKET DATA
    # =============================================================================

    # Current market snapshots for major Dubai areas
    dubai_areas = [
        {
            "area": "Dubai Marina",
            "property_type": "apartment",
            "metrics": {
                "avg_price_per_sqft": 1200,
                "total_inventory": 450,
                "sales_this_month": 23,
                "avg_days_on_market": 45,
                "price_trend": "stable",
            },
            "trend_analysis": {
                "yoy_growth": "5.2%",
                "market_velocity": "moderate",
                "buyer_profile": "international_investors",
            },
        },
        {
            "area": "Downtown Dubai",
            "property_type": "apartment",
            "metrics": {
                "avg_price_per_sqft": 1500,
                "total_inventory": 320,
                "sales_this_month": 31,
                "avg_days_on_market": 38,
                "price_trend": "increasing",
            },
            "trend_analysis": {
                "yoy_growth": "8.7%",
                "market_velocity": "high",
                "buyer_profile": "luxury_seekers",
            },
        },
        {
            "area": "Palm Jumeirah",
            "property_type": "villa",
            "metrics": {
                "avg_price_per_sqft": 2200,
                "total_inventory": 85,
                "sales_this_month": 12,
                "avg_days_on_market": 62,
                "price_trend": "increasing",
            },
            "trend_analysis": {
                "yoy_growth": "12.3%",
                "market_velocity": "low",
                "buyer_profile": "ultra_high_net_worth",
            },
        },
        {
            "area": "Business Bay",
            "property_type": "apartment",
            "metrics": {
                "avg_price_per_sqft": 950,
                "total_inventory": 680,
                "sales_this_month": 45,
                "avg_days_on_market": 52,
                "price_trend": "stable",
            },
            "trend_analysis": {
                "yoy_growth": "3.1%",
                "market_velocity": "moderate",
                "buyer_profile": "young_professionals",
            },
        },
        {
            "area": "Jumeirah Beach Residence",
            "property_type": "apartment",
            "metrics": {
                "avg_price_per_sqft": 1350,
                "total_inventory": 280,
                "sales_this_month": 19,
                "avg_days_on_market": 41,
                "price_trend": "increasing",
            },
            "trend_analysis": {
                "yoy_growth": "6.8%",
                "market_velocity": "moderate_high",
                "buyer_profile": "lifestyle_buyers",
            },
        },
    ]

    today = date.today()
    for area_data in dubai_areas:
        op.execute(
            f"""
            INSERT INTO market_snapshots (area, snapshot_date, property_type, metrics, trend_analysis, data_source) VALUES 
            (
                '{area_data["area"]}',
                '{today}',
                '{area_data["property_type"]}',
                '{json.dumps(area_data["metrics"])}',
                '{json.dumps(area_data["trend_analysis"])}',
                'propertypro_analytics'
            )
        """
        )

    # =============================================================================
    # SEED COMMUNICATION TEMPLATES
    # =============================================================================

    # Inspection Scheduled Email
    op.execute(
        f"""
        INSERT INTO communication_templates (name, category, trigger_event, subject, content, variables, created_by) VALUES 
        (
            'Inspection Scheduled - Client Notification',
            'email',
            'inspection_scheduled',
            'Property Inspection Confirmed - {{property_title}}',
            'Dear {{client_name}},

This email confirms your property inspection appointment:

**Property Details:**
- Property: {{property_title}}
- Address: {{property_address}}
- Type: {{property_type}}
- Price: AED {{property_price}}

**Inspection Details:**
- Date: {{inspection_date}}
- Time: {{inspection_time}}
- Duration: Approximately 45 minutes
- Meeting Point: {{meeting_location}}

**What to Bring:**
- Government-issued ID
- Pre-approval letter (if applicable)
- Questions list

**Contact Information:**
Your agent {{agent_name}} will meet you at the property.
Phone: {{agent_phone}}
Email: {{agent_email}}

We look forward to showing you this beautiful property!

Best regards,
{{agent_name}}
{{brokerage_name}}
RERA License: {{brokerage_license}}',
            '{json.dumps([
                "client_name", "property_title", "property_address", "property_type", 
                "property_price", "inspection_date", "inspection_time", "meeting_location",
                "agent_name", "agent_phone", "agent_email", "brokerage_name", "brokerage_license"
            ])}',
            1
        )
    """
    )

    # Offer Received SMS
    op.execute(
        f"""
        INSERT INTO communication_templates (name, category, trigger_event, content, variables, created_by) VALUES 
        (
            'Offer Received - Seller Alert',
            'sms',
            'offer_received',
            'OFFER ALERT: We received an offer of AED {{offer_amount}} for {{property_title}}. Offer expires {{expiry_time}}. Call {{agent_name}} at {{agent_phone}} immediately to discuss. - {{brokerage_name}}',
            '{json.dumps([
                "offer_amount", "property_title", "expiry_time", 
                "agent_name", "agent_phone", "brokerage_name"
            ])}',
            1
        )
    """
    )


def downgrade() -> None:
    # Clear seeded data (in reverse order of creation)
    op.execute("DELETE FROM communication_templates WHERE created_by = 1")
    op.execute(
        "DELETE FROM market_snapshots WHERE data_source = 'propertypro_analytics'"
    )
    op.execute("DELETE FROM workflow_packages WHERE created_by = 1")
    op.execute("DELETE FROM marketing_templates WHERE created_by = 1")
    op.execute("DELETE FROM brokerages WHERE name = 'PropertyPro Real Estate'")
