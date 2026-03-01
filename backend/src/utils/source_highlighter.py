import json
import fitz
import re
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from html.parser import HTMLParser

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from configs.config import credentials
from lib.logger import logging
from utils.database import doc_db
from services.llm_service import highlight_brain


# Helper: Strip HTML tags
def strip_html_tags(html_content: str) -> str:
    """Remove HTML tags and return plain text content, excluding style/script tags."""
    try:
        # First, remove style and script tags with their content
        text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<head[^>]*>.*?</head>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove all other HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)

        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")

        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        logging.error(f"[source_highlighter] HTML stripping failed: {e}")
        return ""

# Constants
MAX_RESPONSE_CHARS = 999999  
MAX_LINES_PER_PAGE = 999999  
MAX_TOTAL_LINES = 999999     

# --- AZURE SETUP (LAZY INITIALIZATION) ---
def get_blob_container_client():
    """
    Lazily initializes and returns the Azure Blob Container Client.
    This ensures credentials are fully loaded before we attempt to connect.
    """
    conn_str = credentials.AZURE_STORAGE_CONNECTION_STRING
    container_name = credentials.AZURE_CONTAINER_NAME

    if not conn_str or not container_name:
        logging.error(
            f"[source_highlighter] Azure credentials missing! "
            f"Conn String set: {bool(conn_str)}, Container: {container_name}"
        )
        return None

    try:
        blob_service = BlobServiceClient.from_connection_string(conn_str)
        return blob_service.get_container_client(container_name)
    except Exception as e:
        logging.error(f"[source_highlighter] Failed to create blob container client: {e}")
        return None


# Helper: Generate SAS URL for blob
def generate_sas_url(blob_path: str, expiry_days: int = 365) -> str:
    """Generates a SAS URL for a specific blob path."""
    try:
        sas_token = generate_blob_sas(
            account_name=credentials.AZURE_STORAGE_ACCOUNT_NAME,
            container_name=credentials.AZURE_CONTAINER_NAME,
            blob_name=blob_path,
            account_key=credentials.AZURE_STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(days=expiry_days),
        )

        return (
            f"https://{credentials.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"
            f"{credentials.AZURE_CONTAINER_NAME}/{blob_path}?{sas_token}"
        )
    except Exception as e:
        logging.error(f"[source_highlighter] Failed to generate SAS URL: {e}")
        return ""


# Fallback parser
def parse_pointer_text(raw_text: str) -> dict:
    """
    Parse document info from RAG doc text.
    Handles both formats:
    - Old: "Document_Name filename.pdf, Total_Pages N, PAGE_M"
    - New: "Document_Name filename.pdf <PMCXXXXXX>, Total_Pages N, PAGE_M"
    """
    result = {
        "document_name": None,
        "pmc_id": None,
        "page": None,
        "chunk_text": ""
    }

    if not raw_text:
        return result

    # Try to extract PMC ID from <PMCXXXXXX> format
    pmc_match = re.search(r"<(PMC\d+)>", raw_text)
    if pmc_match:
        result["pmc_id"] = pmc_match.group(1)

    # Extract document name and page
    # Handle both: "Document_Name file.pdf <PMC123>" and "Document_Name file.pdf"
    header_re = re.compile(
        r"Document_Name\s+(?P<doc>[^,<\n]+?)(?:\s*<PMC\d+>)?\s*,.*?PAGE_(?P<page>\d+)",
        re.IGNORECASE
    )
    m = header_re.search(raw_text)
    if m:
        result["document_name"] = m.group("doc").strip()
        result["page"] = int(m.group("page"))

    # Try to extract the chunk body between `--` and trailing `==`
    try:
        # Typical marker shape:
        # "Document_Name <doc>, Total_Pages <N>, PAGE_<n>\n--<chunk_text>=="
        chunk_match = re.search(r"--\s*(.*?)\s*==\s*$", raw_text, flags=re.DOTALL)
        if chunk_match:
            chunk = chunk_match.group(1).strip()
            # Normalize whitespace a bit
            chunk = re.sub(r"\s+", " ", chunk)
            result["chunk_text"] = chunk
    except Exception as e:
        logging.warning(f"[source_highlighter] Failed to parse chunk_text: {e}")

    return result

# Highlight Engine
class PreciseHighlightService:

    def extract_lines(self, pdf_doc: fitz.Document, page_no: int) -> List[Dict]:
        try:
            page = pdf_doc.load_page(page_no - 1)
            blocks = page.get_text("dict", flags=2).get("blocks", [])

            lines = []
            for b_idx, block in enumerate(blocks):
                for l_idx, line in enumerate(block.get("lines", [])):
                    text = " ".join(span["text"] for span in line["spans"])
                    if text.strip():
                        lines.append({
                            "line_id": f"p{page_no}_b{b_idx}_l{l_idx}",
                            "text": text,
                            "bbox": line["bbox"]
                        })
            return lines
        except Exception as e:
            logging.error(f"[source_highlighter] extract_lines failed for page {page_no}: {e}")
            return []

    async def find_relevant_lines(
        self,
        assistant_response: str,
        documents_data: Dict
    ) -> Dict:
        # Return STRICT JSON using ONLY the document names provided below.

        system_prompt = """
You are a document source matcher. Your task is to identify which lines from the PDF document were used as sources for the generated response.

MATCHING RULES:
1. Match lines that contain the same medical facts, data, or clinical information
2. Match even if the response paraphrases, summarizes, or rephrases the source
3. Match based on semantic meaning, not exact text
4. If the response mentions a specific fact (e.g., "response rate of 42%"), find the source line containing that fact
5. Be INCLUSIVE - match all lines that contributed any information to the response
6. Look for key medical terms, drug names, percentages, statistics, and clinical outcomes
7. Don't assume all content comes from one document only
8. Generate content from all documents mentioned

EXAMPLES:
- Response: "The overall response rate was 42% in patients"
  Source line: "Overall response rate: 42% (95% CI: 38-46%)"
  → MATCH (same data)

- Response: "Studies showed improved survival outcomes"
  Source line: "median overall survival increased from 8.2 to 12.5 months"
  → MATCH (talks about survival improvement)

- Response: "Common side effects included nausea and fatigue"
  Source line: "Adverse events: nausea (30%), fatigue (25%), headache (15%)"
  → MATCH (mentions these side effects)

Additional rules:
1. SEARCH ALL DOCUMENTS - The response may draw from multiple documents. You MUST check every document provided.
2. MATCH ACROSS DOCUMENTS - If a paragraph mentions multiple facts, find sources from ALL relevant documents, not just one.
3. BE COMPREHENSIVE - Include matches from every document that contributed any information to the response.
4. Don't stop at first match - Even if you find matches in Document A, continue searching Documents B, C, etc.

EXAMPLES OF MULTI-DOCUMENT MATCHING:

Example 1 - Content from multiple documents:
Response: "Treatment efficacy was 42% in adults and 38% in pediatric patients. Common side effects included nausea."
→ Should return matches from:
  - PMC123456 (contains adult efficacy data: 42%)
  - PMC789012 (contains pediatric efficacy data: 38%)
  - PMC345678 (contains side effect data: nausea)

Example 2 - Content primarily from one document:
Response: "The study enrolled 150 patients with median age 45 years."
→ If only PMC123456 contains this data, return only that document

Return ONLY valid JSON in this format:
{
  "<document_name>": {
     "page_<number>": ["<line_id>", "<line_id>"]
  }
}

If no matches exist, return {}.
NO explanations. NO markdown. NO text outside JSON.
"""

        # Strip HTML tags from response to get plain text content
        plain_text_response = strip_html_tags(assistant_response)

        # Truncate response to reduce prompt size (saves 60-70% on large responses)
        response_text = plain_text_response[:MAX_RESPONSE_CHARS]
        if len(plain_text_response) > MAX_RESPONSE_CHARS:
            logging.info(
                f"[source_highlighter] Truncated response from {len(plain_text_response)} "
                f"to {MAX_RESPONSE_CHARS} chars"
            )

        # Log what we're sending
        total_lines = sum(len(page_dict[page_key]) for page_dict in documents_data.values() for page_key in page_dict)
        logging.info(
            f"[source_highlighter] Stripped HTML: {len(assistant_response)} chars → {len(plain_text_response)} chars plain text"
        )
        logging.info(
            f"[source_highlighter] Matching response ({len(response_text)} chars) "
            f"against {total_lines} lines from {len(documents_data)} documents"
        )

        user_prompt = f"Generated Response:\n{response_text}\n\n"

        # Limit lines per document to reduce prompt size
        total_lines_added = 0
        for doc, pages in documents_data.items():
            user_prompt += f"\n=== {doc} ===\n"
            doc_data = {}
            
            for page_key, lines in pages.items():
                # Limit lines per page
                limited_lines = lines[:MAX_LINES_PER_PAGE]
                doc_data[page_key] = limited_lines
                total_lines_added += len(limited_lines)
                
                # Stop if we've added too many total lines
                if total_lines_added >= MAX_TOTAL_LINES:
                    logging.info(f"[source_highlighter] Reached max {MAX_TOTAL_LINES} lines, stopping")
                    break
            
            user_prompt += json.dumps(doc_data, indent=2)
            
            if total_lines_added >= MAX_TOTAL_LINES:
                break
        
        logging.info(f"[source_highlighter] Sending {total_lines_added} lines to LLM (limited from {total_lines})")

        resp = await highlight_brain.call_invoke(
            prompt=user_prompt,
            system_message=system_prompt,
            disable_cache=True  # Disable cache for source matching - must be fresh
        )

        cleaned = re.sub(r"```json|```", "", resp.content or "").strip()

        if not cleaned:
            logging.warning("[source_highlighter] Empty LLM response for matching")
            return {}

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            logging.error(
                "[source_highlighter] LLM returned invalid JSON. Raw output:\n"
                f"{resp.content[:500]}"
            )
            return {}

        if not isinstance(parsed, dict):
            logging.warning("[source_highlighter] LLM JSON is not a dict")
            return {}

        # Log what we got back
        if parsed:
            match_count = sum(len(line_ids) for pages in parsed.values() for line_ids in pages.values())
            logging.info(f"[source_highlighter] LLM matched {match_count} lines across {len(parsed)} documents")
        else:
            logging.warning(
                f"[source_highlighter] LLM returned empty matches. Response preview: {resp.content[:200]}"
            )

        return parsed

    def _normalize(self, s: str) -> str:
        s = s or ""
        s = s.lower()
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    def _extract_candidate_phrases(self, chunk_text: str) -> List[str]:
        """Create candidate phrases from a chunk to match against PDF lines."""
        chunk_text_norm = self._normalize(chunk_text)
        if not chunk_text_norm:
            return []

        cands = []
        
        # Extract sentences (for exact/substring matching)
        sentences = re.split(r"[.!?]+\s+", chunk_text_norm)
        for s in sentences:
            s = s.strip()
            if len(s) >= 20:
                cands.append(s)
        
        # Extract comma-separated phrases
        phrases = [p.strip() for p in chunk_text_norm.split(',') if len(p.strip()) >= 15]
        cands.extend(phrases)
        
        # Extract shorter key phrases (2-5 word sequences) for better line matching
        words = chunk_text_norm.split()
        for i in range(len(words)):
            for length in [3, 4, 5]:  # 3-5 word phrases
                if i + length <= len(words):
                    phrase = " ".join(words[i:i+length])
                    if len(phrase) >= 12:  # At least 12 chars
                        cands.append(phrase)
        
        # Deduplicate while preserving order
        seen = set()
        unique_cands = []
        for c in cands:
            if c not in seen:
                seen.add(c)
                unique_cands.append(c)
        
        return unique_cands[:50]  # Limit to prevent explosion

    def _extract_key_words(self, text: str) -> set:
        """Extract significant words (excluding common stopwords) for overlap matching."""
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
            'that', 'these', 'those', 'it', 'its', 'they', 'their', 'we', 'our',
            'you', 'your', 'he', 'she', 'him', 'her', 'his', 'which', 'who',
            'whom', 'what', 'where', 'when', 'why', 'how', 'all', 'each', 'every',
            'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not',
            'only', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now'
        }
        words = set(self._normalize(text).split())
        # Keep words that are meaningful (not stopwords, length >= 3)
        return {w for w in words if w not in stopwords and len(w) >= 3}

    def match_lines_by_chunks(self, documents_data: Dict, grouped_chunks: Dict) -> Dict:
        """Return mapping {doc: {page_key: [line_ids...]}} by matching chunk_texts to lines."""
        matches: Dict[str, Dict[str, List[str]]] = {}
        
        for doc_name, pages in grouped_chunks.items():
            if doc_name not in documents_data:
                continue
                
            for page_key, chunk_texts in pages.items():
                page_lines = documents_data.get(doc_name, {}).get(page_key, [])
                if not page_lines:
                    continue

                # Collect ALL phrases from ALL chunks
                all_phrases = set()
                all_chunk_words = set()  # For word overlap matching
                
                for chunk_text in chunk_texts or []:
                    phrases = self._extract_candidate_phrases(chunk_text)
                    all_phrases.update(phrases)
                    # Also collect key words from chunks for overlap matching
                    all_chunk_words.update(self._extract_key_words(chunk_text))
                
                # If no phrases extracted, mark entire page if chunks existed
                if not all_phrases and not all_chunk_words:
                    if chunk_texts:
                        matches.setdefault(doc_name, {})[page_key] = ["__ALL__"]
                    continue

                matched_line_ids = []
                
                for pl in page_lines:
                    line_id = pl["line_id"]
                    norm_text = self._normalize(pl["text"])
                    
                    if not norm_text or len(norm_text) < 5:
                        continue
                    
                    is_matched = False
                    
                    # Strategy 1: Bidirectional substring matching
                    for phrase in all_phrases:
                        # Check both directions: phrase in line OR line in phrase
                        if phrase in norm_text or norm_text in phrase:
                            is_matched = True
                            break
                    
                    # Strategy 2: Word overlap matching (if substring didn't match)
                    if not is_matched and all_chunk_words:
                        line_words = self._extract_key_words(norm_text)
                        if line_words:
                            # Calculate overlap ratio
                            overlap = line_words & all_chunk_words
                            overlap_ratio = len(overlap) / len(line_words)
                            # Match if >= 50% of line's key words are in chunks
                            if overlap_ratio >= 0.5 and len(overlap) >= 2:
                                is_matched = True
                    
                    if is_matched:
                        matched_line_ids.append(line_id)

                # Fallback: mark entire page if no matches but chunks exist
                if not matched_line_ids and chunk_texts:
                    matched_line_ids = ["__ALL__"]

                if matched_line_ids:
                    matches.setdefault(doc_name, {})[page_key] = matched_line_ids

        return matches


# Core Pipeline
async def process_highlights_for_chat_response(
    session_id: str,
    message_id: int,
    rag_docs: List[str],
    assistant_response: str
):
    logging.info(
        f"[source_highlighter] Start | session_id={session_id}, message_id={message_id}"
    )

    # 1. Fetch session docs
    session_doc = await doc_db._db["session_docs"].find_one({
        "session_id": session_id
    })

    if not session_doc or not session_doc.get("documents"):
        logging.warning("[source_highlighter] No session_docs found")
        return

    pmc_ids = session_doc["documents"]
    logging.info(f"[MULTI-DOC] Session has {len(pmc_ids)} documents to process: {pmc_ids}")

    # 2. Validate PMC IDs and build filename-to-pmc mapping AND pmc-to-blob-path mapping
    valid_pmc_ids = []
    filename_to_pmc = {}  # Maps filename -> pmc_id for user-uploaded docs
    pmc_to_blob_path = {}  # Maps pmc_id -> actual blob path (s3_key)
    
    async for d in doc_db._db["document_status"].find({"pmc_id": {"$in": pmc_ids}}):
        pmc_id = d["pmc_id"]
        valid_pmc_ids.append(pmc_id)
        # Build mapping from filename to PMC ID
        if d.get("filename"):
            filename_to_pmc[d["filename"]] = pmc_id
            # Also map without extension
            base_name = d["filename"].rsplit('.', 1)[0] if '.' in d["filename"] else d["filename"]
            filename_to_pmc[base_name] = pmc_id
        # Store s3_key if available
        if d.get("s3_key"):
            pmc_to_blob_path[pmc_id] = d["s3_key"]
    
    # Also check articles collection for user uploads
    async for a in doc_db._db["articles"].find({"pmc_id": {"$in": pmc_ids}}):
        if a.get("filename") and a.get("pmc_id"):
            filename_to_pmc[a["filename"]] = a["pmc_id"]
            base_name = a["filename"].rsplit('.', 1)[0] if '.' in a["filename"] else a["filename"]
            filename_to_pmc[base_name] = a["pmc_id"]
        # Store s3_key from articles (user uploads)
        if a.get("s3_key") and a.get("pmc_id"):
            pmc_to_blob_path[a["pmc_id"]] = a["s3_key"]

    if not valid_pmc_ids:
        logging.warning("[source_highlighter] No valid PMC IDs")
        return
    
    logging.info(f"[source_highlighter] Filename to PMC mapping: {filename_to_pmc}")

    # 3. Group pages using rag_docs 
    grouped = {}

    if rag_docs:
        logging.info(f"[source_highlighter] Processing {len(rag_docs)} rag_docs")
        parsed_count = 0
        docs_found = set()  # Track unique documents found
        
        for idx, raw in enumerate(rag_docs):
            parsed = parse_pointer_text(raw)
            if not parsed["document_name"]:
                if idx < 3:  # Log first few failures
                    logging.warning(
                        f"[source_highlighter] Failed to parse doc from rag_doc #{idx}. "
                        f"Preview: {raw[:200]}"
                    )
                continue

            parsed_count += 1
            doc_name = parsed["document_name"]
            
            # Check against ALL valid PMC IDs and preserve ALL unique documents
            matched_pmc = None
            
            # First priority: Use PMC ID extracted directly from the rag_doc (new format)
            if parsed.get("pmc_id") and parsed["pmc_id"] in valid_pmc_ids:
                matched_pmc = parsed["pmc_id"]
            
            # Second: try direct PMC ID match in document name
            if not matched_pmc:
                for pmc in valid_pmc_ids:
                    if pmc in doc_name:
                        matched_pmc = pmc
                        break
            
            # Third: try filename-to-PMC mapping (for user uploads)
            if not matched_pmc:
                # Try exact filename match
                if doc_name in filename_to_pmc:
                    matched_pmc = filename_to_pmc[doc_name]
                else:
                    # Try matching without extension
                    base_name = doc_name.rsplit('.', 1)[0] if '.' in doc_name else doc_name
                    if base_name in filename_to_pmc:
                        matched_pmc = filename_to_pmc[base_name]
                    else:
                        # Try partial match (filename might be truncated or have slight differences)
                        for filename, pmc in filename_to_pmc.items():
                            if filename in doc_name or doc_name in filename:
                                matched_pmc = pmc
                                break
            
            if matched_pmc:
                page = parsed["page"] or 1
                
                # Explicit initialization to ensure all documents are preserved
                if doc_name not in grouped:
                    grouped[doc_name] = {}
                    docs_found.add(doc_name)
                
                page_key = f"page_{page}"
                if page_key not in grouped[doc_name]:
                    grouped[doc_name][page_key] = []
                # Preserve chunk text for deterministic matching later
                if parsed.get("chunk_text"):
                    grouped[doc_name][page_key].append(parsed["chunk_text"])
                
                if idx < 5:  # Log first few successes
                    logging.info(
                        f"[source_highlighter] rag_doc #{idx}: matched {doc_name} -> {matched_pmc}, page={page}"
                    )
            else:
                if idx < 3:
                    logging.warning(
                        f"[source_highlighter] rag_doc #{idx} parsed but didn't match any PMC ID. "
                        f"Doc name: {doc_name}, Parsed PMC: {parsed.get('pmc_id')}, "
                        f"Valid PMCs: {valid_pmc_ids[:3]}, "
                        f"Filename mapping keys: {list(filename_to_pmc.keys())[:3]}..."
                    )

        logging.info(
            f"[source_highlighter] Successfully parsed {parsed_count}/{len(rag_docs)} rag_docs "
            f"into {len(grouped)} unique documents"
        )
        if docs_found:
            logging.info(f"[source_highlighter] Documents found: {list(docs_found)}")

    # 4. Fallback ONLY if rag_docs empty
    elif assistant_response:
        logging.info("[source_highlighter] No rag_docs, using fallback parsing from assistant_response")
        parsed = parse_pointer_text(assistant_response)
        if parsed["document_name"]:
            doc_name = parsed["document_name"]
            page = parsed["page"] or 1
            grouped[doc_name] = {f"page_{page}": []}
            logging.info(f"[source_highlighter] Fallback parsed: {doc_name}, page={page}")

    if not grouped:
        logging.warning("[source_highlighter] Nothing to highlight - no documents found")
        return

    logging.info(
        f"[source_highlighter] Final grouped structure: "
        f"{[(doc, list(pages.keys())) for doc, pages in grouped.items()]}"
    )
    logging.info(f"[source_highlighter] PMC to blob path mapping: {pmc_to_blob_path}")

    # 5. Load PDFs & extract lines
    highlighter = PreciseHighlightService()
    documents_data = {}
    pdf_cache = {}

    # Initialize client ONCE before the loop
    blob_client_container = get_blob_container_client()
    if not blob_client_container:
        logging.error("[source_highlighter] Aborting: Could not initialize Azure Blob Client.")
        return

    for doc_name in grouped:
        # Try multiple methods to find PMC ID:
        # 1. Check if PMC ID is directly in doc_name
        pmc_id = next((p for p in valid_pmc_ids if p in doc_name), None)
        
        # 2. If not found, use filename_to_pmc mapping (for user uploads)
        if not pmc_id:
            if doc_name in filename_to_pmc:
                pmc_id = filename_to_pmc[doc_name]
            else:
                # Try without extension
                base_name = doc_name.rsplit('.', 1)[0] if '.' in doc_name else doc_name
                if base_name in filename_to_pmc:
                    pmc_id = filename_to_pmc[base_name]
        
        if not pmc_id:
            logging.warning(f"[source_highlighter] No PMC ID found for document: {doc_name}. Available mappings: {list(filename_to_pmc.keys())}")
            continue
        
        # Get actual blob path from mapping (for user uploads) or construct default path
        if pmc_id in pmc_to_blob_path:
            blob_path = pmc_to_blob_path[pmc_id]
            logging.info(f"[source_highlighter] Loading PDF for {doc_name} using stored blob path: {blob_path}")
        else:
            blob_path = f"Epocrates/documents/{pmc_id}.pdf"
            logging.info(f"[source_highlighter] Loading PDF for {doc_name} using default path: {blob_path}")
        
        try:
            # Use the lazily initialized client
            pdf_bytes = blob_client_container.get_blob_client(blob_path).download_blob().readall()

            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pdf_cache[doc_name] = pdf_doc
            documents_data[doc_name] = {}

            for page_key in grouped[doc_name]:
                page_no = int(page_key.split("_")[1])
                lines = highlighter.extract_lines(pdf_doc, page_no)
                documents_data[doc_name][page_key] = [
                    {"line_id": l["line_id"], "text": l["text"]}
                    for l in lines
                ]
                logging.info(
                    f"[source_highlighter] Extracted {len(lines)} lines from {doc_name} page {page_no}"
                )
        except Exception as e:
            logging.error(f"[source_highlighter] Failed to load PDF for {doc_name} (path={blob_path}): {e}")
            continue

    if not documents_data:
        logging.warning("[source_highlighter] No documents loaded successfully")
        return

    # 6. Match lines to chunks (prefer deterministic match; fallback to LLM)
    logging.info(
        f"[source_highlighter] Preparing matches for {len(documents_data)} documents: {list(documents_data.keys())}"
    )

    # Determine if we have chunk_texts to use
    has_chunk_texts = any(
        any(chunks for chunks in pages.values()) for pages in grouped.values()
    )

    if has_chunk_texts:
        matches = highlighter.match_lines_by_chunks(documents_data, grouped)
        # If still nothing matched (very unlikely), fallback to LLM
        if not matches and assistant_response:
            logging.info("[source_highlighter] Chunk-based matching yielded no results, falling back to LLM")
            matches = await highlighter.find_relevant_lines(
                assistant_response, documents_data
            )
    else:
        matches = await highlighter.find_relevant_lines(
            assistant_response, documents_data
        )

    if not matches:
        logging.warning("[source_highlighter] LLM returned no matches")
        return

    # 7. Apply highlights & save images
    for doc_name, pages in matches.items():

        if doc_name not in pdf_cache:
            logging.warning(
                f"[source_highlighter] Skipping unknown document from LLM: {doc_name}"
            )
            continue

        pdf_doc = pdf_cache[doc_name]

        images = []

        for page_key, line_ids in pages.items():
            page_no = int(page_key.split("_")[1])
            page = pdf_doc.load_page(page_no - 1)

            # Apply highlights
            extracted_lines = highlighter.extract_lines(pdf_doc, page_no)
            if "__ALL__" in line_ids:
                # No specific lines matched: mark the full page with a transparent overlay
                # Create a large rectangle covering the page
                rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
                annot = page.add_rect_annot(rect)
                try:
                    annot.set_colors(stroke=(1, 1, 0), fill=(1, 1, 0))
                    annot.set_opacity(0.05)
                except Exception:
                    pass
            else:
                for line in extracted_lines:
                    if line["line_id"] in line_ids:
                        page.add_highlight_annot(fitz.Rect(line["bbox"]))

            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = pix.tobytes()

            path = (
                f"sources/ChatHighlights/"
                f"{session_id}/{doc_name}/Page_{page_no}.png"
            )

            try:
                # Use the lazily initialized client for upload
                blob_client_container.get_blob_client(path).upload_blob(
                    img,
                    overwrite=True,
                    content_settings=ContentSettings(
                        content_type="image/png",
                        content_disposition="inline"
                    )
                )
                
                # Generate SAS URL with 1 year expiry
                sas_url = generate_sas_url(path, expiry_days=365)

                images.append({
                    "page_no": page_no,
                    "blob_path": path,
                    "url": sas_url
                })
            except Exception as e:
                logging.error(f"[source_highlighter] Failed to upload image {path}: {e}")

        if images:
            # Insert into database
            await doc_db._db["session_images"].insert_one({
                "session_id": session_id,
                "message_id": message_id,
                "document_name": doc_name,
                "images": images,
                "timestamp": datetime.utcnow()
            })

            logging.info(
                f"[source_highlighter] Saved {len(images)} images for "
                f"session={session_id}, message_id={message_id}, doc={doc_name}"
            )

    logging.info(
        f"[source_highlighter] Highlighting completed successfully - "
        f"processed {len(matches)} documents"
    )


# Per-Paragraph Highlighting
async def process_highlights_per_paragraph(
    paragraph_text: str,
    rag_docs: List[str],
    session_id: str,
    message_id: int,
    paragraph_index: int
) -> List[Dict]:
    """
    Generate highlighted images for a single paragraph.

    Args:
        paragraph_text: The text content of a single paragraph
        rag_docs: List of raw RAG document chunks
        session_id: Session identifier
        message_id: Message identifier
        paragraph_index: Index of the paragraph in the response

    Returns:
        List of dicts: [{"document_name": str, "page_no": int, "url": str}, ...]
    """
    logging.info(
        f"[source_highlighter] Per-paragraph highlight | session_id={session_id}, "
        f"message_id={message_id}, paragraph_index={paragraph_index}"
    )

    # 1. Fetch session docs
    session_doc = await doc_db._db["session_docs"].find_one({
        "session_id": session_id
    })

    if not session_doc or not session_doc.get("documents"):
        logging.warning("[source_highlighter] No session_docs found for per-paragraph highlight")
        return []

    pmc_ids = session_doc["documents"]

    # 2. Validate PMC IDs
    valid_pmc_ids = [
        d["pmc_id"]
        async for d in doc_db._db["document_status"].find(
            {"pmc_id": {"$in": pmc_ids}}
        )
    ]

    if not valid_pmc_ids:
        logging.warning("[source_highlighter] No valid PMC IDs for per-paragraph highlight")
        return []

    # 3. Group pages using rag_docs
    grouped = {}
    
    # Build filename to PMC mapping for this session
    filename_to_pmc = {}
    async for article in doc_db._db["articles"].find({"pmc_id": {"$in": valid_pmc_ids}}):
        filename = article.get("filename", "")
        pmc_id = article.get("pmc_id", "")
        if filename and pmc_id:
            filename_to_pmc[filename] = pmc_id
            # Also map without extension
            name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
            filename_to_pmc[name_without_ext] = pmc_id
    
    logging.info(f"[source_highlighter] Per-paragraph filename to PMC mapping: {filename_to_pmc}")

    if rag_docs:
        logging.info(f"[source_highlighter] Processing {len(rag_docs)} rag_docs for paragraph {paragraph_index}")
        parsed_count = 0
        docs_found = set()

        for idx, raw in enumerate(rag_docs):
            parsed = parse_pointer_text(raw)
            if not parsed["document_name"]:
                continue

            parsed_count += 1
            doc_name = parsed["document_name"]

            # Check for PMC ID match - first try parsed pmc_id, then filename mapping
            matched_pmc = parsed.get("pmc_id")
            if not matched_pmc or matched_pmc not in valid_pmc_ids:
                # Try filename mapping
                matched_pmc = filename_to_pmc.get(doc_name)
                if not matched_pmc:
                    # Try without extension
                    name_without_ext = doc_name.rsplit('.', 1)[0] if '.' in doc_name else doc_name
                    matched_pmc = filename_to_pmc.get(name_without_ext)

            if matched_pmc and matched_pmc in valid_pmc_ids:
                page = parsed["page"] or 1

                if doc_name not in grouped:
                    grouped[doc_name] = {}
                    docs_found.add(doc_name)

                page_key = f"page_{page}"
                if page_key not in grouped[doc_name]:
                    grouped[doc_name][page_key] = []

        logging.info(
            f"[source_highlighter] Paragraph {paragraph_index}: parsed {parsed_count}/{len(rag_docs)} "
            f"rag_docs into {len(grouped)} unique documents"
        )

    if not grouped:
        logging.warning(f"[source_highlighter] Paragraph {paragraph_index}: no documents found to highlight")
        return []

    # 4. Load PDFs & extract lines - need to get actual blob paths from articles collection
    highlighter = PreciseHighlightService()
    documents_data = {}
    pdf_cache = {}
    
    # Initialize client ONCE
    blob_client_container = get_blob_container_client()
    if not blob_client_container:
        logging.error("[source_highlighter] Aborting per-paragraph: Could not initialize Azure Blob Client.")
        return []

    # Build PMC to blob path mapping
    pmc_to_blob = {}
    async for article in doc_db._db["articles"].find({"pmc_id": {"$in": valid_pmc_ids}}):
        pmc_id = article.get("pmc_id", "")
        s3_key = article.get("s3_key", "")
        if pmc_id and s3_key:
            pmc_to_blob[pmc_id] = s3_key
    
    logging.info(f"[source_highlighter] Per-paragraph PMC to blob mapping: {pmc_to_blob}")

    for doc_name in grouped:
        # Find PMC ID for this document using filename mapping
        matched_pmc = filename_to_pmc.get(doc_name)
        if not matched_pmc:
            name_without_ext = doc_name.rsplit('.', 1)[0] if '.' in doc_name else doc_name
            matched_pmc = filename_to_pmc.get(name_without_ext)
        
        if not matched_pmc:
            logging.warning(f"[source_highlighter] No PMC ID found for document: {doc_name}")
            continue

        # Get blob path from articles collection
        blob_path = pmc_to_blob.get(matched_pmc)
        if not blob_path:
            logging.warning(f"[source_highlighter] No blob path found for PMC: {matched_pmc}")
            continue

        try:
            # Use lazily initialized client
            pdf_bytes = blob_client_container.get_blob_client(blob_path).download_blob().readall()

            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pdf_cache[doc_name] = pdf_doc
            documents_data[doc_name] = {}

            for page_key in grouped[doc_name]:
                page_no = int(page_key.split("_")[1])
                lines = highlighter.extract_lines(pdf_doc, page_no)
                documents_data[doc_name][page_key] = [
                    {"line_id": l["line_id"], "text": l["text"]}
                    for l in lines
                ]
                logging.info(
                    f"[source_highlighter] Paragraph {paragraph_index}: extracted {len(lines)} lines "
                    f"from {doc_name} page {page_no}"
                )
        except Exception as e:
            logging.error(f"[source_highlighter] Failed to load PDF for {doc_name}: {e}")
            continue

    if not documents_data:
        logging.warning(f"[source_highlighter] Paragraph {paragraph_index}: no documents loaded successfully")
        return []

    # 5. LLM Matching for single paragraph
    logging.info(
        f"[source_highlighter] Paragraph {paragraph_index}: matching against "
        f"{len(documents_data)} documents with {len(paragraph_text)} chars"
    )

    matches = await highlighter.find_relevant_lines(
        paragraph_text, documents_data
    )

    if not matches:
        logging.warning(f"[source_highlighter] Paragraph {paragraph_index}: LLM returned no matches")
        return []

    # 6. Apply highlights & save images
    result_sources = []

    for doc_name, pages in matches.items():
        if doc_name not in pdf_cache:
            logging.warning(
                f"[source_highlighter] Paragraph {paragraph_index}: skipping unknown document from LLM: {doc_name}"
            )
            continue

        pdf_doc = pdf_cache[doc_name]

        for page_key, line_ids in pages.items():
            page_no = int(page_key.split("_")[1])
            page = pdf_doc.load_page(page_no - 1)

            # Apply highlights
            for line in highlighter.extract_lines(pdf_doc, page_no):
                if line["line_id"] in line_ids:
                    page.add_highlight_annot(fitz.Rect(line["bbox"]))

            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = pix.tobytes()

            # Save with paragraph index in path
            path = (
                f"sources/ChatHighlights/"
                f"{session_id}/paragraph_{paragraph_index}/{doc_name}/Page_{page_no}.png"
            )

            try:
                # Use lazily initialized client for upload
                blob_client_container.get_blob_client(path).upload_blob(
                    img,
                    overwrite=True,
                    content_settings=ContentSettings(
                        content_type="image/png",
                        content_disposition="inline"
                    )
                )

                # Generate SAS URL with 1 year expiry
                sas_url = generate_sas_url(path, expiry_days=365)

                # Add to result
                result_sources.append({
                    "document_name": doc_name,
                    "page_no": page_no,
                    "url": sas_url
                })
            except Exception as e:
                logging.error(f"[source_highlighter] Failed to upload paragraph image {path}: {e}")

    logging.info(
        f"[source_highlighter] Paragraph {paragraph_index}: generated {len(result_sources)} highlighted images"
    )

    return result_sources