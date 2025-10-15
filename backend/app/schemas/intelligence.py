"""
Intelligence API Schemas
========================

Pydantic models for the unified intelligence pipeline API.
Harmonizes frontend TypeScript interfaces with backend validation.
"""

from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class ContentType(str, Enum):
    """Content types supported by the intelligence engine"""

    CMA_REPORT = "CMA_REPORT"
    PITCH_DECK = "PITCH_DECK"
    SOCIAL_POST = "SOCIAL_POST"
    MARKET_REPORT = "MARKET_REPORT"
    EMAIL_CAMPAIGN = "EMAIL_CAMPAIGN"
    PROPERTY_DESCRIPTION = "PROPERTY_DESCRIPTION"
    LISTING_STRATEGY = "LISTING_STRATEGY"
    GENERAL = "GENERAL"
    PROPERTY_BROCHURE = "PROPERTY_BROCHURE"


class TaskStatus(str, Enum):
    """Task processing status"""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class QualityRequirements(BaseModel):
    """Quality requirements for content generation"""

    min_score: float = Field(default=0.8, ge=0.0, le=1.0)
    brand_consistency: bool = Field(default=True)
    compliance_checks: List[str] = Field(default=["readability", "brand", "compliance"])


class MemoryContext(BaseModel):
    """Memory and context information"""

    relevant_memories: List[Dict[str, Any]] = Field(default=[])
    contextual_insights: List[str] = Field(default=[])
    brand_alignment: float = Field(default=0.8, ge=0.0, le=1.0)


class QualityScores(BaseModel):
    """Quality assessment scores"""

    overall_score: float = Field(..., ge=0.0, le=1.0)
    content_quality: float = Field(..., ge=0.0, le=1.0)
    brand_compliance: float = Field(..., ge=0.0, le=1.0)
    validation_score: float = Field(..., ge=0.0, le=1.0)


class GeneratedContent(BaseModel):
    """Generated content structure"""

    structured: Dict[str, Any] = Field(default={})
    narrative: str = Field(default="")
    key_insights: List[str] = Field(default=[])
    actionable_recommendations: List[str] = Field(default=[])


class ContentMetadata(BaseModel):
    """Content metadata"""

    generation_timestamp: datetime
    model: str = Field(..., description="Model used for generation")
    processing_time_ms: int = Field(default=0, ge=0)
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0)
    sources: List[str] = Field(default=[])
    listing_id: Optional[str] = Field(
        default=None, description="Associated listing identifier"
    )
    mock_origin: bool = Field(default=False, description="Generated in mock mode")


# Request Models


class ContentGenerationRequest(BaseModel):
    """Request to generate content"""

    user_input: str = Field(..., min_length=1, max_length=5000)
    content_type: Optional[ContentType] = None
    session_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    quality_requirements: Optional[QualityRequirements] = None
    memory_enhanced: bool = Field(default=True)
    context: Optional[Dict[str, Any]] = None

    @validator("user_input")
    def validate_input(cls, v):
        """Clean and validate user input"""
        v = v.strip()
        if not v:
            raise ValueError("User input cannot be empty")
        return v


class TranscriptionRequest(BaseModel):
    """Request for audio transcription"""

    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")
    language: str = Field(default="en")
    use_mock: bool = Field(
        default=False, description="Use mock transcription for testing"
    )


class RefinementRequest(BaseModel):
    """Request to refine existing content"""

    content_id: str = Field(..., min_length=1)
    refinement_prompt: str = Field(..., min_length=1, max_length=2000)
    quality_requirements: Optional[QualityRequirements] = None
    context: Optional[Dict[str, Any]] = None


# Response Models


class TranscriptionResponse(BaseModel):
    """Transcription result"""

    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    language_detected: str
    is_mock: bool = Field(default=False)
    processing_time_ms: int = Field(default=0)


class TaskStatusResponse(BaseModel):
    """Task status and progress"""

    task_id: str
    status: TaskStatus
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    retries: int = Field(default=0, ge=0)


class IntelligenceContent(BaseModel):
    """Complete intelligence content structure"""

    content_id: str
    task_id: str
    content_type: ContentType
    title: str
    enhanced: bool = Field(description="Whether content was enhanced by intelligence")
    quality_scores: QualityScores
    memory_context: MemoryContext
    generated_content: GeneratedContent
    metadata: ContentMetadata
    export_ready: bool = Field(default=True)
    version: str = Field(default="3.4")


class ContentGenerationResponse(BaseModel):
    """Response from content generation"""

    task_id: str
    status: TaskStatus
    message: str
    estimated_duration_ms: int = Field(default=30000)
    content_id: Optional[str] = None  # Available when completed


class ContentRetrievalResponse(BaseModel):
    """Response when retrieving generated content"""

    content: IntelligenceContent
    recommendations: List[str] = Field(default=[])
    refinement_suggestions: List[str] = Field(default=[])


class RefinementResponse(BaseModel):
    """Response from content refinement"""

    task_id: str
    original_content_id: str
    refined_content_id: str
    status: TaskStatus
    message: str
    improvements_made: List[str] = Field(default=[])


class StreamProgressEvent(BaseModel):
    """SSE progress event"""

    event: str = Field(default="progress")
    task_id: str
    status: TaskStatus
    progress: int = Field(ge=0, le=100)
    current_step: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MockPromptResponse(BaseModel):
    """Mock transcription prompt for testing"""

    text: str
    mock_type: str
    description: str


class PropertyBrochureSection(BaseModel):
    """Structured section within a property brochure"""

    label: str = Field(..., description="Section label (e.g., Highlights, Amenities)")
    body: str = Field(..., description="Narrative copy for the section")
    bullets: List[str] = Field(default_factory=list, description="Optional bullet list")


class PropertyBrochureContent(BaseModel):
    """Structured payload returned for property brochures"""

    listing_id: str = Field(..., description="Identifier of the source listing")
    title: str = Field(..., description="Marketing title for the brochure")
    subtitle: Optional[str] = Field(
        default=None, description="Optional subtitle or tagline"
    )
    price: str = Field(..., description="Formatted price label (AED)")
    location: str = Field(..., description="Primary location string")
    property_type: Optional[str] = Field(
        default=None, description="Property type label"
    )
    bedrooms: Optional[float] = Field(
        default=None, ge=0, description="Number of bedrooms"
    )
    bathrooms: Optional[float] = Field(
        default=None, ge=0, description="Number of bathrooms"
    )
    area_sqft: Optional[float] = Field(
        default=None, ge=0, description="Built-up area in square feet"
    )
    highlights: List[str] = Field(
        default_factory=list, description="Top bullet highlights"
    )
    description: str = Field(..., description="Primary marketing narrative")
    sections: List[PropertyBrochureSection] = Field(
        default_factory=list, description="Detailed brochure sections"
    )
    neighborhood_insights: List[str] = Field(
        default_factory=list, description="Neighborhood callouts"
    )
    amenities: Dict[str, List[str]] = Field(
        default_factory=dict, description="Categorized amenities"
    )
    call_to_action: Optional[str] = Field(
        default=None, description="Suggested CTA copy"
    )
    images: List[str] = Field(
        default_factory=list, description="Collection of image URLs"
    )

    @validator("price")
    def validate_price(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Price cannot be empty")
        if not value.upper().startswith("AED"):
            raise ValueError("Price must start with AED")
        return value

    @validator("highlights", "neighborhood_insights", each_item=True)
    def strip_lists(cls, value: str) -> str:
        return value.strip()


# Error Response Models


class IntelligenceError(BaseModel):
    """Standardized error response"""

    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorDetail(BaseModel):
    """Detailed validation error"""

    field: str
    message: str
    value: Any


class ValidationErrorResponse(BaseModel):
    """422 validation error response"""

    error_code: str = "validation_error"
    message: str = "Request validation failed"
    details: List[ValidationErrorDetail]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
