#!/usr/bin/env python3
"""
Improved RAG Service for Dubai Real Estate
Addresses core issues: conversational tone, data presentation, information architecture, and generic content
"""

import os
import re
import time
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from sqlalchemy import create_engine, text
import logging
from dataclasses import dataclass
from enum import Enum

# Reelly service removed

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    PROPERTY_SEARCH = "property_search"
    MARKET_INFO = "market_info"
    POLICY_QUESTION = "policy_question"
    AGENT_SUPPORT = "agent_support"
    INVESTMENT_QUESTION = "investment_question"
    REGULATORY_QUESTION = "regulatory_question"
    NEIGHBORHOOD_QUESTION = "neighborhood_question"
    DEVELOPER_QUESTION = "developer_question"
    # Report Generation Intents
    REPORT_GENERATION = "report_generation"
    MARKET_REPORT = "market_report"
    CMA_REPORT = "cma_report"
    LISTING_PRESENTATION = "listing_presentation"
    TERMS_CONDITIONS = "terms_conditions"
    # New Action Intents for Phase 3
    UPDATE_LEAD = "update_lead"
    LOG_INTERACTION = "log_interaction"
    SCHEDULE_FOLLOW_UP = "schedule_follow_up"
    GENERAL = "general"


def get_system_prompt(
    user_role: str, intent: QueryIntent, retrieved_context: str, user_name: str = "User"
):
    """
    Generates a dynamic system prompt based on user role, intent, and retrieved context.
    """

    # Base Persona and Core Directives
    system_prompt = f"""
You are "Dubai Realty AI," an expert-level real estate intelligence assistant for the Dubai property market. Your primary function is to synthesize and present information retrieved from our comprehensive local databases (8,000+ properties, market data, transactions, policies) to provide data-driven, accurate, and actionable insights.

## CORE DIRECTIVES:
1.  **Prioritize Local Database**: Our local database contains 8,000+ properties, 50,000+ transactions, market data, policies, and comprehensive real estate information. This is your primary and most reliable source of information.
2.  **Data-Driven and Specific**: Always use specific figures, names, and statistics from the retrieved context. Instead of "high rental yields," state "rental yields between 5-8% in Dubai Marina for a 1-bedroom apartment."
3.  **No Conversational Fluff**: For all substantive queries, immediately address the user's question. Avoid generic greetings or filler phrases, following the specific rules outlined in the 'Conversational Engagement' section below.
4.  **Handle Insufficient Data**: If the retrieved context does not contain the answer, state that clearly. For example, "I do not have specific data on that property in our database at the moment." Do not attempt to guess.
5.  **Structured and Professional Formatting**: Utilize Markdown (headers, bold keywords, bullet points, and tables) to create a clear, professional, and easy-to-read response.
6.  **Use Local Data Sources**: When presenting data, clearly indicate that this information comes from our comprehensive local database with 8,000+ properties and extensive market data.
7.  **Enhanced Context Understanding**: Analyze the user's query deeply and provide comprehensive, multi-faceted responses that address both explicit and implicit needs.
8.  **Proactive Insights**: Offer additional relevant information that the user might not have asked for but would find valuable.

## CONVERSATIONAL ENGAGEMENT
- **Initial Interaction**: On the very first message of a new conversation, you may use a brief, professional greeting, such as "Hello {user_name}."
- **Responding to Greetings**: If the user's entire message is a simple greeting (e.g., "Hi," "Hello there"), respond politely and invite a query (e.g., "Hello. How can I assist you with the Dubai real estate market today?"). For these interactions, you do not need to use the full structured response format.
- **Responding to Thanks**: If the user's message is solely an expression of gratitude (e.g., "Thank you," "Great, thanks"), respond concisely (e.g., "You're welcome. Is there anything else I can help with?").
- **Default Behavior**: For ANY other query that contains a request for information, you must revert to the default 'No Fluff' behavior. Omit any greeting and proceed directly to the "Executive Summary."

---

## USER and INTENT ANALYSIS:
-   **User Role**: {user_role.upper()}
-   **Query Intent**: {intent.name}

---

## [RETRIEVED CONTEXT - Your Primary Source of Truth]
This information has been sourced directly from our internal databases (PostgreSQL, ChromaDB) to answer the user's query.

{retrieved_context}

---

## ENHANCED RESPONSE STRUCTURE

### **1. Executive Summary**
(Provide a 2-3 sentence direct answer to the user's core question with key insights.)

### **2. Key Insights & Data Points**
(Use bullet points to highlight the most critical data from the retrieved context. Each point must be a specific, quantifiable fact.)
-   **Data Point 1**: ...
-   **Data Point 2**: ...
-   **Data Point 3**: ...

### **3. Detailed Analysis & Market Context**
(Elaborate on the key insights. Explain the "why" behind the data, referencing current market conditions, trends, or regulatory factors mentioned in the context. This section should be tailored to the user's role.)
{get_role_specific_guidance(user_role, intent)}

### **4. Actionable Recommendations**
(Provide specific, actionable steps the user should consider next. These should be logical conclusions derived *only* from the provided context.)

### **5. Proactive Insights**
(Offer 2-3 additional insights or suggestions that the user might not have explicitly asked for but would find valuable based on their query and role.)

### **6. Next Steps**
(Suggest 2-3 clear, concise actions the user can take, such as "Request a detailed property comparison" or "Ask for financing options for properties in Business Bay.")

## SPECIAL INSTRUCTIONS FOR PROPERTY SEARCH:
If the user is searching for specific properties (QueryIntent.PROPERTY_SEARCH), focus on listing the actual properties found in the database with their key details like price, location, bedrooms, and features. Present the properties clearly and concisely rather than providing market analysis.

**FOR PROPERTY SEARCH QUERIES ONLY**: Instead of the standard structured format above, directly list the properties found in the database. Use this format:

### **Available Properties**

**Property 1: [Property Name]**
- **Location:** [Location]
- **Price:** [Price]
- **Bedrooms:** [Number]
- **Bathrooms:** [Number]
- **Size:** [Size] sq ft
- **Type:** [Property Type]
- **Description:** [Brief description]

**Property 2: [Property Name]**
- **Location:** [Location]
- **Price:** [Price]
- **Bedrooms:** [Number]
- **Bathrooms:** [Number]
- **Size:** [Size] sq ft
- **Type:** [Property Type]
- **Description:** [Brief description]

[Continue for all properties found...]

## RESPONSE QUALITY ENHANCEMENTS:
- **Be Comprehensive**: Address all aspects of the user's query, including implicit needs
- **Provide Context**: Explain market conditions, trends, and factors affecting decisions
- **Offer Alternatives**: Suggest related options or areas the user might consider
- **Include Timing**: Mention market timing considerations when relevant
- **Highlight Opportunities**: Point out unique advantages or opportunities
- **Address Concerns**: Proactively address potential concerns or risks
- **Use Visual Elements**: Employ emojis, bold text, and structured formatting for clarity
"""
    return system_prompt


def get_role_specific_guidance(user_role: str, intent: QueryIntent):
    """
    Provides role- and intent-specific instructions for the Detailed Analysis section.
    """
    if user_role == "client":
        return """
        - **For the Client**: Focus on what the data means for their property search or investment. Explain pricing, compare neighborhood amenities, and clarify investment benefits like the Golden Visa or rental yields. If discussing properties, mention developers and unique features.
        """
    elif user_role == "agent":
        return """
        - **For the Agent**: Frame the analysis to provide a competitive edge. Highlight market trends, compare pricing with competing areas, and identify key selling points. Provide data that helps in client negotiations, property valuation, or lead generation strategies.
        """
    elif user_role == "admin":
        return """
        - **For the Admin**: Analyze the data from a business intelligence perspective. Summarize system performance, data quality, or user engagement metrics. Highlight trends that could inform business strategy or system improvements.
        """
    return ""


@dataclass
class QueryAnalysis:
    intent: QueryIntent
    entities: Dict[str, Any]
    parameters: Dict[str, Any]
    confidence: float


@dataclass
class ContextItem:
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any]


class EnhancedRAGService:
    def __init__(self):
        self.engine = create_engine(os.getenv("DATABASE_URL"))

        # Enhanced ChromaDB initialization with retry logic
        self.chroma_client = self._initialize_chroma_client()

        # Reelly service removed

        # Initialize intent patterns
        self.intent_patterns = {
            QueryIntent.PROPERTY_SEARCH: [
                r"\b(looking for|searching for|find|need)\b.*\b(apartment|villa|house|property|home)\b",
                r"\b(budget|price|cost)\b.*\b(\d+)\b.*\b(million|thousand|k|m)\b",
                r"\b(bedroom|bed)\b.*\b(\d+)\b",
                r"\b(bathroom|bath)\b.*\b(\d+)\b",
                r"\b(dubai marina|downtown|palm jumeirah|business bay)\b.*\b(property|apartment|villa)\b",
            ],
            QueryIntent.MARKET_INFO: [
                r"\b(market|trend|price|appreciation|rental yield|investment)\b",
                r"\b(how is|what is the|tell me about)\b.*\b(market|trend)\b",
                r"\b(price|cost)\b.*\b(trend|change|increase|decrease)\b",
            ],
            QueryIntent.REPORT_GENERATION: [
                r"\b(create|generate|make|build)\b.*\b(report|analysis|presentation)\b",
                r"\b(can you|please|would you)\b.*\b(create|generate|make)\b.*\b(report|analysis)\b",
                r"\b(market report|cma|comparative market analysis|listing presentation)\b",
                r"\b(terms|conditions|agreement)\b.*\b(generate|create|draft)\b",
            ],
            QueryIntent.MARKET_REPORT: [
                r"\b(market report|market analysis|market study)\b",
                r"\b(create|generate|make)\b.*\b(market report)\b",
                r"\b(area|neighborhood|location)\b.*\b(market|trend|analysis)\b",
            ],
            QueryIntent.CMA_REPORT: [
                r"\b(cma|comparative market analysis|property valuation)\b",
                r"\b(create|generate|make)\b.*\b(cma|comparative)\b",
                r"\b(property value|valuation|price estimate)\b",
            ],
            QueryIntent.LISTING_PRESENTATION: [
                r"\b(listing presentation|property brochure|property presentation)\b",
                r"\b(create|generate|make)\b.*\b(presentation|brochure)\b",
                r"\b(property marketing|listing materials)\b",
            ],
            QueryIntent.TERMS_CONDITIONS: [
                r"\b(terms|conditions|agreement|contract)\b",
                r"\b(create|generate|draft)\b.*\b(terms|conditions|agreement)\b",
                r"\b(legal|contractual|deal terms)\b",
            ],
            QueryIntent.INVESTMENT_QUESTION: [
                r"\b(investment|roi|return|yield|profit)\b",
                r"\b(rental|rent|tenant)\b",
                r"\b(buy|sell|hold)\b.*\b(property|investment)\b",
            ],
            QueryIntent.REGULATORY_QUESTION: [
                r"\b(law|regulation|rera|escrow|legal|compliance)\b",
                r"\b(golden visa|visa requirements|residency visa)\b",
                r"\b(freehold|leasehold|ownership rights)\b",
                r"\b(dubai land department|dld|mortgage regulations)\b",
            ],
            QueryIntent.NEIGHBORHOOD_QUESTION: [
                r"\b(dubai marina|downtown|palm jumeirah|business bay|jbr|jumeirah|dubai hills|arabian ranches|emirates hills)\b.*\b(area|neighborhood|community|amenities)\b",
                r"\b(tell me about|describe|what is)\b.*\b(dubai marina|downtown|palm jumeirah|business bay)\b",
                r"\b(schools|hospitals|transport|metro|amenities)\b.*\b(area|neighborhood)\b",
            ],
            QueryIntent.DEVELOPER_QUESTION: [
                r"\b(emaar|damac|nakheel|sobha|dubai properties|meraas)\b",
                r"\b(developer|builder|construction company)\b",
                r"\b(who built|who developed|which developer)\b",
            ],
            QueryIntent.POLICY_QUESTION: [
                r"\b(policy|procedure|how to|what is|process|requirement)\b",
                r"\b(commission|fee|cost|charge|payment)\b",
                r"\b(contract|agreement|terms|conditions)\b",
            ],
            QueryIntent.AGENT_SUPPORT: [
                r"\b(deal|close|negotiate|client|commission|strategy)\b",
                r"\b(sales|objection|technique|approach|method)\b",
                r"\b(how to handle|deal with|manage)\b.*\b(client|situation)\b",
            ],
            # New Action Intents for Phase 3
            QueryIntent.UPDATE_LEAD: [
                r"\b(update|change|set)\b.*\b(lead|client|status)\b",
                r"\b(status to)\b",
                r"\b(mark|move)\b.*\b(lead|client)\b.*\b(to|as)\b",
            ],
            QueryIntent.LOG_INTERACTION: [
                r"\b(log|note|add a note|just finished|feedback)\b",
                r"\b(viewing with|call with|meeting with)\b",
                r"\b(record|document)\b.*\b(interaction|conversation)\b",
            ],
            QueryIntent.SCHEDULE_FOLLOW_UP: [
                r"\b(schedule|remind me|set a reminder|follow up)\b",
                r"\b(call|meeting|email)\b.*\b(tomorrow|monday|next week|at \d+[ap]m)\b",
                r"\b(book|arrange)\b.*\b(appointment|meeting)\b",
            ],
        }

        # Entity extraction patterns
        self.entity_patterns = {
            "budget": [
                r"under\s+(\d+)\s*(?:k|thousand|million|m)",
                r"less\s+than\s+(\d+)\s*(?:k|thousand|million|m)",
                r"below\s+(\d+)\s*(?:k|thousand|million|m)",
                r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|thousand|million|m)?",
                r"(\d+)\s*(?:k|thousand|million|m)\s*(?:dollars?|aed)?",
                r"budget.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"price.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            ],
            "location": [
                r"\b(dubai marina|downtown|palm jumeirah|business bay|jbr|jumeirah|marina)\b",
                r"\b(area|neighborhood|location)\b.*?\b(\w+(?:\s+\w+)*)\b",
                r"in\s+(\w+(?:\s+\w+)*)",
                r"(\w+(?:\s+\w+)*)\s+area",
            ],
            "property_type": [
                r"\b(apartment|condo|villa|house|townhouse|penthouse|studio)\b",
                r"\b(residential|commercial|office|retail)\b",
            ],
            "bedrooms": [r"(\d+)\s*bedroom", r"(\d+)\s*br", r"(\d+)\s*bed"],
            "bathrooms": [r"(\d+(?:\.\d+)?)\s*bathroom", r"(\d+(?:\.\d+)?)\s*bath"],
            # Enhanced Entity Extraction patterns for Phase 3
            "lead_name": [
                r"\b(with|for|client|lead)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
                r"\b(update|change)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b.*\b(status|lead)\b",
            ],
            "new_status": [
                r'\b(status to)\s+[\'"]?(\w+)[\'"]?\b',
                r'\b(mark|move)\b.*\b(to|as)\s+[\'"]?(\w+)[\'"]?\b',
                r'\b(set|change)\b.*\b(status)\b.*\b(to)\s+[\'"]?(\w+)[\'"]?\b',
            ],
            "task_datetime": [
                r"\b(tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week)\b(?:\s+at\s+(\d{1,2}(?::\d{2})?\s*[ap]m))?",
                r"\b(at)\s+(\d{1,2}(?::\d{2})?\s*[ap]m)\b",
                r"\b(on)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            ],
            "interaction_notes": [
                r"\b(note is|feedback was|said that|felt that)\s+(.+)",
                r"\b(call|meeting|viewing)\b.*\b(went|was)\s+(.+)",
                r"\b(client|lead)\b.*\b(mentioned|said|expressed)\s+(.+)",
            ],
        }

    def _initialize_chroma_client(self, max_retries=5, retry_delay=2):
        """Initialize ChromaDB client with retry logic"""
        for attempt in range(max_retries):
            try:
                client = chromadb.HttpClient(
                    host=os.getenv("CHROMA_HOST", "localhost"),
                    port=int(os.getenv("CHROMA_PORT", "8000")),
                )
                # Test connection
                client.heartbeat()
                logger.info("✅ ChromaDB client initialized successfully")
                return client
            except Exception as e:
                logger.warning(
                    f"⚠️ ChromaDB connection attempt {attempt + 1} failed: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("❌ Failed to connect to ChromaDB after all retries")
                    raise

    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze user query to extract intent, entities, and parameters"""
        query_lower = query.lower()

        # Determine intent
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 1
            intent_scores[intent] = score

        # Get the intent with highest score
        if intent_scores:
            intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[intent] / max(
                len(patterns) for patterns in self.intent_patterns.values()
            )
        else:
            intent = QueryIntent.GENERAL
            confidence = 0.0

        # Extract entities
        entities = {}
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, query_lower, re.IGNORECASE)
                if matches:
                    entities[entity_type] = (
                        matches[0] if isinstance(matches[0], str) else matches[0][0]
                    )
                    break

        # Extract parameters
        parameters = self._extract_parameters(query_lower, entities)

        return QueryAnalysis(
            intent=intent,
            entities=entities,
            parameters=parameters,
            confidence=confidence,
        )

    def _extract_parameters(
        self, query: str, entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract search parameters from entities"""
        parameters = {}

        # Budget parameters
        if "budget" in entities:
            budget_str = entities["budget"]
            try:
                # Handle different budget formats
                if "k" in budget_str or "thousand" in budget_str:
                    budget = (
                        float(budget_str.replace("k", "").replace("thousand", ""))
                        * 1000
                    )
                elif "m" in budget_str or "million" in budget_str:
                    budget = (
                        float(budget_str.replace("m", "").replace("million", ""))
                        * 1000000
                    )
                else:
                    budget = float(budget_str.replace(",", ""))

                # Check if query contains "under", "less than", "below" for max budget
                query_lower = query.lower()
                if any(word in query_lower for word in ["under", "less than", "below"]):
                    parameters["budget_max"] = budget * 1000000  # Convert to AED
                    parameters["budget_min"] = 0  # No minimum
                else:
                    # Set budget range (±20%)
                    parameters["budget_min"] = budget * 0.8
                    parameters["budget_max"] = budget * 1.2
            except:
                pass

        # Location parameter
        if "location" in entities:
            parameters["location"] = entities["location"]

        # Property type
        if "property_type" in entities:
            parameters["property_type"] = entities["property_type"]

        # Bedrooms
        if "bedrooms" in entities:
            try:
                parameters["bedrooms"] = int(entities["bedrooms"])
            except:
                pass

        # Bathrooms
        if "bathrooms" in entities:
            try:
                parameters["bathrooms"] = float(entities["bathrooms"])
            except:
                pass

        return parameters

    # Reelly methods removed

    def get_relevant_context(
        self, query: str, analysis: QueryAnalysis, max_items: int = 8
    ) -> List[ContextItem]:
        """Get relevant context from multiple sources based on query analysis with enhanced retrieval"""
        context_items = []

        # 1. Get relevant properties from our comprehensive local database (8,000+ properties)
        if analysis.intent == QueryIntent.PROPERTY_SEARCH:
            prop_context = self._get_property_context(analysis.parameters, max_items)
            context_items.extend(prop_context)

            # For property search, focus on properties, not market analysis
            # Only add minimal market context if specifically requested

        # 2. Enhanced document retrieval from ChromaDB with multiple query variations
        # Skip document context for property search to focus on actual properties
        if analysis.intent != QueryIntent.PROPERTY_SEARCH:
            doc_context = self._get_enhanced_document_context(
                query, analysis.intent, max_items
            )
            context_items.extend(doc_context)

        # 4. Get relevant neighborhoods and market data
        if analysis.intent in [
            QueryIntent.NEIGHBORHOOD_QUESTION,
            QueryIntent.MARKET_INFO,
        ]:
            neighborhood_context = self._get_neighborhood_context(query, max_items)
            context_items.extend(neighborhood_context)

            market_context = self._get_market_context(query, max_items)
            context_items.extend(market_context)

        # 5. Get additional market insights for investment questions
        if analysis.intent == QueryIntent.INVESTMENT_QUESTION:
            investment_context = self._get_investment_context(query, max_items)
            context_items.extend(investment_context)

        # 6. Get agent-specific data for agent support queries
        if analysis.intent == QueryIntent.AGENT_SUPPORT:
            agent_context = self._get_agent_context(query, max_items)
            context_items.extend(agent_context)

        # 7. Sort all combined context items by relevance and return the best ones
        context_items.sort(key=lambda x: x.relevance_score, reverse=True)
        return context_items[:max_items]

    def _get_enhanced_document_context(
        self, query: str, intent: QueryIntent, max_items: int
    ) -> List[ContextItem]:
        """Get relevant documents from ChromaDB collections with enhanced query variations"""
        context_items = []

        # Enhanced collection mapping to use ALL specialized collections
        collection_mapping = {
            QueryIntent.PROPERTY_SEARCH: [
                "real_estate_docs",
                "market_analysis",
                "neighborhood_profiles",
                "developer_profiles",
            ],
            QueryIntent.MARKET_INFO: [
                "market_analysis",
                "market_forecasts",
                "financial_insights",
                "investment_insights",
            ],
            QueryIntent.INVESTMENT_QUESTION: [
                "investment_insights",
                "market_analysis",
                "financial_insights",
                "market_forecasts",
            ],
            QueryIntent.REGULATORY_QUESTION: [
                "regulatory_framework",
                "transaction_guidance",
                "real_estate_docs",
            ],
            QueryIntent.NEIGHBORHOOD_QUESTION: [
                "neighborhood_profiles",
                "urban_planning",
                "market_analysis",
            ],
            QueryIntent.DEVELOPER_QUESTION: [
                "developer_profiles",
                "market_analysis",
                "investment_insights",
            ],
            QueryIntent.POLICY_QUESTION: [
                "regulatory_framework",
                "agent_resources",
                "transaction_guidance",
            ],
            QueryIntent.AGENT_SUPPORT: [
                "agent_resources",
                "transaction_guidance",
                "market_analysis",
            ],
            QueryIntent.GENERAL: [
                "real_estate_docs",
                "comprehensive_data",
                "market_analysis",
            ],
        }

        collections = collection_mapping.get(intent, ["comprehensive_data"])

        # Create multiple query variations for better context retrieval
        query_variations = [
            query,
            query.replace("apartment", "property").replace("villa", "property"),
            query.replace("dubai marina", "marina").replace(
                "downtown", "downtown dubai"
            ),
            query + " dubai real estate",
            query + " market trends",
            query + " investment",
        ]

        for collection_name in collections:
            try:
                collection = self.chroma_client.get_collection(collection_name)

                # Query with multiple variations
                all_results = []
                for q_var in query_variations[:3]:  # Use top 3 variations
                    try:
                        results = collection.query(
                            query_texts=[q_var], n_results=max_items * 2
                        )

                        if results["documents"] and results["documents"][0]:
                            all_results.extend(results["documents"][0])
                    except Exception as e:
                        logger.warning(
                            f"Error querying collection {collection_name} with variation '{q_var}': {e}"
                        )
                        continue

                # Remove duplicates and add to context
                seen_docs = set()
                for doc in all_results:
                    if doc not in seen_docs:
                        seen_docs.add(doc)
                        # Calculate relevance score based on query similarity
                        score = 0.8
                        if any(
                            keyword in doc.lower() for keyword in query.lower().split()
                        ):
                            score += 0.1

                        context_items.append(
                            ContextItem(
                                content=doc,
                                source=f"chroma_{collection_name}",
                                relevance_score=score,
                                metadata={
                                    "type": "document",
                                    "collection": collection_name,
                                },
                            )
                        )
            except Exception as e:
                logger.warning(f"Error querying collection {collection_name}: {e}")
                continue

        return context_items

    def _get_document_context(
        self, query: str, intent: QueryIntent, max_items: int
    ) -> List[ContextItem]:
        """Legacy method - now calls enhanced version"""
        return self._get_enhanced_document_context(query, intent, max_items)

    def _get_property_context(
        self, parameters: Dict[str, Any], max_items: int
    ) -> List[ContextItem]:
        """Get relevant properties from database based on parameters"""
        context_items = []

        # Build SQL query based on parameters - use correct properties table with our 25-column schema
        sql_parts = [
            "SELECT id, title, description, price_aed as price, location, property_type, bedrooms, bathrooms, area_sqft, price_per_sqft, listing_status FROM properties WHERE 1=1"
        ]
        sql_parts.append(
            "AND listing_status = 'live'"
        )  # This ensures only public listings are shown
        query_params = {}

        # Always get some properties even without specific parameters
        if not parameters:
            sql_parts.append("AND price > 0")

        if "budget_min" in parameters and "budget_max" in parameters:
            sql_parts.append("AND price_aed BETWEEN :budget_min AND :budget_max")
            query_params["budget_min"] = parameters["budget_min"]
            query_params["budget_max"] = parameters["budget_max"]
        elif "budget_max" in parameters:
            sql_parts.append("AND price_aed <= :budget_max")
            query_params["budget_max"] = parameters["budget_max"]

        if "location" in parameters:
            sql_parts.append("AND location ILIKE :location")
            query_params["location"] = f"%{parameters['location']}%"

        if "property_type" in parameters:
            sql_parts.append("AND property_type ILIKE :property_type")
            query_params["property_type"] = f"%{parameters['property_type']}%"

        if "bedrooms" in parameters:
            sql_parts.append("AND bedrooms >= :bedrooms")
            query_params["bedrooms"] = parameters["bedrooms"]

        if "bathrooms" in parameters:
            sql_parts.append("AND bathrooms >= :bathrooms")
            query_params["bathrooms"] = parameters["bathrooms"]

        sql_parts.append("ORDER BY price_aed ASC LIMIT :limit")
        query_params["limit"] = max_items * 2  # Get more to filter better

        sql = " ".join(sql_parts)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), query_params)
                for row in result:
                    try:
                        # Handle null values safely
                        location = row.location or "Location not specified"
                        price_str = (
                            f"${row.price:,.0f}"
                            if row.price and row.price > 0
                            else "Price on request"
                        )
                        bedrooms = row.bedrooms or "Not specified"
                        bathrooms = row.bathrooms or "Not specified"
                        property_type = row.property_type or "Not specified"

                        property_info = f"Location: {location}, Price: {price_str}, Bedrooms: {bedrooms}, Bathrooms: {bathrooms}, Type: {property_type}"

                        if row.description:
                            property_info += f", Description: {row.description}"
                    except Exception as e:
                        logger.warning(f"Error formatting property info: {e}")
                        property_info = (
                            f"Property in {row.location or 'Unknown location'}"
                        )

                    # Calculate relevance score based on parameter match
                    relevance_score = self._calculate_property_relevance(
                        row, parameters
                    )

                    context_items.append(
                        ContextItem(
                            content=property_info,
                            source="database_properties",
                            relevance_score=relevance_score,
                            metadata={
                                "location": row.location,
                                "price": float(row.price) if row.price else 0,
                                "bedrooms": row.bedrooms,
                                "bathrooms": float(row.bathrooms)
                                if row.bathrooms
                                else 0,
                                "property_type": row.property_type,
                            },
                        )
                    )
        except Exception as e:
            logger.error(f"Error querying properties: {e}")

        return context_items

    def _calculate_property_relevance(
        self, property_row, parameters: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for a property based on parameters"""
        score = 0.5  # Base score

        # Budget relevance
        if (
            "budget_min" in parameters
            and "budget_max" in parameters
            and property_row.price
        ):
            price = float(property_row.price)
            if parameters["budget_min"] <= price <= parameters["budget_max"]:
                score += 0.3
            elif price <= parameters["budget_max"] * 1.5:  # Within 50% of max budget
                score += 0.1

        # Location relevance
        if "location" in parameters and property_row.location:
            if parameters["location"].lower() in property_row.location.lower():
                score += 0.2

        # Property type relevance
        if "property_type" in parameters and property_row.property_type:
            if (
                parameters["property_type"].lower()
                in property_row.property_type.lower()
            ):
                score += 0.2

        # Bedrooms relevance
        if "bedrooms" in parameters and property_row.bedrooms:
            if property_row.bedrooms >= parameters["bedrooms"]:
                score += 0.1

        # Bathrooms relevance
        if "bathrooms" in parameters and property_row.bathrooms:
            if float(property_row.bathrooms) >= parameters["bathrooms"]:
                score += 0.1

        return min(score, 1.0)

    # Reelly property context method removed

    def build_structured_context(self, context_items: List[ContextItem]) -> str:
        """Build a structured, scannable context string"""
        if not context_items:
            return "No relevant data found."

        # Separate different types of data
        properties = [
            item for item in context_items if item.source == "database_properties"
        ]
        neighborhoods = [
            item
            for item in context_items
            if item.source == "comprehensive_neighborhoods"
        ]
        market_data = [
            item for item in context_items if item.source == "comprehensive_market_data"
        ]
        documents = [
            item for item in context_items if item.source.startswith("chroma_")
        ]

        context_parts = []

        # Properties section with structured data
        if properties:
            context_parts.append("**INTERNAL PROPERTY DATA:**")
            for i, prop in enumerate(properties[:5], 1):  # Limit to top 5
                metadata = prop.metadata
                context_parts.append(f"{i}. **{metadata.get('address', 'N/A')}**")
                context_parts.append(f"   • Price: AED {metadata.get('price', 0):,.0f}")
                context_parts.append(
                    f"   • Type: {metadata.get('property_type', 'N/A')}"
                )
                context_parts.append(
                    f"   • Bedrooms: {metadata.get('bedrooms', 'N/A')}"
                )
                context_parts.append(
                    f"   • Bathrooms: {metadata.get('bathrooms', 'N/A')}"
                )
                context_parts.append("")

        # Reelly section removed

        # Market data section
        if market_data:
            context_parts.append("**MARKET INSIGHTS:**")
            for data in market_data[:3]:  # Limit to top 3
                context_parts.append(f"• {data.content}")
            context_parts.append("")

        # Neighborhood data section
        if neighborhoods:
            context_parts.append("**NEIGHBORHOOD INFORMATION:**")
            for hood in neighborhoods[:2]:  # Limit to top 2
                context_parts.append(f"• {hood.content}")
            context_parts.append("")

        # Document data section
        if documents:
            context_parts.append("**ADDITIONAL DATA:**")
            for doc in documents[:2]:  # Limit to top 2
                context_parts.append(f"• {doc.content[:200]}...")
            context_parts.append("")

        return "\n".join(context_parts)

    def build_context_string(self, context_items: List[ContextItem]) -> str:
        """Build context string for prompt creation (alias for build_structured_context)"""
        return self.build_structured_context(context_items)

    def create_improved_prompt(
        self,
        query: str,
        analysis: QueryAnalysis,
        context: str,
        user_role: str = "client",
    ) -> str:
        """Create an improved prompt with enhanced Dubai real estate context"""

        # Enhanced system prompt with specific Dubai real estate expertise
        system_prompt = f"""
You are an expert Dubai real estate AI assistant. Provide helpful, accurate responses based on available data.

RESPONSE REQUIREMENTS:
1. **Keep responses concise** - Answer directly without unnecessary elaboration
2. **Use available data** - Only reference information from the provided context
3. **Be honest about limitations** - If you don't have specific data, say so
4. **Focus on user intent** - Match response length to query complexity
5. **Avoid hallucination** - Don't make up specific prices, statistics, or data

AVAILABLE CONTEXT:
- Use only the information provided in the context below
- If no relevant context is available, provide general guidance
- Don't reference specific prices or statistics unless they're in the context

USER ROLE: {user_role.upper()}

RESPONSE GUIDELINES:
- For simple greetings: Brief, friendly response
- For property queries: Use available property data
- For market questions: Provide general guidance if no specific data available
- For complex queries: Structured but concise response
"""

        # Role-specific context
        role_context = ""
        if user_role == "client":
            role_context = """
CLIENT ROLE CONTEXT:
- Focus on property search, market information, and investment opportunities
- Provide pricing guidance and area recommendations
- Include financing options and payment plans
- Mention Golden Visa benefits and residency requirements
"""
        elif user_role == "agent":
            role_context = """
AGENT ROLE CONTEXT:
- Provide market analysis and competitive insights
- Include lead generation and client management tips
- Share sales strategies and negotiation techniques
- Offer property valuation and listing optimization advice
"""
        elif user_role == "admin":
            role_context = """
ADMIN ROLE CONTEXT:
- Focus on system management and data analysis
- Provide performance metrics and reporting insights
- Include user management and security considerations
- Offer business intelligence and market forecasting
"""

        # Intent-specific context
        intent_context = ""
        if analysis.intent == QueryIntent.PROPERTY_SEARCH:
            intent_context = """
PROPERTY SEARCH CONTEXT:
- Provide specific property recommendations based on budget and preferences
- Include current market prices and availability
- Mention payment plans and financing options
- Suggest similar properties and alternatives
"""
        elif analysis.intent == QueryIntent.MARKET_INFO:
            intent_context = """
MARKET INFORMATION CONTEXT:
- Provide current market statistics and trends
- Include price movements and market forecasts
- Mention investment opportunities and risks
- Compare different areas and property types
"""
        elif analysis.intent == QueryIntent.INVESTMENT_QUESTION:
            intent_context = """
INVESTMENT CONTEXT:
- Focus on ROI and investment returns
- Include rental yields and capital appreciation
- Mention Golden Visa benefits and tax advantages
- Provide investment strategy recommendations
"""

        # Build the complete prompt
        prompt = f"""
{system_prompt}

{role_context}

{intent_context}

RELEVANT CONTEXT FROM DATABASE:
{context}

USER QUERY: {query}

QUERY ANALYSIS:
- Intent: {analysis.intent.value}
- Entities: {analysis.entities}
- Parameters: {analysis.parameters}
- Confidence: {analysis.confidence:.2f}

IMPORTANT: Provide specific Dubai real estate information, actual prices, and actionable recommendations. Avoid generic responses.
"""

        return prompt

    def _get_neighborhood_context(
        self, query: str, max_items: int
    ) -> List[ContextItem]:
        """Get relevant neighborhood information from database"""
        context_items = []

        try:
            with self.engine.connect() as conn:
                # Check if table exists
                check_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'neighborhood_profiles'
                    );
                """
                result = conn.execute(text(check_sql))
                table_exists = result.scalar()

                if not table_exists:
                    logger.info(
                        "Neighborhood profiles table does not exist, skipping neighborhood context"
                    )
                    return context_items

                sql = """
                    SELECT name, description, price_ranges, rental_yields, amenities, pros, cons, source_file
                    FROM neighborhood_profiles 
                    WHERE name ILIKE :query OR description ILIKE :query
                    LIMIT :limit
                """

                result = conn.execute(
                    text(sql), {"query": f"%{query}%", "limit": max_items}
                )

                for row in result:
                    content = f"""
                    Neighborhood: {row.name}
                    Description: {row.description}
                    Price Ranges: {row.price_ranges}
                    Rental Yields: {row.rental_yields}
                    Amenities: {row.amenities}
                    Pros: {row.pros}
                    Cons: {row.cons}
                    Source: {row.source_file}
                    """

                    context_items.append(
                        ContextItem(
                            content=content,
                            source="comprehensive_neighborhoods",
                            relevance_score=0.9,
                            metadata={"type": "neighborhood", "name": row.name},
                        )
                    )

        except Exception as e:
            logger.warning(f"Error getting neighborhood context: {e}")

        return context_items

    def _get_market_context(self, query: str, max_items: int) -> List[ContextItem]:
        """Get relevant market information from database"""
        context_items = []

        try:
            with self.engine.connect() as conn:
                # Check if table exists
                check_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'market_data'
                    );
                """
                result = conn.execute(text(check_sql))
                table_exists = result.scalar()

                if not table_exists:
                    logger.info(
                        "Market data table does not exist, skipping market context"
                    )
                    return context_items

                sql = """
                    SELECT content, type, source_file
                    FROM market_data 
                    WHERE content ILIKE :query OR type ILIKE :query
                    LIMIT :limit
                """

                result = conn.execute(
                    text(sql), {"query": f"%{query}%", "limit": max_items}
                )

                for row in result:
                    context_items.append(
                        ContextItem(
                            content=row.content,
                            source="comprehensive_market_data",
                            relevance_score=0.8,
                            metadata={"type": "market_data", "data_type": row.type},
                        )
                    )

        except Exception as e:
            logger.warning(f"Error getting market context: {e}")

        return context_items

        # TODO: [CLEANUP] - Review for removal - Duplicate method definition
        # def analyze_query(self, query: str) -> QueryAnalysis:
        #     """Analyze query to determine intent and extract entities"""
        #     # Determine intent
        #     intent = QueryIntent.GENERAL
        #     max_confidence = 0.0
        #
        #     for query_intent, patterns in self.intent_patterns.items():
        #         for pattern in patterns:
        #             if re.search(pattern, query, re.IGNORECASE):
        #                 confidence = len(re.findall(pattern, query, re.IGNORECASE)) / len(query.split())
        #                 if confidence > max_confidence:
        #                     max_confidence = confidence
        #                     intent = query_intent
        #
        #     # Extract entities
        #     entities = {}
        #     for entity_type, patterns in self.entity_patterns.items():
        #         for pattern in patterns:
        #             matches = re.findall(pattern, query, re.IGNORECASE)
        #             if matches:
        #                 entities[entity_type] = matches[0] if isinstance(matches[0], str) else matches[0][0]
        #
        #     # Extract parameters
        #     parameters = self._extract_parameters(entities)
        #
        #     return QueryAnalysis(
        #         intent=intent,
        #         entities=entities,
        #         parameters=parameters,
        #         confidence=max_confidence
        #     )

        # TODO: [CLEANUP] - Review for removal - Duplicate method definition
        # def _extract_parameters(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        #     """Extract and normalize parameters from entities"""
        #     parameters = {}
        #
        #     # Budget parameters
        #     if 'budget' in entities:
        #         try:
        #             budget_str = str(entities['budget']).lower()
        #             if 'million' in budget_str or 'm' in budget_str:
        #                 # Convert to AED (assuming 1M = 1,000,000 AED)
        #                 budget_val = float(re.findall(r'[\d.]+', budget_str)[0]) * 1000000
        #                 parameters['budget_max'] = budget_val
        #                 parameters['budget_min'] = budget_val * 0.8
        #             elif 'thousand' in budget_str or 'k' in budget_str:
        #                 budget_val = float(re.findall(r'[\d.]+', budget_str)[0]) * 1000
        #                 parameters['budget_max'] = budget_val
        #                 parameters['budget_min'] = budget_val * 0.8
        #             else:
        #                 budget_val = float(re.findall(r'[\d,]+', budget_str)[0].replace(',', ''))
        #                 parameters['budget_max'] = budget_val
        #                 parameters['budget_min'] = budget_val * 0.8
        #         except:
        #             pass
        #
        #     # Location parameters
        #     if 'location' in entities:
        #         parameters['location'] = entities['location']
        #
        #     # Property type parameters
        #     if 'property_type' in entities:
        #         parameters['property_type'] = entities['property_type']
        #
        #     # Bedrooms
        #     if 'bedrooms' in entities:
        #         try:
        #             parameters['bedrooms'] = int(entities['bedrooms'])
        #         except:
        #             pass
        #
        #     # Bathrooms
        #     if 'bathrooms' in entities:
        #         try:
        #             parameters['bathrooms'] = float(entities['bathrooms'])
        #         except:
        #             pass
        #
        #     return parameters

        # TODO: [CLEANUP] - Review for removal - Duplicate method definition
        # def get_relevant_context(self, query: str, analysis: QueryAnalysis, max_items: int = 5) -> List[ContextItem]:
        #     """Get relevant context from multiple sources based on query analysis"""
        #     context_items = []
        #
        #     # Get relevant documents from ChromaDB
        #     doc_context = self._get_document_context(query, analysis.intent, max_items)
        #     context_items.extend(doc_context)
        #
        #     # Get relevant properties from database
        if analysis.intent == QueryIntent.PROPERTY_SEARCH:
            prop_context = self._get_property_context(
                analysis.parameters, max_items * 2
            )
            context_items.extend(prop_context)
        else:
            prop_context = self._get_property_context(analysis.parameters, max_items)
            context_items.extend(prop_context)

        # Get relevant neighborhoods and market data
        if analysis.intent in [
            QueryIntent.NEIGHBORHOOD_QUESTION,
            QueryIntent.MARKET_INFO,
        ]:
            neighborhood_context = self._get_neighborhood_context(query, max_items)
            context_items.extend(neighborhood_context)

            market_context = self._get_market_context(query, max_items)
            context_items.extend(market_context)

        # Sort by relevance and return top items
        context_items.sort(key=lambda x: x.relevance_score, reverse=True)
        return context_items[:max_items]

    def _get_document_context(
        self, query: str, intent: QueryIntent, max_items: int
    ) -> List[ContextItem]:
        """Get relevant documents from ChromaDB collections"""
        context_items = []

        # Enhanced collection mapping to use ALL specialized collections
        collection_mapping = {
            QueryIntent.PROPERTY_SEARCH: [
                "real_estate_docs",
                "market_analysis",
                "neighborhood_profiles",
                "developer_profiles",
            ],
            QueryIntent.MARKET_INFO: [
                "market_analysis",
                "market_forecasts",
                "financial_insights",
                "investment_insights",
            ],
            QueryIntent.INVESTMENT_QUESTION: [
                "investment_insights",
                "market_analysis",
                "financial_insights",
                "market_forecasts",
            ],
            QueryIntent.REGULATORY_QUESTION: [
                "regulatory_framework",
                "transaction_guidance",
                "real_estate_docs",
            ],
            QueryIntent.NEIGHBORHOOD_QUESTION: [
                "neighborhood_profiles",
                "urban_planning",
                "market_analysis",
            ],
            QueryIntent.DEVELOPER_QUESTION: [
                "developer_profiles",
                "market_analysis",
                "investment_insights",
            ],
            QueryIntent.POLICY_QUESTION: [
                "regulatory_framework",
                "agent_resources",
                "transaction_guidance",
            ],
            QueryIntent.AGENT_SUPPORT: [
                "agent_resources",
                "transaction_guidance",
                "market_analysis",
            ],
            QueryIntent.GENERAL: [
                "real_estate_docs",
                "comprehensive_data",
                "market_analysis",
            ],
        }

        collections = collection_mapping.get(intent, ["comprehensive_data"])

        for collection_name in collections:
            try:
                collection = self.chroma_client.get_collection(collection_name)
                results = collection.query(query_texts=[query], n_results=max_items * 2)

                if results["documents"] and results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        score = 1.0 - (
                            results["distances"][0][i]
                            if results["distances"] and results["distances"][0]
                            else 0.5
                        )
                        metadata = (
                            results["metadatas"][0][i]
                            if results["metadatas"] and results["metadatas"][0]
                            else {}
                        )

                        context_items.append(
                            ContextItem(
                                content=doc,
                                source=f"chroma_{collection_name}",
                                relevance_score=score,
                                metadata=metadata,
                            )
                        )
            except Exception as e:
                logger.warning(f"Error querying collection {collection_name}: {e}")
                continue

        return context_items

    def _get_property_context(
        self, parameters: Dict[str, Any], max_items: int
    ) -> List[ContextItem]:
        """Get relevant properties from database based on parameters"""
        context_items = []

        # Build SQL query based on parameters - use correct column names
        sql_parts = [
            "SELECT id, title, description, price_aed as price, location, property_type, bedrooms, bathrooms, area_sqft FROM properties WHERE 1=1"
        ]
        query_params = {}

        if not parameters:
            sql_parts.append("AND price_aed > 0")

        if "budget_min" in parameters and "budget_max" in parameters:
            sql_parts.append("AND price_aed BETWEEN :budget_min AND :budget_max")
            query_params["budget_min"] = parameters["budget_min"]
            query_params["budget_max"] = parameters["budget_max"]

        if "location" in parameters:
            sql_parts.append("AND location ILIKE :location")

        if "property_type" in parameters:
            sql_parts.append("AND property_type ILIKE :property_type")

        if "bedrooms" in parameters:
            sql_parts.append("AND bedrooms >= :bedrooms")

        if "bathrooms" in parameters:
            sql_parts.append("AND bathrooms >= :bathrooms")

        sql_parts.append("ORDER BY price_aed ASC LIMIT :limit")
        query_params["limit"] = max_items

        try:
            with self.engine.connect() as conn:
                sql = " ".join(sql_parts)
                result = conn.execute(text(sql), query_params)

                for row in result:
                    try:
                        # Handle null values safely
                        title = row.title or "Untitled"
                        price_str = (
                            f"AED {row.price:,.0f}"
                            if row.price and row.price > 0
                            else "Price on request"
                        )
                        property_type = row.property_type or "Not specified"
                        bedrooms = row.bedrooms or "Not specified"
                        bathrooms = row.bathrooms or "Not specified"
                        location = row.location or "Location not specified"
                        area_sqft = row.area_sqft or "Not specified"
                        description = row.description or "No description available"

                        content = f"""
                        Property: {title}
                        Price: {price_str}
                        Type: {property_type}
                        Bedrooms: {bedrooms}
                        Bathrooms: {bathrooms}
                        Location: {location}
                        Area: {area_sqft} sqft
                        Description: {description}
                        """
                    except Exception as format_error:
                        logger.warning(
                            f"Error formatting property content: {format_error}"
                        )
                        content = f"Property in {row.location or 'Unknown location'}"

                    context_items.append(
                        ContextItem(
                            content=content,
                            source="properties",
                            relevance_score=0.9,
                            metadata={
                                "type": "property",
                                "title": row.title,
                                "price": row.price,
                                "property_type": row.property_type,
                                "bedrooms": row.bedrooms,
                                "bathrooms": row.bathrooms,
                                "location": row.location,
                                "area_sqft": row.area_sqft,
                            },
                        )
                    )

        except Exception as e:
            logger.warning(f"Error getting property context: {e}")

        return context_items

    def _get_investment_context(self, query: str, max_items: int) -> List[ContextItem]:
        """Get investment-specific context for investment questions"""
        context_items = []

        try:
            with self.engine.connect() as conn:
                # Get market performance data
                market_query = text(
                    """
                    SELECT location, property_type, avg_price, avg_rent, price_appreciation, rental_yield
                    FROM market_data 
                    WHERE location ILIKE :query OR property_type ILIKE :query
                    ORDER BY price_appreciation DESC
                    LIMIT :limit
                """
                )

                market_results = conn.execute(
                    market_query, {"query": f"%{query}%", "limit": max_items}
                )

                for row in market_results:
                    content = f"📈 **Investment Opportunity**: {row[0]} - {row[1]} | 💰 Avg Price: {row[2]} | 🏠 Avg Rent: {row[3]} | 📊 Appreciation: {row[4]}% | 💸 Yield: {row[5]}%"
                    context_items.append(
                        ContextItem(
                            content=content,
                            source="market_data",
                            relevance_score=0.85,
                            metadata={"type": "investment_data"},
                        )
                    )

                # Get transaction insights
                transaction_query = text(
                    """
                    SELECT property_type, location, avg_days_on_market, transaction_count, avg_price_per_sqft
                    FROM transactions 
                    WHERE location ILIKE :query OR property_type ILIKE :query
                    GROUP BY property_type, location
                    ORDER BY transaction_count DESC
                    LIMIT :limit
                """
                )

                transaction_results = conn.execute(
                    transaction_query, {"query": f"%{query}%", "limit": max_items}
                )

                for row in transaction_results:
                    content = f"🔄 **Market Activity**: {row[0]} in {row[1]} | ⏱️ Avg Days: {row[2]} | 📊 Transactions: {row[3]} | 💰 Price/sqft: {row[4]}"
                    context_items.append(
                        ContextItem(
                            content=content,
                            source="transactions",
                            relevance_score=0.80,
                            metadata={"type": "transaction_data"},
                        )
                    )

        except Exception as e:
            logger.warning(f"Error getting investment context: {e}")

        return context_items

    def _get_agent_context(self, query: str, max_items: int) -> List[ContextItem]:
        """Get agent-specific context for agent support queries"""
        context_items = []

        try:
            with self.engine.connect() as conn:
                # Get lead insights
                leads_query = text(
                    """
                    SELECT lead_source, status, avg_budget, preferred_location, property_type, conversion_rate
                    FROM leads 
                    WHERE preferred_location ILIKE :query OR property_type ILIKE :query
                    GROUP BY lead_source, status, avg_budget, preferred_location, property_type
                    ORDER BY conversion_rate DESC
                    LIMIT :limit
                """
                )

                leads_results = conn.execute(
                    leads_query, {"query": f"%{query}%", "limit": max_items}
                )

                for row in leads_results:
                    content = f"👥 **Lead Insights**: {row[0]} | 📊 Status: {row[1]} | 💰 Avg Budget: {row[2]} | 📍 Location: {row[3]} | 🏠 Type: {row[4]} | 🎯 Conversion: {row[5]}%"
                    context_items.append(
                        ContextItem(
                            content=content,
                            source="leads",
                            relevance_score=0.85,
                            metadata={"type": "lead_data"},
                        )
                    )

                # Get agent performance data
                performance_query = text(
                    """
                    SELECT agent_name, total_sales, avg_commission, success_rate, avg_deal_size
                    FROM agent_performance 
                    WHERE agent_name ILIKE :query OR specializations ILIKE :query
                    ORDER BY total_sales DESC
                    LIMIT :limit
                """
                )

                performance_results = conn.execute(
                    performance_query, {"query": f"%{query}%", "limit": max_items}
                )

                for row in performance_results:
                    content = f"🏆 **Agent Performance**: {row[0]} | 📈 Sales: {row[1]} | 💰 Commission: {row[2]} | 🎯 Success Rate: {row[3]}% | 💎 Avg Deal: {row[4]}"
                    context_items.append(
                        ContextItem(
                            content=content,
                            source="agent_performance",
                            relevance_score=0.80,
                            metadata={"type": "performance_data"},
                        )
                    )

        except Exception as e:
            logger.warning(f"Error getting agent context: {e}")

        return context_items

    def get_response(
        self,
        message: str,
        role: str = "client",
        session_id: str = None,
        user_name: str = "User",
    ) -> str:
        """
        Main method to generate a response using the RAG service.
        This is the single source of truth for conversational AI responses.
        """
        try:
            # 1. Analyze the query
            analysis = self.analyze_query(message)

            # 2. Get relevant context with enhanced retrieval
            context_items = self.get_relevant_context(message, analysis, max_items=8)

            # 3. Build enhanced context string
            context = self.build_structured_context(context_items)

            # 4. Create enhanced prompt using the improved system prompt
            system_prompt = get_system_prompt(role, analysis.intent, context, user_name)

            # 5. Build the complete prompt
            full_prompt = f"""
{system_prompt}

## USER QUERY:
{message}

## RESPONSE:
"""

            # 6. Generate response using AI model with enhanced parameters
            import google.generativeai as genai
            from app.core.settings import GOOGLE_API_KEY

            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Enhanced generation parameters for better quality
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more focused responses
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=2048,  # Allow longer, more detailed responses
                ),
            )
            response_text = response.text.strip()

            return response_text

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your request. Please try again or contact support if the issue persists."
