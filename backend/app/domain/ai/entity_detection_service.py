"""
Entity Detection Service for Phase 3: Advanced In-Chat Experience

This service provides NLP-based entity extraction from AI response messages,
specifically designed for real estate domain entities.
"""

import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Entity data class"""

    entity_type: str
    entity_value: str
    confidence_score: float
    context_source: str
    metadata: Dict[str, Any] = None


class EntityDetectionService:
    """Service for detecting entities in AI response messages"""

    def __init__(self):
        # Real estate domain-specific entity patterns
        self.entity_patterns = {
            "property": {
                "patterns": [
                    r"\b\d+\s+(?:bedroom|bed|BR)\b",
                    r"\b(?:apartment|villa|townhouse|penthouse|studio)\b",
                    r"\b(?:Dubai Marina|Palm Jumeirah|Downtown Dubai|JBR|DIFC)\b",
                    r"\b(?:AED|USD)\s*[\d,]+(?:\.\d{2})?\b",
                    r"\b\d+\s*(?:sq\s*ft|square\s*feet|m²)\b",
                ],
                "keywords": [
                    "property",
                    "listing",
                    "unit",
                    "floor",
                    "view",
                    "amenities",
                    "parking",
                    "balcony",
                    "garden",
                    "pool",
                    "gym",
                    "security",
                ],
            },
            "client": {
                "patterns": [
                    r"\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b",
                    r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # Simple name pattern
                    r"\b[\w\.-]+@[\w\.-]+\.\w+\b",  # Email pattern
                    r"\b\+?[\d\s\-\(\)]{10,}\b",  # Phone pattern
                ],
                "keywords": [
                    "client",
                    "buyer",
                    "seller",
                    "investor",
                    "tenant",
                    "landlord",
                    "preference",
                    "requirement",
                    "budget",
                    "timeline",
                ],
            },
            "location": {
                "patterns": [
                    r"\b(?:Dubai|Abu Dhabi|Sharjah|Ajman|Umm Al Quwain|Ras Al Khaimah|Fujairah)\b",
                    r"\b(?:Marina|Palm|Downtown|JBR|DIFC|Business Bay|Silicon Oasis)\b",
                    r"\b(?:Street|Road|Avenue|Boulevard|Lane|Drive)\b",
                ],
                "keywords": [
                    "location",
                    "area",
                    "neighborhood",
                    "district",
                    "zone",
                    "proximity",
                    "access",
                    "transportation",
                ],
            },
            "market_data": {
                "patterns": [
                    r"\b(?:price|value|valuation|market|trend|growth|decline)\b",
                    r"\b(?:ROI|return|yield|rental|capital|appreciation)\b",
                    r"\b(?:comparable|comp|similar|market\s*rate)\b",
                ],
                "keywords": [
                    "market",
                    "trend",
                    "analysis",
                    "comparison",
                    "valuation",
                    "investment",
                    "return",
                    "yield",
                    "growth",
                ],
            },
        }

        # Confidence scoring weights
        self.confidence_weights = {
            "pattern_match": 0.8,
            "keyword_match": 0.6,
            "context_relevance": 0.4,
            "entity_frequency": 0.2,
        }

    def detect_entities(self, message: str) -> List[Entity]:
        """
        Detect entities in a message

        Args:
            message: The message text to analyze

        Returns:
            List of detected entities with confidence scores
        """
        try:
            entities = []

            # Detect entities for each type
            for entity_type, config in self.entity_patterns.items():
                type_entities = self._detect_entity_type(message, entity_type, config)
                entities.extend(type_entities)

            # Remove duplicates and sort by confidence
            unique_entities = self._deduplicate_entities(entities)
            unique_entities.sort(key=lambda x: x.confidence_score, reverse=True)

            logger.info(f"Detected {len(unique_entities)} entities in message")
            return unique_entities

        except Exception as e:
            logger.error(f"Error detecting entities: {e}")
            return []

    def _detect_entity_type(
        self, message: str, entity_type: str, config: Dict
    ) -> List[Entity]:
        """Detect entities of a specific type"""
        entities = []
        message_lower = message.lower()

        # Pattern-based detection
        for pattern in config["patterns"]:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                entity_value = match.group()
                confidence = self._calculate_confidence(
                    message, entity_value, entity_type, config, "pattern"
                )

                entities.append(
                    Entity(
                        entity_type=entity_type,
                        entity_value=entity_value,
                        confidence_score=confidence,
                        context_source="pattern_match",
                        metadata={"pattern": pattern, "position": match.span()},
                    )
                )

        # Keyword-based detection
        for keyword in config["keywords"]:
            if keyword.lower() in message_lower:
                # Find the actual keyword occurrence
                keyword_matches = re.finditer(
                    rf"\b{re.escape(keyword)}\b", message, re.IGNORECASE
                )
                for match in keyword_matches:
                    confidence = self._calculate_confidence(
                        message, match.group(), entity_type, config, "keyword"
                    )

                    entities.append(
                        Entity(
                            entity_type=entity_type,
                            entity_value=match.group(),
                            confidence_score=confidence,
                            context_source="keyword_match",
                            metadata={"keyword": keyword, "position": match.span()},
                        )
                    )

        return entities

    def _calculate_confidence(
        self,
        message: str,
        entity_value: str,
        entity_type: str,
        config: Dict,
        detection_method: str,
    ) -> float:
        """Calculate confidence score for detected entity"""
        confidence = 0.0

        # Base confidence based on detection method
        if detection_method == "pattern":
            confidence += self.confidence_weights["pattern_match"]
        elif detection_method == "keyword":
            confidence += self.confidence_weights["keyword_match"]

        # Context relevance scoring
        context_relevance = self._calculate_context_relevance(
            message, entity_value, entity_type
        )
        confidence += context_relevance * self.confidence_weights["context_relevance"]

        # Entity frequency scoring
        frequency_score = self._calculate_frequency_score(message, entity_value)
        confidence += frequency_score * self.confidence_weights["entity_frequency"]

        # Normalize confidence to 0-1 range
        confidence = min(1.0, max(0.0, confidence))

        return round(confidence, 3)

    def _calculate_context_relevance(
        self, message: str, entity_value: str, entity_type: str
    ) -> float:
        """Calculate context relevance score"""
        # Simple context relevance based on surrounding words
        message_lower = message.lower()
        entity_lower = entity_value.lower()

        # Find entity position
        pos = message_lower.find(entity_lower)
        if pos == -1:
            return 0.0

        # Extract context window (50 characters before and after)
        start = max(0, pos - 50)
        end = min(len(message), pos + len(entity_value) + 50)
        context = message_lower[start:end]

        # Count relevant words in context
        relevant_words = {
            "property": [
                "property",
                "listing",
                "unit",
                "apartment",
                "villa",
                "price",
                "bedroom",
            ],
            "client": [
                "client",
                "buyer",
                "seller",
                "contact",
                "email",
                "phone",
                "preference",
            ],
            "location": ["location", "area", "neighborhood", "Dubai", "Marina", "Palm"],
            "market_data": [
                "market",
                "trend",
                "analysis",
                "comparison",
                "valuation",
                "investment",
            ],
        }

        relevant_count = 0
        for word in relevant_words.get(entity_type, []):
            if word in context:
                relevant_count += 1

        # Normalize to 0-1 range
        max_relevant = len(relevant_words.get(entity_type, []))
        return relevant_count / max_relevant if max_relevant > 0 else 0.0

    def _calculate_frequency_score(self, message: str, entity_value: str) -> float:
        """Calculate frequency score for entity"""
        # Count occurrences of entity in message
        count = message.lower().count(entity_value.lower())

        # Higher frequency = higher confidence (up to a point)
        if count == 1:
            return 0.5
        elif count == 2:
            return 0.7
        elif count >= 3:
            return 0.9
        else:
            return 0.0

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities, keeping the highest confidence ones"""
        unique_entities = {}

        for entity in entities:
            key = (entity.entity_type, entity.entity_value.lower())

            if (
                key not in unique_entities
                or entity.confidence_score > unique_entities[key].confidence_score
            ):
                unique_entities[key] = entity

        return list(unique_entities.values())

    def get_entity_context_mapping(self, entity: Entity) -> Dict[str, Any]:
        """Get context source mapping for entity"""
        mapping = {
            "property": {
                "api_endpoint": f"/properties/search?q={entity.entity_value}",
                "cache_key": f"property:{entity.entity_value}",
                "context_type": "property_details",
            },
            "client": {
                "api_endpoint": f"/clients/search?q={entity.entity_value}",
                "cache_key": f"client:{entity.entity_value}",
                "context_type": "client_info",
            },
            "location": {
                "api_endpoint": f"/market/context?location={entity.entity_value}",
                "cache_key": f"location:{entity.entity_value}",
                "context_type": "market_data",
            },
            "market_data": {
                "api_endpoint": f"/market/analysis?type={entity.entity_value}",
                "cache_key": f"market:{entity.entity_value}",
                "context_type": "market_analysis",
            },
        }

        return mapping.get(
            entity.entity_type,
            {"api_endpoint": None, "cache_key": None, "context_type": "unknown"},
        )


# Global instance
entity_detection_service = EntityDetectionService()
