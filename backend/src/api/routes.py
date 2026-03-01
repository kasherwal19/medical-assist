from fastapi import APIRouter
from api.endpoints.endpoints import search_pmc_endpoint
from api.endpoints.doc_extraction import router as extration_router
from api.endpoints.image_search import router as image_search_router
from api.endpoints.image_upload import image_upload_router
from api.endpoints.file_upload import upload_router
from api.endpoints.file_view import view_router
from api.endpoints.chat import router as chat
from api.endpoints.source import router as source_router
from api.endpoints.news import router as news_router

from datetime import datetime
routes = APIRouter()

routes.include_router(image_search_router)
routes.include_router(image_upload_router)

@routes.get("/health-check")
def health_check():
    return {
        "status_code": 200,
        "message": "Healthy like a fresh virtualenv on a Monday morning",
    }

@routes.get("/test-deployment")
def test_deployment():
    return {
        "status": "success",
        "message": "Deployment test endpoint - CODE UPDATED v2.0",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0",
        "database": "Cosmos DB Serverless",
    }


routes.post("/pubmed/search")(search_pmc_endpoint)
routes.include_router(extration_router)
routes.include_router(upload_router)
routes.include_router(view_router)
routes.include_router(chat)
routes.include_router(source_router)
routes.include_router(news_router)

