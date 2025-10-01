"""
Property Detection Router for Dubai Real Estate RAG System

This router handles property detection, document processing, and building-specific data queries.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional, List
import logging
from pydantic import BaseModel

from services.property_detection_service import PropertyDetectionService
from services.document_processing_service import DocumentProcessingService
from auth import get_current_user
from auth.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/property", tags=["property-detection"])

# Initialize services
property_detector = PropertyDetectionService()
document_processor = DocumentProcessingService()

# Request/Response Models
class PropertyDetectionRequest(BaseModel):
    message: str

class PropertyDetectionResponse(BaseModel):
    building_name: Optional[str] = None
    unit_number: Optional[str] = None
    community: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    size_sqft: Optional[float] = None
    confidence: float = 0.0
    detected_entities: List[str] = []
    address: Optional[str] = None

class PropertySearchRequest(BaseModel):
    building_name: Optional[str] = None
    community: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class BuildingDataResponse(BaseModel):
    building_name: str
    community: str
    total_properties: int
    average_price: Optional[float] = None
    price_range: Dict[str, float] = {}
    property_types: List[str] = []
    transactions: List[Dict[str, Any]] = []

class CommunityMarketDataResponse(BaseModel):
    community: str
    total_properties: int
    average_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    average_price_per_sqft: Optional[float] = None
    average_bedrooms: Optional[float] = None
    average_bathrooms: Optional[float] = None
    average_size: Optional[float] = None
    last_updated: str

@router.post("/detect", response_model=PropertyDetectionResponse)
async def detect_property(
    request: PropertyDetectionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Detect property information from a user message
    """
    try:
        logger.info(f"Property detection request from user {current_user.id}: {request.message}")
        
        # Detect property information
        property_info = property_detector.detect_property_from_request(request.message)
        
        if not property_info:
            raise HTTPException(status_code=400, detail="No property information detected")
        
        # Query database for additional property details
        db_property = property_detector.query_property_from_database(property_info)
        
        # Enhance response with database data
        response_data = {
            "building_name": property_info.get("building_name"),
            "unit_number": property_info.get("unit_number"),
            "community": property_info.get("community"),
            "property_type": property_info.get("property_type"),
            "bedrooms": property_info.get("bedrooms"),
            "bathrooms": property_info.get("bathrooms"),
            "size_sqft": property_info.get("size_sqft"),
            "confidence": property_info.get("confidence", 0.0),
            "detected_entities": property_info.get("detected_entities", []),
            "address": property_info.get("address")
        }
        
        # Add database property data if available
        if db_property:
            response_data.update({
                "bedrooms": response_data["bedrooms"] or db_property.get("bedrooms"),
                "bathrooms": response_data["bathrooms"] or db_property.get("bathrooms"),
                "size_sqft": response_data["size_sqft"] or db_property.get("square_feet"),
                "address": response_data["address"] or db_property.get("address")
            })
        
        return PropertyDetectionResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error in property detection: {e}")
        raise HTTPException(status_code=500, detail=f"Property detection failed: {str(e)}")

@router.post("/search", response_model=List[Dict[str, Any]])
async def search_properties(
    request: PropertySearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search for properties based on criteria
    """
    try:
        logger.info(f"Property search request from user {current_user.id}: {request.dict()}")
        
        # Convert request to property info format
        property_info = {
            "building_name": request.building_name,
            "community": request.community,
            "property_type": request.property_type,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms
        }
        
        # Query database
        db_property = property_detector.query_property_from_database(property_info)
        
        if db_property:
            return [db_property]
        else:
            return []
        
    except Exception as e:
        logger.error(f"Error in property search: {e}")
        raise HTTPException(status_code=500, detail=f"Property search failed: {str(e)}")

@router.get("/building", response_model=BuildingDataResponse)
async def get_building_data(
    building_name: str,
    community: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get building-specific transaction data
    """
    try:
        logger.info(f"Building data request from user {current_user.id}: {building_name} in {community}")
        
        # Get building-specific transactions
        transactions = property_detector.get_building_specific_transactions(building_name, community)
        
        if not transactions:
            raise HTTPException(status_code=404, detail="No data found for this building")
        
        # Calculate building statistics
        prices = [t.get('price', 0) for t in transactions if t.get('price')]
        property_types = list(set([t.get('property_type') for t in transactions if t.get('property_type')]))
        
        response_data = {
            "building_name": building_name,
            "community": community or "Unknown",
            "total_properties": len(transactions),
            "average_price": sum(prices) / len(prices) if prices else None,
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0
            },
            "property_types": property_types,
            "transactions": transactions
        }
        
        return BuildingDataResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting building data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get building data: {str(e)}")

@router.get("/market/community/{community}", response_model=CommunityMarketDataResponse)
async def get_community_market_data(
    community: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get market data for a specific community
    """
    try:
        logger.info(f"Community market data request from user {current_user.id}: {community}")
        
        # Get community market data
        market_data = property_detector.get_community_market_data(community)
        
        if not market_data:
            raise HTTPException(status_code=404, detail="No market data found for this community")
        
        return CommunityMarketDataResponse(**market_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting community market data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get community market data: {str(e)}")

@router.post("/document/process")
async def process_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Process uploaded document to extract property information
    """
    try:
        logger.info(f"Document processing request from user {current_user.id}: {file.filename}")
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8', errors='ignore')
        
        # Process document
        result = document_processor.process_document(content_str, file.filename)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@router.get("/document/{document_id}")
async def get_document_processing_result(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get document processing results by ID
    """
    try:
        logger.info(f"Document result request from user {current_user.id}: {document_id}")
        
        # This would typically fetch from a database or cache
        # For now, return a placeholder
        return {
            "document_id": document_id,
            "status": "processed",
            "message": "Document processing results would be retrieved here"
        }
        
    except Exception as e:
        logger.error(f"Error getting document result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document result: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for property detection service
    """
    return {
        "status": "healthy",
        "service": "property-detection",
        "version": "1.0.0"
    }
