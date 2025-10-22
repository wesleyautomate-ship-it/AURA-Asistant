from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class BrochureInput(BaseModel):
    title: Optional[str] = Field(None, description="Brochure title")
    subtitle: Optional[str] = Field(None, description="Optional subtitle")
    address: Optional[str] = Field(None, description="Property address")
    price: Optional[str] = Field(None, description="Price label e.g. $1,250,000")
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[float] = Field(None, ge=0)
    area_sqft: Optional[int] = Field(None, ge=0)
    property_type: Optional[str] = None
    highlights: Optional[List[str]] = Field(default=None, description="Key highlights")
    amenities: Optional[List[str]] = Field(default=None, description="Amenities list")


class BrochureResult(BaseModel):
    task_id: str
    file_url: str
    status: Literal["completed"]

class BrochureDraftCreate(BaseModel):
    templateKey: str = Field("clean-minimal")
    data: Optional[Dict[str, Any]] = None
    property_id: Optional[str] = None


class BrochureDraftUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None


class BrochureDraftOut(BaseModel):
    id: str
    data: Dict[str, Any]
    status: str
    download_url: Optional[str]
    created_at: str
    updated_at: str


class BrochureTemplateOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    file_path: str
    created_at: str
