"""
Advanced AI Enhancements for Dubai Real Estate RAG Chat System
============================================================

This module provides advanced AI capabilities including:
- Conversation Memory Management
- Context Window Optimization
- Response Quality Enhancement
- Multi-modal Processing
- Dynamic Prompt Engineering
- Sentiment Analysis
- Query Understanding
- Response Personalization
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from enum import Enum
import hashlib
from collections import deque
import numpy as np
from sqlalchemy import create_engine, text
import google.generativeai as genai

logger = logging.getLogger(__name__)


class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    STRUCTURED_DATA = "structured_data"


class SentimentType(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFUSED = "confused"


@dataclass
class ConversationMemory:
    """Manages conversation context and memory"""

    session_id: str
    conversation_id: Optional[int] = None
    messages: deque = field(default_factory=lambda: deque(maxlen=50))
    context_window: deque = field(default_factory=lambda: deque(maxlen=20))
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_summary: str = ""
    last_updated: datetime = field(default_factory=datetime.now)

    def add_message(
        self,
        role: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict] = None,
    ):
        """Add a message to the conversation memory"""
        message = {
            "role": role,
            "content": content,
            "type": message_type.value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.messages.append(message)
        self.last_updated = datetime.now()

        # Update context window for recent messages
        if len(self.context_window) >= 20:
            self.context_window.popleft()
        self.context_window.append(message)

    def get_recent_context(self, num_messages: int = 10) -> List[Dict]:
        """Get recent conversation context"""
        return list(self.context_window)[-num_messages:]

    def get_user_preferences(self) -> Dict[str, Any]:
        """Extract user preferences from conversation history"""
        preferences = {
            "budget_range": None,
            "preferred_locations": [],
            "property_types": [],
            "bedrooms": None,
            "bathrooms": None,
            "amenities": [],
            "investment_goals": [],
            "timeline": None,
        }

        # Analyze conversation for preferences
        for message in self.messages:
            if message["role"] == "user":
                content = message["content"].lower()

                # Extract budget information
                budget_patterns = [
                    r"budget.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:aed|dollars?|dirhams?)",
                    r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:aed|dollars?|dirhams?).*?budget",
                    r"looking.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:aed|dollars?|dirhams?)",
                    r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:aed|dollars?|dirhams?).*?range",
                ]

                for pattern in budget_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        try:
                            budget = float(matches[0].replace(",", ""))
                            if not preferences["budget_range"]:
                                preferences["budget_range"] = [
                                    budget * 0.8,
                                    budget * 1.2,
                                ]
                            break
                        except ValueError:
                            continue

                # Extract location preferences
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
                    if (
                        area in content
                        and area not in preferences["preferred_locations"]
                    ):
                        preferences["preferred_locations"].append(area)

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
                    if (
                        prop_type in content
                        and prop_type not in preferences["property_types"]
                    ):
                        preferences["property_types"].append(prop_type)

                # Extract bedroom/bathroom preferences
                bedroom_match = re.search(r"(\d+)\s*bedroom", content)
                if bedroom_match:
                    preferences["bedrooms"] = int(bedroom_match.group(1))

                bathroom_match = re.search(r"(\d+(?:\.\d+)?)\s*bathroom", content)
                if bathroom_match:
                    preferences["bathrooms"] = float(bathroom_match.group(1))

        return preferences
