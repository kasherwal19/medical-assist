"""
RAG retrieval mixin for chat service.
Handles document retrieval from Qdrant vector store and RAG prompt generation.
"""

import re
from typing import List, Dict, Optional
from lib.logger import logging
from services.llm_service import brain, azure_embedding_client
from utils.prompt import RAG_QUERY_GEN_PROMPT
from qdrant_client import models
from configs.config import azure_openai_settings
from .constants import DOCUMENT_TEXT_COLLECTION_NAME


class RetrievalMixin:
    """Mixin class for RAG retrieval methods."""

    async def generate_RAG_prompt(
        self,
        query: Optional[str] = None,
        parameters: Optional[Dict] = None,
        context: List[Dict] = []
    ) -> str:
        """
        Generate optimized RAG query using LLM.
        """
        try:
            required_prompt = RAG_QUERY_GEN_PROMPT.format(
                parameters=parameters if parameters else "None provided",
                user_query=query if query else "None provided",
                context=context if context else "None provided"
            )

            result = await brain.call_invoke(prompt=required_prompt)
            generated_query = result.content.strip()

            if generated_query:
                logging.info(f"Generated RAG query: {generated_query[:100]}...")
                return generated_query
            else:
                logging.warning("Empty RAG query generated, using original")
                return query or ""

        except Exception as e:
            logging.error(f"RAG prompt generation failed: {str(e)}", exc_info=True)
            return query or ""

    async def retriever(
        self,
        query: str,
        pmc_ids: List[str],
        limit: int = 100,
        score_threshold: float = 0.1,
        max_results: int = 30,
        min_per_doc: int = 3
    ) -> List[str]:
        """
        Retrieve relevant documents from Qdrant vector store.
        Ensures results from ALL requested PMC IDs are included (multi-document support).
        
        Args:
            query: Search query
            pmc_ids: List of PMC IDs to search within
            limit: Maximum points to retrieve from Qdrant
            score_threshold: Minimum relevance score
            max_results: Maximum total results to return
            min_per_doc: Minimum results per document to ensure multi-doc coverage
        """
        try:
            if not pmc_ids:
                logging.warning("No PMC IDs provided for retrieval")
                return []

            logging.info(f"[MULTI-DOC] Starting retrieval for {len(pmc_ids)} PMC IDs: {pmc_ids}")

            embedding_response = azure_embedding_client.embeddings.create(
                input=query,
                model=azure_openai_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
            )

            docs = self.qdrant_client.query_points(
                collection_name=DOCUMENT_TEXT_COLLECTION_NAME,
                query=embedding_response.data[0].embedding,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="pmc_id",
                            match=models.MatchAny(any=pmc_ids),
                        )
                    ]
                ),
                limit=limit,
            )

            # Group results by PMC ID for balanced selection
            results_by_pmc = {pmc_id: [] for pmc_id in pmc_ids}
            
            for point in docs.points:
                if point.score > score_threshold:
                    pmc_id = point.payload.get("pmc_id", "")
                    if pmc_id in results_by_pmc:
                        text = point.payload["text"]
                        # Ensure PMC ID is embedded in the text for downstream processing
                        if f"<{pmc_id}>" not in text:
                            if text.startswith("Document_Name "):
                                comma_idx = text.find(",")
                                if comma_idx > 0:
                                    text = text[:comma_idx] + f" <{pmc_id}>" + text[comma_idx:]
                        results_by_pmc[pmc_id].append({
                            "text": text,
                            "score": point.score
                        })

            # Log retrieval stats per document
            for pmc_id, results in results_by_pmc.items():
                if results:
                    scores = [r["score"] for r in results]
                    logging.info(
                        f"[MULTI-DOC] {pmc_id}: {len(results)} results, "
                        f"score range: {min(scores):.4f} - {max(scores):.4f}"
                    )
                else:
                    logging.warning(f"[MULTI-DOC] {pmc_id}: NO results above threshold {score_threshold}")

            # BALANCED SELECTION: Ensure minimum representation from each document
            # This prevents one document from dominating the results
            final_texts = []
            
            # First pass: get minimum required from each document
            for pmc_id in pmc_ids:
                doc_results = results_by_pmc.get(pmc_id, [])
                # Sort by score descending
                doc_results.sort(key=lambda x: x["score"], reverse=True)
                # Take up to min_per_doc from each document
                for result in doc_results[:min_per_doc]:
                    if len(final_texts) < max_results:
                        final_texts.append(result["text"])
            
            logging.info(f"[MULTI-DOC] After minimum allocation: {len(final_texts)} results")
            
            # Second pass: fill remaining slots with highest scoring across all docs
            if len(final_texts) < max_results:
                all_remaining = []
                for pmc_id in pmc_ids:
                    doc_results = results_by_pmc.get(pmc_id, [])
                    # Skip the ones we already took
                    for result in doc_results[min_per_doc:]:
                        all_remaining.append(result)
                
                # Sort by score and fill remaining slots
                all_remaining.sort(key=lambda x: x["score"], reverse=True)
                for result in all_remaining:
                    if len(final_texts) >= max_results:
                        break
                    if result["text"] not in final_texts:  # Avoid duplicates
                        final_texts.append(result["text"])

            # Final logging
            pmc_ids_in_final = set()
            for text in final_texts:
                pmc_match = re.search(r"<(PMC\d+)>", text)
                if pmc_match:
                    pmc_ids_in_final.add(pmc_match.group(1))
            
            logging.info(
                f"[MULTI-DOC] FINAL: Retrieved {len(final_texts)} document chunks from "
                f"{len(pmc_ids_in_final)}/{len(pmc_ids)} documents: {pmc_ids_in_final}"
            )
            
            # Warn if any documents are missing
            missing_docs = set(pmc_ids) - pmc_ids_in_final
            if missing_docs:
                logging.warning(
                    f"[MULTI-DOC] WARNING: {len(missing_docs)} documents have NO representation: {missing_docs}"
                )

            return final_texts

        except Exception as e:
            logging.error(f"Retrieval failed: {str(e)}", exc_info=True)
            return []
