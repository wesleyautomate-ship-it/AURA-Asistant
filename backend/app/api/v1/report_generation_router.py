"""
Report Generation Router for Dubai Real Estate RAG System

This module provides API endpoints for generating various types of reports:
- Market Reports
- CMA (Comparative Market Analysis) Reports
- Listing Presentations
- Terms & Conditions
- Property Brochures

Each report can be generated as a web page with a unique URL.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import logging

from ai_manager import AIEnhancementManager
from rag_service import EnhancedRAGService
from app.core.settings import DATABASE_URL, GOOGLE_API_KEY

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Report Generation"])

# Initialize AI manager and RAG service
ai_manager = AIEnhancementManager(DATABASE_URL, None)  # Will be initialized with model
rag_service = EnhancedRAGService()

# Store generated reports in memory (in production, use database)
generated_reports = {}


class ReportRequest(BaseModel):
    """Base model for report generation requests"""

    report_type: str
    title: str
    description: str
    parameters: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class MarketReportRequest(BaseModel):
    """Request model for market report generation"""

    area: str
    property_type: str
    time_period: str
    bedrooms: Optional[int] = None
    transaction_type: str = "both"  # "sale", "rent", "both"
    include_charts: bool = True
    include_comparisons: bool = True


class CMAReportRequest(BaseModel):
    """Request model for CMA report generation"""

    property_address: str
    property_type: str
    bedrooms: int
    bathrooms: int
    size_sqft: float
    current_price: Optional[float] = None
    comparable_count: int = 5


class ListingPresentationRequest(BaseModel):
    """Request model for listing presentation generation"""

    property_id: Optional[str] = None
    property_details: Dict[str, Any]
    presentation_type: str = "standard"  # "standard", "luxury", "investment"
    include_market_data: bool = True
    include_comparables: bool = True


class TermsConditionsRequest(BaseModel):
    """Request model for terms & conditions generation"""

    deal_type: str  # "sale", "rent", "investment"
    property_type: str
    client_type: str  # "buyer", "seller", "tenant", "landlord"
    special_terms: Optional[List[str]] = None


class ReportResponse(BaseModel):
    """Response model for report generation"""

    report_id: str
    title: str
    report_type: str
    web_url: str
    generated_date: datetime
    status: str
    preview: str


class ReportDetailResponse(BaseModel):
    """Detailed report response"""

    report_id: str
    title: str
    report_type: str
    content: str
    web_url: str
    generated_date: datetime
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]


def get_database_connection():
    """Get database connection"""
    engine = create_engine(DATABASE_URL)
    return engine


def generate_web_page_content(report_data: Dict[str, Any]) -> str:
    """Generate HTML content for the report web page"""

    # Dubai skyline image URL (generic)
    dubai_skyline_url = "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1200&h=400&fit=crop"

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['title']} - Dubai Real Estate Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('{dubai_skyline_url}') center/cover;
            opacity: 0.3;
            z-index: 1;
        }}
        
        .header-content {{
            position: relative;
            z-index: 2;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 300;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .report-meta {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .report-type {{
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        .report-date {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .content {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        
        .content h2 {{
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.8rem;
        }}
        
        .content h3 {{
            color: #333;
            margin: 1.5rem 0 0.5rem 0;
            font-size: 1.3rem;
        }}
        
        .content p {{
            margin-bottom: 1rem;
            text-align: justify;
        }}
        
        .content ul, .content ol {{
            margin: 1rem 0;
            padding-left: 2rem;
        }}
        
        .content li {{
            margin-bottom: 0.5rem;
        }}
        
        .highlight-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 4px 4px 0;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        
        .data-table th, .data-table td {{
            border: 1px solid #ddd;
            padding: 0.75rem;
            text-align: left;
        }}
        
        .data-table th {{
            background: #667eea;
            color: white;
        }}
        
        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 2rem;
        }}
        
        .footer p {{
            margin-bottom: 0.5rem;
        }}
        
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .report-meta {{
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>{report_data['title']}</h1>
            <p>Dubai Real Estate Market Analysis</p>
        </div>
    </div>
    
    <div class="container">
        <div class="report-meta">
            <div>
                <span class="report-type">{report_data['report_type'].upper()}</span>
            </div>
            <div class="report-date">
                Generated on {report_data['generated_date']}
            </div>
        </div>
        
        <div class="content">
            {report_data['content']}
        </div>
    </div>
    
    <div class="footer">
        <p><strong>Dubai Real Estate RAG System</strong></p>
        <p>AI-Powered Market Intelligence & Analysis</p>
        <p>Generated on {report_data['generated_date']}</p>
        <p><a href="/">Back to Dashboard</a></p>
    </div>
</body>
</html>
    """

    return html_template


@router.post("/market-report", response_model=ReportResponse)
async def generate_market_report(request: MarketReportRequest):
    """Generate a comprehensive market report for a specific area"""
    try:
        report_id = str(uuid.uuid4())

        # Get market data from database
        engine = get_database_connection()
        with engine.connect() as conn:
            # Get market statistics
            market_query = text(
                """
                SELECT 
                    AVG(price) as avg_price,
                    COUNT(*) as total_properties,
                    AVG(price_per_sqft) as avg_price_per_sqft,
                    MIN(price) as min_price,
                    MAX(price) as max_price
                FROM properties 
                WHERE location ILIKE :area 
                AND property_type ILIKE :property_type
                AND listing_status = 'live'
            """
            )

            if request.bedrooms:
                market_query = text(
                    """
                    SELECT 
                        AVG(price) as avg_price,
                        COUNT(*) as total_properties,
                        AVG(price_per_sqft) as avg_price_per_sqft,
                        MIN(price) as min_price,
                        MAX(price) as max_price
                    FROM properties 
                    WHERE location ILIKE :area 
                    AND property_type ILIKE :property_type
                    AND bedrooms = :bedrooms
                    AND listing_status = 'live'
                """
                )

            result = conn.execute(
                market_query,
                {
                    "area": f"%{request.area}%",
                    "property_type": f"%{request.property_type}%",
                    "bedrooms": request.bedrooms,
                },
            ).fetchone()

            market_data = {
                "avg_price": float(result.avg_price) if result.avg_price else 0,
                "total_properties": int(result.total_properties)
                if result.total_properties
                else 0,
                "avg_price_per_sqft": float(result.avg_price_per_sqft)
                if result.avg_price_per_sqft
                else 0,
                "min_price": float(result.min_price) if result.min_price else 0,
                "max_price": float(result.max_price) if result.max_price else 0,
            }

        # Generate report content using AI
        report_content = ai_manager.generate_market_report(
            neighborhood=request.area,
            property_type=request.property_type,
            time_period=request.time_period,
            market_data=market_data,
        )

        # Create report data
        report_data = {
            "report_id": report_id,
            "title": f"Market Report: {request.area} - {request.property_type}",
            "report_type": "Market Report",
            "content": report_content,
            "generated_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "parameters": request.dict(),
            "metadata": {
                "area": request.area,
                "property_type": request.property_type,
                "time_period": request.time_period,
                "bedrooms": request.bedrooms,
                "transaction_type": request.transaction_type,
            },
        }

        # Store report
        generated_reports[report_id] = report_data

        # Generate web URL
        web_url = f"/reports/view/{report_id}"

        return ReportResponse(
            report_id=report_id,
            title=report_data["title"],
            report_type=report_data["report_type"],
            web_url=web_url,
            generated_date=datetime.now(),
            status="completed",
            preview=report_content[:200] + "..."
            if len(report_content) > 200
            else report_content,
        )

    except Exception as e:
        logger.error(f"Error generating market report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate market report: {str(e)}"
        )


@router.post("/cma-report", response_model=ReportResponse)
async def generate_cma_report(request: CMAReportRequest):
    """Generate a Comparative Market Analysis report"""
    try:
        report_id = str(uuid.uuid4())

        # Get comparable properties from database
        engine = get_database_connection()
        with engine.connect() as conn:
            comps_query = text(
                """
                SELECT 
                    title, price, bedrooms, bathrooms, area_sqft, location,
                    price_per_sqft, listing_status
                FROM properties 
                WHERE property_type ILIKE :property_type
                AND bedrooms = :bedrooms
                AND bathrooms = :bathrooms
                AND area_sqft BETWEEN :min_size AND :max_size
                AND listing_status = 'live'
                ORDER BY ABS(area_sqft - :target_size)
                LIMIT :limit
            """
            )

            size_variance = request.size_sqft * 0.2  # 20% variance
            result = conn.execute(
                comps_query,
                {
                    "property_type": f"%{request.property_type}%",
                    "bedrooms": request.bedrooms,
                    "bathrooms": request.bathrooms,
                    "min_size": request.size_sqft - size_variance,
                    "max_size": request.size_sqft + size_variance,
                    "target_size": request.size_sqft,
                    "limit": request.comparable_count,
                },
            )

            comparable_properties = []
            for row in result:
                comparable_properties.append(
                    {
                        "title": row.title,
                        "price": float(row.price) if row.price else 0,
                        "bedrooms": int(row.bedrooms) if row.bedrooms else 0,
                        "bathrooms": int(row.bathrooms) if row.bathrooms else 0,
                        "area_sqft": float(row.area_sqft) if row.area_sqft else 0,
                        "location": row.location,
                        "price_per_sqft": float(row.price_per_sqft)
                        if row.price_per_sqft
                        else 0,
                    }
                )

        # Generate CMA content using AI
        subject_property = {
            "address": request.property_address,
            "property_type": request.property_type,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms,
            "size_sqft": request.size_sqft,
            "current_price": request.current_price,
        }

        cma_content = ai_manager.generate_cma_content(
            subject_property, comparable_properties
        )

        # Create report data
        report_data = {
            "report_id": report_id,
            "title": f"CMA Report: {request.property_address}",
            "report_type": "Comparative Market Analysis",
            "content": cma_content,
            "generated_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "parameters": request.dict(),
            "metadata": {
                "property_address": request.property_address,
                "property_type": request.property_type,
                "bedrooms": request.bedrooms,
                "bathrooms": request.bathrooms,
                "size_sqft": request.size_sqft,
                "comparable_count": len(comparable_properties),
            },
        }

        # Store report
        generated_reports[report_id] = report_data

        # Generate web URL
        web_url = f"/reports/view/{report_id}"

        return ReportResponse(
            report_id=report_id,
            title=report_data["title"],
            report_type=report_data["report_type"],
            web_url=web_url,
            generated_date=datetime.now(),
            status="completed",
            preview=cma_content[:200] + "..."
            if len(cma_content) > 200
            else cma_content,
        )

    except Exception as e:
        logger.error(f"Error generating CMA report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate CMA report: {str(e)}"
        )


@router.post("/listing-presentation", response_model=ReportResponse)
async def generate_listing_presentation(request: ListingPresentationRequest):
    """Generate a listing presentation"""
    try:
        report_id = str(uuid.uuid4())

        # Generate property brochure content using AI
        brochure_content = ai_manager.build_property_brochure(request.property_details)

        # Create report data
        report_data = {
            "report_id": report_id,
            "title": f"Listing Presentation: {request.property_details.get('title', 'Property')}",
            "report_type": "Listing Presentation",
            "content": brochure_content,
            "generated_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "parameters": request.dict(),
            "metadata": {
                "property_id": request.property_id,
                "presentation_type": request.presentation_type,
                "include_market_data": request.include_market_data,
                "include_comparables": request.include_comparables,
            },
        }

        # Store report
        generated_reports[report_id] = report_data

        # Generate web URL
        web_url = f"/reports/view/{report_id}"

        return ReportResponse(
            report_id=report_id,
            title=report_data["title"],
            report_type=report_data["report_type"],
            web_url=web_url,
            generated_date=datetime.now(),
            status="completed",
            preview=brochure_content[:200] + "..."
            if len(brochure_content) > 200
            else brochure_content,
        )

    except Exception as e:
        logger.error(f"Error generating listing presentation: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate listing presentation: {str(e)}"
        )


@router.post("/terms-conditions", response_model=ReportResponse)
async def generate_terms_conditions(request: TermsConditionsRequest):
    """Generate terms and conditions for a deal"""
    try:
        report_id = str(uuid.uuid4())

        # Create terms and conditions content
        terms_content = f"""
# Terms and Conditions - {request.deal_type.title()} Agreement

## 1. Parties
This agreement is entered into between the {request.client_type} and the property owner/agent.

## 2. Property Details
- **Property Type**: {request.property_type}
- **Transaction Type**: {request.deal_type.title()}
- **Client Type**: {request.client_type.title()}

## 3. General Terms

### 3.1 Payment Terms
- All payments must be made in UAE Dirhams (AED)
- Payment schedule to be agreed upon by both parties
- Late payments may incur penalties as per UAE law

### 3.2 Property Condition
- Property will be delivered in the condition as described
- Any defects must be reported within 7 days of possession
- Maintenance responsibilities as per UAE real estate regulations

### 3.3 Legal Compliance
- All terms subject to UAE real estate laws and regulations
- RERA compliance mandatory for all transactions
- Dispute resolution through Dubai Courts or RERA

## 4. Special Terms
{chr(10).join([f"- {term}" for term in request.special_terms]) if request.special_terms else "- No special terms specified"}

## 5. Termination
- Agreement may be terminated with 30 days written notice
- Early termination fees may apply
- Force majeure clauses apply

## 6. Governing Law
This agreement is governed by the laws of the United Arab Emirates and the Emirate of Dubai.

## 7. Signatures
Both parties must sign this agreement for it to be legally binding.

---
*Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}*
*Dubai Real Estate RAG System*
        """

        # Create report data
        report_data = {
            "report_id": report_id,
            "title": f"Terms & Conditions - {request.deal_type.title()} Agreement",
            "report_type": "Terms & Conditions",
            "content": terms_content,
            "generated_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "parameters": request.dict(),
            "metadata": {
                "deal_type": request.deal_type,
                "property_type": request.property_type,
                "client_type": request.client_type,
                "special_terms_count": len(request.special_terms)
                if request.special_terms
                else 0,
            },
        }

        # Store report
        generated_reports[report_id] = report_data

        # Generate web URL
        web_url = f"/reports/view/{report_id}"

        return ReportResponse(
            report_id=report_id,
            title=report_data["title"],
            report_type=report_data["report_type"],
            web_url=web_url,
            generated_date=datetime.now(),
            status="completed",
            preview=terms_content[:200] + "..."
            if len(terms_content) > 200
            else terms_content,
        )

    except Exception as e:
        logger.error(f"Error generating terms and conditions: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate terms and conditions: {str(e)}"
        )


@router.get("/view/{report_id}", response_class=HTMLResponse)
async def view_report(report_id: str):
    """View a generated report as a web page"""
    try:
        if report_id not in generated_reports:
            raise HTTPException(status_code=404, detail="Report not found")

        report_data = generated_reports[report_id]
        html_content = generate_web_page_content(report_data)

        return HTMLResponse(content=html_content)

    except Exception as e:
        logger.error(f"Error viewing report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to view report: {str(e)}")


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report_details(report_id: str):
    """Get detailed information about a generated report"""
    try:
        if report_id not in generated_reports:
            raise HTTPException(status_code=404, detail="Report not found")

        report_data = generated_reports[report_id]

        return ReportDetailResponse(
            report_id=report_data["report_id"],
            title=report_data["title"],
            report_type=report_data["report_type"],
            content=report_data["content"],
            web_url=f"/reports/view/{report_id}",
            generated_date=datetime.now(),
            parameters=report_data["parameters"],
            metadata=report_data["metadata"],
        )

    except Exception as e:
        logger.error(f"Error getting report details: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get report details: {str(e)}"
        )


@router.get("/", response_model=List[ReportResponse])
async def list_reports():
    """List all generated reports"""
    try:
        reports = []
        for report_id, report_data in generated_reports.items():
            reports.append(
                ReportResponse(
                    report_id=report_data["report_id"],
                    title=report_data["title"],
                    report_type=report_data["report_type"],
                    web_url=f"/reports/view/{report_id}",
                    generated_date=datetime.now(),
                    status="completed",
                    preview=report_data["content"][:200] + "..."
                    if len(report_data["content"]) > 200
                    else report_data["content"],
                )
            )

        return reports

    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """Delete a generated report"""
    try:
        if report_id not in generated_reports:
            raise HTTPException(status_code=404, detail="Report not found")

        del generated_reports[report_id]

        return {"message": "Report deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete report: {str(e)}"
        )
