"""
AI Content Generator
===================

Handles both mock and real AI content generation.
Supports AURA_MOCK_MODE for development and testing.
"""

import os
import uuid
import json
import logging
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, List, Optional
from datetime import datetime, timedelta
import google.generativeai as genai

from app.schemas.intelligence import (
    ContentType,
    QualityScores,
    GeneratedContent,
    ContentMetadata,
    MemoryContext,
    IntelligenceContent,
)

logger = logging.getLogger(__name__)


def format_aed(amount: Any, *, include_symbol: bool = True) -> str:
    """
    Format a numeric or string value into an AED currency string.

    Keeps behaviour tolerant of values already containing the AED prefix
    while normalising output for UI/tests.
    """
    symbol = "AED " if include_symbol else ""

    if amount is None:
        return f"{symbol}0"

    candidate = amount
    if isinstance(candidate, str):
        stripped = candidate.strip()
        if not stripped:
            return f"{symbol}0"
        if stripped.upper().startswith("AED"):
            stripped = stripped[3:].strip()
        stripped = stripped.replace(",", "")
        candidate = stripped or "0"

    try:
        numeric = Decimal(str(candidate))
    except (InvalidOperation, ValueError, TypeError):
        return f"{symbol}{candidate}"

    if numeric < 0:
        numeric = abs(numeric)

    quantized = numeric.quantize(Decimal("1.00"))
    if quantized == quantized.to_integral():
        formatted_value = f"{quantized.to_integral():,}"
    else:
        formatted_value = f"{quantized:,.2f}"

    return f"{symbol}{formatted_value}"


def extract_property_query(user_input: str) -> str:
    """
    Pull a property identifier from free-form user input.

    The helper is intentionally forgiving and keeps the original casing so the
    result can be used in downstream lookups.
    """
    if not user_input:
        return ""

    text = user_input.strip()
    lowered = text.lower()

    key_phrases = (
        "brochure for ",
        "listing for ",
        "flyer for ",
        "property for ",
    )

    for phrase in key_phrases:
        idx = lowered.find(phrase)
        if idx != -1:
            start = idx + len(phrase)
            return text[start:].strip(" ,.!?:;\"'")

    fallback_markers = ("for ", "about ", "regarding ")
    for marker in fallback_markers:
        idx = lowered.find(marker)
        if idx != -1:
            start = idx + len(marker)
            return text[start:].strip(" ,.!?:;\"'")

    return text


def _coerce_decimal(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        return float(Decimal(str(value)))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _dict_get(source: Any, key: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def serialize_property_for_brochure(property_obj: Any) -> Dict[str, Any]:
    """
    Convert a property ORM object (or dict) into a brochure-ready payload.

    Keeps field names stable for tests and downstream consumers without
    mutating the source object.
    """
    if property_obj is None:
        return {}

    data = property_obj if isinstance(property_obj, dict) else {}
    title = _dict_get(property_obj, "title") or data.get("title") or "Property"
    description = (
        _dict_get(property_obj, "description") or data.get("description") or ""
    )
    property_type = _dict_get(property_obj, "property_type") or data.get(
        "property_type"
    )
    location = _dict_get(property_obj, "location") or data.get("location")

    price = (
        _dict_get(property_obj, "price_aed")
        or _dict_get(property_obj, "price")
        or data.get("price_aed")
        or data.get("price")
    )
    price_numeric = _coerce_decimal(price)

    specs = {
        "price_aed": price_numeric,
        "bedrooms": _dict_get(property_obj, "bedrooms"),
        "bathrooms": _dict_get(property_obj, "bathrooms"),
        "area_sqft": _coerce_decimal(_dict_get(property_obj, "area_sqft")),
        "parking_spaces": _dict_get(property_obj, "parking_spaces"),
        "view_type": _dict_get(property_obj, "view_type"),
        "furnishing_status": _dict_get(property_obj, "furnishing_status"),
    }

    features = _dict_get(property_obj, "features")
    if hasattr(property_obj, "features_dict"):
        features = property_obj.features_dict
    features = features or {}

    market_data = _dict_get(property_obj, "market_data")
    if hasattr(property_obj, "market_data_dict"):
        market_data = property_obj.market_data_dict
    market_data = market_data or {}

    neighborhood = _dict_get(property_obj, "neighborhood_data")
    if hasattr(property_obj, "neighborhood_data_dict"):
        neighborhood = property_obj.neighborhood_data_dict
    neighborhood = neighborhood or {}

    images = _dict_get(property_obj, "property_images") or []
    images = _as_list(images)

    agent = _dict_get(property_obj, "agent")
    agent_first = _dict_get(agent, "first_name", "")
    agent_last = _dict_get(agent, "last_name", "")
    name_candidates: Iterable[Optional[str]] = (
        f"{agent_first} {agent_last}".strip(),
        _dict_get(agent, "full_name"),
        _dict_get(agent, "name"),
    )
    agent_name = next((name for name in name_candidates if name), "Assigned Agent")

    contact = {
        "agent_id": _dict_get(agent, "id") or _dict_get(property_obj, "agent_id"),
        "agent_name": agent_name,
        "email": _dict_get(agent, "email"),
        "phone_number": _dict_get(agent, "phone_number"),
        "office": _dict_get(agent, "office"),
    }

    return {
        "id": _dict_get(property_obj, "id"),
        "title": title,
        "description": description,
        "property_type": property_type,
        "location": location,
        "specs": specs,
        "features": features,
        "market_data": market_data,
        "neighborhood_data": neighborhood,
        "property_images": images,
        "contact": contact,
    }


class AIContentGenerator:
    """
    AI Content Generator with Gemini integration.

    When AURA_MOCK_MODE=true:
    - Returns predefined mock content for testing
    - Fast response times for UI development
    - Consistent test data

    When AURA_MOCK_MODE=false:
    - Uses Gemini Pro for real content generation
    - Production quality output
    - Advanced quality scoring
    """

    def __init__(self):
        self.mock_mode = os.getenv("AURA_MOCK_MODE", "false").lower() == "true"
        self.gemini_model = None
        self.setup_gemini()

        logger.info(f"AIContentGenerator initialized: mock_mode={self.mock_mode}")
    
    def setup_gemini(self):
        """Initialize Gemini API if not in mock mode"""
        if self.mock_mode:
            return

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("No Gemini API key found - defaulting to mock mode")
            self.mock_mode = True
            return

        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("✅ Gemini Pro model configured successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.mock_mode = True

    def _get_content_prompt(self, content_type: ContentType, user_input: str, context: Dict[str, Any]) -> str:
        """Get the appropriate prompt template based on content type"""
        
        if content_type == ContentType.CMA_REPORT:
            return f"""Generate a comprehensive Comparative Market Analysis (CMA) based on:

Input: {user_input}

Structure your response as a professional CMA report with:
1. Executive Summary
2. Market Overview for the area
3. Comparable Properties Analysis (3-5 properties)
4. Two Pricing Strategies:
   - Aggressive Pricing Strategy
   - Standard Pricing Strategy
5. Market Trends and Insights
6. Investment Potential Analysis
7. Recommendations

Format as a professional report suitable for client presentation.
Include specific data points, market statistics, and actionable insights.
"""

        elif content_type == ContentType.PROPERTY_BROCHURE:
            property_data = context.get("property_data", {})
            return f"""Create a compelling property brochure for:

Property: {property_data.get('title', 'Luxury Property')}
Location: {property_data.get('location', 'Dubai')}
Price: {property_data.get('price', 'Premium')}
Details: {property_data.get('beds', '')} bed, {property_data.get('baths', '')} bath
Features: {', '.join(property_data.get('features', []))}

Generate:
1. Property Description (150-200 words) - compelling and engaging
2. Key Selling Points - bullet points highlighting unique features
3. Neighborhood Overview - area benefits and lifestyle
4. Investment Highlights - market potential and value
5. Call-to-Action - clear next steps for potential buyers

Style: Professional, luxurious, emphasizing unique value
Target: High-net-worth buyers and investors
Tone: Sophisticated but warm, highlighting exclusivity and lifestyle
"""

        elif content_type == ContentType.SOCIAL_POST:
            return f"""Create engaging social media content based on:

Input: {user_input}

Generate:
1. Instagram/Facebook Post (2-3 paragraphs)
2. Professional Hashtags (8-10 relevant tags)
3. Call-to-Action
4. Engagement Hooks
5. Story Points (3-4 key highlights)

Style: Professional yet conversational
Tone: Engaging, informative, encouraging action
Focus: Property features, lifestyle benefits, and market opportunity
"""

        elif content_type == ContentType.PITCH_DECK:
            return f"""Create an investment pitch deck outline based on:

Input: {user_input}

Structure:
1. Executive Summary
2. Market Opportunity
3. Property Analysis
4. Investment Highlights
5. Financial Projections
6. Risk Analysis
7. Exit Strategy
8. Call to Action

Style: Professional, data-driven, investor-focused
Include: Key metrics, market data, and actionable insights
Format: Slide-based presentation structure
"""

        else:  # ContentType.GENERAL
            return f"""Generate professional real estate content based on:

Input: {user_input}

Create:
1. Main Content - clear and engaging
2. Key Points - important highlights
3. Market Context - relevant market information
4. Recommendations - next steps or actions
5. Supporting Data - statistics or metrics

Style: Professional and informative
Tone: Clear, confident, market-aware
"""

    def _get_content_temperature(self, content_type: ContentType) -> float:
        """Get appropriate temperature setting for content type"""
        # More creative for marketing, precise for analysis
        if content_type in [ContentType.SOCIAL_POST, ContentType.PROPERTY_BROCHURE]:
            return 0.7  # More creative
        elif content_type in [ContentType.CMA_REPORT, ContentType.PITCH_DECK]:
            return 0.2  # More precise
        return 0.4  # Balanced default

    async def generate_content(
        self,
        user_input: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        context: Optional[Dict[str, Any]] = None,
        quality_requirements: Optional[Dict[str, Any]] = None,
        **extra_kwargs: Any,
    ) -> IntelligenceContent:
        """
        Generate content based on user input.

        Args:
            user_input: User's content request
            content_type: Type of content to generate
            context: Additional context data
            quality_requirements: Quality thresholds
            extra_kwargs: Compatibility kwargs (user_id, prompt, timeout_seconds, etc.)

        Returns:
            IntelligenceContent with generated data
        """
        prompt = extra_kwargs.pop("prompt", None)
        fallback_text = extra_kwargs.pop("text", None)
        user_input = user_input or prompt or fallback_text or ""
        if not content_type:
            content_type = self._detect_content_type(user_input)
        if not content_type:
            content_type = ContentType.GENERAL

        # Ignore legacy kwargs such as user_id/timeout_seconds without raising
        extra_kwargs.pop("user_id", None)
        extra_kwargs.pop("timeout_seconds", None)
        extra_kwargs.pop("request_id", None)
        extra_kwargs.pop("agent_id", None)

        start_time = datetime.utcnow()

        if self.mock_mode:
            content = await self._generate_mock_content(
                user_input, content_type, context
            )
        else:
            content = await self._generate_real_content(
                user_input, content_type, context, quality_requirements
            )

        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        content.metadata.processing_time_ms = processing_time

        logger.info(
            f"Generated content: {content.content_id} ({content_type.value}) in {processing_time}ms"
        )
        return content

    async def _generate_mock_content(
        self,
        user_input: str,
        content_type: ContentType,
        context: Optional[Dict[str, Any]] = None,
    ) -> IntelligenceContent:
        """Generate mock content for testing"""

        content_id = f"mock_{str(uuid.uuid4())[:8]}"

        # Mock content templates
        mock_templates = {
            ContentType.CMA_REPORT: {
                "title": "Comparative Market Analysis - Dubai Marina",
                "structured": {
                    "property_address": "Dubai Marina Luxury Towers",
                    "estimated_value": 2350000,
                    "confidence_range": {"min": 2200000, "max": 2500000},
                    "comparable_properties": [
                        {
                            "address": "Marina Heights Tower",
                            "sold_price": 2280000,
                            "sold_date": "2024-09-15",
                            "size_sqft": 1450,
                            "price_per_sqft": 1572,
                        },
                        {
                            "address": "Ocean View Residences",
                            "sold_price": 2420000,
                            "sold_date": "2024-08-22",
                            "size_sqft": 1520,
                            "price_per_sqft": 1592,
                        },
                    ],
                    "market_trends": {
                        "6_month_change": "+8.5%",
                        "12_month_change": "+15.2%",
                        "days_on_market_avg": 28,
                        "inventory_levels": "Low",
                    },
                },
                "narrative": "Based on comprehensive market analysis of Dubai Marina properties, the subject property shows strong positioning in the luxury segment. Recent comparable sales indicate robust demand with properties selling 12% above list price on average.",
                "key_insights": [
                    "Dubai Marina luxury market showing sustained growth (+15.2% YoY)",
                    "Properties in this tier selling 28% faster than market average",
                    "Waterfront premium commanding 18-25% price advantage",
                    "Q4 2024 expected to maintain momentum with limited new inventory",
                ],
                "recommendations": [
                    "Price aggressively at AED 2.35M to capture current market momentum",
                    "Highlight marina views and luxury amenities in marketing",
                    "Target high-net-worth investors and end-users from GCC region",
                    "Launch marketing campaign within 7-10 days to maximize exposure",
                ],
            },
            ContentType.SOCIAL_POST: {
                "title": "Luxury Marina Living Social Campaign",
                "structured": {
                    "platform": "instagram",
                    "post_type": "carousel",
                    "hashtags": [
                        "#DubaiMarina",
                        "#LuxuryRealEstate",
                        "#DubaiProperty",
                        "#MarinLiving",
                        "#InvestInDubai",
                        "#PropertyPro",
                    ],
                    "call_to_action": "DM for private viewing",
                    "best_posting_times": ["7:00 AM", "12:00 PM", "6:00 PM"],
                },
                "narrative": "🌊 JUST LISTED | Marina Perfection Awaits\n\n✨ Wake up to stunning marina views every morning in this exceptional 2BR luxury apartment. Premium finishes meet waterfront elegance in Dubai's most desirable neighborhood.\n\n🏢 Key Features:\n• Panoramic marina & sea views\n• Premium building amenities\n• Prime location walkable to dining & entertainment\n• Excellent rental yield potential\n\n💎 Perfect for discerning investors and luxury lifestyle seekers.\n\nSerious inquiries only. DM for exclusive private viewing.\n\n#DubaiMarina #LuxuryRealEstate #PropertyInvestment",
                "key_insights": [
                    "Marina content performs 40% better during evening hours",
                    "Luxury property posts see 2.3x engagement with lifestyle imagery",
                    "Video content generates 65% more leads than static posts",
                    "Stories with property tours drive highest conversion rates",
                ],
                "recommendations": [
                    "Post during peak engagement times (6-8 PM GST)",
                    "Include professional photography and video walkthroughs",
                    "Create Instagram Stories with behind-the-scenes content",
                    "Use location tags and relevant luxury lifestyle hashtags",
                ],
            },
            ContentType.PITCH_DECK: {
                "title": "Dubai Marina Investment Opportunity",
                "structured": {
                    "slide_count": 12,
                    "presentation_structure": [
                        "Executive Summary",
                        "Market Overview",
                        "Property Highlights",
                        "Financial Projections",
                        "Investment Thesis",
                        "Risk Analysis",
                        "Next Steps",
                    ],
                    "key_metrics": {
                        "projected_roi": "12.5%",
                        "rental_yield": "6.8%",
                        "capital_appreciation": "8-12% annually",
                        "payback_period": "7.2 years",
                    },
                },
                "narrative": "Comprehensive investment presentation showcasing a premium Dubai Marina opportunity. The deck outlines market fundamentals, property-specific advantages, and detailed financial modeling for sophisticated investors.",
                "key_insights": [
                    "Dubai Marina remains top-performing luxury segment with 15% annual growth",
                    "Limited supply pipeline ensures sustained value appreciation",
                    "High rental demand from expatriate executives and short-term visitors",
                    "Strategic location offers lifestyle and investment benefits",
                ],
                "recommendations": [
                    "Present to qualified investors with minimum AED 2M portfolio",
                    "Emphasize diversification benefits of Dubai real estate",
                    "Include comparative analysis with other global markets",
                    "Provide detailed post-purchase support and management options",
                ],
            },
        }

        # Get template or use general template
        if content_type == ContentType.PROPERTY_BROCHURE:
            template = self._build_property_brochure_template(context, is_mock=True)
        else:
            template = mock_templates.get(
                content_type, mock_templates[ContentType.CMA_REPORT]
            )

        # Create mock intelligence content
        return IntelligenceContent(
            content_id=content_id,
            task_id=f"task_{str(uuid.uuid4())[:8]}",
            content_type=content_type,
            title=template["title"],
            enhanced=True,
            quality_scores=QualityScores(
                overall_score=0.92,
                content_quality=0.89,
                brand_compliance=0.94,
                validation_score=0.91,
            ),
            memory_context=MemoryContext(
                relevant_memories=[
                    {
                        "type": "market_data",
                        "content": "Dubai Marina luxury segment trending +15.2% YoY",
                        "relevance": 0.95,
                    },
                    {
                        "type": "client_preference",
                        "content": "High-net-worth clients prefer waterfront properties",
                        "relevance": 0.87,
                    },
                ],
                contextual_insights=[
                    "Marina properties outperforming broader Dubai market",
                    "Limited new supply driving premium pricing",
                    "Strong rental demand from corporate relocations",
                ],
                brand_alignment=0.94,
            ),
            generated_content=GeneratedContent(
                structured=template["structured"],
                narrative=template["narrative"],
                key_insights=template["key_insights"],
                actionable_recommendations=template["recommendations"],
            ),
            metadata=ContentMetadata(
                generation_timestamp=datetime.utcnow(),
                model="mock-ai-v3.4",
                processing_time_ms=0,  # Will be set by caller
                confidence_level=0.91,
                sources=["mock-data", "template-engine"],
                mock_origin=True,
            ),
            export_ready=True,
            version="3.4-mock",
        )

    async def _generate_real_content(
        self,
        user_input: str,
        content_type: ContentType,
        context: Optional[Dict[str, Any]] = None,
        quality_requirements: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate real content using Gemini"""

        # Get appropriate prompt template
        prompt = self._get_content_prompt(content_type, user_input, context or {})

        # Generate content with Gemini
        generation_config = {
            "temperature": self._get_content_temperature(content_type),
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config=generation_config,
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            )

            # Parse Gemini response into structured format
            content_parts = response.text.split('\n\n')
            title = content_parts[0].strip() if content_parts else "Generated Content"

            structured_data = {
                "content_type": content_type.value,
                "main_content": response.text,
                "sections": [part.strip() for part in content_parts if part.strip()],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "model": "gemini-1.5-pro",
                    "temperature": generation_config["temperature"],
                }
            }

            key_insights = []
            recommendations = []
            for part in content_parts:
                if "recommendation" in part.lower():
                    recommendations.extend([r.strip() for r in part.split('\n') if r.strip() and r.strip().startswith('-')])
                elif "insight" in part.lower() or "highlight" in part.lower():
                    key_insights.extend([i.strip() for i in part.split('\n') if i.strip() and i.strip().startswith('-')])

            return {
                "title": title,
                "structured": structured_data,
                "narrative": response.text,
                "key_insights": key_insights[:5],  # Top 5 insights
                "recommendations": recommendations[:3],  # Top 3 recommendations
            }

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            # Fallback to mock content if Gemini fails
            logger.info("Falling back to mock content generation")
            return await self._generate_mock_content(user_input, content_type, context)

        return IntelligenceContent(
            content_id=content_id,
            task_id=f"task_{str(uuid.uuid4())[:8]}",
            content_type=detected_type,
            title=structured_data["title"],
            enhanced=True,
            quality_scores=QualityScores(
                overall_score=0.87,
                content_quality=0.84,
                brand_compliance=0.89,
                validation_score=0.86,
            ),
            memory_context=MemoryContext(
                relevant_memories=[],
                contextual_insights=["AI-generated content based on user input"],
                brand_alignment=0.89,
            ),
            generated_content=GeneratedContent(
                structured=structured_data["structured"],
                narrative=structured_data["narrative"],
                key_insights=structured_data["key_insights"],
                actionable_recommendations=structured_data["recommendations"],
            ),
            metadata=ContentMetadata(
                generation_timestamp=datetime.utcnow(),
                model=f"{self.llm_provider}-gpt-4",
                processing_time_ms=0,  # Will be set by caller
                confidence_level=0.86,
                sources=["ai-model", "real-time-data"],
                mock_origin=False,
            ),
            export_ready=True,
            version="3.4-real",
        )

    def _detect_content_type(self, user_input: str) -> ContentType:
        """Detect content type from user input"""
        input_lower = user_input.lower()

        if any(
            term in input_lower
            for term in [
                "brochure",
                "listing brochure",
                "property brochure",
                "marketing brochure",
                "flyer",
                "sell sheet",
                "one pager",
            ]
        ):
            return ContentType.PROPERTY_BROCHURE
        if any(
            term in input_lower
            for term in ["cma", "comparative market", "market analysis", "valuation"]
        ):
            return ContentType.CMA_REPORT
        if any(
            term in input_lower
            for term in ["social", "post", "instagram", "facebook", "twitter"]
        ):
            return ContentType.SOCIAL_POST
        if any(
            term in input_lower
            for term in ["pitch", "presentation", "deck", "investor"]
        ):
            return ContentType.PITCH_DECK
        if any(
            term in input_lower
            for term in ["market report", "market trend", "market overview"]
        ):
            return ContentType.MARKET_REPORT
        return ContentType.GENERAL

    async def _generate_cma_content(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate CMA-specific content"""
        return {
            "title": "AI-Generated Comparative Market Analysis",
            "structured": {
                "property_analysis": f"Analysis based on: {user_input[:100]}...",
                "market_data": "Real-time market data integration",
                "comparable_properties": [],
            },
            "narrative": f"Comprehensive market analysis generated based on your request: {user_input}",
            "key_insights": ["AI-powered market insights", "Real-time data analysis"],
            "recommendations": [
                "Strategic pricing recommendations",
                "Market timing suggestions",
            ],
        }

    async def _generate_social_content(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate social media content"""
        return {
            "title": "AI-Generated Social Media Content",
            "structured": {
                "platform_optimized": True,
                "engagement_focused": True,
                "hashtag_research": ["#RealEstate", "#Dubai", "#Property"],
            },
            "narrative": f"Engaging social media content: {user_input}",
            "key_insights": [
                "Optimized for engagement",
                "Platform-specific formatting",
            ],
            "recommendations": ["Post timing optimization", "Engagement strategies"],
        }

    async def _generate_pitch_content(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate pitch deck content"""
        return {
            "title": "AI-Generated Investment Pitch",
            "structured": {
                "executive_summary": f"Investment opportunity based on: {user_input}",
                "financial_modeling": "AI-powered financial projections",
                "market_positioning": "Strategic market analysis",
            },
            "narrative": f"Professional pitch deck content: {user_input}",
            "key_insights": [
                "Investment thesis",
                "Market opportunity",
                "Risk assessment",
            ],
            "recommendations": ["Investor targeting", "Presentation strategy"],
        }

    def _build_property_brochure_template(
        self, context: Optional[Dict[str, Any]], is_mock: bool = False
    ) -> Dict[str, Any]:
        """Build a structured brochure payload for mock or real generation"""
        ctx = context or {}
        listing = {}
        if isinstance(ctx, dict):
            listing_candidate = (
                ctx.get("listing") if isinstance(ctx.get("listing"), dict) else None
            )
            if listing_candidate:
                listing = listing_candidate
            elif all(k in ctx for k in ("title", "location")):
                listing = ctx
        title = listing.get("title") or ctx.get("title") or "Luxury Property Showcase"
        price_value = (
            listing.get("price") or listing.get("price_aed") or ctx.get("price")
        )
        formatted_price = self._format_price(price_value)
        location = listing.get("location") or ctx.get("location") or "Dubai, UAE"
        property_type = listing.get("property_type") or ctx.get("property_type")
        bedrooms = listing.get("bedrooms") or ctx.get("bedrooms")
        bathrooms = listing.get("bathrooms") or ctx.get("bathrooms")
        area_sqft = listing.get("area_sqft") or ctx.get("area_sqft")
        highlights = (
            listing.get("highlights")
            or ctx.get("highlights")
            or [
                "Iconic skyline and waterfront views",
                "Designer interiors with premium European finishes",
                "Resort-style amenities with pool, fitness and concierge services",
            ]
        )
        if isinstance(highlights, str):
            highlights = [h.strip() for h in highlights.split(",") if h.strip()]
        description = (
            listing.get("description")
            or ctx.get("description")
            or (
                "Experience elevated living in this beautifully curated residence featuring open-plan living spaces, panoramic glazing and access to Dubai's most coveted amenities."
            )
        )
        sections = listing.get("sections") or ctx.get("sections")
        if not sections:
            sections = [
                {
                    "label": "Signature Highlights",
                    "body": description,
                    "bullets": highlights[:3],
                },
                {
                    "label": "Lifestyle Overview",
                    "body": "Residents enjoy seamless indoor-outdoor living, access to private club facilities, hotel-inspired services and unbeatable proximity to Dubai Marina, JBR and Sheikh Zayed Road.",
                    "bullets": [
                        "Minutes to Dubai Marina promenade and Bluewaters",
                        "Concierge, valet and residents' lounge",
                        "Dedicated wellness deck with infinity pool and spa suites",
                    ],
                },
            ]
        neighborhood_insights = (
            listing.get("neighborhood_insights")
            or ctx.get("neighborhood_insights")
            or [
                "Moments from Dubai Marina promenade and luxury dining",
                "Easy access to Sheikh Zayed Road and Dubai Metro",
                "Surrounded by five-star resorts, retail and entertainment",
            ]
        )
        amenities = listing.get("amenities") or ctx.get("amenities")
        if not isinstance(amenities, dict):
            amenities = {
                "Interior": [
                    "Floor-to-ceiling glazing",
                    "Chef's kitchen with integrated appliances",
                    "Marble-clad bathrooms",
                ],
                "Building": [
                    "Grand double-height lobby",
                    "24/7 concierge and security",
                    "Dedicated resident lounge",
                ],
                "Community": [
                    "Waterfront promenade",
                    "Fine dining and boutique retail",
                    "Moments to beaches and yacht clubs",
                ],
            }
        images = listing.get("images") or ctx.get("images") or []
        if isinstance(images, str):
            images = [img.strip() for img in images.split(",") if img.strip()]
        if not images:
            images = [
                "https://cdn.propertypro.ai/mock/listings/skyline-suite-hero.jpg",
                "https://cdn.propertypro.ai/mock/listings/skyline-suite-lounge.jpg",
                "https://cdn.propertypro.ai/mock/listings/skyline-suite-amenities.jpg",
            ]
        structured = {
            "listing_id": listing.get("id")
            or ctx.get("listing_id")
            or "mock-listing-001",
            "title": title,
            "subtitle": listing.get("subtitle")
            or ctx.get("subtitle")
            or "Skyline Signature Collection",
            "price": formatted_price,
            "location": location,
            "property_type": property_type,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "area_sqft": area_sqft,
            "highlights": highlights,
            "description": description,
            "sections": sections,
            "neighborhood_insights": neighborhood_insights,
            "amenities": amenities,
            "call_to_action": listing.get("call_to_action")
            or ctx.get("call_to_action")
            or "Book a private tour with our luxury specialists today.",
            "images": images,
        }
        narrative = description
        key_insights = (
            highlights[:3]
            if highlights
            else [
                "Architecturally significant residence in the heart of Dubai",
                "Turn-key interiors with hotel-grade amenities",
                "Ideal for luxury buyers seeking panoramic views",
            ]
        )
        recommendations = [
            "Schedule a private viewing to experience the property in person.",
            "Share the brochure with qualified buyers and relocation partners.",
            "Feature the property in upcoming digital and print campaigns.",
        ]
        return {
            "title": title,
            "structured": structured,
            "narrative": narrative,
            "key_insights": key_insights,
            "recommendations": recommendations,
        }

    def _format_price(self, value: Any) -> str:
        """Format numeric price values to AED string"""
        return format_aed(value)

    async def _generate_general_content(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate general content"""
        return {
            "title": "AI-Generated Content",
            "structured": {
                "content_type": "general",
                "user_request": user_input,
                "ai_interpretation": f"Processed request: {user_input[:100]}...",
            },
            "narrative": f"AI-generated content based on your request: {user_input}",
            "key_insights": ["Content tailored to request", "AI-powered generation"],
            "recommendations": [
                "Content optimization suggestions",
                "Usage recommendations",
            ],
        }


# Singleton instance
ai_content_generator = AIContentGenerator()
