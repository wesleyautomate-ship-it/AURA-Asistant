"""
Knowledge Base Service
======================

This service provides comprehensive knowledge base management capabilities including:
- Company policies management
- Training materials organization
- Best practices documentation
- Knowledge search and retrieval
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from fastapi import HTTPException, status
import json

from app.domain.listings.brokerage_models import KnowledgeBase, Brokerage
from auth.models import User

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """Service for knowledge base management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================
    # KNOWLEDGE BASE CRUD OPERATIONS
    # =====================================================
    
    async def create_knowledge_item(
        self, 
        brokerage_id: int, 
        knowledge_data: Dict[str, Any], 
        created_by: int
    ) -> KnowledgeBase:
        """Create a new knowledge base item"""
        try:
            # Validate required fields
            required_fields = ['title', 'content']
            for field in required_fields:
                if not knowledge_data.get(field):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Field '{field}' is required"
                    )
            
            # Verify brokerage exists
            brokerage = self.db.query(Brokerage).filter(
                Brokerage.id == brokerage_id,
                Brokerage.is_active == True
            ).first()
            
            if not brokerage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brokerage not found"
                )
            
            # Create knowledge item
            knowledge_item = KnowledgeBase(
                brokerage_id=brokerage_id,
                title=knowledge_data['title'],
                content=knowledge_data['content'],
                category=knowledge_data.get('category'),
                tags=knowledge_data.get('tags', []),
                is_active=knowledge_data.get('is_active', True),
                created_by=created_by
            )
            
            self.db.add(knowledge_item)
            self.db.commit()
            self.db.refresh(knowledge_item)
            
            logger.info(f"Created knowledge item: {knowledge_item.title} (ID: {knowledge_item.id})")
            return knowledge_item
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating knowledge item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create knowledge item: {str(e)}"
            )
    
    async def get_knowledge_item(self, knowledge_id: int, brokerage_id: int) -> Optional[KnowledgeBase]:
        """Get knowledge base item by ID"""
        try:
            knowledge_item = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.id == knowledge_id,
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True
            ).first()
            
            if not knowledge_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Knowledge item not found"
                )
            
            return knowledge_item
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting knowledge item {knowledge_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get knowledge item: {str(e)}"
            )
    
    async def update_knowledge_item(
        self, 
        knowledge_id: int, 
        brokerage_id: int, 
        update_data: Dict[str, Any]
    ) -> KnowledgeBase:
        """Update knowledge base item"""
        try:
            knowledge_item = await self.get_knowledge_item(knowledge_id, brokerage_id)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(knowledge_item, field):
                    setattr(knowledge_item, field, value)
            
            knowledge_item.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(knowledge_item)
            
            logger.info(f"Updated knowledge item: {knowledge_item.title} (ID: {knowledge_item.id})")
            return knowledge_item
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating knowledge item {knowledge_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update knowledge item: {str(e)}"
            )
    
    async def delete_knowledge_item(self, knowledge_id: int, brokerage_id: int) -> bool:
        """Soft delete knowledge base item (set is_active to False)"""
        try:
            knowledge_item = await self.get_knowledge_item(knowledge_id, brokerage_id)
            
            knowledge_item.is_active = False
            knowledge_item.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted knowledge item: {knowledge_item.title} (ID: {knowledge_item.id})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting knowledge item {knowledge_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete knowledge item: {str(e)}"
            )
    
    async def list_knowledge_items(
        self, 
        brokerage_id: int, 
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[KnowledgeBase]:
        """List knowledge base items with filtering and search"""
        try:
            query = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True
            )
            
            # Apply filters
            if category:
                query = query.filter(KnowledgeBase.category == category)
            
            if tags:
                # Filter by tags (PostgreSQL array contains)
                for tag in tags:
                    query = query.filter(KnowledgeBase.tags.contains([tag]))
            
            if search_query:
                # Full-text search on title and content
                search_filter = or_(
                    KnowledgeBase.title.ilike(f"%{search_query}%"),
                    KnowledgeBase.content.ilike(f"%{search_query}%")
                )
                query = query.filter(search_filter)
            
            # Order by most recent
            query = query.order_by(KnowledgeBase.updated_at.desc())
            
            knowledge_items = query.offset(skip).limit(limit).all()
            return knowledge_items
            
        except Exception as e:
            logger.error(f"Error listing knowledge items: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list knowledge items: {str(e)}"
            )
    
    # =====================================================
    # CATEGORY MANAGEMENT
    # =====================================================
    
    async def get_categories(self, brokerage_id: int) -> List[Dict[str, Any]]:
        """Get all categories for a brokerage with item counts"""
        try:
            # Get distinct categories with counts
            categories = self.db.query(
                KnowledgeBase.category,
                func.count(KnowledgeBase.id).label('item_count')
            ).filter(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True,
                KnowledgeBase.category.isnot(None)
            ).group_by(KnowledgeBase.category).all()
            
            return [
                {
                    "category": cat.category,
                    "item_count": cat.item_count
                }
                for cat in categories
            ]
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get categories: {str(e)}"
            )
    
    async def get_tags(self, brokerage_id: int) -> List[Dict[str, Any]]:
        """Get all tags for a brokerage with usage counts"""
        try:
            # Get all knowledge items with tags
            knowledge_items = self.db.query(KnowledgeBase.tags).filter(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True,
                KnowledgeBase.tags.isnot(None)
            ).all()
            
            # Count tag usage
            tag_counts = {}
            for item in knowledge_items:
                if item.tags:
                    for tag in item.tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Convert to list sorted by usage
            tags = [
                {"tag": tag, "usage_count": count}
                for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            ]
            
            return tags
            
        except Exception as e:
            logger.error(f"Error getting tags: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get tags: {str(e)}"
            )
    
    # =====================================================
    # SEARCH AND RETRIEVAL
    # =====================================================
    
    async def search_knowledge(
        self, 
        brokerage_id: int, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Advanced search in knowledge base"""
        try:
            # Build search query
            search_filter = and_(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True,
                or_(
                    KnowledgeBase.title.ilike(f"%{query}%"),
                    KnowledgeBase.content.ilike(f"%{query}%")
                )
            )
            
            if category:
                search_filter = and_(search_filter, KnowledgeBase.category == category)
            
            # Execute search
            results = self.db.query(KnowledgeBase).filter(search_filter).limit(limit).all()
            
            # Format results with relevance scoring
            formatted_results = []
            for item in results:
                # Simple relevance scoring based on title match
                title_score = 2 if query.lower() in item.title.lower() else 0
                content_score = 1 if query.lower() in item.content.lower() else 0
                relevance_score = title_score + content_score
                
                formatted_results.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                    "category": item.category,
                    "tags": item.tags,
                    "relevance_score": relevance_score,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat()
                })
            
            # Sort by relevance score
            formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search knowledge base: {str(e)}"
            )
    
    async def get_knowledge_by_category(
        self, 
        brokerage_id: int, 
        category: str, 
        limit: int = 50
    ) -> List[KnowledgeBase]:
        """Get knowledge items by category"""
        try:
            knowledge_items = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.category == category,
                KnowledgeBase.is_active == True
            ).order_by(KnowledgeBase.updated_at.desc()).limit(limit).all()
            
            return knowledge_items
            
        except Exception as e:
            logger.error(f"Error getting knowledge by category: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get knowledge by category: {str(e)}"
            )
    
    # =====================================================
    # ANALYTICS AND INSIGHTS
    # =====================================================
    
    async def get_knowledge_analytics(self, brokerage_id: int) -> Dict[str, Any]:
        """Get knowledge base analytics"""
        try:
            # Get total items
            total_items = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True
            ).count()
            
            # Get categories
            categories = await self.get_categories(brokerage_id)
            
            # Get tags
            tags = await self.get_tags(brokerage_id)
            
            # Get recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_items = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True,
                KnowledgeBase.created_at >= thirty_days_ago
            ).count()
            
            # Get most active categories
            most_active_categories = self.db.query(
                KnowledgeBase.category,
                func.count(KnowledgeBase.id).label('item_count')
            ).filter(
                KnowledgeBase.brokerage_id == brokerage_id,
                KnowledgeBase.is_active == True,
                KnowledgeBase.category.isnot(None)
            ).group_by(KnowledgeBase.category).order_by(
                func.count(KnowledgeBase.id).desc()
            ).limit(5).all()
            
            analytics = {
                "brokerage_id": brokerage_id,
                "total_items": total_items,
                "recent_items_30_days": recent_items,
                "categories": categories,
                "tags": tags[:10],  # Top 10 tags
                "most_active_categories": [
                    {"category": cat.category, "item_count": cat.item_count}
                    for cat in most_active_categories
                ],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting knowledge analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get knowledge analytics: {str(e)}"
            )
    
    # =====================================================
    # BULK OPERATIONS
    # =====================================================
    
    async def bulk_import_knowledge(
        self, 
        brokerage_id: int, 
        knowledge_items: List[Dict[str, Any]], 
        created_by: int
    ) -> Dict[str, Any]:
        """Bulk import knowledge items"""
        try:
            created_count = 0
            failed_count = 0
            errors = []
            
            for item_data in knowledge_items:
                try:
                    await self.create_knowledge_item(brokerage_id, item_data, created_by)
                    created_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append({
                        "item": item_data.get('title', 'Unknown'),
                        "error": str(e)
                    })
            
            result = {
                "brokerage_id": brokerage_id,
                "total_items": len(knowledge_items),
                "created_count": created_count,
                "failed_count": failed_count,
                "errors": errors,
                "imported_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Bulk import completed: {created_count} created, {failed_count} failed")
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to bulk import knowledge: {str(e)}"
            )
    
    async def export_knowledge(self, brokerage_id: int, format: str = "json") -> Dict[str, Any]:
        """Export knowledge base data"""
        try:
            knowledge_items = await self.list_knowledge_items(brokerage_id, limit=10000)
            
            if format == "json":
                export_data = {
                    "brokerage_id": brokerage_id,
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_items": len(knowledge_items),
                    "items": [
                        {
                            "title": item.title,
                            "content": item.content,
                            "category": item.category,
                            "tags": item.tags,
                            "created_at": item.created_at.isoformat(),
                            "updated_at": item.updated_at.isoformat()
                        }
                        for item in knowledge_items
                    ]
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported export format: {format}"
                )
            
            return export_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error exporting knowledge: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to export knowledge: {str(e)}"
            )
