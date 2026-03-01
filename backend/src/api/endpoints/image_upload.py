import warnings
from fastapi import APIRouter, HTTPException, UploadFile, status, File
from services.s3_service import current_s3_client
from configs.config import credentials
from typing import List
from lib.logger import logging
import uuid
import mimetypes
from datetime import datetime

warnings.filterwarnings("ignore")

image_upload_router = APIRouter(prefix="/images", tags=["images"])

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
ALLOWED_IMAGE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "image/bmp"
}

MAX_IMAGE_FILES = 10
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@image_upload_router.post('/upload', status_code=status.HTTP_201_CREATED)
async def upload_images(
    files: List[UploadFile] = File(...)
):
    """
    Upload medical images
    
    - **files**: List of image files (PNG, JPG, GIF, WebP, BMP)
    """
    try:
        if len(files) > MAX_IMAGE_FILES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many files. Maximum {MAX_IMAGE_FILES} files allowed per upload. You tried to upload {len(files)} files."
            )
        
        uploaded_images = []
        failed_images = []
        session_id = str(uuid.uuid4())
        
        # Get async uploaded_images collection (separate from image library)
        from utils.database import AsyncDBHost
        db = AsyncDBHost()
        images_collection = db["uploaded_images"]
        
        for file in files:
            try:
                # Validate file extension
                file_ext = f".{file.filename.split('.')[-1].lower()}" if '.' in file.filename else ""
                
                if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
                    failed_images.append({
                        "filename": file.filename,
                        "error": "Invalid file type. Only PNG, JPG, JPEG, GIF, WebP, and BMP files are allowed."
                    })
                    continue

                # Validate MIME type
                if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
                    failed_images.append({
                        "filename": file.filename,
                        "error": f"Invalid MIME type. Expected image file, got {file.content_type}"
                    })
                    continue

                # Read file data
                file_data = await file.read()
                
                # Validate file size
                if len(file_data) > MAX_FILE_SIZE:
                    failed_images.append({
                        "filename": file.filename,
                        "error": f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024):.1f} MB"
                    })
                    continue

                # Generate unique image ID
                image_id = str(uuid.uuid4())
                
                # Create S3 key
                s3_key = f"{credentials.S3_DATA_STORAGE}/images/{image_id}/{file.filename}"

                # Check if image already exists
                existing_image = await images_collection.find_one({"filename": file.filename})

                if existing_image:
                    existing_s3_key = existing_image.get("s3_key", s3_key)
                    file_exists_in_s3 = await current_s3_client.check_file_exists(existing_s3_key)

                    if file_exists_in_s3:
                        logging.info(f"Image already exists in S3 and database: {file.filename}")
                        image_id = existing_image.get("id", image_id)
                        s3_key = existing_s3_key  # Use existing S3 key
                    else:
                        # Upload to S3
                        await current_s3_client._upload_to_s3(
                            key=s3_key,
                            data=file_data,
                            content_type=file.content_type
                        )
                else:
                    # Upload to S3
                    await current_s3_client._upload_to_s3(
                        key=s3_key,
                        data=file_data,
                        content_type=file.content_type
                    )
                
                # Prepare image metadata
                image_data = {
                    "id": image_id,
                    "session_id": session_id,
                    "filename": file.filename,
                    "s3_key": s3_key,
                    "content_type": file.content_type,
                    "file_size": len(file_data),
                    "uploaded_at": datetime.utcnow().isoformat()
                }
                
                if existing_image:
                    # Update existing image metadata
                    await images_collection.update_one(
                        {"filename": file.filename},
                        {"$set": image_data},
                        upsert=True
                    )
                    logging.info(f"Updated image metadata: {file.filename}")
                else:
                    # Insert new image metadata
                    await images_collection.insert_one(image_data)
                    logging.info(f"Inserted new image: {file.filename}")

                # Generate view URL for the uploaded image
                view_url = await current_s3_client.get_presigned_view_url(
                    key=s3_key,
                    expire_in_n_seconds=18000  # 5 hours
                )

                uploaded_images.append({
                    "id": image_id,
                    "filename": file.filename,
                    "size_bytes": len(file_data),
                    "view_url": view_url,
                    "status": "success"
                })
                
            except Exception as e:
                logging.error(f"Error uploading image {file.filename}: {str(e)}")
                failed_images.append({
                    "filename": file.filename,
                    "error": str(e)
                })

        return {
            "session_id": session_id,
            "total_uploaded": len(uploaded_images),
            "total_failed": len(failed_images),
            "uploaded_images": uploaded_images,
            "failed_images": failed_images,
            "status": "completed"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error during image upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during image upload: {str(e)}"
        )
