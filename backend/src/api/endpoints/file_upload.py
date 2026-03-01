
import warnings
from fastapi import APIRouter, HTTPException, UploadFile, status, File
from services.s3_service import current_s3_client
from configs.config import credentials
from typing import List
from lib.logger import logging
import uuid
from utils.database import article_collection
warnings.filterwarnings("ignore")

upload_router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

MAX_FILES = 5

@upload_router.post('/upload-file', status_code=status.HTTP_201_CREATED)
async def document_upload(files: List[UploadFile] = File(...)):
    try:
        if len(files) > MAX_FILES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many files. Maximum {MAX_FILES} files allowed per upload. You tried to upload {len(files)} files."
            )
        
        uploaded_files = []
        failed_files = []
        session_id = str(uuid.uuid4())
        
        for file in files:
            try:
                file_ext = f".{file.filename.split('.')[-1].lower()}" if '.' in file.filename else ""
                
                if file_ext not in ALLOWED_EXTENSIONS:
                    failed_files.append({
                        "filename": file.filename,
                        "error": "Invalid file type. Only PDF and DOC/DOCX files are allowed."
                    })
                    continue

                if file.content_type not in ALLOWED_MIME_TYPES:
                    failed_files.append({
                        "filename": file.filename,
                        "error": "Invalid file type. Only PDF and DOC/DOCX files are allowed."
                    })
                    continue

                file_data = await file.read()

                s3_key = f"{credentials.S3_DATA_STORAGE}/documents/{file.filename}"

                existing_file = await article_collection.find_one({"s3_key": s3_key})

                if existing_file:
                    file_exists_in_s3 = await current_s3_client.check_file_exists(s3_key)
                    
                    if file_exists_in_s3:
                        pmc_id = existing_file["pmc_id"]
                        logging.info(f"File already exist in s3 and Document DB")
                    else:
                        pmc_id = existing_file["pmc_id"]
                        await current_s3_client._upload_to_s3(
                            key=s3_key,
                            data=file_data,
                            content_type=file.content_type
                        )
                else:
                    pmc_number = str(uuid.uuid4().int & ((1 << 30) - 1))[:9].zfill(9)
                    pmc_id = f"PMC{pmc_number}"

                    # Upload to S3
                    await current_s3_client._upload_to_s3(
                        key=s3_key,
                        data=file_data,
                        content_type=file.content_type
                    )
                
                document_data = {
                    "session_id": session_id,
                    "pmc_id": pmc_id,
                    "s3_key": s3_key,
                    "filename": file.filename
                }
                
                if existing_file:
                    # Update existing document
                    await article_collection.update_one(
                        {"filename": file.filename},
                        {"$set": document_data}, upsert=True
                    )
                else:
                    # Insert new document
                    await article_collection.insert_one(document_data)
                
                uploaded_files.append(pmc_id)
                
            except Exception as e:
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e)
                })

        response = {
            "session_id": session_id,
            "documents": uploaded_files,
            "total_uploaded": len(uploaded_files),
            "total_failed": len(failed_files)
        }
        
        if failed_files:
            response["failed_files"] = failed_files

        if len(uploaded_files) == 0 and len(failed_files) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")