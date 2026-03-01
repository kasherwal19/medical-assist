from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class ImageSchema(BaseModel):
    mongo_id: Optional[Any] = Field(None, alias="_id")
    id: str
    filename: str
    speciality: Optional[str] = None
    disease_area: Optional[List[str]] = None
    azure_url: Optional[str] = None
    blob_key: Optional[str] = None
    content_type: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both "_id" and "mongo_id"


class ImageSearchResponse(BaseModel):
    total: int
    results: List[ImageSchema]


class ImageSearchRequest(BaseModel):
    speciality: Optional[str] = "all"
    disease_area: Optional[str] = "all"

