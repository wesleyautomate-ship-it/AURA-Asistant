#!/usr/bin/env python3
"""
Redis Cache Manager for Dubai Real Estate RAG System
Handles caching of query results, context items, and user sessions for improved performance
"""

import redis
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pickle
import os
from env_loader import load_env

# Load environment variables from centralized loader
load_env()

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager for RAG system performance optimization"""

    def __init__(
        self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0
    ):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=False,  # Keep binary for pickle
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            logger.info(
                f"✅ Redis cache connected successfully to {redis_host}:{redis_port}"
            )
            self.cache_enabled = True
        except Exception as e:
            logger.warning(f"⚠️ Redis cache not available: {e}")
            self.cache_enabled = False
            self.redis_client = None

    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate a unique cache key based on data"""
        if isinstance(data, str):
            data_str = data
        else:
            data_str = json.dumps(data, sort_keys=True, default=str)

        # Create hash for consistent key generation
        hash_obj = hashlib.md5(data_str.encode("utf-8"))
        return f"{prefix}:{hash_obj.hexdigest()}"

    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for Redis storage"""
        try:
            return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Error serializing data: {e}")
            return json.dumps(data, default=str).encode("utf-8")

    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from Redis storage"""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Error deserializing data: {e}")
            return json.loads(data.decode("utf-8"))

    def cache_query_result(
        self, query: str, role: str, result: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """Cache query results with TTL"""
        if not self.cache_enabled:
            return False

        try:
            cache_key = self._generate_cache_key(
                "query_result", {"query": query, "role": role}
            )

            cache_data = {
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
            }

            serialized_data = self._serialize_data(cache_data)
            self.redis_client.setex(cache_key, ttl, serialized_data)

            logger.debug(f"Cached query result: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error caching query result: {e}")
            return False

    def get_cached_query_result(
        self, query: str, role: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached query result"""
        if not self.cache_enabled:
            return None

        try:
            cache_key = self._generate_cache_key(
                "query_result", {"query": query, "role": role}
            )

            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                cache_data = self._deserialize_data(cached_data)
                logger.debug(f"Cache hit for query: {cache_key}")
                return cache_data["result"]

            return None

        except Exception as e:
            logger.error(f"Error retrieving cached query result: {e}")
            return None

    def cache_context_items(
        self,
        query: str,
        intent: str,
        context_items: List[Dict[str, Any]],
        ttl: int = 1800,
    ) -> bool:
        """Cache context items for faster retrieval"""
        if not self.cache_enabled:
            return False

        try:
            cache_key = self._generate_cache_key(
                "context_items", {"query": query, "intent": intent}
            )

            cache_data = {
                "context_items": context_items,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
            }

            serialized_data = self._serialize_data(cache_data)
            self.redis_client.setex(cache_key, ttl, serialized_data)

            logger.debug(f"Cached context items: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error caching context items: {e}")
            return False

    def get_cached_context_items(
        self, query: str, intent: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached context items"""
        if not self.cache_enabled:
            return None

        try:
            cache_key = self._generate_cache_key(
                "context_items", {"query": query, "intent": intent}
            )

            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                cache_data = self._deserialize_data(cached_data)
                logger.debug(f"Cache hit for context items: {cache_key}")
                return cache_data["context_items"]

            return None

        except Exception as e:
            logger.error(f"Error retrieving cached context items: {e}")
            return None

    def cache_user_session(
        self, session_id: str, user_data: Dict[str, Any], ttl: int = 7200
    ) -> bool:
        """Cache user session data"""
        if not self.cache_enabled:
            return False

        try:
            cache_key = f"user_session:{session_id}"

            cache_data = {
                "user_data": user_data,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
            }

            serialized_data = self._serialize_data(cache_data)
            self.redis_client.setex(cache_key, ttl, serialized_data)

            logger.debug(f"Cached user session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error caching user session: {e}")
            return False

    def get_cached_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached user session data"""
        if not self.cache_enabled:
            return None

        try:
            cache_key = f"user_session:{session_id}"

            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                cache_data = self._deserialize_data(cached_data)
                logger.debug(f"Cache hit for user session: {session_id}")
                return cache_data["user_data"]

            return None

        except Exception as e:
            logger.error(f"Error retrieving cached user session: {e}")
            return None

    def cache_frequent_queries(
        self, query_pattern: str, results: List[Dict[str, Any]], ttl: int = 86400
    ) -> bool:
        """Cache frequently asked queries for faster response"""
        if not self.cache_enabled:
            return False

        try:
            cache_key = self._generate_cache_key("frequent_query", query_pattern)

            cache_data = {
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
            }

            serialized_data = self._serialize_data(cache_data)
            self.redis_client.setex(cache_key, ttl, serialized_data)

            logger.debug(f"Cached frequent query: {query_pattern}")
            return True

        except Exception as e:
            logger.error(f"Error caching frequent query: {e}")
            return False

    def get_cached_frequent_query(
        self, query_pattern: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached frequent query results"""
        if not self.cache_enabled:
            return None

        try:
            cache_key = self._generate_cache_key("frequent_query", query_pattern)

            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                cache_data = self._deserialize_data(cached_data)
                logger.debug(f"Cache hit for frequent query: {query_pattern}")
                return cache_data["results"]

            return None

        except Exception as e:
            logger.error(f"Error retrieving cached frequent query: {e}")
            return None

    def cache_property_search(
        self,
        search_params: Dict[str, Any],
        results: List[Dict[str, Any]],
        ttl: int = 1800,
    ) -> bool:
        """Cache property search results for faster retrieval"""
        if not self.cache_enabled:
            return False

        try:
            cache_key = self._generate_cache_key("property_search", search_params)

            cache_data = {
                "results": results,
                "search_params": search_params,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
            }

            serialized_data = self._serialize_data(cache_data)
            self.redis_client.setex(cache_key, ttl, serialized_data)

            logger.debug(f"Cached property search: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error caching property search: {e}")
            return False

    def get_cached_property_search(
        self, search_params: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached property search results"""
        if not self.cache_enabled:
            return None

        try:
            cache_key = self._generate_cache_key("property_search", search_params)

            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                cache_data = self._deserialize_data(cached_data)
                logger.debug(f"Cache hit for property search: {cache_key}")
                return cache_data["results"]

            return None

        except Exception as e:
            logger.error(f"Error retrieving cached property search: {e}")
            return None

    def cache_market_data(
        self, area: str, property_type: str, data: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """Cache market data for specific area and property type"""
        if not self.cache_enabled:
            return False

        try:
            cache_key = f"market_data:{area}:{property_type}"

            cache_data = {
                "data": data,
                "area": area,
                "property_type": property_type,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
            }

            serialized_data = self._serialize_data(cache_data)
            self.redis_client.setex(cache_key, ttl, serialized_data)

            logger.debug(f"Cached market data: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error caching market data: {e}")
            return False

    def get_cached_market_data(
        self, area: str, property_type: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached market data"""
        if not self.cache_enabled:
            return None

        try:
            cache_key = f"market_data:{area}:{property_type}"

            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                cache_data = self._deserialize_data(cached_data)
                logger.debug(f"Cache hit for market data: {cache_key}")
                return cache_data["data"]

            return None

        except Exception as e:
            logger.error(f"Error retrieving cached market data: {e}")
            return None

    def invalidate_cache_pattern(self, pattern: str) -> bool:
        """Invalidate cache entries matching a pattern"""
        if not self.cache_enabled:
            return False

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(
                    f"Invalidated {len(keys)} cache entries matching pattern: {pattern}"
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache_enabled:
            return {"status": "disabled"}

        try:
            info = self.redis_client.info()
            keys = self.redis_client.keys("*")

            stats = {
                "status": "enabled",
                "total_keys": len(keys),
                "memory_usage": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime": info.get("uptime_in_seconds", 0),
                "cache_patterns": {
                    "query_results": len(
                        [k for k in keys if k.startswith(b"query_result:")]
                    ),
                    "context_items": len(
                        [k for k in keys if k.startswith(b"context_items:")]
                    ),
                    "user_sessions": len(
                        [k for k in keys if k.startswith(b"user_session:")]
                    ),
                    "frequent_queries": len(
                        [k for k in keys if k.startswith(b"frequent_query:")]
                    ),
                },
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "message": str(e)}

    def clear_all_cache(self) -> bool:
        """Clear all cache entries"""
        if not self.cache_enabled:
            return False

        try:
            self.redis_client.flushdb()
            logger.info("Cleared all cache entries")
            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Check cache health and performance"""
        if not self.cache_enabled:
            return {"status": "disabled", "message": "Redis cache not available"}

        try:
            start_time = datetime.now()
            self.redis_client.ping()
            ping_time = (datetime.now() - start_time).total_seconds() * 1000

            stats = self.get_cache_stats()
            stats["ping_time_ms"] = ping_time
            stats["status"] = "healthy"

            return stats

        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}


# Global cache manager instance
cache_manager = CacheManager()
