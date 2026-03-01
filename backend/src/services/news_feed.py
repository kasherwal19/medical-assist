import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException
from typing import Dict
from configs.config import news_config

load_dotenv()

if not news_config.NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY not set")

async def fetch_health_news(days: int, limit: int) -> Dict:
    """
    Fetch recent medical and health-related news articles from NewsData.io using predefined
    backend filters. 

    Args:
        days (int): Number of past days to consider when filtering articles based on their 
        publication date.
        limit (int): Maximum number of articles to return.

    Returns:
        dict: A dictionary containing:
            - days (int): The number of days used for filtering.
            - count (int): Number of articles returned.
            - articles (list[dict]): List of filtered news articles, each with:
                - title (str): Article title.
                - description (str): Short article description.
                - source (str): Source identifier.
                - published_at (str): Publication date/time.
                - url (str): Article URL.

    Raises:
        HTTPException:
            - 502 if the external NewsData.io API request fails.
            - 400 if the API response status is not successful.
    """

    # Input validation
    if days < 0:
        raise HTTPException(status_code=422, detail="days must be >= 0")

    if limit < 1 or limit > 10:
        raise HTTPException(
            status_code=422,
            detail="limit must be between 1 and 10"
        )

    # Backend-only query parameters
    params = {
        "apikey": news_config.NEWS_API_KEY,
        "q": "health medical diseases",
        "language": "en",
        "category": "health",
        "removeduplicate": 1
    }

    try:
        response = requests.get(news_config.NEWS_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

    data = response.json()
    if data.get("status") != "success":
        raise HTTPException(status_code=400, detail=data)
    
    # Backend date filtering logic
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    articles = []
    for article in data.get("results", []):
        pub_date_str = article.get("pubDate")
        if not pub_date_str:
            continue

        pub_date = datetime.strptime(pub_date_str[:10], "%Y-%m-%d")
        if pub_date >= cutoff_date:
            articles.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "source": article.get("source_id"),
                "published_at": article.get("pubDate"),
                "url": article.get("link"),
            })

        if len(articles) >= limit:
            break

    return {
        "days": days,
        "count": len(articles),
        "articles": articles
    }