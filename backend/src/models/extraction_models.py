from datetime import datetime
from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field
from utils.database import get_database_connection

class ExtractionRequest(BaseModel):
    session_id: str
    documents: List[str]
    user_upload: bool = False

class ExtractionResponse(BaseModel):
    response: str

db_client = get_database_connection()

class StatusRequest(BaseModel):
    pmc_ids: List[str]

class DocumentStatusInfo(BaseModel):
    pmc_id: str
    status: str

class DocumentStatus(BaseModel):
    """Model for the Document Processing Status"""
    filename: str
    pmc_id: str = Field(..., description="PubMed Central ID (e.g., PMC1234567)")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    s3_csv_key: Optional[str] = None
    s3_key: Optional[str] = None
    status: Literal["SUCCESS", "FAILED"]
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        example_schema = {
            "filename": "PMC12701663.pdf",
            "pmc_id": "PMC12701663",
            "createdAt": "2025-12-16T11:57:40.690+00:00",
            "s3_csv_key": "Epocrates//highlight_helper_tables/PMC12701663.csv",
            "s3_key": "Epocrates/documents/PMC12701663.pdf",
            "status": "SUCCESS",
            "updatedAt": "2025-12-16T11:57:40.690+00:00"
        }

class SessionInfo(BaseModel):
    """Model for Session wise user selected Documents"""
    session_id: str = Field(..., description="An unique ID generated for each session")
    documents: List[str] = Field(..., description="A list of PubMed Central ID's (e.g., [PMC1234567,...])")

    class Config:
        example_schema = {
            "session_id": "faint",
            "documents": [
                "PMC6494975",
                "PMC12370137"
            ]
        }