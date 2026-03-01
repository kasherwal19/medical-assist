"""
Content generation mixin for chat service.
Handles LLM-based content generation for chat responses.
"""

import json
import re
from typing import List, Dict, Optional, Any
from lib.logger import logging
from services.llm_service import brain
from utils.prompt import CONTENT_GEN_PROMPT, STRUCTURED_CONTENT_GEN_PROMPT, QA_RESPONSE_PROMPT


class ContentMixin:
    """Mixin class for content generation methods."""

    async def generate_content(
        self,
        query: str,
        rag_docs: List[str] = [],
        parameters: Optional[Dict[str, List]] = None,
        context: List[Dict] = []
    ) -> str:
        """
        Generate final response using LLM with RAG documents and context.
        """
        try:
            refined_prompt = CONTENT_GEN_PROMPT.format(
                query=query,
                parameters=parameters or {},
                rag_documents=rag_docs
            )

            response = await brain.call_invoke(prompt=refined_prompt)

            generated_content = response.content.strip()
            logging.info(f"Content generated successfully ({len(generated_content)} chars)")
            return generated_content

        except Exception as e:
            logging.error(f"Content Generation Failed: {str(e)}", exc_info=True)
            return ""

    async def generate_structured_content(
        self,
        query: str,
        rag_docs: List[str] = [],
        parameters: Optional[Dict[str, List]] = None,
        context: List[Dict] = []
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response using LLM with RAG documents and context.
        Returns a dict with 'title' and 'sections' (list of {heading, paragraph}).
        """
        try:
            # Log what PMC IDs are being sent to LLM
            pmc_ids_in_rag = set()
            for doc in rag_docs:
                pmc_match = re.search(r"<(PMC\d+)>", doc)
                if pmc_match:
                    pmc_ids_in_rag.add(pmc_match.group(1))
            logging.info(f"[MULTI-DOC] Sending {len(rag_docs)} rag_docs to LLM from {len(pmc_ids_in_rag)} unique PMC IDs: {pmc_ids_in_rag}")
            
            # Prepend explicit PMC ID list to help LLM track all documents
            pmc_list_header = ""
            if len(pmc_ids_in_rag) > 1:
                pmc_list_header = (
                    f"\n\n=== IMPORTANT: THIS RESPONSE MUST CITE ALL {len(pmc_ids_in_rag)} DOCUMENTS ===\n"
                    f"Documents you MUST cite: {', '.join(sorted(pmc_ids_in_rag))}\n"
                    f"Your response will be REJECTED if any of these PMC IDs are missing from source_refs.\n"
                    f"=======================================================================\n\n"
                )
            
            rag_docs_text = pmc_list_header + "\n\n".join(rag_docs)
            
            refined_prompt = STRUCTURED_CONTENT_GEN_PROMPT.format(
                query=query,
                parameters=parameters or {},
                rag_documents=rag_docs_text
            )

            response = await brain.call_invoke(prompt=refined_prompt)
            response_text = response.content.strip()
            
            # Clean up potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON response
            try:
                structured_content = json.loads(response_text)
                
                # Validate structure
                if "title" not in structured_content:
                    structured_content["title"] = "Clinical Summary"
                if "sections" not in structured_content:
                    structured_content["sections"] = []
                
                # Track which PMC IDs the LLM cited
                pmc_ids_cited = set()
                
                # Ensure sections have the correct structure
                validated_sections = []
                for section in structured_content.get("sections", []):
                    if isinstance(section, dict) and "heading" in section and "paragraph" in section:
                        source_refs = section.get("source_refs", [])
                        
                        # Track cited PMC IDs
                        for ref in source_refs:
                            pmc_match = re.search(r"(PMC\d+)", ref)
                            if pmc_match:
                                pmc_ids_cited.add(pmc_match.group(1))
                        
                        validated_sections.append({
                            "heading": str(section["heading"]),
                            "paragraph": str(section["paragraph"]),
                            "source_refs": source_refs  # Preserve source references from LLM
                        })
                
                structured_content["sections"] = validated_sections
                
                # Log multi-document citation analysis
                missing_pmc_ids = pmc_ids_in_rag - pmc_ids_cited
                if missing_pmc_ids:
                    logging.warning(
                        f"[MULTI-DOC] LLM did NOT cite {len(missing_pmc_ids)} documents: {missing_pmc_ids}. "
                        f"Cited: {pmc_ids_cited}"
                    )
                else:
                    logging.info(f"[MULTI-DOC] LLM cited ALL {len(pmc_ids_cited)} documents: {pmc_ids_cited}")
                
                logging.info(f"Structured content generated successfully - Title: {structured_content['title'][:50]}..., Sections: {len(structured_content['sections'])}")
                return structured_content
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse structured content JSON: {e}")
                # Fallback: create structured content from the raw response
                return {
                    "title": "Clinical Summary",
                    "sections": [
                        {
                            "heading": "Overview",
                            "paragraph": response_text,
                            "source_refs": []
                        }
                    ]
                }

        except Exception as e:
            logging.error(f"Structured Content Generation Failed: {str(e)}", exc_info=True)
            return {
                "title": "Error",
                "sections": [
                    {
                        "heading": "Error",
                        "paragraph": "Failed to generate content. Please try again.",
                        "source_refs": []
                    }
                ]
            }

    async def generate_qa_response(
        self,
        user_question: str,
        conversation_history: List[Dict],
        rag_docs: List[str] = [],
    ) -> str:
        """
        Generate a direct plain-text Q&A response based on previously generated content and RAG docs.
        Used for follow-up questions after initial content generation.
        Returns a plain text string answer (single LLM call).
        """
        try:
            # Build conversation history string from previous messages
            history_parts = []
            for entry in conversation_history:
                if isinstance(entry, dict):
                    user_msg = entry.get("user", "")
                    assistant_msg = entry.get("assistant", "")
                    if user_msg:
                        history_parts.append(f"User: {user_msg}")
                    if assistant_msg:
                        if isinstance(assistant_msg, dict):
                            # Structured content - flatten for context
                            title = assistant_msg.get("title", "")
                            sections = assistant_msg.get("sections", [])
                            content_parts = [f"Title: {title}"]
                            for section in sections:
                                heading = section.get("heading", "")
                                paragraph = section.get("paragraph", "")
                                content_parts.append(f"{heading}: {paragraph}")
                            history_parts.append(f"Assistant: {chr(10).join(content_parts)}")
                        else:
                            history_parts.append(f"Assistant: {assistant_msg}")

            conversation_history_str = "\n\n".join(history_parts) if history_parts else "No previous conversation."

            refined_prompt = QA_RESPONSE_PROMPT.format(
                conversation_history=conversation_history_str,
                rag_documents="\n\n".join(rag_docs) if rag_docs else "No additional documents.",
                user_question=user_question
            )

            response = await brain.call_invoke(prompt=refined_prompt)
            answer_text = response.content.strip()

            logging.info(f"Q&A plain text response generated ({len(answer_text)} chars)")
            return answer_text

        except Exception as e:
            logging.error(f"Q&A Response Generation Failed: {str(e)}", exc_info=True)
            return "I encountered an error while processing your question. Please try again."
