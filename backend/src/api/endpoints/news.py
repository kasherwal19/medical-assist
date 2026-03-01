from fastapi import APIRouter, HTTPException, Query
from lib.logger import logging
from services.news_feed import fetch_health_news

router = APIRouter()

@router.get("/news/health")
async def get_health_news_endpoint(
    days: int = Query(7, ge=1, le=7),
    limit: int = Query(10, ge=1, le=10)
):
    
    try:
        return await fetch_health_news(days=days, limit=limit)

    except HTTPException as e:
        raise e

    except Exception as e:
        message = f"Error while fetching health news: {str(e)}"
        logging.error(message)
        raise HTTPException(status_code=500, detail=message)
