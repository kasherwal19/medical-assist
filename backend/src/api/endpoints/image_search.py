from fastapi import APIRouter, Query
from schema.image import ImageSearchResponse
from services.image_service import image_service

router = APIRouter(prefix="/images", tags=["images"])


@router.get("", response_model=ImageSearchResponse)
async def get_all_images():
    """Get all images from Azure Blob Storage"""
    results = image_service.search_images(speciality="all", disease_area="all")
    return ImageSearchResponse(
        total=results["total"],
        results=results["results"]
    )


@router.get("/filter", response_model=ImageSearchResponse)
async def filter_images(
    speciality: str = Query("all", description="all | oncologist | pediatrician | general physician"),
    disease_area: str = Query("all", description="all | disease name such as cancer, leukemia, heart disease"),
):
    """Filter images by speciality and disease area"""
    results = image_service.search_images(speciality=speciality, disease_area=disease_area)
    return ImageSearchResponse(
        total=results["total"],
        results=results["results"]
    )

