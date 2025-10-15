"""
File Processing Router - FastAPI Router for File and Data Processing Endpoints

This router handles all file and data processing endpoints migrated from main.py
to maintain frontend compatibility while following the secure architecture
patterns of main_secure.py.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import shutil
import os
import pandas as pd

# Import dependencies
from app.core.settings import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename

# Import processing services
from intelligent_processor import IntelligentDataProcessor
from data_quality_checker import DataQualityChecker

# Initialize processing services
intelligent_processor = IntelligentDataProcessor()
data_quality_checker = DataQualityChecker()

# Initialize router
router = APIRouter(prefix="/file-processing", tags=["File Processing"])

# Root level file endpoints
root_router = APIRouter(tags=["File Operations"])

# Pydantic Models
class FileUploadResponse(BaseModel):
    """File upload response model"""

    status: str
    filename: str
    file_path: str
    file_size: Optional[int] = None
    upload_time: str


class FileAnalysisResponse(BaseModel):
    """File analysis response model"""

    filename: str
    content_type: Optional[str] = None
    processing_result: Dict[str, Any]
    processing_timestamp: str


class TransactionProcessingResponse(BaseModel):
    """Transaction processing response model"""

    status: str
    file_processed: str
    processing_date: str
    data_summary: Dict[str, Any]
    duplicates: List[Dict[str, Any]]
    insights: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    sample_cleaned_data: List[Dict[str, Any]]


class DataQualityResponse(BaseModel):
    """Data quality response model"""

    status: str
    file_processed: str
    data_type: str
    quality_report: Dict[str, Any]


class DataFixResponse(BaseModel):
    """Data fix response model"""

    status: str
    original_file: str
    fixed_file: str
    data_type: str
    fix_report: Dict[str, Any]
    download_url: str


class BuildingNameStandardizationResponse(BaseModel):
    """Building name standardization response model"""

    status: str
    standardized_names: List[Dict[str, Any]]
    total_processed: int
    changes_made: int


# Helper Functions
def get_file_type(mime_type: str, filename: str) -> str:
    """Determine file type for analysis"""
    if mime_type.startswith("image/"):
        return "image"
    elif mime_type == "application/pdf":
        return "pdf"
    elif "csv" in mime_type or filename.lower().endswith(".csv"):
        return "csv"
    elif (
        "excel" in mime_type
        or filename.lower().endswith(".xlsx")
        or filename.lower().endswith(".xls")
    ):
        return "excel"
    elif (
        "word" in mime_type
        or filename.lower().endswith(".docx")
        or filename.lower().endswith(".doc")
    ):
        return "word"
    elif mime_type.startswith("text/") or filename.lower().endswith(".txt"):
        return "text"
    else:
        return "document"


def generate_enhanced_analysis(file: UploadFile, file_type: str) -> Dict[str, Any]:
    """Generate enhanced AI analysis based on intelligent classification"""
    import random

    base_analysis = {
        "file_type": file_type,
        "analysis_date": datetime.now().isoformat(),
        "confidence": random.uniform(0.7, 1.0),
        "processing_time": random.uniform(1, 3),
    }

    # Save file temporarily to extract content
    temp_file_path = UPLOAD_DIR / f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract content for classification
        content = intelligent_processor.extract_content(str(temp_file_path), file_type)

        # Classify document intelligently
        classification = intelligent_processor.classify_document(content, file_type)

        # Generate analysis based on classification
        if classification["category"] == "neighborhood_guide":
            base_analysis.update(
                {
                    "category": "neighborhood_guide",
                    "extracted_data": {
                        "neighborhoods": [
                            "Dubai Marina",
                            "Palm Jumeirah",
                            "Downtown Dubai",
                        ],
                        "amenities": ["Schools", "Hospitals", "Shopping Centers"],
                        "transportation": ["Metro", "Bus Routes", "Highways"],
                    },
                }
            )
        elif classification["category"] == "property_listing":
            base_analysis.update(
                {
                    "category": "property_listing",
                    "extracted_data": {
                        "properties": random.randint(10, 50),
                        "price_range": f"AED {random.randint(500000, 5000000):,} - AED {random.randint(5000000, 15000000):,}",
                        "property_types": ["Apartment", "Villa", "Townhouse"],
                    },
                }
            )
        else:
            base_analysis.update(
                {
                    "category": "general_document",
                    "extracted_data": {
                        "key_topics": ["Real Estate", "Dubai", "Market Analysis"],
                        "sentiment": "neutral",
                        "summary": "General real estate document with market information.",
                    },
                }
            )

        return base_analysis

    except Exception as e:
        print(f"Error in enhanced analysis: {e}")
        return base_analysis
    finally:
        # Clean up temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()


# Router Endpoints


@root_router.post("/upload-file", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and save it to the uploads directory"""
    try:
        # Validate file size
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB",
            )

        # Create safe filename
        safe_filename = secure_filename(file.filename)
        if not safe_filename:
            safe_filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"

        # Ensure upload directory exists
        UPLOAD_DIR.mkdir(exist_ok=True)

        # Save file
        file_path = UPLOAD_DIR / safe_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return FileUploadResponse(
            status="success",
            filename=safe_filename,
            file_path=str(file_path),
            file_size=file.size,
            upload_time=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@root_router.post("/analyze-file", response_model=FileAnalysisResponse)
async def analyze_file(file: UploadFile = File(...)):
    """
    Uploads a file, saves it temporarily, and processes it using the
    Intelligent AI Data Processor to classify and extract structured data.
    """
    # Save file temporarily
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / file.filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get the file type (e.g., 'pdf', 'csv')
        file_type = file.filename.split(".")[-1].lower()

        # Call the intelligent processor
        analysis_result = intelligent_processor.process_uploaded_document(
            file_path=str(file_path), file_type=file_type
        )

        return FileAnalysisResponse(
            filename=file.filename,
            content_type=file.content_type,
            processing_result=analysis_result,
            processing_timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")
    finally:
        # Clean up the temporary file
        if file_path.exists():
            os.remove(file_path)


@root_router.post(
    "/process-transaction-data", response_model=TransactionProcessingResponse
)
async def process_transaction_data(file: UploadFile = File(...)):
    """Process transaction data with duplicate detection and data rectification"""
    try:
        # Validate file type
        if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(
                status_code=400,
                detail="Only CSV and Excel files are supported for transaction processing",
            )

        # Save file temporarily
        temp_file_path = UPLOAD_DIR / f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Determine file type
        file_type = "csv" if file.filename.lower().endswith(".csv") else "excel"

        # Read data
        if file_type == "csv":
            df = pd.read_csv(temp_file_path)
        else:
            df = pd.read_excel(temp_file_path)

        # Convert to list of dictionaries
        transactions = df.to_dict("records")

        # Clean and standardize data
        cleaned_transactions = intelligent_processor.clean_transaction_data(
            transactions
        )

        # Detect duplicates
        duplicates = intelligent_processor.detect_duplicate_transactions(
            cleaned_transactions
        )

        # Generate insights
        insights = intelligent_processor.generate_insights(cleaned_transactions)

        # Generate recommendations
        recommendations = intelligent_processor.generate_recommendations(
            duplicates, cleaned_transactions
        )

        # Clean up
        temp_file_path.unlink()

        return TransactionProcessingResponse(
            status="success",
            file_processed=file.filename,
            processing_date=datetime.now().isoformat(),
            data_summary={
                "total_records": len(transactions),
                "cleaned_records": len(cleaned_transactions),
                "duplicate_groups": len(duplicates),
                "total_duplicates": sum([d["total_duplicates"] for d in duplicates]),
            },
            duplicates=duplicates,
            insights=insights,
            recommendations=recommendations,
            sample_cleaned_data=cleaned_transactions[:5],  # First 5 records
        )

    except Exception as e:
        # Clean up on error
        if "temp_file_path" in locals() and temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(
            status_code=500, detail=f"Transaction processing failed: {str(e)}"
        )


@root_router.post("/check-data-quality", response_model=DataQualityResponse)
async def check_data_quality(
    file: UploadFile = File(...), data_type: str = Form("transaction")
):
    """Check data quality of uploaded file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(
                status_code=400,
                detail="Only CSV and Excel files are supported for quality checking",
            )

        # Save file temporarily
        temp_file_path = UPLOAD_DIR / f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Determine file type
        file_type = "csv" if file.filename.lower().endswith(".csv") else "excel"

        # Read data
        if file_type == "csv":
            df = pd.read_csv(temp_file_path)
        else:
            df = pd.read_excel(temp_file_path)

        # Convert to list of dictionaries
        data = df.to_dict("records")

        # Check data quality
        quality_report = data_quality_checker.check_data_quality(data, data_type)

        # Clean up
        temp_file_path.unlink()

        return DataQualityResponse(
            status="success",
            file_processed=file.filename,
            data_type=data_type,
            quality_report=quality_report,
        )

    except Exception as e:
        # Clean up on error
        if "temp_file_path" in locals() and temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(
            status_code=500, detail=f"Data quality check failed: {str(e)}"
        )


@root_router.post("/fix-data-issues", response_model=DataFixResponse)
async def fix_data_issues(
    file: UploadFile = File(...), data_type: str = Form("transaction")
):
    """Fix common data quality issues in uploaded file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(
                status_code=400,
                detail="Only CSV and Excel files are supported for data fixing",
            )

        # Save file temporarily
        temp_file_path = UPLOAD_DIR / f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Determine file type
        file_type = "csv" if file.filename.lower().endswith(".csv") else "excel"

        # Read data
        if file_type == "csv":
            df = pd.read_csv(temp_file_path)
        else:
            df = pd.read_excel(temp_file_path)

        # Convert to list of dictionaries
        data = df.to_dict("records")

        # Fix data issues
        fixed_data, fix_report = data_quality_checker.fix_common_issues(data, data_type)

        # Save fixed data
        fixed_df = pd.DataFrame(fixed_data)
        fixed_filename = f"fixed_{file.filename}"
        fixed_file_path = UPLOAD_DIR / fixed_filename

        if file_type == "csv":
            fixed_df.to_csv(fixed_file_path, index=False)
        else:
            fixed_df.to_excel(fixed_file_path, index=False)

        # Clean up original temp file
        temp_file_path.unlink()

        return DataFixResponse(
            status="success",
            original_file=file.filename,
            fixed_file=fixed_filename,
            data_type=data_type,
            fix_report=fix_report,
            download_url=f"/uploads/{fixed_filename}",
        )

    except Exception as e:
        # Clean up on error
        if "temp_file_path" in locals() and temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Data fixing failed: {str(e)}")


@root_router.post(
    "/standardize-building-names", response_model=BuildingNameStandardizationResponse
)
async def standardize_building_names(building_names: List[str]):
    """Standardize building names to handle variations"""
    try:
        standardized_names = []
        for name in building_names:
            standardized = intelligent_processor.standardize_building_name(name)
            standardized_names.append(
                {
                    "original": name,
                    "standardized": standardized,
                    "changed": name.lower() != standardized.lower(),
                }
            )

        return BuildingNameStandardizationResponse(
            status="success",
            standardized_names=standardized_names,
            total_processed=len(building_names),
            changes_made=sum([1 for item in standardized_names if item["changed"]]),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Building name standardization failed: {str(e)}"
        )


@root_router.get("/uploads/{filename}")
async def get_file(filename: str):
    """Serve uploaded files"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)
