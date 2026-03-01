"""
Chat Service - Main RAG Pipeline

This module provides the main ConversationRAGPipeline class that combines
all chat functionality through mixins:
- ConversationMixin: Conversation history management
- ValidationMixin: Document validation in Qdrant
- RetrievalMixin: RAG retrieval from vector store
- ContentMixin: Content generation using LLM
- TemplateMixin: Template formatting (HTML/Markdown)
- SourceMixin: Source extraction and mapping
"""

import asyncio
from typing import List, Dict, Optional, Any
from lib.logger import logging
from utils.database import doc_db
from services.qdrant_host import current_qdrant_client

# Import mixins
from services.chat_mixins import (
    ConversationMixin,
    ValidationMixin,
    RetrievalMixin,
    ContentMixin,
    TemplateMixin,
    SourceMixin,
    CONVERSATION_COLLECTION_NAME,
    SESSION_DOCS_COLLECTION_NAME,
    clean_text
)


class ConversationRAGPipeline(
    ConversationMixin,
    ValidationMixin,
    RetrievalMixin,
    ContentMixin,
    TemplateMixin,
    SourceMixin
):
    """
    Main RAG Pipeline with sequential message_id-based memory.
    
    This class combines functionality from multiple mixins to provide
    a complete chat pipeline with:
    - Conversation history tracking
    - Document validation
    - RAG-based retrieval
    - LLM content generation
    - Template formatting
    - Source highlighting
    """

    def __init__(self):
        self.conv_collection = doc_db[CONVERSATION_COLLECTION_NAME]
        self.session_collection = doc_db[SESSION_DOCS_COLLECTION_NAME]
        self.qdrant_client = current_qdrant_client

    async def process_query_v2(
        self,
        session_id: str,
        query: Optional[str],
        template: str,
        images: Optional[List[str]] = None,
        parameters: Optional[Dict[str, List]] = None,
        message_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main pipeline using message_id-only sequential logic.
        Returns structured JSON response with session_id, template, images, query, and structured content.
        """
        if message_id is None:
            message_id = await self.get_next_message_id(session_id)
        if images is None:
            images = []
        if parameters is None:
            parameters = {}

        try:
            # Get conversation history if not the first message
            if message_id == 1:
                context = []
            else:
                context = await self.get_conversation_history(session_id, message_id - 1)

            # Get PMC IDs first
            pmc_ids = await self.get_selected_pmc_ids(session_id)

            # Validate documents are indexed in Qdrant BEFORE proceeding
            # Will wait up to 180 seconds (3 minutes) for indexing to complete
            validation = await self.validate_documents_indexed(
                pmc_ids=pmc_ids,
                wait_for_indexing=True,
                max_wait_seconds=180,
                check_interval=3
            )

            if not validation["indexed"]:
                error_message = (
                    f"Cannot process chat: {validation['message']}. "
                    f"Indexed: {validation['indexed_count']}/{validation['total_count']}. "
                    f"Missing documents: {', '.join(validation['missing']) if validation['missing'] else 'none'}"
                )
                logging.error(error_message)

                timeout_msg = " The documents are taking too long to index." if validation.get("timeout") else ""

                return {
                    "session_id": session_id,
                    "selected_template": template,
                    "selected_images": images,
                    "user_query": query,
                    "parameters": parameters,
                    "response": {
                        "title": "Documents Not Ready",
                        "sections": [
                            {
                                "heading": "Indexing Issue",
                                "paragraph": f"Unable to process your request.{timeout_msg} {validation['message']}. Please try again later or contact support if this persists."
                            }
                        ]
                    },
                    "error": error_message,
                    "validation": validation
                }

            wait_msg = f" (waited {validation.get('wait_time', 0)}s)" if validation.get('wait_time', 0) > 0 else ""
            logging.info(f"✓ All documents validated - proceeding with chat{wait_msg}")
            logging.info(f"[MULTI-DOC] Session {session_id} has {len(pmc_ids)} documents: {pmc_ids}")

            # Determine if this is a follow-up Q&A (message_id > 1 means content was already generated)
            is_followup_qa = message_id > 1 and query and len(context) > 0

            if is_followup_qa:
                # ===== Q&A MODE: Simple RAG Q&A — 1 LLM call, plain text answer =====
                logging.info(f"[Q&A MODE] Session {session_id}, message_id={message_id} - Follow-up question: {query[:100]}...")

                # Retrieve relevant chunks for the question (embedding lookup only, no LLM call)
                rag_docs = await self.retriever(query, pmc_ids)
                logging.info(f"[Q&A MODE] Retrieved {len(rag_docs)} rag_docs for Q&A")

                # Single LLM call: generate plain text answer
                answer_text = await self.generate_qa_response(
                    user_question=query,
                    conversation_history=context,
                    rag_docs=rag_docs
                )
                logging.info(f"[Q&A MODE] Answer generated ({len(answer_text)} chars)")

                # Save conversation with the plain text Q&A response
                convo = {
                    "user": query,
                    "assistant": answer_text
                }

                await self.save_conversation(
                    session_id=session_id,
                    images=images,
                    parameters=parameters,
                    message_id=message_id,
                    conversation=convo,
                    rag_docs=rag_docs
                )
                logging.info(f"[Q&A MODE] Response ready for session={session_id}, message_id={message_id}")

                # Return plain text answer — no template, no highlights, no source mapping
                return {
                    "session_id": session_id,
                    "selected_template": template,
                    "selected_images": images,
                    "user_query": query,
                    "parameters": parameters,
                    "qa_answer": answer_text,
                    "response": {
                        "title": "",
                        "sections": []
                    }
                }

            else:
                # ===== CONTENT GENERATION MODE: First message - generate full content =====
                logging.info(f"[CONTENT GEN MODE] Session {session_id}, message_id={message_id}")

                rag_prompt = await self.generate_RAG_prompt(query=query, parameters=parameters, context=context)
                rag_docs = await self.retriever(rag_prompt, pmc_ids)
                
                # Log multi-document retrieval summary
                logging.info(f"[MULTI-DOC] Retrieved {len(rag_docs)} rag_docs for content generation")

                # Generate structured content with title and sections
                structured_content = await self.generate_structured_content(
                    query=query or rag_prompt,
                    rag_docs=rag_docs,
                    parameters=parameters,
                    context=context
                )

                # Initialize empty sources for all sections
                sections = structured_content.get("sections", [])
                for section in sections:
                    section["sources"] = []
                logging.info(f"Initialized {len(sections)} sections")

                # Save conversation with the structured response
                convo = {
                    "user": query or rag_prompt,
                    "assistant": structured_content
                }

                await self.save_conversation(
                    session_id=session_id,
                    images=images,
                    parameters=parameters,
                    message_id=message_id,
                    conversation=convo,
                    rag_docs=rag_docs
                )
                
                # Generate highlights synchronously (needed before source mapping)
                logging.info(f"[chat_service] Generating highlights for session={session_id}, message_id={message_id}")
                await self.trigger_highlight_generation_background(session_id, message_id)
                
                # Extract valid sources from rag_docs
                valid_sources = self._extract_valid_sources_from_rag_docs(rag_docs)
                logging.info(f"[chat_service] Valid sources from rag_docs: {list(valid_sources)}")
                
                # Fetch generated images and map to sections
                structured_content = await self.map_sources_to_sections(
                    session_id, message_id, structured_content, valid_sources
                )
                logging.info(f"[chat_service] Response ready for session={session_id}, message_id={message_id}")

                # Return the new structured JSON format
                return {
                    "session_id": session_id,
                    "selected_template": template,
                    "selected_images": images,
                    "user_query": query,
                    "parameters": parameters,
                    "response": structured_content
                }

        except Exception as e:
            logging.error(f"Error in pipeline: {str(e)}", exc_info=True)
            return {
                "session_id": session_id,
                "selected_template": template,
                "selected_images": images,
                "user_query": query,
                "parameters": parameters,
                "response": {
                    "title": "Error",
                    "sections": [
                        {
                            "heading": "Error Occurred",
                            "paragraph": "I encountered an error while processing your request. Please try again.",
                            "sources": []
                        }
                    ]
                },
                "error": str(e)
            }


# Export clean_text for backward compatibility
__all__ = ['ConversationRAGPipeline', 'clean_text']