#!/usr/bin/env python3
"""
Hybrid Search Engine for Dubai Real Estate RAG System
Combines vector search (ChromaDB) with structured search (PostgreSQL) for optimal results
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
try:  # Optional dependency
    import chromadb  # type: ignore
except ImportError:  # pragma: no cover
    chromadb = None  # type: ignore
from sqlalchemy import create_engine, text
import json
import hashlib
from cache_manager import cache_manager

logger = logging.getLogger(__name__)

class SearchType(Enum):
    VECTOR_ONLY = "vector_only"
    STRUCTURED_ONLY = "structured_only"
    HYBRID = "hybrid"

@dataclass
class SearchResult:
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any]
    search_type: SearchType
    execution_time: float

@dataclass
class SearchParams:
    query: str
    search_type: SearchType = SearchType.HYBRID
    max_results: int = 10
    location: Optional[str] = None
    property_type: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    intent: Optional[str] = None

class HybridSearchEngine:
    """Hybrid search engine combining vector and structured search"""
    
    def __init__(self, database_url: str, chroma_host: str = "localhost", chroma_port: int = 8000):
        if chromadb is None:
            raise RuntimeError(
                "chromadb package is required to use HybridSearchEngine but is not installed."
            )
        self.engine = create_engine(database_url)
        self.chroma_client = self._initialize_chroma_client(chroma_host, chroma_port)
        self.cache_manager = cache_manager
        
        # Search performance metrics
        self.search_metrics = {
            "total_searches": 0,
            "cache_hits": 0,
            "vector_searches": 0,
            "structured_searches": 0,
            "hybrid_searches": 0,
            "avg_execution_time": 0.0
        }
    
    def _initialize_chroma_client(self, host: str, port: int) -> chromadb.HttpClient:
        """Initialize ChromaDB client with retry logic"""
        try:
            client = chromadb.HttpClient(host=host, port=port)
            client.heartbeat()
            logger.info("✅ ChromaDB client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"❌ Failed to connect to ChromaDB: {e}")
            raise
    
    def _generate_search_cache_key(self, params: SearchParams) -> str:
        """Generate cache key for search parameters"""
        cache_data = {
            "query": params.query,
            "search_type": params.search_type.value,
            "max_results": params.max_results,
            "location": params.location,
            "property_type": params.property_type,
            "budget_min": params.budget_min,
            "budget_max": params.budget_max,
            "bedrooms": params.bedrooms,
            "bathrooms": params.bathrooms,
            "intent": params.intent
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def search(self, params: SearchParams) -> List[SearchResult]:
        """Main search method that orchestrates hybrid search"""
        start_time = time.time()
        self.search_metrics["total_searches"] += 1
        
        # Check cache first
        cache_key = self._generate_search_cache_key(params)
        cached_results = self.cache_manager.get_cached_property_search({
            "cache_key": cache_key,
            "search_type": params.search_type.value
        })
        
        if cached_results:
            self.search_metrics["cache_hits"] += 1
            logger.debug(f"Cache hit for search: {cache_key}")
            return [SearchResult(**result) for result in cached_results]
        
        # Perform search based on type
        if params.search_type == SearchType.VECTOR_ONLY:
            results = self._vector_search(params)
            self.search_metrics["vector_searches"] += 1
        elif params.search_type == SearchType.STRUCTURED_ONLY:
            results = self._structured_search(params)
            self.search_metrics["structured_searches"] += 1
        else:  # HYBRID
            results = self._hybrid_search(params)
            self.search_metrics["hybrid_searches"] += 1
        
        # Cache results
        cache_data = [result.__dict__ for result in results]
        self.cache_manager.cache_property_search({
            "cache_key": cache_key,
            "search_type": params.search_type.value
        }, cache_data, ttl=1800)
        
        # Update metrics
        execution_time = time.time() - start_time
        self._update_metrics(execution_time)
        
        return results
    
    def _vector_search(self, params: SearchParams) -> List[SearchResult]:
        """Perform vector search using ChromaDB"""
        start_time = time.time()
        results = []
        
        try:
            # Determine collection based on intent
            collection_name = self._get_collection_for_intent(params.intent)
            collection = self.chroma_client.get_collection(collection_name)
            
            # Perform vector search
            search_results = collection.query(
                query_texts=[params.query],
                n_results=params.max_results
            )
            
            if search_results['documents'] and search_results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    search_results['documents'][0],
                    search_results['metadatas'][0] if search_results['metadatas'] else [{}] * len(search_results['documents'][0]),
                    search_results['distances'][0] if search_results['distances'] else [0.5] * len(search_results['documents'][0])
                )):
                    relevance_score = 1.0 - distance
                    execution_time = time.time() - start_time
                    
                    results.append(SearchResult(
                        content=doc,
                        source=f"chroma_{collection_name}",
                        relevance_score=relevance_score,
                        metadata=metadata,
                        search_type=SearchType.VECTOR_ONLY,
                        execution_time=execution_time
                    ))
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
        
        return results
    
    def _structured_search(self, params: SearchParams) -> List[SearchResult]:
        """Perform structured search using PostgreSQL"""
        start_time = time.time()
        results = []
        
        try:
            # Build SQL query based on parameters
            sql_parts = [
                "SELECT id, title, description, price_aed, location, property_type, bedrooms, bathrooms, area_sqft",
                "FROM properties WHERE listing_status = 'live'"
            ]
            query_params = {}
            
            # Add filters
            if params.location:
                sql_parts.append("AND location ILIKE :location")
                query_params['location'] = f"%{params.location}%"
            
            if params.property_type:
                sql_parts.append("AND property_type ILIKE :property_type")
                query_params['property_type'] = f"%{params.property_type}%"
            
            if params.budget_min and params.budget_max:
                sql_parts.append("AND price_aed BETWEEN :budget_min AND :budget_max")
                query_params['budget_min'] = params.budget_min
                query_params['budget_max'] = params.budget_max
            elif params.budget_max:
                sql_parts.append("AND price_aed <= :budget_max")
                query_params['budget_max'] = params.budget_max
            
            if params.bedrooms:
                sql_parts.append("AND bedrooms >= :bedrooms")
                query_params['bedrooms'] = params.bedrooms
            
            if params.bathrooms:
                sql_parts.append("AND bathrooms >= :bathrooms")
                query_params['bathrooms'] = params.bathrooms
            
            # Add text search if query provided
            if params.query:
                sql_parts.append("AND (title ILIKE :query OR description ILIKE :query)")
                query_params['query'] = f"%{params.query}%"
            
            sql_parts.append("ORDER BY price_aed ASC LIMIT :limit")
            query_params['limit'] = params.max_results
            
            sql = " ".join(sql_parts)
            
            with self.engine.connect() as conn:
                db_results = conn.execute(text(sql), query_params)
                
                for row in db_results:
                    # Create content string for consistency
                    content = f"""
                    Property: {row.title or 'Untitled'}
                    Location: {row.location or 'Not specified'}
                    Price: AED {row.price_aed:,.0f} if row.price_aed else 'Price on request'
                    Type: {row.property_type or 'Not specified'}
                    Bedrooms: {row.bedrooms or 'Not specified'}
                    Bathrooms: {row.bathrooms or 'Not specified'}
                    Area: {row.area_sqft or 'Not specified'} sq ft
                    Description: {row.description or 'No description available'}
                    """
                    
                    execution_time = time.time() - start_time
                    
                    results.append(SearchResult(
                        content=content.strip(),
                        source="postgresql_properties",
                        relevance_score=0.9,  # High relevance for exact matches
                        metadata={
                            'id': row.id,
                            'title': row.title,
                            'price_aed': row.price_aed,
                            'location': row.location,
                            'property_type': row.property_type,
                            'bedrooms': row.bedrooms,
                            'bathrooms': row.bathrooms,
                            'area_sqft': row.area_sqft
                        },
                        search_type=SearchType.STRUCTURED_ONLY,
                        execution_time=execution_time
                    ))
        
        except Exception as e:
            logger.error(f"Error in structured search: {e}")
        
        return results
    
    def _hybrid_search(self, params: SearchParams) -> List[SearchResult]:
        """Perform hybrid search combining vector and structured results"""
        start_time = time.time()
        
        # Get results from both search types
        vector_results = self._vector_search(params)
        structured_results = self._structured_search(params)
        
        # Combine and rank results
        all_results = vector_results + structured_results
        
        # Remove duplicates based on content similarity
        unique_results = self._deduplicate_results(all_results)
        
        # Re-rank based on relevance and search type
        ranked_results = self._rank_hybrid_results(unique_results, params)
        
        # Return top results
        return ranked_results[:params.max_results]
    
    def _get_collection_for_intent(self, intent: Optional[str]) -> str:
        """Get appropriate ChromaDB collection based on intent"""
        collection_mapping = {
            "property_search": "real_estate_docs",
            "market_info": "market_analysis",
            "investment_question": "investment_insights",
            "regulatory_question": "regulatory_framework",
            "neighborhood_question": "neighborhood_profiles",
            "developer_question": "developer_profiles",
            "agent_support": "agent_resources",
            "general": "comprehensive_data"
        }
        
        return collection_mapping.get(intent, "comprehensive_data")
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on content similarity"""
        unique_results = []
        seen_content = set()
        
        for result in results:
            # Create a simple hash of the content for deduplication
            content_hash = hashlib.md5(result.content.encode()).hexdigest()
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    def _rank_hybrid_results(self, results: List[SearchResult], params: SearchParams) -> List[SearchResult]:
        """Rank hybrid search results based on relevance and search type"""
        def calculate_hybrid_score(result: SearchResult) -> float:
            base_score = result.relevance_score
            
            # Boost structured results for exact matches
            if result.search_type == SearchType.STRUCTURED_ONLY:
                base_score *= 1.2
            
            # Boost vector results for semantic similarity
            elif result.search_type == SearchType.VECTOR_ONLY:
                base_score *= 1.1
            
            # Apply parameter-based boosting
            if params.location and params.location.lower() in result.content.lower():
                base_score *= 1.15
            
            if params.property_type and params.property_type.lower() in result.content.lower():
                base_score *= 1.1
            
            return base_score
        
        # Sort by hybrid score
        results.sort(key=calculate_hybrid_score, reverse=True)
        return results
    
    def _update_metrics(self, execution_time: float):
        """Update search performance metrics"""
        total_searches = self.search_metrics["total_searches"]
        current_avg = self.search_metrics["avg_execution_time"]
        
        # Calculate running average
        new_avg = ((current_avg * (total_searches - 1)) + execution_time) / total_searches
        self.search_metrics["avg_execution_time"] = new_avg
    
    def get_search_metrics(self) -> Dict[str, Any]:
        """Get search performance metrics"""
        cache_hit_rate = 0
        if self.search_metrics["total_searches"] > 0:
            cache_hit_rate = (self.search_metrics["cache_hits"] / self.search_metrics["total_searches"]) * 100
        
        return {
            **self.search_metrics,
            "cache_hit_rate": cache_hit_rate,
            "search_distribution": {
                "vector": self.search_metrics["vector_searches"],
                "structured": self.search_metrics["structured_searches"],
                "hybrid": self.search_metrics["hybrid_searches"]
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check search engine health"""
        try:
            # Test PostgreSQL connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            postgres_status = "healthy"
        except Exception as e:
            postgres_status = f"unhealthy: {e}"
        
        try:
            # Test ChromaDB connection
            self.chroma_client.heartbeat()
            chroma_status = "healthy"
        except Exception as e:
            chroma_status = f"unhealthy: {e}"
        
        return {
            "status": "healthy" if postgres_status == "healthy" and chroma_status == "healthy" else "unhealthy",
            "postgres": postgres_status,
            "chromadb": chroma_status,
            "cache": self.cache_manager.health_check(),
            "metrics": self.get_search_metrics()
        }

# Global hybrid search engine instance
hybrid_search_engine = None

def get_hybrid_search_engine() -> HybridSearchEngine:
    """Get or create global hybrid search engine instance"""
    global hybrid_search_engine
    if hybrid_search_engine is None:
        hybrid_search_engine = HybridSearchEngine(
            database_url=os.getenv("DATABASE_URL"),
            chroma_host=os.getenv("CHROMA_HOST", "localhost"),
            chroma_port=int(os.getenv("CHROMA_PORT", "8000"))
        )
    return hybrid_search_engine
