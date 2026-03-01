"""
Document validation mixin for chat service.
Handles validation of documents indexed in Qdrant.
"""

import asyncio
from typing import List, Dict, Any
from lib.logger import logging
from qdrant_client import models
from .constants import DOCUMENT_TEXT_COLLECTION_NAME


class ValidationMixin:
    """Mixin class for document validation methods."""

    async def get_selected_pmc_ids(self, session_id: str) -> List[str]:
        """
        Retrieve PMC document IDs associated with the session.
        """
        try:
            result = await self.session_collection.find_one(
                filter={
                    "session_id": session_id,
                    "documents": {"$exists": True}
                }
            )

            if result:
                pmc_ids = result.get("documents", [])
                logging.info(f"Found {len(pmc_ids)} PMC IDs for session {session_id}")
                return pmc_ids
            else:
                logging.warning(f"No documents found for session {session_id}")
                return []

        except Exception as e:
            logging.error(
                f"Failed to get PMC IDs: {str(e)}",
                exc_info=True
            )
            return []

    async def validate_documents_indexed(
        self,
        pmc_ids: List[str],
        wait_for_indexing: bool = True,
        max_wait_seconds: int = 60,
        check_interval: int = 3
    ) -> Dict[str, Any]:
        """
        Check if documents are indexed in Qdrant before processing chat.
        If wait_for_indexing=True, will poll until documents are ready or timeout.
        Also checks for failed documents to provide better error messages.

        Returns: {"indexed": bool, "missing": [], "indexed_count": 0, "total_count": 0, "failed": []}
        """
        if not pmc_ids:
            return {
                "indexed": False,
                "missing": [],
                "indexed_count": 0,
                "total_count": 0,
                "message": "No PMC IDs provided"
            }

        elapsed_time = 0
        
        # Check for failed documents in MongoDB to provide early feedback
        failed_docs = []
        try:
            from utils.database import get_async_database_connection
            client = get_async_database_connection()
            db = client["epocrates"]
            status_collection = db["document_status"]
            
            for pmc_id in pmc_ids:
                doc = await status_collection.find_one({"pmc_id": pmc_id})
                if doc and doc.get("status", "").startswith("FAILED"):
                    failed_docs.append({
                        "pmc_id": pmc_id,
                        "error": doc.get("status", "Unknown error")
                    })
            
            if failed_docs:
                # Extract error messages for user
                error_messages = [f"{fd['pmc_id']}: {fd['error']}" for fd in failed_docs]
                logging.error(f"❌ {len(failed_docs)} document(s) failed processing: {error_messages}")
                
                # If ALL documents failed, return immediately
                if len(failed_docs) == len(pmc_ids):
                    return {
                        "indexed": False,
                        "missing": [fd['pmc_id'] for fd in failed_docs],
                        "indexed_count": 0,
                        "total_count": len(pmc_ids),
                        "message": f"All documents failed to process: {'; '.join(error_messages)}",
                        "failed": failed_docs
                    }
        except Exception as e:
            logging.warning(f"Could not check document status in MongoDB: {e}")

        while elapsed_time < max_wait_seconds:
            try:
                # Check each PMC ID in Qdrant
                indexed_docs = []
                missing_docs = []

                for pmc_id in pmc_ids:
                    # Skip documents we know have failed
                    if any(fd['pmc_id'] == pmc_id for fd in failed_docs):
                        missing_docs.append(pmc_id)
                        continue
                        
                    # Query Qdrant to see if this pmc_id has any points
                    result = self.qdrant_client.scroll(
                        collection_name=DOCUMENT_TEXT_COLLECTION_NAME,
                        scroll_filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="pmc_id",
                                    match=models.MatchValue(value=pmc_id)
                                )
                            ]
                        ),
                        limit=1  # Just check if at least one point exists
                    )

                    if result[0]:  # If points exist
                        indexed_docs.append(pmc_id)
                        logging.info(f"✓ Document {pmc_id} is indexed in Qdrant")
                    else:
                        missing_docs.append(pmc_id)

                all_indexed = len(missing_docs) == 0

                # If all documents indexed, return success
                if all_indexed:
                    if elapsed_time > 0:
                        logging.info(
                            f"✓ All documents ready after waiting {elapsed_time}s"
                        )
                    return {
                        "indexed": True,
                        "missing": [],
                        "indexed_count": len(indexed_docs),
                        "total_count": len(pmc_ids),
                        "message": "All documents indexed",
                        "wait_time": elapsed_time
                    }

                # If not all indexed and wait_for_indexing is False, return immediately
                if not wait_for_indexing:
                    logging.warning(
                        f"✗ {len(missing_docs)} documents not indexed: {missing_docs}"
                    )
                    return {
                        "indexed": False,
                        "missing": missing_docs,
                        "indexed_count": len(indexed_docs),
                        "total_count": len(pmc_ids),
                        "message": f"{len(missing_docs)} documents not indexed"
                    }

                # Wait and retry
                if elapsed_time == 0:
                    logging.info(
                        f"⏳ Waiting for {len(missing_docs)} documents to be indexed: {missing_docs}"
                    )
                else:
                    logging.info(
                        f"⏳ Still waiting... {elapsed_time}/{max_wait_seconds}s elapsed"
                    )

                await asyncio.sleep(check_interval)
                elapsed_time += check_interval

            except Exception as e:
                logging.error(f"Failed to validate documents in Qdrant: {e}", exc_info=True)
                if not wait_for_indexing:
                    return {
                        "indexed": False,
                        "missing": pmc_ids,
                        "indexed_count": 0,
                        "total_count": len(pmc_ids),
                        "message": f"Validation failed: {str(e)}"
                    }
                # If waiting, continue retry loop
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval

        # Timeout reached - check if any documents failed
        timeout_message = f"Timeout after {max_wait_seconds}s - documents still not indexed"
        if failed_docs:
            failed_pmc_ids = [fd['pmc_id'] for fd in failed_docs]
            timeout_message = f"Document(s) {failed_pmc_ids} failed to process (may be scanned/image-based PDFs). Other documents timed out."
        
        logging.error(
            f"⏱️ Timeout after {max_wait_seconds}s waiting for documents to be indexed"
        )
        return {
            "indexed": False,
            "missing": missing_docs if 'missing_docs' in locals() else pmc_ids,
            "indexed_count": len(indexed_docs) if 'indexed_docs' in locals() else 0,
            "total_count": len(pmc_ids),
            "message": timeout_message,
            "timeout": True,
            "failed": failed_docs if failed_docs else []
        }
