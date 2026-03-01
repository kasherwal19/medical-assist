from pydantic import BaseModel, Field
from typing import List, Optional


class EndpointNameRequest(BaseModel):
    variable: str

class EndpointNameResponse(BaseModel):
    variable: str

class AuthorSchema(BaseModel):
    """Author information in API responses"""
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    full_name: Optional[str] = None
    affiliation: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "given_name": "John",
                "family_name": "Doe",
                "full_name": "John Doe",
                "affiliation": "Stanford University, Department of Medicine"
            }
        }


class ArticleMetadataSchema(BaseModel):
    """Article metadata in API responses"""
    pmc_id: str
    title: Optional[str] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    publisher: Optional[str] = None
    article_url: Optional[str] = None
    pdf_url: Optional[str] = None
    abstract: Optional[str] = None
    authors: List[AuthorSchema] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "pmc_id": "PMC1234567",
                "title": "Advances in Machine Learning for Healthcare",
                "journal": "Nature Medicine",
                "doi": "10.1038/s41591-023-12345-6",
                "publisher": "Nature Publishing Group",
                "article_url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/",
                "pdf_url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/pdf/",
                "abstract": "This study explores the application of machine learning...",
                "authors": [
                    {
                        "given_name": "John",
                        "family_name": "Doe",
                        "full_name": "John Doe",
                        "affiliation": "Stanford University"
                    }
                ]
            }
        }


class SearchPMCRequest(BaseModel):
    """Request schema for PubMed search endpoint"""
    keyword: str = Field(..., description="Search keyword or query term")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    limit: int = Field(5, ge=1, le=100, description="Number of results to return")
    timeframe: Optional[str] = Field(None, description="Time filter: '24h' or '7d'")

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "machine learning healthcare",
                "offset": 0,
                "limit": 5,
                "timeframe": "7d"
            }
        }


class SearchPMCResponse(BaseModel):
    """Response schema for PubMed search endpoint"""
    session_id: str
    keyword: str
    offset: int
    results_count: int
    results: List[ArticleMetadataSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "keyword": "machine learning healthcare",
                "offset": 0,
                "results_count": 5,
                "results": [
                    {
                        "pmc_id": "PMC1234567",
                        "title": "Article Title",
                        "journal": "Journal Name",
                        "doi": "10.1038/example",
                        "publisher": "Publisher",
                        "article_url": "https://...",
                        "pdf_url": "https://...",
                        "abstract": "Abstract text...",
                        "authors": []
                    }
                ]
            }
        }


class SelectArticlesRequest(BaseModel):
    """Request schema for selecting articles"""
    pmc_ids: List[str] = Field(..., description="List of PMC IDs to select")
    session_id: str = Field(..., description="Session ID from search response")

    class Config:
        json_schema_extra = {
            "example": {
                "pmc_ids": ["PMC1234567", "PMC7654321"],
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class SelectArticlesResponse(BaseModel):
    """Response schema for selected articles"""
    session_id: str
    selected_count: int
    selected_ids: List[str]
    not_found: List[str]
    selected_metadata: List[ArticleMetadataSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "selected_count": 2,
                "selected_ids": ["PMC1234567", "PMC7654321"],
                "not_found": [],
                "selected_metadata": []
            }
        }

# - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - 