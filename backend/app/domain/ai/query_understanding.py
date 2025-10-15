"""
Query Understanding and Analysis Module
======================================

This module provides advanced query understanding capabilities including:
- Intent Classification
- Entity Extraction
- Sentiment Analysis
- Urgency Detection
- Complexity Assessment
- Follow-up Detection
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from ai_enhancements import SentimentType


@dataclass
class QueryUnderstanding:
    """Advanced query understanding and analysis"""

    original_query: str
    intent: str
    entities: Dict[str, Any]
    sentiment: SentimentType
    urgency_level: int  # 1-5 scale
    complexity_level: int  # 1-5 scale
    requires_follow_up: bool
    suggested_actions: List[str]

    @classmethod
    def analyze(
        cls, query: str, conversation_history: List[Dict]
    ) -> "QueryUnderstanding":
        """Analyze a query for understanding"""
        query_lower = query.lower()

        # Intent classification
        intent = cls._classify_intent(query_lower)

        # Entity extraction
        entities = cls._extract_entities(query_lower)

        # Sentiment analysis
        sentiment = cls._analyze_sentiment(query_lower)

        # Urgency detection
        urgency_level = cls._detect_urgency(query_lower)

        # Complexity assessment
        complexity_level = cls._assess_complexity(query_lower)

        # Follow-up detection
        requires_follow_up = cls._detect_follow_up_needed(
            query_lower, conversation_history
        )

        # Suggested actions
        suggested_actions = cls._suggest_actions(intent, entities, sentiment)

        return cls(
            original_query=query,
            intent=intent,
            entities=entities,
            sentiment=sentiment,
            urgency_level=urgency_level,
            complexity_level=complexity_level,
            requires_follow_up=requires_follow_up,
            suggested_actions=suggested_actions,
        )

    @staticmethod
    def _classify_intent(query: str) -> str:
        """Classify the intent of the query"""
        intent_patterns = {
            "property_search": [
                r"\b(buy|rent|purchase|find|search|looking for|need)\b.*\b(property|house|apartment|condo|villa|home)\b",
                r"\b(show me|display|list)\b.*\b(properties|houses|apartments)\b",
                r"\b(bedroom|bathroom|price|budget|location|area)\b.*\b(property|apartment|villa)\b",
            ],
            "market_inquiry": [
                r"\b(market|trend|price|investment|rental|yield|forecast)\b",
                r"\b(how much|what is the price|market value)\b",
                r"\b(area|neighborhood|community)\b.*\b(market|trends|prices)\b",
            ],
            "investment_advice": [
                r"\b(investment|roi|return|profit|yield|capital appreciation)\b",
                r"\b(golden visa|residency|visa)\b.*\b(property|investment)\b",
                r"\b(foreign|international|expat)\b.*\b(invest|buy|purchase)\b",
            ],
            "legal_question": [
                r"\b(law|regulation|rera|escrow|legal|compliance)\b",
                r"\b(freehold|leasehold|ownership rights)\b",
                r"\b(dubai land department|dld|mortgage regulations)\b",
            ],
            "area_information": [
                r"\b(tell me about|describe|what is)\b.*\b(dubai marina|downtown|palm jumeirah)\b",
                r"\b(schools|hospitals|transport|metro|amenities)\b.*\b(area|neighborhood)\b",
                r"\b(what)\b.*\b(schools|hospitals|amenities)\b.*\b(available|in)\b",
            ],
            "transaction_help": [
                r"\b(how to buy|purchase process|buying process|transaction)\b",
                r"\b(legal requirements|documentation|contract|agreement)\b",
                r"\b(escrow|payment|financing|mortgage)\b",
            ],
            "developer_question": [
                r"\b(emaar|damac|nakheel|sobha|dubai properties|meraas)\b",
                r"\b(developer|builder|construction company)\b",
                r"\b(who built|who developed|which developer)\b",
            ],
        }

        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return intent

        return "general_inquiry"

    @staticmethod
    def _extract_entities(query: str) -> Dict[str, Any]:
        """Extract entities from the query"""
        entities = {
            "locations": [],
            "property_types": [],
            "price_range": None,
            "bedrooms": None,
            "bathrooms": None,
            "amenities": [],
            "developers": [],
        }

        # Extract locations
        dubai_areas = [
            "dubai marina",
            "downtown dubai",
            "palm jumeirah",
            "business bay",
            "jbr",
            "jumeirah",
            "dubai hills estate",
            "arabian ranches",
            "emirates hills",
            "springs",
            "meadows",
            "lakes",
            "motor city",
            "sports city",
            "international city",
            "silicon oasis",
            "academic city",
        ]
        for area in dubai_areas:
            if area in query:
                entities["locations"].append(area)

        # Extract property types
        property_types = [
            "apartment",
            "villa",
            "townhouse",
            "penthouse",
            "studio",
            "duplex",
        ]
        for prop_type in property_types:
            if prop_type in query:
                entities["property_types"].append(prop_type)

        # Extract price range
        price_patterns = [
            r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:aed|dollars?|dirhams?)",
            r"budget.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:aed|dollars?|dirhams?)",
            r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:aed|dollars?|dirhams?).*?budget",
        ]

        for pattern in price_patterns:
            price_match = re.search(pattern, query)
            if price_match:
                try:
                    entities["price_range"] = float(
                        price_match.group(1).replace(",", "")
                    )
                    break
                except ValueError:
                    continue

        # Extract bedrooms/bathrooms
        bedroom_match = re.search(r"(\d+)\s*bedroom", query)
        if bedroom_match:
            entities["bedrooms"] = int(bedroom_match.group(1))

        bathroom_match = re.search(r"(\d+(?:\.\d+)?)\s*bathroom", query)
        if bathroom_match:
            entities["bathrooms"] = float(bathroom_match.group(1))

        # Extract amenities
        amenities = [
            "pool",
            "gym",
            "parking",
            "balcony",
            "garden",
            "elevator",
            "security",
            "concierge",
            "maid",
            "school",
            "hospital",
            "metro",
        ]
        for amenity in amenities:
            if amenity in query:
                entities["amenities"].append(amenity)

        # Extract developers
        developers = [
            "emaar",
            "damac",
            "nakheel",
            "sobha",
            "dubai properties",
            "meraas",
            "azizi",
            "ellington",
            "mag",
            "select",
            "binghatti",
        ]
        for developer in developers:
            if developer in query:
                entities["developers"].append(developer)

        return entities

    @staticmethod
    def _analyze_sentiment(query: str) -> SentimentType:
        """Analyze the sentiment of the query"""
        positive_words = [
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "perfect",
            "love",
            "interested",
            "excited",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "disappointed",
            "frustrated",
            "angry",
            "worried",
        ]
        urgent_words = ["urgent", "asap", "immediately", "quick", "fast", "now", "soon"]
        confused_words = [
            "confused",
            "not sure",
            "unclear",
            "don't understand",
            "help",
            "what",
            "how",
        ]

        query_lower = query.lower()

        if any(word in query_lower for word in confused_words):
            return SentimentType.CONFUSED
        elif any(word in query_lower for word in urgent_words):
            return SentimentType.EXCITED
        elif any(word in query_lower for word in negative_words):
            return SentimentType.NEGATIVE
        elif any(word in query_lower for word in positive_words):
            return SentimentType.POSITIVE
        else:
            return SentimentType.NEUTRAL

    @staticmethod
    def _detect_urgency(query: str) -> int:
        """Detect urgency level (1-5)"""
        urgent_indicators = [
            ("urgent", 5),
            ("asap", 5),
            ("immediately", 5),
            ("now", 5),
            ("quick", 4),
            ("fast", 4),
            ("soon", 3),
            ("when", 2),
            ("timeline", 2),
            ("deadline", 4),
            ("expire", 4),
        ]

        query_lower = query.lower()
        max_urgency = 1

        for indicator, level in urgent_indicators:
            if indicator in query_lower:
                max_urgency = max(max_urgency, level)

        return max_urgency

    @staticmethod
    def _assess_complexity(query: str) -> int:
        """Assess query complexity (1-5)"""
        complexity_indicators = [
            ("investment", 4),
            ("legal", 4),
            ("regulations", 4),
            ("rera", 4),
            ("process", 3),
            ("requirements", 3),
            ("documentation", 3),
            ("contract", 3),
            ("market", 2),
            ("trends", 2),
            ("prices", 2),
            ("analysis", 3),
            ("golden visa", 4),
            ("residency", 4),
            ("mortgage", 3),
            ("financing", 3),
        ]

        query_lower = query.lower()
        complexity = 1

        for indicator, level in complexity_indicators:
            if indicator in query_lower:
                complexity = max(complexity, level)

        return complexity

    @staticmethod
    def _detect_follow_up_needed(query: str, history: List[Dict]) -> bool:
        """Detect if follow-up questions are needed"""
        follow_up_indicators = [
            "maybe",
            "not sure",
            "don't know",
            "what about",
            "how about",
            "could you",
            "would you",
            "can you tell me more",
            "what else",
            "and",
            "also",
            "additionally",
            "furthermore",
            "moreover",
        ]

        query_lower = query.lower()
        return any(indicator in query_lower for indicator in follow_up_indicators)

    @staticmethod
    def _suggest_actions(
        intent: str, entities: Dict, sentiment: SentimentType
    ) -> List[str]:
        """Suggest actions based on query analysis"""
        actions = []

        if intent == "property_search":
            actions.extend(
                ["search_properties", "show_similar_properties", "schedule_viewing"]
            )
            if entities.get("price_range"):
                actions.append("show_payment_plans")
            if entities.get("locations"):
                actions.append("show_area_analysis")
        elif intent == "market_inquiry":
            actions.extend(
                ["show_market_data", "provide_market_analysis", "show_trends"]
            )
            if entities.get("locations"):
                actions.append("show_area_market_report")
        elif intent == "investment_advice":
            actions.extend(
                ["calculate_roi", "show_investment_properties", "explain_golden_visa"]
            )
            if "golden visa" in str(entities).lower():
                actions.append("show_visa_requirements")
        elif intent == "legal_question":
            actions.extend(
                ["explain_regulations", "connect_legal_expert", "show_requirements"]
            )
            if "rera" in str(entities).lower():
                actions.append("show_rera_guidelines")
        elif intent == "area_information":
            actions.extend(["show_area_details", "show_amenities", "show_transport"])
            if entities.get("locations"):
                actions.append("show_area_properties")
        elif intent == "transaction_help":
            actions.extend(["explain_process", "show_documentation", "connect_agent"])
            if "mortgage" in str(entities).lower():
                actions.append("show_financing_options")
        elif intent == "developer_question":
            actions.extend(
                [
                    "show_developer_info",
                    "show_developer_properties",
                    "show_quality_analysis",
                ]
            )

        # Sentiment-based actions
        if sentiment == SentimentType.CONFUSED:
            actions.append("provide_simplified_explanation")
        elif sentiment == SentimentType.EXCITED:
            actions.append("expedite_process")
        elif sentiment == SentimentType.FRUSTRATED:
            actions.append("provide_detailed_help")

        return actions
