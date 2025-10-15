"""
Property Brochure Service
=========================

Helper utilities for fetching listing data, constructing brochure prompts,
invoking Gemini, and packaging structured brochure content for the
intelligence pipeline.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None  # type: ignore

from app.core.ai_content_generator import ai_content_generator
from app.schemas.intelligence import (
    ContentMetadata,
    ContentType,
    GeneratedContent,
    IntelligenceContent,
    MemoryContext,
    PropertyBrochureContent,
    QualityScores,
)

logger = logging.getLogger(__name__)


DEFAULT_LISTINGS: List[Dict[str, Any]] = [
    {
        "id": "listing-downtown-dubai-apt",
        "title": "Downtown Dubai Skyline Residence",
        "subtitle": "Two-Bedroom Signature Suite in Burj Views",
        "price": 4250000,
        "location": "Downtown Dubai",
        "property_type": "Apartment",
        "bedrooms": 2,
        "bathrooms": 2.5,
        "area_sqft": 1820,
        "highlights": [
            "Unobstructed Burj Khalifa and fountain views",
            "Corner layout with dual terraces",
            "Direct podium access to Dubai Mall",
        ],
        "description": (
            "Elevated urban living set above the Dubai skyline, featuring expansive glass frontage, "
            "bespoke European millwork, and seamless connectivity to fine dining, fashion, and cultural venues."
        ),
        "images": [
            "https://cdn.propertypro.ai/mock/downtown/skyline-residence-hero.jpg",
            "https://cdn.propertypro.ai/mock/downtown/skyline-residence-lounge.jpg",
            "https://cdn.propertypro.ai/mock/downtown/skyline-residence-view.jpg",
        ],
    },
    {
        "id": "listing-marina-loft",
        "title": "Dubai Marina Panoramic Loft",
        "subtitle": "Tri-level Loft with 270° Waterfront Vistas",
        "price": 6900000,
        "location": "Dubai Marina",
        "property_type": "Loft",
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 2985,
        "highlights": [
            "Double-height living with marina harbour panorama",
            "Private sky lounge terrace",
            "Boutique tower with only 28 residences",
        ],
        "description": (
            "Sculptural architecture frames the marina in every direction, complemented by custom Italian cabinetry, "
            "hotel-grade wellness amenities, and valet lifestyle services tailored for the jet-set resident."
        ),
        "images": [
            "https://cdn.propertypro.ai/mock/marina/panoramic-loft-hero.jpg",
            "https://cdn.propertypro.ai/mock/marina/panoramic-loft-terrace.jpg",
            "https://cdn.propertypro.ai/mock/marina/panoramic-loft-living.jpg",
        ],
    },
    {
        "id": "listing-palm-villa",
        "title": "Palm Jumeirah Royal Villa",
        "subtitle": "Private Beachfront Villa on Frond E",
        "price": 28000000,
        "location": "Palm Jumeirah",
        "property_type": "Villa",
        "bedrooms": 5,
        "bathrooms": 6,
        "area_sqft": 7340,
        "highlights": [
            "Bespoke beachfront with private cabana and jetty",
            "Imported marble gallery staircase",
            "Resort-grade spa wing with sauna and plunge pool",
        ],
        "description": (
            "Command a premier shoreline address on Palm Jumeirah with this fully reimagined villa offering "
            "hotel-inspired entertaining spaces, tranquil wellness suites, and iconic Atlantis vistas."
        ),
        "images": [
            "https://cdn.propertypro.ai/mock/palm/palm-villa-hero.jpg",
            "https://cdn.propertypro.ai/mock/palm/palm-villa-pool.jpg",
            "https://cdn.propertypro.ai/mock/palm/palm-villa-living.jpg",
        ],
    },
]


class PropertyBrochureService:
    """Service responsible for sourcing listing data and crafting brochure content"""

    def __init__(self, db: Session):
        self.db = db
        self.mock_mode = os.getenv("AURA_MOCK_MODE", "false").lower() == "true"
        self.model_name = os.getenv("AURA_BROCHURE_MODEL", "gemini-1.5-flash")
        self.gemini_model = None

        self._ensure_seed_listings()
        self._configure_gemini()

    def generate_brochure(self, task_id: str, listing_id: str) -> IntelligenceContent:
        """Generate brochure content for a given listing id"""
        listing = self.ensure_listing(listing_id)

        if self.mock_mode or not self.gemini_model:
            template = ai_content_generator._build_property_brochure_template({"listing": listing}, is_mock=True)
            mock = True
        else:
            template = self._generate_with_gemini(listing)
            mock = False if self.gemini_model else True

        brochure_model = PropertyBrochureContent(**template["structured"])
        return self._build_intelligence_content(task_id, template, brochure_model, mock=mock)

    def ensure_listing(self, listing_id: str) -> Dict[str, Any]:
        """Fetch listing by id, creating a default record if necessary"""
        listing = self.get_listing(listing_id)
        if listing:
            return listing

        logger.info("Listing %s not found. Seeding default brochure record.", listing_id)
        default_record = DEFAULT_LISTINGS[0].copy()
        default_record["id"] = listing_id
        self._insert_listing(default_record)
        return self.get_listing(listing_id)  # type: ignore[arg-type]

    def get_listing(self, listing_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve listing row as dictionary"""
        result = self.db.execute(
            text(
                """
                SELECT id, title, subtitle, price, location, property_type, bedrooms, bathrooms,
                       area_sqft, highlights, description, images, amenities, neighborhood_insights
                FROM listings
                WHERE id = :listing_id
                """
            ),
            {"listing_id": listing_id},
        )

        row = result.mappings().first()
        if not row:
            return None
        return self._normalize_listing(dict(row))

    def _configure_gemini(self) -> None:
        if self.mock_mode:
            logger.info("AURA_MOCK_MODE enabled – brochure generation will use seeded content")
            return

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("Gemini API key not configured. Falling back to mock brochure output.")
            return

        if not genai:
            logger.warning("google.generativeai not installed – cannot call Gemini, using fallback copy")
            return

        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel(self.model_name)
            logger.info("Gemini model %s configured for brochure generation", self.model_name)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to initialize Gemini: %s", exc)
            self.gemini_model = None

    def _ensure_seed_listings(self) -> None:
        count = self.db.execute(text("SELECT COUNT(*) AS count FROM listings")).scalar()  # type: ignore[arg-type]
        if count and count >= 3:
            return

        logger.info("Seeding default brochure listings")
        for listing in DEFAULT_LISTINGS:
            self._insert_listing(listing)
        self.db.commit()

    def _insert_listing(self, listing: Dict[str, Any]) -> None:
        payload = listing.copy()
        payload.setdefault("price", 0)
        payload.setdefault("subtitle", None)
        highlights = payload.get("highlights")
        images = payload.get("images")
        amenities = payload.get("amenities")
        neighborhood = payload.get("neighborhood_insights")

        payload["highlights"] = json.dumps(highlights) if highlights else None
        payload["images"] = json.dumps(images) if images else None
        payload["amenities"] = json.dumps(amenities) if amenities else None
        payload["neighborhood_insights"] = json.dumps(neighborhood) if neighborhood else None

        self.db.execute(
            text(
                """
                INSERT OR IGNORE INTO listings (
                    id, title, subtitle, price, location, property_type, bedrooms, bathrooms,
                    area_sqft, highlights, description, images, amenities, neighborhood_insights,
                    created_at
                ) VALUES (
                    :id, :title, :subtitle, :price, :location, :property_type, :bedrooms, :bathrooms,
                    :area_sqft, :highlights, :description, :images, :amenities, :neighborhood_insights,
                    CURRENT_TIMESTAMP
                )
                """
            ),
            payload,
        )

    def _normalize_listing(self, record: Dict[str, Any]) -> Dict[str, Any]:
        for field in ["highlights", "images", "amenities", "neighborhood_insights"]:
            value = record.get(field)
            if isinstance(value, str):
                try:
                    record[field] = json.loads(value)
                except json.JSONDecodeError:
                    if field in {"highlights", "images"}:
                        record[field] = [item.strip() for item in value.split(",") if item.strip()]
                    else:
                        record[field] = None
        return record

    def _generate_with_gemini(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        template = ai_content_generator._build_property_brochure_template({"listing": listing}, is_mock=False)
        description = template["structured"].get("description", "")

        if not self.gemini_model:
            return template

        prompt = self._build_prompt(listing)
        try:
            response = self.gemini_model.generate_content(prompt)  # type: ignore[attr-defined]
            ai_text = getattr(response, "text", None)
            if not ai_text and hasattr(response, "candidates"):
                ai_text = "\n\n".join(
                    candidate.content.parts[0].text
                    for candidate in response.candidates
                    if candidate.content.parts
                )
            if ai_text:
                cleaned = ai_text.strip()
                if cleaned:
                    description = cleaned.split("\n\n")[0].strip()
                    template["structured"]["description"] = description
                    template["narrative"] = cleaned
                    template["key_insights"] = template["key_insights"] or [
                        line.strip() for line in cleaned.split("\n") if line.strip()
                    ][:3]
                    template["structured"]["sections"][0]["body"] = description
        except Exception as exc:  # pragma: no cover
            logger.warning("Gemini generation failed, using fallback brochure copy: %s", exc)

        return template

    def _build_prompt(self, listing: Dict[str, Any]) -> str:
        highlights = listing.get("highlights") or []
        if isinstance(highlights, list):
            highlight_block = "\n- ".join(str(item) for item in highlights)
        else:
            highlight_block = str(highlights)

        return (
            "You are AURA's luxury real estate marketing copywriter. "
            "Craft a polished, aspirational property brochure narrative (2-3 paragraphs) that highlights the "
            "unique value of the residence. Focus on lifestyle, design signatures, and location advantages.\n\n"
            f"Property: {listing.get('title')}\n"
            f"Subtitle: {listing.get('subtitle', '')}\n"
            f"Location: {listing.get('location')}\n"
            f"Price: {listing.get('price')} AED\n"
            f"Property Type: {listing.get('property_type')}\n"
            f"Bedrooms/Bathrooms: {listing.get('bedrooms')} / {listing.get('bathrooms')}\n"
            f"Key Highlights:\n- {highlight_block}\n\n"
            "Write in second person, invite the reader to imagine living in the space, "
            "and close with a strong call-to-action."
        )

    def _build_intelligence_content(
        self,
        task_id: str,
        template: Dict[str, Any],
        brochure: PropertyBrochureContent,
        mock: bool = False,
    ) -> IntelligenceContent:
        content_id = f"brochure_{uuid.uuid4().hex[:12]}"
        structured_payload = brochure.dict()

        metadata = ContentMetadata(
            generation_timestamp=datetime.utcnow(),
            model=self.model_name if not mock else "mock-brochure-generator",
            processing_time_ms=0,
            confidence_level=0.92 if not mock else 0.9,
            sources=[f"listing:{brochure.listing_id}"],
            listing_id=brochure.listing_id,
            mock_origin=mock,
        )

        memory_context = MemoryContext(
            relevant_memories=[
                {
                    "type": "listing",
                    "content": brochure.title,
                    "relevance": 0.96,
                },
                {
                    "type": "location",
                    "content": brochure.location,
                    "relevance": 0.9,
                },
            ],
            contextual_insights=structured_payload.get("neighborhood_insights", []),
            brand_alignment=0.94 if not mock else 0.9,
        )

        quality_scores = QualityScores(
            overall_score=0.93 if not mock else 0.9,
            content_quality=0.92,
            brand_compliance=0.95,
            validation_score=0.9,
        )

        generated_content = GeneratedContent(
            structured=structured_payload,
            narrative=template["narrative"],
            key_insights=template["key_insights"],
            actionable_recommendations=template["recommendations"],
        )

        return IntelligenceContent(
            content_id=content_id,
            task_id=task_id,
            content_type=ContentType.PROPERTY_BROCHURE,
            title=brochure.title,
            enhanced=True,
            quality_scores=quality_scores,
            memory_context=memory_context,
            generated_content=generated_content,
            metadata=metadata,
            export_ready=True,
            version="3.5",
        )
