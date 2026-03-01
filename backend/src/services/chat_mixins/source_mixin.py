"""
Source extraction and mapping mixin for chat service.
Handles extraction of valid sources from RAG docs and mapping to sections.
"""

import re
from typing import List, Dict, Any
from lib.logger import logging
from utils.database import doc_db


class SourceMixin:
    """Mixin class for source extraction and mapping methods."""

    async def trigger_highlight_generation_background(self, session_id: str, message_id: int):
        """Trigger highlight generation in background without blocking response"""
        try:
            from services.highlight_image import process_highlights_for_chat_response_wrapper
            logging.info(f"[chat_service] Triggering background highlights for session={session_id}, message_id={message_id}")
            await process_highlights_for_chat_response_wrapper(
                session_id=session_id,
                message_id=message_id
            )
            logging.info(f"[chat_service] Background highlights completed for session={session_id}, message_id={message_id}")
        except Exception as e:
            logging.error(f"[chat_service] Background highlight generation failed: {e}", exc_info=True)

    def _extract_valid_sources_from_rag_docs(self, rag_docs: List[str]) -> set:
        """
        Extract all valid (PMC_ID, PAGE_NUMBER) combinations that actually exist in rag_docs.
        Format: returns set of "PMCXXXXXXXX_PAGE_N" strings
        """
        valid_sources = set()
        pmc_ids_found = set()
        
        logging.info(f"[MULTI-DOC] Extracting sources from {len(rag_docs)} rag_docs")
        
        for idx, rag_doc in enumerate(rag_docs):
            try:
                # Parse Document_Name and PAGE_N from rag_doc markers
                # New format: "Document_Name filename.pdf <PMC12345678>, ..., PAGE_5\n--content=="
                # Old format: "Document_Name <PMC12345678>, ..., PAGE_5\n--content=="
                
                page_match = re.search(r"PAGE_(\d+)", rag_doc)
                if not page_match:
                    continue
                    
                page_num = page_match.group(1)
                
                # First try to extract PMC ID from <PMCXXXXXX> format (new format)
                pmc_match = re.search(r"<(PMC\d+)>", rag_doc)
                if pmc_match:
                    pmc_id = pmc_match.group(1)
                    source_key = f"{pmc_id}_PAGE_{page_num}"
                    valid_sources.add(source_key)
                    pmc_ids_found.add(pmc_id)
                    if idx < 5:  # Log first few for debugging
                        logging.debug(f"[MULTI-DOC] rag_doc #{idx}: Valid source (new format): {source_key}")
                else:
                    # Fallback: Try to extract PMC ID from document name (old format)
                    doc_match = re.search(r"Document_Name\s+([^,\n]+)", rag_doc)
                    if doc_match:
                        doc_name = doc_match.group(1).strip()
                        pmc_match_old = re.search(r"(PMC\d+)", doc_name)
                        if pmc_match_old:
                            pmc_id = pmc_match_old.group(1)
                            source_key = f"{pmc_id}_PAGE_{page_num}"
                            valid_sources.add(source_key)
                            pmc_ids_found.add(pmc_id)
                            if idx < 5:
                                logging.debug(f"[MULTI-DOC] rag_doc #{idx}: Valid source (old format): {source_key}")
            except Exception as e:
                logging.warning(f"[MULTI-DOC] Failed to parse rag_doc #{idx} source info: {e}")
                continue
        
        logging.info(
            f"[MULTI-DOC] Extracted {len(valid_sources)} valid sources from "
            f"{len(pmc_ids_found)} unique PMC IDs: {pmc_ids_found}"
        )
        return valid_sources

    async def map_sources_to_sections(
        self, 
        session_id: str, 
        message_id: int, 
        structured_content: Dict[str, Any],
        valid_sources: set = None
    ) -> Dict[str, Any]:
        """
        Map generated highlight images to sections based on source_refs.
        Validates source_refs against valid_sources and deduplicates URLs.
        Ensures ALL documents with sources are represented.
        """
        if valid_sources is None:
            valid_sources = set()
        
        logging.info(f"[MULTI-DOC] Starting source mapping with {len(valid_sources)} valid sources")
            
        try:
            # First, build a filename-to-PMC mapping from the session documents
            session_doc = await doc_db._db["session_docs"].find_one({"session_id": session_id})
            pmc_ids = session_doc.get("documents", []) if session_doc else []
            
            logging.info(f"[MULTI-DOC] Session has {len(pmc_ids)} documents: {pmc_ids}")
            
            filename_to_pmc = {}
            pmc_to_filename = {}
            
            # Get mappings from articles collection
            async for article in doc_db._db["articles"].find({"pmc_id": {"$in": pmc_ids}}):
                if article.get("filename") and article.get("pmc_id"):
                    filename_to_pmc[article["filename"]] = article["pmc_id"]
                    pmc_to_filename[article["pmc_id"]] = article["filename"]
            
            # Also check document_status collection
            async for doc_status in doc_db._db["document_status"].find({"pmc_id": {"$in": pmc_ids}}):
                if doc_status.get("filename") and doc_status.get("pmc_id"):
                    filename_to_pmc[doc_status["filename"]] = doc_status["pmc_id"]
                    pmc_to_filename[doc_status["pmc_id"]] = doc_status["filename"]
            
            logging.info(f"[MULTI-DOC] PMC to filename mapping: {pmc_to_filename}")
            
            # Fetch all generated images for this message
            cursor = doc_db._db["session_images"].find({
                "session_id": session_id,
                "message_id": message_id
            })
            
            # Build a lookup map with BOTH filename and PMC ID keys
            # {"PMCXXXXXX_PAGE_N": [url], "filename.pdf_PAGE_N": [url]}
            source_to_urls = {}
            docs_with_images = set()
            
            async for doc in cursor:
                doc_name = doc.get("document_name", "")
                
                # Get the PMC ID for this filename
                pmc_id = filename_to_pmc.get(doc_name)
                if pmc_id:
                    docs_with_images.add(pmc_id)
                
                for img in doc.get("images", []):
                    page_no = img.get("page_no")
                    url = img.get("url")
                    if page_no and url:
                        # Add with filename key
                        filename_key = f"{doc_name}_PAGE_{page_no}"
                        if filename_key not in source_to_urls:
                            source_to_urls[filename_key] = []
                        source_to_urls[filename_key].append(url)
                        
                        # Also add with PMC ID key if available
                        if pmc_id:
                            pmc_key = f"{pmc_id}_PAGE_{page_no}"
                            if pmc_key not in source_to_urls:
                                source_to_urls[pmc_key] = []
                            source_to_urls[pmc_key].append(url)
            
            logging.info(
                f"[MULTI-DOC] Built source lookup with {len(source_to_urls)} entries from "
                f"{len(docs_with_images)} documents with images: {docs_with_images}"
            )
            logging.debug(f"[MULTI-DOC] Source lookup keys: {list(source_to_urls.keys())[:20]}...")
            
            # Track which PMC IDs actually get mapped to sections
            pmc_ids_mapped = set()
            total_sources_mapped = 0
            
            # Map sources to each section
            for section_idx, section in enumerate(structured_content.get("sections", [])):
                source_refs = section.get("source_refs", [])
                source_objects = []
                hallucinated_refs = []
                
                # Use a set to track unique page identifiers we've already added
                unique_pages_added = set()
                
                logging.debug(f"[MULTI-DOC] Section {section_idx} '{section.get('heading', 'Unknown')}' has {len(source_refs)} source_refs: {source_refs}")
                
                for ref in source_refs:
                    # ref format: "PMCXXXXXXXX_PAGE_N"
                    # Validate against actual rag_docs if valid_sources provided
                    if valid_sources and ref not in valid_sources:
                        hallucinated_refs.append(ref)
                        logging.warning(
                            f"[MULTI-DOC] Section '{section.get('heading', 'Unknown')}' "
                            f"cites source_ref '{ref}' which was NOT in rag_docs"
                        )
                        continue
                    
                    if ref in source_to_urls:
                        # Get the first URL (latest SAS token) for this page
                        url = source_to_urls[ref][0]
                        # Only add if we haven't added this page yet (deduplication)
                        if ref not in unique_pages_added:
                            # Parse the ref to extract PMC ID and page number
                            parts = ref.split("_PAGE_")
                            if len(parts) == 2:
                                pmc_id_or_filename = parts[0]
                                page_no = int(parts[1])
                                
                                # Get the document name
                                document_name = pmc_to_filename.get(pmc_id_or_filename, pmc_id_or_filename)
                                
                                # Track that this PMC ID was used
                                if pmc_id_or_filename.startswith("PMC"):
                                    pmc_ids_mapped.add(pmc_id_or_filename)
                                
                                # Create a proper Source object
                                source_obj = {
                                    "url": url,
                                    "page_no": page_no,
                                    "document_name": document_name
                                }
                                source_objects.append(source_obj)
                                unique_pages_added.add(ref)
                                total_sources_mapped += 1
                                logging.debug(f"[MULTI-DOC] Mapped {ref} to image URL with metadata")
                    else:
                        logging.warning(f"[MULTI-DOC] No image found for source_ref: {ref}")
                
                # Replace source_refs with actual source objects
                section["sources"] = source_objects
                # Remove source_refs from final output
                section.pop("source_refs", None)
                
                if hallucinated_refs:
                    logging.warning(
                        f"[MULTI-DOC] Section '{section.get('heading', 'Unknown')}' had "
                        f"{len(hallucinated_refs)} hallucinated source(s): {hallucinated_refs}"
                    )
                
                logging.info(
                    f"[MULTI-DOC] Section '{section.get('heading', 'Unknown')}' - "
                    f"mapped {len(source_refs)} refs to {len(source_objects)} sources"
                )
            
            # Final summary logging
            logging.info(
                f"[MULTI-DOC] SOURCE MAPPING COMPLETE: "
                f"Total {total_sources_mapped} sources from {len(pmc_ids_mapped)}/{len(pmc_ids)} documents: {pmc_ids_mapped}"
            )
            
            # Warn if not all documents are represented
            missing_docs = set(pmc_ids) - pmc_ids_mapped
            if missing_docs:
                logging.warning(
                    f"[MULTI-DOC] WARNING: {len(missing_docs)} documents have NO sources in output: {missing_docs}"
                )
            
            return structured_content
            
        except Exception as e:
            logging.error(f"[MULTI-DOC] Failed to map sources to sections: {e}", exc_info=True)
            # On error, just clear source_refs and leave sources empty
            for section in structured_content.get("sections", []):
                section.pop("source_refs", None)
                section["sources"] = []
            return structured_content
