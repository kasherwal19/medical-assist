# imports
import requests
import uuid
from fastapi import Request, Body, Query
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Literal
from datetime import datetime, timedelta
from utils.database import get_articles_collection, get_selected_articles_collection
from models.db_models import Article, Author
from pydantic import Field

# Added imports for reliability and logging
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import asyncio

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# In-memory storage for search results (session-based)
search_cache: Dict[str, Dict[str, List[dict]]] = {}
seen_pmc_ids: Dict[str, set] = {}

# Configure a requests Session with retries/backoff to reduce intermittent failures
logger = logging.getLogger(__name__)
_session = requests.Session()
_retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(["GET", "POST", "HEAD", "OPTIONS"])
)
_adapter = HTTPAdapter(max_retries=_retry_strategy)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

# PDF CHECK
def is_pdf_available(pmcid: str) -> bool:
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
    try:
        r = _session.head(pdf_url, timeout=10, allow_redirects=True)
        if r.status_code == 200 and "pdf" in r.headers.get("Content-Type", "").lower():
            return True
    except Exception:
        pass
    return False

# SAVE TO DATABASE
def save_article_to_db(metadata: dict, session_id: str, keyword: str = None):
    """
    Save article metadata to MongoDB.
    Uses upsert to update if article already exists.
    """
    try:
        collection = get_articles_collection()
        # Prepare article data
        article_data = {
            "pmc_id": metadata["pmc_id"],
            "title": metadata.get("title"),
            "journal": metadata.get("journal"),
            "doi": metadata.get("doi"),
            "publisher": metadata.get("publisher"),
            "article_url": metadata.get("article_url"),
            "pdf_url": metadata.get("pdf_url"),
            "abstract": metadata.get("abstract"),
            "authors": metadata.get("authors", []),
            "session_id": session_id,
            "keyword": keyword,
            "updated_at": datetime.utcnow()
        }
        # Upsert: update if exists, insert if not
        collection.update_one(
            {"pmc_id": metadata["pmc_id"]},
            {
                "$set": article_data,
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        return True
    except Exception as e:
        logger.exception("Error saving article to database: %s", e)
        return False
    
def save_selected_articles_to_db(session_id: str, pmc_ids: List[str]):
    """
    Save a record of user-selected articles to MongoDB.
    """
    try:
        collection = get_selected_articles_collection()
        selection_data = {
            "session_id": session_id,
            "pmc_ids": pmc_ids,
            "selected_at": datetime.utcnow()
        }
        collection.insert_one(selection_data)
        return True
    except Exception as e:
        logger.exception("Error saving selected articles to database: %s", e)
        return False
    
# KEYWORD VISIBILITY RULE
def keyword_in_title_or_abstract(keyword: str, title: Optional[str], abstract: Optional[str]) -> bool:
    """
    Enforce that the keyword appears in title or abstract.
    - Single word: substring match
    - Multi-word: exact phrase match
    """
    if not keyword:
        return True
    keyword_lc = keyword.lower()
    text_parts = []
    if title:
        text_parts.append(title.lower())
    if abstract:
        text_parts.append(abstract.lower())
    combined_text = " ".join(text_parts)
    return keyword_lc in combined_text
def keyword_in_text(keyword: str, text: Optional[str]) -> bool:
    if not keyword or not text:
        return False
    return keyword.lower() in text.lower()

# language filter helper
def build_english_search_term(keyword: str) -> str:
    if not keyword:
        return "english[lang]"
    return f"({keyword}) AND english[lang]"

# FETCH DETAILS
def fetch_pmc_details(pmcid: str) -> dict:
    """
    Robust efetch wrapper:
    - Uses a requests.Session with retries/backoff
    - Tries both numeric uid and PMC-prefixed id if needed
    - Logs failures and returns default dict with None values on failure
    """
    url = f"{EUTILS}/efetch.fcgi"

    # Try both the provided id and PMC-prefixed id (if not already)
    ids_to_try = [str(pmcid)]
    if not str(pmcid).upper().startswith("PMC"):
        ids_to_try.append(f"PMC{pmcid}")
    default = {"abstract": None, "doi": None, "publisher": None, "authors": []}
    for id_try in ids_to_try:
        try:
            res = _session.get(url, params={"db": "pmc", "id": id_try, "retmode": "xml"}, timeout=15)
            res.raise_for_status()
        except Exception as e:
            logger.exception("efetch request failed for id=%s: %s", id_try, e)
            # try next id format
            continue

        # Parse xml safely
        try:
            root = ET.fromstring(res.text)
        except Exception as e:
            logger.exception("efetch xml parse error for id=%s: %s. Response snippet: %.200s", id_try, e, res.text)
            continue
        article = root.find(".//article")
        if article is None:
            logger.warning("efetch returned no <article> element for id=%s. Trying next format if available.", id_try)
            continue

        data = {"abstract": None, "doi": None, "publisher": None, "authors": []}
        abs_elem = article.find(".//abstract")
        if abs_elem is not None:
            paragraphs = ["".join(p.itertext()).strip() for p in abs_elem.findall(".//p") if "".join(p.itertext()).strip()]
            if paragraphs:
                data["abstract"] = "\n".join(paragraphs)

        for id_elem in article.findall(".//article-id"):
            if id_elem.attrib.get("pub-id-type") == "doi":
                data["doi"] = id_elem.text
        publisher_elem = article.find(".//journal-meta/publisher/publisher-name")
        if publisher_elem is not None:
            data["publisher"] = publisher_elem.text

        # Extract authors
        authors = []
        contrib_group = article.find(".//contrib-group")
        if contrib_group is not None:
            for contrib in contrib_group.findall(".//contrib[@contrib-type='author']"):
                author_data = {}

                # Get given name
                given_names = contrib.find(".//given-names")
                if given_names is not None:
                    author_data["given_name"] = given_names.text

                # Get family name (surname)
                surname = contrib.find(".//surname")
                if surname is not None:
                    author_data["family_name"] = surname.text

                # Create full name
                if "given_name" in author_data and "family_name" in author_data:
                    author_data["full_name"] = f"{author_data['given_name']} {author_data['family_name']}"
                elif "given_name" in author_data:
                    author_data["full_name"] = author_data["given_name"]
                elif "family_name" in author_data:
                    author_data["full_name"] = author_data["family_name"]

                # Get affiliation
                aff = contrib.find(".//aff")
                if aff is not None:
                    aff_text = "".join(aff.itertext()).strip()
                    if aff_text:
                        author_data["affiliation"] = aff_text
                if author_data:  # Only add if we found at least some author info
                    authors.append(author_data)
        data["authors"] = authors

        # Successful parse; small pause to be polite to upstream
        time.sleep(0.08)
        return data
    
    # If we reach here, all attempts failed
    logger.error("efetch could not retrieve details for pmcid=%s (tried: %s). Returning defaults.", pmcid, ids_to_try)
    return default

# -----------------SEARCH ENDPOINT---------------
async def search_pmc(
    keyword: str,
    session_id: str,
    offset: int = 0,
    limit: int = 5,
    # timeframe: Optional[str] = Body(default=None, description="24h, 7d, or null for no filter"),
    timeframe: Optional[str] = Field(default=None, description="24h, 7d, or null for no filter"),
    request: Request = None
):
    if timeframe not in (None, "24h", "7d"):
        return {"error": "Invalid timeframe. Allowed values: 24h, 7d"}
    
    """
    Search endpoint with offset-based pagination.
    Stores all fetched metadata in memory for later retrieval via /select
   
    - offset: number of results to skip (0 for initial, 5 for load more(it will skip first 5 results), etc.)
    - limit: number of results to return (default 5)
    """
    # Initialize cache for this session if not exists
    if session_id not in search_cache:
        search_cache[session_id] = {}
        seen_pmc_ids[session_id] = set()
    query_key = f"{keyword}_{timeframe or 'all'}"
    if query_key not in search_cache[session_id]:
        search_cache[session_id][query_key] = []
    cached_results = search_cache[session_id][query_key]

    # RETURN FROM CACHE IF POSSIBLE
    if len(cached_results) >= offset + limit:
        return {
            "session_id": session_id,
            "keyword": keyword,
            "offset": offset,
            "results_count": limit,
            "results": cached_results[offset: offset + limit]
        }
   
    # FETCH MORE ONLY IF NEEDED
    api_offset = len(cached_results)
    target_count = offset + limit
    search_term = build_english_search_term(keyword)
    
    while len(cached_results) < target_count:
        search_params = {
            "db": "pmc",
            "term": search_term,
            "retmode": "json",
            "retstart": api_offset,
            "retmax": 10
        }

        if timeframe is not None:
            if timeframe == "24h":
                today = datetime.today()
                mindate = today - timedelta(days=1)
            elif timeframe == "7d":
                today = datetime.today()
                mindate = today - timedelta(days=7)
            elif timeframe in ("null", "", None):
                # Treat empty or "null" string as no filter
                pass
            else:
                return {"error": "Invalid timeframe. Allowed values: 24h, 7d, null"}
            
            # Apply filter only if mindate was set
            if timeframe in ("24h", "7d"):
                search_params.update({
                    "datetype": "pdat",
                    "mindate": mindate.strftime("%Y/%m/%d"),
                    "maxdate": today.strftime("%Y/%m/%d")
                })

        esearch = _session.get(
            f"{EUTILS}/esearch.fcgi",
            params=search_params
        ).json()
        ids = esearch.get("esearchresult", {}).get("idlist", [])
        if not ids:
            break
        api_offset += len(ids)
        summary = _session.get(
            f"{EUTILS}/esummary.fcgi",
            params={"db": "pmc", "id": ",".join(ids), "retmode": "json"}
        ).json()

        for uid in summary["result"]["uids"]:
            pmcid = f"PMC{uid}"

            # DUPLICATE PREVENTION
            if pmcid in seen_pmc_ids[session_id]:
                continue
            title = summary["result"][uid].get("title")
            if keyword_in_text(keyword, title):
                abstract = None
                match_source = "title"
            else:
                extra = await asyncio.to_thread(fetch_pmc_details, uid)
                abstract = extra.get("abstract")
            # keword visibility rule
                if not keyword_in_title_or_abstract(keyword, title, abstract):
                    continue
                match_source = "abstract"
            metadata = {
                "pmc_id": pmcid,
                "title": title,
                "journal": summary["result"][uid].get("fulljournalname"),
                "doi": extra.get("doi"),
                "publisher": extra.get("publisher"),
                "abstract": abstract,
                "article_url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/",
                "pdf_url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/",
            }
            cached_results.append(metadata)
            seen_pmc_ids[session_id].add(pmcid)
            if len(cached_results) >= target_count:
                break
            # NOTE: removed saving searched articles to DB — results are kept in cache only.
            if len(cached_results) >= target_count:
                break
            
    return {
        "session_id": session_id,
        "keyword": keyword,
        "timeframe": timeframe,
        "offset": offset,
        "results_count": len(cached_results[offset: offset + limit]),
        "results": cached_results[offset: offset + limit]
    }