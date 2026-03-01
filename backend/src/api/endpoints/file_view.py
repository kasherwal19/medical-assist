"""
File View/Download Endpoint
Generates Azure SAS URLs for viewing/downloading uploaded files
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from services.s3_service import current_s3_client
from utils.database import article_collection
from lib.logger import logging
from typing import Optional

view_router = APIRouter()


class FileViewRequest(BaseModel):
    """Request model for getting file view URL."""
    pmc_id: Optional[str] = None
    filename: Optional[str] = None
    s3_key: Optional[str] = None
    expire_in_seconds: Optional[int] = 18000  


class FileViewResponse(BaseModel):
    """Response model for file view URL."""
    view_url: str
    filename: str
    s3_key: str
    expires_in_seconds: int


@view_router.post('/get-view-url', status_code=status.HTTP_200_OK, response_model=FileViewResponse)
async def get_file_view_url(request: FileViewRequest):
    """
    Generate a temporary SAS URL for viewing/downloading a file.

    You can provide one of:
    - pmc_id: Document ID (e.g., "PMC123456789")
    - filename: Original filename
    - s3_key: Full blob path (e.g., "Epocrates/documents/file.pdf")

    Returns:
    - view_url: Temporary Azure SAS URL (expires in 5 hours by default)
    - filename: Original filename
    - s3_key: Full path in Azure Blob Storage
    """
    try:
        # Case 1: Get file by PMC ID
        if request.pmc_id:
            # First try articles collection (for uploaded files)
            document = await article_collection.find_one({"pmc_id": request.pmc_id})
            if document and document.get("s3_key"):
                s3_key = document.get("s3_key")
                filename = document.get("filename")
            else:
                # If not found in articles, check document_status (for PubMed downloads)
                from utils.database import status_collection
                status_doc = await status_collection.find_one({"pmc_id": request.pmc_id, "status": "SUCCESS"})
                if not status_doc or not status_doc.get("s3_key"):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Document with PMC ID '{request.pmc_id}' not found or not yet processed"
                    )
                s3_key = status_doc.get("s3_key")
                filename = status_doc.get("filename", f"{request.pmc_id}.pdf")

        # Case 2: Get file by filename
        elif request.filename:
            document = await article_collection.find_one({"filename": request.filename})
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document with filename '{request.filename}' not found"
                )
            s3_key = document.get("s3_key")
            filename = document.get("filename")

        # Case 3: Direct s3_key provided
        elif request.s3_key:
            s3_key = request.s3_key
            filename = s3_key.split("/")[-1]

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either pmc_id, filename, or s3_key"
            )

        # Check if file exists in Azure Blob Storage
        file_exists = await current_s3_client.check_file_exists(s3_key)
        if not file_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found in Azure Blob Storage: {s3_key}"
            )

        # Generate SAS view URL
        view_url = await current_s3_client.get_presigned_view_url(
            key=s3_key,
            expire_in_n_seconds=request.expire_in_seconds
        )

        logging.info(f"Generated view URL for {filename} (key: {s3_key})")

        return FileViewResponse(
            view_url=view_url,
            filename=filename,
            s3_key=s3_key,
            expires_in_seconds=request.expire_in_seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating view URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate view URL: {str(e)}"
        )


@view_router.get('/view/{pmc_id}', status_code=status.HTTP_200_OK, response_model=FileViewResponse)
async def get_file_view_url_by_id(pmc_id: str, expire_in_seconds: int = 18000):
    """
    Generate a temporary SAS URL for viewing/downloading a file by PMC ID.

    Simple GET endpoint - just provide PMC ID in URL.

    Example: GET /api/view/PMC123456789

    Returns:
    - view_url: Temporary Azure SAS URL (expires in 5 hours by default)
    - filename: Original filename
    - s3_key: Full path in Azure Blob Storage
    """
    request = FileViewRequest(pmc_id=pmc_id, expire_in_seconds=expire_in_seconds)
    return await get_file_view_url(request)
