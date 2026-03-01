# ------for pubmed_api--------
from services.pubmed_api import search_pmc as search_pmc_service
import uuid
from models.db_models import SearchArticle

async def search_pmc_endpoint(request: SearchArticle):

    keyword = request.keyword
    offset = request.offset
    limit = request.limit
    timeframe = request.timeframe
    session_id = str(uuid.uuid4())

    return await search_pmc_service(
        keyword=keyword,
        session_id=session_id,
        offset=offset,
        limit=limit,
        timeframe=timeframe
    )
