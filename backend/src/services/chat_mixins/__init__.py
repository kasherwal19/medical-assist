"""
Chat Service Mixins

This package contains mixin classes that together form the ConversationRAGPipeline.
Each mixin handles a specific concern:
- ConversationMixin: Conversation history management
- ValidationMixin: Document validation in Qdrant
- RetrievalMixin: RAG retrieval from vector store
- ContentMixin: Content generation using LLM
- TemplateMixin: Template formatting (HTML/Markdown)
- SourceMixin: Source extraction and mapping
"""

from .conversation_mixin import ConversationMixin
from .validation_mixin import ValidationMixin
from .retrieval_mixin import RetrievalMixin
from .content_mixin import ContentMixin
from .template_mixin import TemplateMixin
from .source_mixin import SourceMixin
from .constants import (
    CONVERSATION_COLLECTION_NAME,
    SESSION_DOCS_COLLECTION_NAME,
    DOCUMENT_TEXT_COLLECTION_NAME
)
from .utils import clean_text

__all__ = [
    'ConversationMixin',
    'ValidationMixin',
    'RetrievalMixin',
    'ContentMixin',
    'TemplateMixin',
    'SourceMixin',
    'CONVERSATION_COLLECTION_NAME',
    'SESSION_DOCS_COLLECTION_NAME',
    'DOCUMENT_TEXT_COLLECTION_NAME',
    'clean_text'
]
