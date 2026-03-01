from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: str
    user_query: Optional[str] = None
    images: Optional[List[str]] = []
    parameters: Optional[Dict[str, List]]
    template: str
    message_id: int = None


class Source(BaseModel):
    """A source reference with document metadata"""
    url: str = Field(..., description="The URL to the highlighted source image")
    page_no: int = Field(..., description="The page number in the document")
    document_name: str = Field(..., description="The name of the source document")


class ContentSection(BaseModel):
    """A section of the response containing a heading and paragraph"""
    heading: str = Field(..., description="The heading for this section")
    paragraph: str = Field(..., description="The paragraph content for this section")
    sources: List[Source] = Field(default_factory=list, description="List of highlighted source references with metadata")


class StructuredContent(BaseModel):
    """Structured content response with title and sections"""
    title: str = Field(..., description="The main title of the response")
    sections: List[ContentSection] = Field(default_factory=list, description="List of content sections with headings and paragraphs")


class ChatResponse(BaseModel):
    """Structured response format for the chat endpoint"""
    session_id: str = Field(..., description="The session identifier")
    selected_template: str = Field(..., description="The template that was selected")
    selected_images: List[str] = Field(default_factory=list, description="List of selected image URLs")
    user_query: Optional[str] = Field(None, description="The original user query")
    parameters: Optional[Dict[str, List]] = Field(None, description="The parameters selected by the user")
    response: StructuredContent = Field(..., description="The structured content response")
    qa_answer: Optional[str] = Field(None, description="Plain text Q&A answer for follow-up questions")