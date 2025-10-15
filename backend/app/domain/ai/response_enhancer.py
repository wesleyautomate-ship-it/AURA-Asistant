"""
Response Enhancement Module
==========================

This module enhances AI responses with:
- Personalization based on user preferences
- Sentiment-appropriate language
- Urgency indicators
- Follow-up suggestions
- Conversation continuity
"""

from typing import Dict, Any, List

try:
    from ai_enhancements import SentimentType
except ImportError:

    class SentimentType:
        CONFUSED = "confused"
        EXCITED = "excited"
        NEUTRAL = "neutral"
        FRUSTRATED = "frustrated"


try:
    from query_understanding import QueryUnderstanding
except ImportError:

    class QueryUnderstanding:
        def __init__(self):
            self.sentiment = SentimentType.NEUTRAL
            self.urgency_level = 1
            self.requires_follow_up = False


class ResponseEnhancer:
    """Enhances AI responses for better quality and personalization"""

    def __init__(self, model):
        self.model = model
        self.response_templates = self._load_response_templates()

    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different scenarios"""
        return {
            "property_search": [
                "Based on your requirements for {property_type} in {location}, I found several excellent options. Here are the top properties that match your criteria:",
                "I've identified some great {property_type} properties in {location} that fit your budget and requirements. Let me show you the best options:",
                "Perfect! I found {count} {property_type} properties in {location} that match your needs. Here are the highlights:",
            ],
            "market_inquiry": [
                "The Dubai real estate market in {location} is currently showing {trend}. Here's what you need to know:",
                "Great question! The {location} market is experiencing {trend}. Let me break down the current situation:",
                "The market trends in {location} are quite interesting. Here's the latest analysis:",
            ],
            "investment_advice": [
                "Excellent investment opportunity! The {location} area offers strong ROI potential. Here's my analysis:",
                "Smart thinking! {location} is one of Dubai's best investment areas. Let me show you why:",
                "For investment purposes, {location} is highly recommended. Here's the investment breakdown:",
            ],
            "confused_user": [
                "I understand this can be confusing! Let me break this down in simple terms:",
                "No worries! Let me explain this step by step in a way that's easy to understand:",
                "I'll make this crystal clear for you. Here's what you need to know:",
            ],
            "excited_user": [
                "I'm excited to help you with this! Here's everything you need to know:",
                "Fantastic! This is a great opportunity. Let me get you all the details:",
                "Excellent choice! I'm thrilled to assist you with this. Here's the complete information:",
            ],
        }

    def enhance_response(
        self,
        base_response: str,
        query_understanding: QueryUnderstanding,
        user_preferences: Dict[str, Any],
        conversation_history: List[Dict],
    ) -> str:
        """Enhance the base response with personalization and context"""

        enhanced_response = base_response

        # Add personalization based on user preferences
        if user_preferences.get("preferred_locations"):
            enhanced_response = self._add_location_personalization(
                enhanced_response, user_preferences
            )

        # Add sentiment-appropriate language
        enhanced_response = self._add_sentiment_appropriate_language(
            enhanced_response, query_understanding.sentiment
        )

        # Add urgency indicators
        if query_understanding.urgency_level >= 4:
            enhanced_response = self._add_urgency_indicators(enhanced_response)

        # Add follow-up suggestions
        if query_understanding.requires_follow_up:
            enhanced_response = self._add_follow_up_suggestions(
                enhanced_response, query_understanding
            )

        # Add conversation continuity
        enhanced_response = self._add_conversation_continuity(
            enhanced_response, conversation_history
        )

        # Add Dubai-specific context
        enhanced_response = self._add_dubai_context(
            enhanced_response, query_understanding
        )

        return enhanced_response

    def _add_location_personalization(
        self, response: str, preferences: Dict[str, Any]
    ) -> str:
        """Add location-based personalization"""
        if preferences.get("preferred_locations"):
            locations = ", ".join(preferences["preferred_locations"][:3])
            location_lower = locations.lower()

            if "dubai marina" in location_lower:
                response += f"\n\n💡 **Pro Tip**: {locations} is one of Dubai's most sought-after areas with excellent rental yields (6-8%) and strong capital appreciation potential."
            elif "downtown" in location_lower:
                response += f"\n\n💡 **Pro Tip**: {locations} offers premium lifestyle with world-class amenities and strong investment returns. Properties here typically appreciate 8-12% annually."
            elif "palm jumeirah" in location_lower:
                response += f"\n\n💡 **Pro Tip**: {locations} is Dubai's iconic waterfront destination with luxury properties and high-end amenities. Perfect for premium investments."
            elif "business bay" in location_lower:
                response += f"\n\n💡 **Pro Tip**: {locations} is Dubai's emerging business district with excellent connectivity and growing property values."
            elif "dubai hills estate" in location_lower:
                response += f"\n\n💡 **Pro Tip**: {locations} offers family-friendly living with excellent schools, parks, and golf courses. Great for long-term investment."

        return response

    def _add_sentiment_appropriate_language(
        self, response: str, sentiment: SentimentType
    ) -> str:
        """Add sentiment-appropriate language to the response"""
        if sentiment == SentimentType.CONFUSED:
            response = (
                "I understand this might seem complex, but don't worry! Let me break it down for you: "
                + response
            )
        elif sentiment == SentimentType.EXCITED:
            response = "I'm excited to help you with this! " + response
        elif sentiment == SentimentType.FRUSTRATED:
            response = (
                "I completely understand your concern. Let me help clarify this for you: "
                + response
            )
        elif sentiment == SentimentType.NEGATIVE:
            response = (
                "I understand this might be concerning. Let me provide you with clear, helpful information: "
                + response
            )
        elif sentiment == SentimentType.POSITIVE:
            response = "I'm glad you're interested! " + response

        return response

    def _add_urgency_indicators(self, response: str) -> str:
        """Add urgency indicators to the response"""
        response += "\n\n⚡ **Quick Action**: I can help you expedite this process. Would you like me to connect you with our priority service team or schedule an immediate consultation?"
        return response

    def _add_follow_up_suggestions(
        self, response: str, query_understanding: QueryUnderstanding
    ) -> str:
        """Add follow-up suggestions based on query analysis"""
        follow_ups = {
            "property_search": [
                "Would you like me to show you similar properties in other areas?",
                "Should I schedule a virtual tour for any of these properties?",
                "Would you like to know more about the payment plans available?",
                "Should I provide a detailed area analysis for the properties you're interested in?",
            ],
            "market_inquiry": [
                "Would you like me to show you historical price trends?",
                "Should I provide a detailed market analysis report?",
                "Would you like to know about upcoming developments in this area?",
                "Should I show you investment opportunities in this market?",
            ],
            "investment_advice": [
                "Would you like me to calculate the potential ROI for specific properties?",
                "Should I explain the Golden Visa requirements in detail?",
                "Would you like to know about financing options for investors?",
                "Should I show you the best investment areas in Dubai?",
            ],
            "legal_question": [
                "Would you like me to explain the legal process in detail?",
                "Should I connect you with our legal experts?",
                "Would you like to know about the required documentation?",
                "Should I provide a step-by-step legal guide?",
            ],
            "area_information": [
                "Would you like me to show you properties in this area?",
                "Should I provide a detailed area guide?",
                "Would you like to know about schools and amenities?",
                "Should I show you transport and connectivity options?",
            ],
            "transaction_help": [
                "Would you like me to explain the complete buying process?",
                "Should I show you the required documents?",
                "Would you like to know about financing options?",
                "Should I connect you with our transaction specialists?",
            ],
        }

        intent_follow_ups = follow_ups.get(query_understanding.intent, [])
        if intent_follow_ups:
            response += f"\n\n🤔 **Next Steps**: {intent_follow_ups[0]}"

        return response

    def _add_conversation_continuity(self, response: str, history: List[Dict]) -> str:
        """Add conversation continuity elements"""
        if len(history) > 1:
            # Check if this is a follow-up to a previous property search
            recent_messages = history[-3:]
            property_mentions = []
            budget_mentions = []

            for msg in recent_messages:
                if msg["role"] == "user":
                    content_lower = msg["content"].lower()
                    if any(
                        word in content_lower
                        for word in ["property", "apartment", "villa", "house"]
                    ):
                        property_mentions.append(msg["content"])
                    if any(
                        word in content_lower
                        for word in ["budget", "price", "aed", "dirham"]
                    ):
                        budget_mentions.append(msg["content"])

            if property_mentions:
                response += "\n\n📋 **Previous Discussion**: I remember you were interested in properties. Let me make sure this information builds on our previous conversation."

            if budget_mentions:
                response += "\n\n💰 **Budget Context**: Based on our previous discussion about your budget, I've tailored these recommendations accordingly."

        return response

    def _add_dubai_context(
        self, response: str, query_understanding: QueryUnderstanding
    ) -> str:
        """Add Dubai-specific context and insights"""
        dubai_insights = {
            "property_search": [
                "\n\n🏗️ **Dubai Market Insight**: Dubai's real estate market is currently experiencing strong growth with increasing demand for quality properties.",
                "\n\n🌆 **Dubai Advantage**: Dubai offers tax-free returns, freehold ownership for foreigners, and world-class infrastructure.",
                "\n\n📈 **Market Trend**: Dubai property prices have shown consistent appreciation, making it an attractive investment destination.",
            ],
            "investment_advice": [
                "\n\n💎 **Dubai Investment Edge**: Dubai offers unique advantages including Golden Visa eligibility, tax-free returns, and high rental yields.",
                "\n\n🌍 **Global Appeal**: Dubai attracts international investors due to its strategic location, business-friendly environment, and luxury lifestyle.",
                "\n\n📊 **ROI Potential**: Dubai properties typically offer 6-10% rental yields and 8-15% annual appreciation potential.",
            ],
            "market_inquiry": [
                "\n\n📊 **Dubai Market Overview**: Dubai's real estate market is driven by strong economic fundamentals, government initiatives, and international demand.",
                "\n\n🏛️ **Government Support**: Dubai's government actively supports the real estate sector through various initiatives and regulations.",
                "\n\n🌐 **Global Hub**: Dubai's position as a global business and tourism hub continues to drive property demand.",
            ],
        }

        intent_insights = dubai_insights.get(query_understanding.intent, [])
        if intent_insights:
            import random

            response += random.choice(intent_insights)

        return response

    def add_property_recommendations(
        self, response: str, user_preferences: Dict[str, Any]
    ) -> str:
        """Add personalized property recommendations"""
        if not user_preferences.get("preferred_locations"):
            return response

        recommendations = []

        for location in user_preferences["preferred_locations"][:2]:
            if "dubai marina" in location.lower():
                recommendations.append(
                    "🏢 **Dubai Marina**: Luxury waterfront apartments with stunning views, excellent amenities, and strong rental demand."
                )
            elif "downtown" in location.lower():
                recommendations.append(
                    "🏙️ **Downtown Dubai**: Premium properties near Burj Khalifa with world-class shopping, dining, and entertainment."
                )
            elif "palm jumeirah" in location.lower():
                recommendations.append(
                    "🌴 **Palm Jumeirah**: Iconic waterfront villas and apartments with private beaches and luxury amenities."
                )
            elif "business bay" in location.lower():
                recommendations.append(
                    "🏢 **Business Bay**: Modern business district with contemporary apartments and excellent connectivity."
                )

        if recommendations:
            response += "\n\n🏠 **Personalized Recommendations**:\n" + "\n".join(
                recommendations
            )

        return response

    def add_market_insights(
        self, response: str, query_understanding: QueryUnderstanding
    ) -> str:
        """Add relevant market insights"""
        insights = {
            "property_search": [
                "📈 **Current Market**: Dubai's property market is experiencing strong demand with increasing prices across all segments.",
                "🏗️ **New Developments**: Several major projects are launching, offering excellent investment opportunities.",
                "🌍 **International Demand**: Strong interest from international buyers, especially from Europe and Asia.",
            ],
            "investment_advice": [
                "💰 **Investment Climate**: Dubai offers excellent investment opportunities with high rental yields and capital appreciation.",
                "🏛️ **Government Support**: Various government initiatives support real estate investment and foreign ownership.",
                "📊 **Market Performance**: Dubai properties have shown consistent growth and strong returns over the past decade.",
            ],
        }

        intent_insights = insights.get(query_understanding.intent, [])
        if intent_insights:
            import random

            response += f"\n\n{random.choice(intent_insights)}"

        return response
