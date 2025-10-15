"""
Content Validation Service
===========================

Per-content-type validators that return structured ValidationResult.
Used for pre-flight checks before content generation to prevent 422 errors.

Version: 3.2
Phase: Track 1.2 - Validation Layer
"""

import re
from typing import Dict, Any, List, Optional
from app.schemas.content_types import ValidationResult, ContentType


# =============================================================================
# VALIDATION HELPERS
# =============================================================================


def normalize_location(location: str) -> str:
    """Normalize location string to standard format"""
    if not location:
        return ""

    # Common Dubai neighborhoods
    known_areas = [
        "Dubai Marina",
        "Downtown Dubai",
        "Jumeirah Beach Residence",
        "JBR",
        "Palm Jumeirah",
        "Business Bay",
        "Dubai Hills",
        "Arabian Ranches",
        "Emirates Hills",
        "Dubai Sports City",
        "Jumeirah Lakes Towers",
        "JLT",
        "DIFC",
        "Deira",
        "Bur Dubai",
        "Al Barsha",
        "Motor City",
        "Dubai Silicon Oasis",
        "International City",
        "Discovery Gardens",
    ]

    # Check for known areas (case-insensitive)
    location_lower = location.lower().strip()
    for area in known_areas:
        if area.lower() in location_lower:
            return area

    # Return cleaned version
    return location.strip().title()


def normalize_property_type(prop_type: Optional[str]) -> str:
    """Normalize property type to standard values"""
    if not prop_type:
        return "mixed"

    prop_type_lower = prop_type.lower().strip()

    # Map common variations
    type_mapping = {
        "apartment": ["apartment", "flat", "unit", "condo"],
        "villa": ["villa", "house", "townhouse", "single-family"],
        "commercial": ["commercial", "office", "retail", "warehouse"],
        "residential": ["residential", "resi"],
        "mixed": ["mixed", "all", "any"],
    }

    for standard, variations in type_mapping.items():
        if prop_type_lower in variations:
            return standard

    return "mixed"


def extract_number_from_text(text: str, keyword: str) -> Optional[int]:
    """Extract number following a keyword from text"""
    pattern = rf"{keyword}\s*:?\s*(\d+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else None


# =============================================================================
# CMA REPORT VALIDATOR
# =============================================================================


def validate_cma_report(payload: Dict[str, Any]) -> ValidationResult:
    """
    Validate CMA Report generation request.

    Required fields: location
    Optional but recommended: property_type, bedrooms, bathrooms, sqft
    """
    missing = []
    tips = []
    normalized = {}

    # Required: location
    location = payload.get("location", "").strip()
    if not location or len(location) < 2:
        missing.append("location")
        tips.append(
            "Please specify a location (e.g., 'Dubai Marina', 'Downtown Dubai', or a specific address)"
        )
    else:
        normalized["location"] = normalize_location(location)

    # Optional: property_type with default
    property_type = payload.get("property_type", "mixed")
    normalized["property_type"] = normalize_property_type(property_type)

    # Optional: numeric fields
    for field in ["bedrooms", "bathrooms", "sqft"]:
        value = payload.get(field)
        if value is not None:
            try:
                normalized[field] = int(value)
            except (ValueError, TypeError):
                tips.append(f"{field.title()} should be a number")

    # Optional: time_range with default
    normalized["time_range"] = payload.get("time_range", "6 months")

    # Optional: comparable_count with validation
    comp_count = payload.get("comparable_count", 5)
    try:
        comp_count = int(comp_count)
        if comp_count < 3:
            comp_count = 3
            tips.append("Using minimum of 3 comparables for accurate analysis")
        elif comp_count > 10:
            comp_count = 10
            tips.append("Using maximum of 10 comparables for concise reporting")
        normalized["comparable_count"] = comp_count
    except (ValueError, TypeError):
        normalized["comparable_count"] = 5

    # Confidence calculation
    confidence = 1.0
    if "property_type" not in payload:
        confidence -= 0.1  # Slight reduction if type not specified
    if not payload.get("bedrooms") and not payload.get("sqft"):
        confidence -= 0.2  # Moderate reduction if no property details

    valid = len(missing) == 0

    return ValidationResult(
        valid=valid,
        missing_fields=missing,
        normalized_payload=normalized,
        tips=tips,
        confidence=max(0.0, confidence),
    )


# =============================================================================
# PITCH DECK VALIDATOR
# =============================================================================


def validate_pitch_deck(payload: Dict[str, Any]) -> ValidationResult:
    """
    Validate Pitch Deck generation request.

    Required fields: property_address
    Optional: investment_type, target_audience, slide_count
    """
    missing = []
    tips = []
    normalized = {}

    # Required: property_address
    property_address = payload.get("property_address", "").strip()
    if not property_address or len(property_address) < 5:
        missing.append("property_address")
        tips.append("Please provide the property address or project name")
    else:
        normalized["property_address"] = property_address

    # Optional: investment_type with default
    investment_type = payload.get("investment_type", "acquisition").lower()
    valid_types = ["acquisition", "development", "renovation", "flip"]
    if investment_type not in valid_types:
        investment_type = "acquisition"
        tips.append(f"Investment type should be one of: {', '.join(valid_types)}")
    normalized["investment_type"] = investment_type

    # Optional: target_audience with default
    target_audience = payload.get("target_audience", "investors").lower()
    valid_audiences = ["investors", "partners", "lenders", "stakeholders"]
    if target_audience not in valid_audiences:
        target_audience = "investors"
    normalized["target_audience"] = target_audience

    # Optional: slide_count with bounds
    slide_count = payload.get("slide_count", 10)
    try:
        slide_count = int(slide_count)
        if slide_count < 5:
            slide_count = 5
            tips.append("Using minimum of 5 slides for complete presentation")
        elif slide_count > 20:
            slide_count = 20
            tips.append("Using maximum of 20 slides for audience attention")
        normalized["slide_count"] = slide_count
    except (ValueError, TypeError):
        normalized["slide_count"] = 10

    # Optional: include_financials
    normalized["include_financials"] = payload.get("include_financials", True)

    valid = len(missing) == 0
    confidence = 1.0 if valid else 0.5

    return ValidationResult(
        valid=valid,
        missing_fields=missing,
        normalized_payload=normalized,
        tips=tips,
        confidence=confidence,
    )


# =============================================================================
# MARKET REPORT VALIDATOR
# =============================================================================


def validate_market_report(payload: Dict[str, Any]) -> ValidationResult:
    """
    Validate Market Report generation request.

    Required fields: region
    Optional: property_type, time_period, metrics
    """
    missing = []
    tips = []
    normalized = {}

    # Required: region
    region = payload.get("region", "").strip()
    if not region or len(region) < 2:
        missing.append("region")
        tips.append(
            "Please specify a region or neighborhood (e.g., 'Dubai Marina', 'Downtown Dubai')"
        )
    else:
        normalized["region"] = normalize_location(region)

    # Optional: property_type
    normalized["property_type"] = normalize_property_type(
        payload.get("property_type", "mixed")
    )

    # Optional: time_period
    time_period = payload.get("time_period", "Q3 2025")
    normalized["time_period"] = time_period

    # Optional: metrics with defaults
    metrics = payload.get(
        "metrics", ["price_per_sqft", "trend_analysis", "demand_index"]
    )
    if not isinstance(metrics, list) or len(metrics) == 0:
        metrics = ["price_per_sqft", "trend_analysis", "demand_index"]
        tips.append(
            "Using default metrics: price per sqft, trend analysis, demand index"
        )
    normalized["metrics"] = metrics

    valid = len(missing) == 0
    confidence = 1.0 if valid else 0.5

    return ValidationResult(
        valid=valid,
        missing_fields=missing,
        normalized_payload=normalized,
        tips=tips,
        confidence=confidence,
    )


# =============================================================================
# NEWSLETTER VALIDATOR
# =============================================================================


def validate_newsletter(payload: Dict[str, Any]) -> ValidationResult:
    """
    Validate Newsletter generation request.

    Required fields: topic
    Optional: tone, target_audience, include_listings, max_length
    """
    missing = []
    tips = []
    normalized = {}

    # Required: topic
    topic = payload.get("topic", "").strip()
    if not topic or len(topic) < 5:
        missing.append("topic")
        tips.append(
            "Please provide a topic or theme for the newsletter (e.g., 'Q3 Market Update', 'New Luxury Listings')"
        )
    else:
        normalized["topic"] = topic

    # Optional: tone with validation
    tone = payload.get("tone", "professional").lower()
    valid_tones = ["professional", "casual", "friendly", "authoritative"]
    if tone not in valid_tones:
        tone = "professional"
        tips.append(f"Tone should be one of: {', '.join(valid_tones)}")
    normalized["tone"] = tone

    # Optional: target_audience
    target_audience = payload.get("target_audience", "clients").lower()
    valid_audiences = ["clients", "investors", "agents", "partners"]
    if target_audience not in valid_audiences:
        target_audience = "clients"
    normalized["target_audience"] = target_audience

    # Optional: include_listings
    normalized["include_listings"] = payload.get("include_listings", True)

    # Optional: max_length with bounds
    max_length = payload.get("max_length", 500)
    try:
        max_length = int(max_length)
        if max_length < 100:
            max_length = 100
            tips.append("Using minimum of 100 words for meaningful content")
        elif max_length > 2000:
            max_length = 2000
            tips.append("Using maximum of 2000 words for reader engagement")
        normalized["max_length"] = max_length
    except (ValueError, TypeError):
        normalized["max_length"] = 500

    valid = len(missing) == 0
    confidence = 1.0 if valid else 0.5

    return ValidationResult(
        valid=valid,
        missing_fields=missing,
        normalized_payload=normalized,
        tips=tips,
        confidence=confidence,
    )


# =============================================================================
# SOCIAL POST VALIDATOR
# =============================================================================


def validate_social_post(payload: Dict[str, Any]) -> ValidationResult:
    """
    Validate Social Media Post generation request.

    Required fields: platform, topic
    Optional: tone, include_hashtags, character_limit, property_id
    """
    missing = []
    tips = []
    normalized = {}

    # Required: platform
    platform = payload.get("platform", "").strip().lower()
    valid_platforms = ["instagram", "facebook", "linkedin", "twitter", "tiktok"]
    if not platform or platform not in valid_platforms:
        missing.append("platform")
        tips.append(f"Platform must be one of: {', '.join(valid_platforms)}")
    else:
        normalized["platform"] = platform

        # Set platform-specific character limits if not provided
        if "character_limit" not in payload:
            platform_limits = {
                "twitter": 280,
                "instagram": 2200,
                "facebook": 5000,
                "linkedin": 3000,
                "tiktok": 2200,
            }
            normalized["character_limit"] = platform_limits.get(platform)

    # Required: topic
    topic = payload.get("topic", "").strip()
    if not topic or len(topic) < 5:
        missing.append("topic")
        tips.append(
            "Please provide a topic or highlight for the post (e.g., 'Luxury Villa Sale', 'Market Trends')"
        )
    else:
        normalized["topic"] = topic

    # Optional: tone
    tone = payload.get("tone", "engaging").lower()
    valid_tones = ["engaging", "professional", "casual", "inspirational", "urgent"]
    if tone not in valid_tones:
        tone = "engaging"
    normalized["tone"] = tone

    # Optional: include_hashtags
    normalized["include_hashtags"] = payload.get("include_hashtags", True)

    # Optional: property_id
    if "property_id" in payload:
        normalized["property_id"] = payload["property_id"]

    valid = len(missing) == 0
    confidence = 1.0 if valid else 0.4

    return ValidationResult(
        valid=valid,
        missing_fields=missing,
        normalized_payload=normalized,
        tips=tips,
        confidence=confidence,
    )


# =============================================================================
# MAIN VALIDATION DISPATCHER
# =============================================================================


def validate_content_request(
    content_type: ContentType, payload: Dict[str, Any]
) -> ValidationResult:
    """
    Main validation dispatcher.
    Routes to appropriate validator based on content type.
    """
    validators = {
        ContentType.CMA_REPORT: validate_cma_report,
        ContentType.PITCH_DECK: validate_pitch_deck,
        ContentType.MARKET_REPORT: validate_market_report,
        ContentType.NEWSLETTER: validate_newsletter,
        ContentType.SOCIAL_POST: validate_social_post,
    }

    validator = validators.get(content_type)
    if not validator:
        return ValidationResult(
            valid=False,
            missing_fields=["content_type"],
            normalized_payload={},
            tips=[f"Unknown content type: {content_type}"],
            confidence=0.0,
        )

    return validator(payload)


# =============================================================================
# ENRICHMENT HELPERS
# =============================================================================


def enrich_from_context(
    payload: Dict[str, Any], recent_tasks: List[Dict[str, Any]], user_prompt: str
) -> Dict[str, Any]:
    """
    Attempt to enrich payload from context (recent tasks, user prompt).
    Used by orchestrator when validation fails.
    """
    enriched = payload.copy()

    # Extract location from prompt if missing
    if "location" not in enriched or not enriched["location"]:
        # Try to extract from recent tasks
        for task in recent_tasks:
            if task.get("metadata", {}).get("location"):
                enriched["location"] = task["metadata"]["location"]
                break

        # Try to extract from prompt
        if "location" not in enriched or not enriched["location"]:
            location = extract_location_from_text(user_prompt)
            if location:
                enriched["location"] = location

    # Extract property type from prompt if missing
    if "property_type" not in enriched or not enriched["property_type"]:
        prop_type = extract_property_type_from_text(user_prompt)
        if prop_type:
            enriched["property_type"] = prop_type

    # Extract numeric fields from prompt
    if "bedrooms" not in enriched:
        bedrooms = extract_number_from_text(user_prompt, "bedroom")
        if bedrooms:
            enriched["bedrooms"] = bedrooms

    if "bathrooms" not in enriched:
        bathrooms = extract_number_from_text(user_prompt, "bathroom")
        if bathrooms:
            enriched["bathrooms"] = bathrooms

    return enriched


def extract_location_from_text(text: str) -> Optional[str]:
    """Extract location mentions from text"""
    known_areas = [
        "Dubai Marina",
        "Downtown Dubai",
        "Jumeirah Beach Residence",
        "JBR",
        "Palm Jumeirah",
        "Business Bay",
        "Dubai Hills",
        "Arabian Ranches",
        "Emirates Hills",
        "DIFC",
        "Deira",
        "Bur Dubai",
        "Al Barsha",
    ]

    text_lower = text.lower()
    for area in known_areas:
        if area.lower() in text_lower:
            return area

    return None


def extract_property_type_from_text(text: str) -> Optional[str]:
    """Extract property type from text"""
    text_lower = text.lower()

    type_keywords = {
        "apartment": ["apartment", "flat", "unit"],
        "villa": ["villa", "house", "townhouse"],
        "commercial": ["commercial", "office", "retail"],
    }

    for prop_type, keywords in type_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return prop_type

    return None
