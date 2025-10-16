from pydantic import BaseModel, Field
from typing import List, Optional, Literal


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

