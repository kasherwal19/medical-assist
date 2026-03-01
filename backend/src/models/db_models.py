from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime


class Author(BaseModel):
    """Author information for a research article"""
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    full_name: Optional[str] = None
    affiliation: Optional[str] = None


class Article(BaseModel):
    """MongoDB model for storing PubMed Central articles"""
    pmc_id: str = Field(..., description="PubMed Central ID (e.g., PMC1234567)")
    title: Optional[str] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    publisher: Optional[str] = None
    article_url: Optional[str] = None
    pdf_url: Optional[str] = None
    abstract: Optional[str] = None
    authors: List[Author] = Field(default_factory=list, description="List of article authors")
    session_id: Optional[str] = Field(None, description="Session ID when article was searched")
    keyword: Optional[str] = Field(None, description="Search keyword used to find this article")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "pmc_id": "PMC1234567",
                "title": "Example Research Article",
                "journal": "Nature Medicine",
                "doi": "10.1038/example",
                "publisher": "Nature Publishing Group",
                "article_url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/",
                "pdf_url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/pdf/",
                "abstract": "This is an example abstract...",
                "authors": [
                    {
                        "given_name": "John",
                        "family_name": "Doe",
                        "full_name": "John Doe",
                        "affiliation": "University of Example"
                    }
                ],
                "session_id": "abc123",
                "keyword": "machine learning",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class SearchArticle(BaseModel):
    """Model for Search PMC Endpoint"""
    keyword: str
    offset: Optional[int] = 0
    limit: int = 5
    timeframe: Optional[Literal["24h", "7d"]] = None


