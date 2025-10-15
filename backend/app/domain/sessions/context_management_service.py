"""
Context Management Service for Phase 3: Advanced In-Chat Experience

This service manages fetching, caching, and providing context data for detected entities.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from sqlalchemy import text
from database_manager import get_db_connection

logger = logging.getLogger(__name__)


class ContextManagementService:
    """Service for managing entity context data"""

    def __init__(self):
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        self.max_cache_size = 1000  # Maximum cached items

    async def fetch_entity_context(
        self, entity_type: str, entity_id: str
    ) -> Dict[str, Any]:
        """
        Fetch context data for a specific entity

        Args:
            entity_type: Type of entity ('property', 'client', 'location', 'market_data')
            entity_id: Identifier for the entity

        Returns:
            Context data dictionary
        """
        try:
            # Check cache first
            cached_data = await self._get_cached_context(entity_type, entity_id)
            if cached_data:
                logger.info(f"Retrieved cached context for {entity_type}:{entity_id}")
                return cached_data

            # Fetch fresh data
            context_data = await self._fetch_fresh_context(entity_type, entity_id)

            # Cache the data
            if context_data:
                await self._cache_context(entity_type, entity_id, context_data)

            return context_data or {}

        except Exception as e:
            logger.error(f"Error fetching context for {entity_type}:{entity_id}: {e}")
            return {}

    async def _get_cached_context(
        self, entity_type: str, entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get context data from cache"""
        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT context_data, last_fetched, expires_at
                    FROM context_cache
                    WHERE entity_type = :entity_type AND entity_id = :entity_id
                """
                    ),
                    {"entity_type": entity_type, "entity_id": entity_id},
                )

                row = result.fetchone()
                if row and row["expires_at"] > datetime.now():
                    return (
                        json.loads(row["context_data"]) if row["context_data"] else {}
                    )

                return None

        except Exception as e:
            logger.error(f"Error getting cached context: {e}")
            return None

    async def _cache_context(
        self, entity_type: str, entity_id: str, context_data: Dict[str, Any]
    ):
        """Cache context data"""
        try:
            expires_at = datetime.now() + self.cache_duration

            with get_db_connection() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO context_cache (entity_type, entity_id, context_data, expires_at)
                    VALUES (:entity_type, :entity_id, :context_data, :expires_at)
                    ON CONFLICT (entity_type, entity_id)
                    DO UPDATE SET
                        context_data = :context_data,
                        last_fetched = CURRENT_TIMESTAMP,
                        expires_at = :expires_at
                """
                    ),
                    {
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "context_data": json.dumps(context_data),
                        "expires_at": expires_at,
                    },
                )

            logger.info(f"Cached context for {entity_type}:{entity_id}")

        except Exception as e:
            logger.error(f"Error caching context: {e}")

    async def _fetch_fresh_context(
        self, entity_type: str, entity_id: str
    ) -> Dict[str, Any]:
        """Fetch fresh context data from various sources"""
        try:
            if entity_type == "property":
                return await self._fetch_property_context(entity_id)
            elif entity_type == "client":
                return await self._fetch_client_context(entity_id)
            elif entity_type == "location":
                return await self._fetch_location_context(entity_id)
            elif entity_type == "market_data":
                return await self._fetch_market_context(entity_id)
            else:
                logger.warning(f"Unknown entity type: {entity_type}")
                return {}

        except Exception as e:
            logger.error(f"Error fetching fresh context: {e}")
            return {}

    async def _fetch_property_context(self, property_id: str) -> Dict[str, Any]:
        """Fetch property context data"""
        try:
            with get_db_connection() as conn:
                # Try to find property by ID first
                result = conn.execute(
                    text(
                        """
                    SELECT p.*, 
                           u.name as agent_name,
                           u.email as agent_email
                    FROM properties p
                    LEFT JOIN users u ON p.agent_id = u.id
                    WHERE p.id = :property_id
                """
                    ),
                    {"property_id": property_id},
                )

                property_data = result.fetchone()

                if not property_data:
                    # Try to find by address or description
                    result = conn.execute(
                        text(
                            """
                        SELECT p.*, 
                               u.name as agent_name,
                               u.email as agent_email
                        FROM properties p
                        LEFT JOIN users u ON p.agent_id = u.id
                        WHERE p.address ILIKE :search_term 
                           OR p.description ILIKE :search_term
                        LIMIT 1
                    """
                        ),
                        {"search_term": f"%{property_id}%"},
                    )

                    property_data = result.fetchone()

                if property_data:
                    # Get market data for the area
                    market_data = await self._get_market_data_for_area(
                        property_data["address"]
                    )

                    return {
                        "property": dict(property_data),
                        "market_data": market_data,
                        "similar_properties": await self._get_similar_properties(
                            property_data
                        ),
                        "context_type": "property_details",
                        "last_updated": datetime.now().isoformat(),
                    }

                return {}

        except Exception as e:
            logger.error(f"Error fetching property context: {e}")
            return {}

    async def _fetch_client_context(self, client_id: str) -> Dict[str, Any]:
        """Fetch client context data"""
        try:
            with get_db_connection() as conn:
                # Try to find client by ID first
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM clients WHERE id = :client_id
                """
                    ),
                    {"client_id": client_id},
                )

                client_data = result.fetchone()

                if not client_data:
                    # Try to find by name or email
                    result = conn.execute(
                        text(
                            """
                        SELECT * FROM clients 
                        WHERE name ILIKE :search_term 
                           OR email ILIKE :search_term
                        LIMIT 1
                    """
                        ),
                        {"search_term": f"%{client_id}%"},
                    )

                    client_data = result.fetchone()

                if client_data:
                    # Get client history
                    history = await self._get_client_history(client_data["id"])

                    return {
                        "client": dict(client_data),
                        "history": history,
                        "preferences": await self._get_client_preferences(
                            client_data["id"]
                        ),
                        "context_type": "client_info",
                        "last_updated": datetime.now().isoformat(),
                    }

                return {}

        except Exception as e:
            logger.error(f"Error fetching client context: {e}")
            return {}

    async def _fetch_location_context(self, location: str) -> Dict[str, Any]:
        """Fetch location context data"""
        try:
            with get_db_connection() as conn:
                # Get market data for location
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM market_data 
                    WHERE location ILIKE :location
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                    ),
                    {"location": f"%{location}%"},
                )

                market_data = result.fetchall()

                # Get neighborhood profile
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM neighborhood_profiles 
                    WHERE name ILIKE :location
                    LIMIT 1
                """
                    ),
                    {"location": f"%{location}%"},
                )

                neighborhood = result.fetchone()

                return {
                    "location": location,
                    "market_data": [dict(row) for row in market_data],
                    "neighborhood": dict(neighborhood) if neighborhood else {},
                    "properties_in_area": await self._get_properties_in_area(location),
                    "context_type": "location_data",
                    "last_updated": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error fetching location context: {e}")
            return {}

    async def _fetch_market_context(self, market_term: str) -> Dict[str, Any]:
        """Fetch market context data"""
        try:
            with get_db_connection() as conn:
                # Get market analysis data
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM market_data 
                    WHERE description ILIKE :search_term
                    ORDER BY created_at DESC
                    LIMIT 10
                """
                    ),
                    {"search_term": f"%{market_term}%"},
                )

                market_data = result.fetchall()

                # Get investment insights
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM investment_insights 
                    WHERE title ILIKE :search_term OR content ILIKE :search_term
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                    ),
                    {"search_term": f"%{market_term}%"},
                )

                insights = result.fetchall()

                return {
                    "market_term": market_term,
                    "market_data": [dict(row) for row in market_data],
                    "insights": [dict(row) for row in insights],
                    "trends": await self._get_market_trends(market_term),
                    "context_type": "market_analysis",
                    "last_updated": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error fetching market context: {e}")
            return {}

    async def _get_market_data_for_area(self, address: str) -> List[Dict[str, Any]]:
        """Get market data for a specific area"""
        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM market_data 
                    WHERE location ILIKE :area
                    ORDER BY created_at DESC
                    LIMIT 3
                """
                    ),
                    {"area": f'%{address.split(",")[0]}%'},
                )

                return [dict(row) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error getting market data for area: {e}")
            return []

    async def _get_similar_properties(
        self, property_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get similar properties"""
        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM properties 
                    WHERE property_type = :property_type 
                      AND bedrooms = :bedrooms
                      AND price BETWEEN :min_price AND :max_price
                      AND id != :exclude_id
                    ORDER BY ABS(price - :target_price)
                    LIMIT 3
                """
                    ),
                    {
                        "property_type": property_data["property_type"],
                        "bedrooms": property_data["bedrooms"],
                        "min_price": float(property_data["price"]) * 0.8,
                        "max_price": float(property_data["price"]) * 1.2,
                        "exclude_id": property_data["id"],
                        "target_price": float(property_data["price"]),
                    },
                )

                return [dict(row) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error getting similar properties: {e}")
            return []

    async def _get_client_history(self, client_id: int) -> List[Dict[str, Any]]:
        """Get client interaction history"""
        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM client_interactions 
                    WHERE client_id = :client_id
                    ORDER BY created_at DESC
                    LIMIT 10
                """
                    ),
                    {"client_id": client_id},
                )

                return [dict(row) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error getting client history: {e}")
            return []

    async def _get_client_preferences(self, client_id: int) -> Dict[str, Any]:
        """Get client preferences"""
        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM conversation_preferences 
                    WHERE user_id = :client_id
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                    ),
                    {"client_id": client_id},
                )

                row = result.fetchone()
                return dict(row) if row else {}

        except Exception as e:
            logger.error(f"Error getting client preferences: {e}")
            return {}

    async def _get_properties_in_area(self, location: str) -> List[Dict[str, Any]]:
        """Get properties in a specific area"""
        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM properties 
                    WHERE address ILIKE :location
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                    ),
                    {"location": f"%{location}%"},
                )

                return [dict(row) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error getting properties in area: {e}")
            return []

    async def _get_market_trends(self, market_term: str) -> List[Dict[str, Any]]:
        """Get market trends"""
        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT * FROM market_data 
                    WHERE description ILIKE :search_term
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                    ),
                    {"search_term": f"%{market_term}%"},
                )

                return [dict(row) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error getting market trends: {e}")
            return []

    async def clear_expired_cache(self):
        """Clear expired cache entries"""
        try:
            with get_db_connection() as conn:
                conn.execute(
                    text(
                        """
                    DELETE FROM context_cache 
                    WHERE expires_at < CURRENT_TIMESTAMP
                """
                    )
                )

            logger.info("Cleared expired cache entries")

        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")


# Global instance
context_management_service = ContextManagementService()
