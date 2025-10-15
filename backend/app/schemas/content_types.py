"""
Content Type Schemas and Enums
================================

Standardized content types and base schemas for Aura content generation system.
Aligns with frontend content templates and ensures consistent API contracts.

Version: 3.2
Phase: Track 1.1 - Backend Content Taxonomy
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date


# =============================================================================
# CONTENT TYPE ENUMS
# =============================================================================


class ContentType(str, Enum):
    """
    Canonical content types supported by Aura.
    Maps 1:1 with frontend ContentType and docs/content_templates/
    """

    CMA_REPORT = "CMA_REPORT"
    PITCH_DECK = "PITCH_DECK"
    MARKET_REPORT = "MARKET_REPORT"
    NEWSLETTER = "NEWSLETTER"
    SOCIAL_POST = "SOCIAL_POST"


class TaskStatus(str, Enum):
    """Standardized task status across all workflows"""

    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETE = "Complete"
    ERROR = "Error"


# =============================================================================
# BASE REQUEST/RESPONSE MODELS
# =============================================================================


class ContentGenerationRequest(BaseModel):
    """Base model for all content generation requests"""

    content_type: ContentType
    user_prompt: str = Field(
        ..., min_length=1, description="Original user request text"
    )
    parent_task_id: Optional[str] = Field(
        None, description="Parent task ID for follow-up requests"
    )

    class Config:
        use_enum_values = True


class ValidationResult(BaseModel):
    """
    Validation result returned by validators.
    Used for pre-flight checks and enrichment decisions.
    """

    valid: bool = Field(..., description="Whether payload passes validation")
    missing_fields: List[str] = Field(
        default_factory=list, description="List of required fields that are missing"
    )
    normalized_payload: Dict[str, Any] = Field(
        default_factory=dict, description="Cleaned and normalized payload"
    )
    tips: List[str] = Field(
        default_factory=list,
        description="Helpful suggestions for filling missing fields",
    )
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in validation (0-1)"
    )


class ValidationError422(BaseModel):
    """
    Standardized 422 error response with machine-parsable fields.
    Ensures frontend never sees raw errors and can auto-heal or ask clarifying questions.
    """

    detail: str = Field(..., description="Human-readable error message")
    missing_fields: List[str] = Field(
        ..., description="List of missing required fields"
    )
    hints: List[str] = Field(
        default_factory=list, description="User-friendly hints for each missing field"
    )
    suggested_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Suggested default values"
    )
    can_auto_heal: bool = Field(
        default=False, description="Whether frontend enrichment can fix this"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Missing required fields for CMA Report generation",
                "missing_fields": ["location", "property_type"],
                "hints": [
                    "Please specify a location (e.g., 'Dubai Marina' or 'Downtown Dubai')",
                    "Property type can be 'residential', 'commercial', 'villa', or 'apartment'",
                ],
                "suggested_defaults": {
                    "property_type": "mixed",
                    "time_range": "6 months",
                },
                "can_auto_heal": True,
            }
        }


class TaskResponse(BaseModel):
    """
    Canonical task response shape.
    Used across /api/v1/tasks, /api/v1/tasks/sync, and all content generation endpoints.
    """

    id: str
    title: str
    status: TaskStatus
    type: ContentType
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    # Content flags
    has_content: bool = Field(
        default=False, description="Whether content has been generated"
    )
    content_type: Optional[ContentType] = Field(
        None, description="Type of generated content"
    )

    # Relationships
    parent_id: Optional[str] = Field(None, description="Parent task ID for follow-ups")
    related_tasks: List[str] = Field(
        default_factory=list, description="Related task IDs"
    )

    # Export metadata
    exported_at: Optional[datetime] = Field(None, description="Last export timestamp")
    export_formats: List[str] = Field(
        default_factory=list, description="Available export formats"
    )

    # Error handling
    error: Optional[str] = Field(None, description="Error message if status is Error")

    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Type-specific metadata"
    )

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "task_123",
                "title": "CMA Report for Dubai Marina",
                "status": "Complete",
                "type": "CMA_REPORT",
                "timestamp": "2025-10-10T08:00:00Z",
                "created_at": "2025-10-10T08:00:00Z",
                "updated_at": "2025-10-10T08:05:00Z",
                "has_content": True,
                "content_type": "CMA_REPORT",
                "parent_id": None,
                "related_tasks": [],
                "exported_at": None,
                "export_formats": ["pdf", "html"],
                "error": None,
                "metadata": {
                    "location": "Dubai Marina",
                    "property_type": "apartment",
                    "comparables_count": 5,
                },
            }
        }


class TaskSyncResponse(BaseModel):
    """
    Response for /api/v1/tasks/sync endpoint.
    Returns only changed tasks since last sync.
    """

    tasks: List[TaskResponse]
    last_sync: datetime
    has_more: bool = Field(
        default=False, description="Whether more updates exist beyond this batch"
    )
    cursor: Optional[str] = Field(None, description="Pagination cursor for next batch")


# =============================================================================
# CONTENT-SPECIFIC REQUEST MODELS
# =============================================================================


class CMAReportRequest(ContentGenerationRequest):
    """Request model for CMA Report generation"""

    location: str = Field(
        ..., min_length=2, description="Property location (neighborhood or address)"
    )
    property_type: Optional[str] = Field(
        "mixed",
        description="Property type: residential, commercial, villa, apartment, mixed",
    )
    bedrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(
        None, ge=0, le=20, description="Number of bathrooms"
    )
    sqft: Optional[int] = Field(None, gt=0, description="Property square footage")
    time_range: Optional[str] = Field(
        "6 months", description="Historical time range for comparables"
    )
    comparable_count: Optional[int] = Field(
        5, ge=3, le=10, description="Number of comparable properties"
    )

    content_type: ContentType = ContentType.CMA_REPORT


class PitchDeckRequest(ContentGenerationRequest):
    """Request model for Investor Pitch Deck generation"""

    property_address: str = Field(
        ..., min_length=5, description="Property address or project name"
    )
    investment_type: Optional[str] = Field(
        "acquisition",
        description="Investment type: acquisition, development, renovation",
    )
    target_audience: Optional[str] = Field(
        "investors", description="Target audience: investors, partners, lenders"
    )
    slide_count: Optional[int] = Field(
        10, ge=5, le=20, description="Number of slides to generate"
    )
    include_financials: bool = Field(True, description="Include financial projections")

    content_type: ContentType = ContentType.PITCH_DECK


class MarketReportRequest(ContentGenerationRequest):
    """Request model for Market Report generation"""

    region: str = Field(
        ..., min_length=2, description="Geographic region or neighborhood"
    )
    property_type: Optional[str] = Field("mixed", description="Property type filter")
    time_period: Optional[str] = Field("Q3 2025", description="Reporting period")
    metrics: List[str] = Field(
        default_factory=lambda: ["price_per_sqft", "trend_analysis", "demand_index"],
        description="Metrics to include in report",
    )

    content_type: ContentType = ContentType.MARKET_REPORT


class NewsletterRequest(ContentGenerationRequest):
    """Request model for Newsletter generation"""

    topic: str = Field(..., min_length=5, description="Newsletter topic or theme")
    tone: Optional[str] = Field(
        "professional",
        description="Tone: professional, casual, friendly, authoritative",
    )
    target_audience: Optional[str] = Field(
        "clients", description="Target audience: clients, investors, agents"
    )
    include_listings: bool = Field(
        True, description="Include featured property listings"
    )
    max_length: Optional[int] = Field(500, gt=100, description="Maximum word count")

    content_type: ContentType = ContentType.NEWSLETTER


class SocialPostRequest(ContentGenerationRequest):
    """Request model for Social Media Post generation"""

    platform: str = Field(
        ..., description="Social platform: instagram, facebook, linkedin, twitter"
    )
    topic: str = Field(..., min_length=5, description="Post topic or listing highlight")
    tone: Optional[str] = Field(
        "engaging", description="Tone: engaging, professional, casual, inspirational"
    )
    include_hashtags: bool = Field(True, description="Include relevant hashtags")
    character_limit: Optional[int] = Field(
        None, description="Character limit (platform-specific)"
    )
    property_id: Optional[str] = Field(
        None, description="Property ID if promoting a listing"
    )

    content_type: ContentType = ContentType.SOCIAL_POST

    @validator("platform")
    def validate_platform(cls, v):
        allowed = ["instagram", "facebook", "linkedin", "twitter", "tiktok"]
        if v.lower() not in allowed:
            raise ValueError(f"Platform must be one of: {', '.join(allowed)}")
        return v.lower()


# =============================================================================
# CONTENT GENERATION RESPONSE
# =============================================================================


class ContentGenerationResponse(BaseModel):
    """
    Unified response for all content generation endpoints.
    Includes task metadata and optional inline content preview.
    """

    success: bool
    task_id: str
    message: str
    content_type: ContentType
    status: TaskStatus

    # Optional inline data
    data: Optional[Dict[str, Any]] = Field(
        None, description="Generated content data (if available)"
    )
    preview_url: Optional[str] = Field(
        None, description="URL to preview generated content"
    )

    # Enrichment metadata
    enrichment: Optional[Dict[str, Any]] = Field(
        None, description="Validation and enrichment metadata"
    )

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "success": True,
                "task_id": "task_456",
                "message": "CMA Report generated successfully",
                "content_type": "CMA_REPORT",
                "status": "Complete",
                "data": {
                    "property": {"address": "Dubai Marina, Tower A"},
                    "comparables": [],
                    "valuation": {},
                },
                "preview_url": "/api/v1/content/task_456/preview",
                "enrichment": {
                    "status": "valid",
                    "inferred_fields": ["property_type"],
                    "debug_log": [],
                },
            }
        }
