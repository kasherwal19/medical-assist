from pydantic import BaseModel, Field
from typing import List, Optional


class SourceRequest(BaseModel):
    """Request Model for fetching highlighted sources"""
    session_id: str = Field(..., description="Unique session identifier", min_length=1)
    message_id: int = Field(default=1, description="message id number", ge=0)

    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123xyz",
                "message_id": 1
            }
        }


class SourceMetadata(BaseModel):
    """Metadata for a single source image"""
    url: Optional[str] = Field(None, description="Image URL or data URL")
    page_no: Optional[int] = Field(None, description="Page number")
    document_name: Optional[str] = Field(None, description="Source document name (PDF)")


class SourceResponse(BaseModel):
    """Response Model for fetching highlighted sources"""
    session_id: str = Field(..., description="Session identifier from request")
    message_id: int = Field(..., description="message id number from request")
    source_url: List[SourceMetadata] = Field(default_factory=list, description="List of image metadata")
    count: int = Field(default=0, description="Number of images returned")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123xyz",
                "message_id": 1,
                "source_url": [
                    {
                        "url": "https://blob.storage.azure.net/...",
                        "page_no": 2,
                        "document_name": "Page_2.png"
                    }
                ],
                "count": 1
            }
        }


class HighlightRequest(BaseModel):
    """Request Model for triggering highlighting"""
    session_id: str = Field(..., description="Session identifier to process", min_length=1)
    message_id: int = Field(default=1, description="message id number", ge=0)

    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123xyz",
                "message_id": 1
            }
        }


class HighlightResponse(BaseModel):
    """Response Model for highlighting operation"""
    session_id: str = Field(..., description="Session identifier")
    message_id: int = Field(..., description="message id number")
    status: str = Field(..., description="Processing status: success/error")
    documents_processed: int = Field(default=0, description="Number of documents processed")
    total_highlights: int = Field(default=0, description="Total highlights created")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123xyz",
                "message_id": 1,
                "status": "success",
                "documents_processed": 3,
                "total_highlights": 15,
                "errors": []
            }
        }