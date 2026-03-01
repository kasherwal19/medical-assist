import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.extraction_models import DocumentStatusInfo, ExtractionRequest, ExtractionResponse, StatusRequest
from utils.document_handling import DOCUMENT_TEXT_COLLECTION_NAME, initialize_collection_v2
from lib.hasher import hash_param
from typing import List
from lib.logger import logging
from utils.database import upsert_session_documents
from utils.doc_ext_utils import get_documents_status, process_document


router = APIRouter()

async def run_async_process(session_id: str, pmc_ids: List[str], user_upload: bool):
    """Process documents concurrently using asyncio instead of ThreadPoolExecutor"""
    try:
        initialize_collection_v2(collection_name=DOCUMENT_TEXT_COLLECTION_NAME)
        
        # Process all documents concurrently using asyncio.gather
        tasks = [
            asyncio.to_thread(process_document, session_id, pmc_id, user_upload)
            for pmc_id in pmc_ids
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log any errors but don't block on them
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Document processing failed for {pmc_ids[i]}: {result}")
        
        return results
    except Exception as e:
        logging.error(f"run_async_process failed: {e}")
        raise e

@router.post("/trigger-doc-processing")
async def trigger_document_processing(request: ExtractionRequest, background_tasks: BackgroundTasks):
    session_id = request.session_id
    document_ids = request.documents
    user_upload = request.user_upload
    try:
        if not session_id.strip() or not document_ids or not all(u.strip() for u in document_ids):
            raise HTTPException(status_code=400, detail="Both userId and uuid are required fields")
        
        session_id = await hash_param(session_id)

        upsert_session_documents(session_id=session_id, documents= document_ids)
        background_tasks.add_task(run_async_process, session_id, document_ids, user_upload)

        return ExtractionResponse(response= "Documents processing start...")
    except HTTPException as e:
        raise e
    except Exception as e:
        message = f"Error processing document: {str(e)}"
        logging.error(message)
        raise HTTPException(status_code=500, detail=message)
    

@router.post("/documents-status", response_model= List[DocumentStatusInfo])
async def check_documents_status(request: StatusRequest):
    if not request.pmc_ids:
        raise HTTPException(status_code=400, detail="pmc_ids list cannot be empty")
    
    if len(request.pmc_ids) > 100:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 100 documents can be checked at once"
        )
    
    try:
        documents = await get_documents_status(request.pmc_ids)
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching document status: {str(e)}"
        )