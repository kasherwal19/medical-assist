import asyncio
from time import time
from typing import List
from lib.logger import logging
from configs.config import credentials, mongo_db_settings
from playwright.async_api import async_playwright
from services.s3_service import current_s3_client
from utils.database import is_pmc_already_processed, update_document_status
from utils.document_handling import add_document_to_collection_v2
from utils.document_handling import extract_text_from_pdf_data_for_vectorisation
from models.extraction_models import DocumentStatusInfo

async def get_documents_status(pmc_ids: List[str]) -> List[DocumentStatusInfo]:
    """
    Fetch status of multiple documents from MongoDB.
    Adjust this function based on your MongoDB collection structure.
    """
    try:
        from utils.database import get_async_database_connection, status_collection
        
        client = get_async_database_connection()
        db = client["epocrates"]
        collection = db["document_status"]
        
        results = []
        for pmc_id in pmc_ids:
            doc = await status_collection.find_one({"pmc_id": pmc_id})
            if doc:
                results.append(DocumentStatusInfo(pmc_id= pmc_id, status= doc.get("status", "UNKNOWN")))
            else:
                results.append(DocumentStatusInfo(pmc_id= pmc_id, status= doc.get("status", "NOT_FOUND")))
        
        return results
    except Exception as e:
        raise ValueError(f"Error: {str(e)}")


# async def process_pmc_document(session_id: str, pmc_id: str, user_upload: bool):
#     start_time = time()
#     pdf_filename = f"{pmc_id}.pdf"
    
#     try:
#         if user_upload:
#             # Create a fresh MongoDB client in this event loop
#             from motor.motor_asyncio import AsyncIOMotorClient
#             mongo_client = AsyncIOMotorClient(mongo_db_settings.DOCUMENT_DB_CONNECTION_STRING)
#             db = mongo_client["epocrates"]
#             collection = db["articles"]
            
#             try:
#                 document_data = await collection.find_one({"pmc_id": pmc_id})
                
#                 if not document_data or not document_data.get('s3_key'):
#                     raise RuntimeError(f"Document data not found in DB for {pmc_id}")
                
#                 existing_s3_key = document_data['s3_key']
#                 pdf_filename = document_data.get('filename', f"{pmc_id}.pdf")
#             finally:
#                 mongo_client.close()

#         update_document_status(
#             pmc_id=pmc_id,
#             filename=pdf_filename,
#             status="IN_PROGRESS",
#             s3_key="Not generated",
#             s3_csv_key="not generated"
#         )

#         if user_upload:
#             pdf_bytes = await current_s3_client.get_from_s3(existing_s3_key)
            
#             if not pdf_bytes:
#                 update_document_status(
#                     pmc_id=pmc_id,
#                     filename=pdf_filename,
#                     status=f"FAILED to fetch pdf from s3"
#                 )
#                 raise RuntimeError(f"Failed to retrieve PDF from S3: {existing_s3_key}")
            
#             logging.info(f"PDF retrieved from S3 for user upload: {pmc_id}")
#             s3_key = existing_s3_key
#         else:
#             async with async_playwright() as p:
#                 browser = await p.chromium.launch(headless=True)
#                 context = await browser.new_context(
#                     user_agent=(
#                         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                         "AppleWebKit/537.36 (KHTML, like Gecko) "
#                         "Chrome/114.0.0.0 Safari/537.36"
#                     )
#                 )
#                 page = await context.new_page()

#                 url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc_id}/pdf/"
#                 await page.goto(url, timeout=60_000)

#                 cookie_name = "cloudpmc-viewer-pow"
#                 for _ in range(60):
#                     cookies = await context.cookies()
#                     if any(c["name"] == cookie_name for c in cookies):
#                         break
#                     await asyncio.sleep(1)
#                 else:
#                     await browser.close()
#                     raise RuntimeError("PoW validation failed")

#                 resp = await context.request.get(url)
#                 content_type = resp.headers.get("content-type", "").lower()

#                 if not (resp.ok and "application/pdf" in content_type):
#                     await browser.close()
#                     raise RuntimeError("Downloaded content is not a PDF")

#                 pdf_bytes = await resp.body()
#                 await browser.close()

#             s3_key = f"{credentials.S3_DATA_STORAGE}/documents/{pmc_id}.pdf"
#             await current_s3_client.save_to_s3(
#                 file_data=pdf_bytes,
#                 key=s3_key
#             )

#             logging.info(f"PDF downloaded successfully for {pmc_id}")

#         extracted_text, s3_csv_key = await extract_text_from_pdf_data_for_vectorisation(
#             pdf_content=pdf_bytes,
#             pdf_name=pdf_filename,
#             filetype= filetype,
#             session_id=session_id,
#             pmc_id=pmc_id
#         )

#         add_document_to_collection_v2(extracted_text, pmc_id)

#         update_document_status(
#             pmc_id=pmc_id,
#             filename=pdf_filename,
#             status="SUCCESS",
#             s3_key=s3_key,
#             s3_csv_key=s3_csv_key
#         )

#         total_time = time() - start_time
#         logging.info(
#             f"Document {pmc_id} fully processed in {total_time:.2f} seconds"
#         )

#         return True

#     except Exception as e:
#         update_document_status(
#             pmc_id=pmc_id,
#             filename=pdf_filename,
#             status=f"FAILED, ERROR: {e}"
#         )
#         logging.exception(f"Processing failed for {pmc_id}: {e}")
#         raise


async def process_pmc_document(session_id: str, pmc_id: str, user_upload: bool):
    start_time = time()
    pdf_filename = f"{pmc_id}.pdf"
    filetype = "pdf"  # Default filetype
    
    try:
        if user_upload:
            # Create a fresh MongoDB client in this event loop
            from motor.motor_asyncio import AsyncIOMotorClient
            mongo_client = AsyncIOMotorClient(mongo_db_settings.DOCUMENT_DB_CONNECTION_STRING)
            db = mongo_client["epocrates"]
            collection = db["articles"]
            
            try:
                document_data = await collection.find_one({"pmc_id": pmc_id})
                
                if not document_data or not document_data.get('s3_key'):
                    raise RuntimeError(f"Document data not found in DB for {pmc_id}")
                
                existing_s3_key = document_data['s3_key']
                pdf_filename = document_data.get('filename', f"{pmc_id}.pdf")
                
                # Determine filetype based on filename extension
                if pdf_filename.lower().endswith('.docx'):
                    filetype = "docx"
                elif pdf_filename.lower().endswith('.pdf'):
                    filetype = "pdf"
                else:
                    # Fallback: check s3_key if filename doesn't have extension
                    if existing_s3_key.lower().endswith('.docx'):
                        filetype = "docx"
                    elif existing_s3_key.lower().endswith('.pdf'):
                        filetype = "pdf"
                    else:
                        raise RuntimeError(f"Unsupported file type for {pmc_id}. Only PDF and DOCX are supported.")
                        
            finally:
                mongo_client.close()

        update_document_status(
            pmc_id=pmc_id,
            filename=pdf_filename,
            status="IN_PROGRESS",
            s3_key="Not generated",
            s3_csv_key="not generated"
        )

        if user_upload:
            pdf_bytes = await current_s3_client.get_from_s3(existing_s3_key)
            
            if not pdf_bytes:
                update_document_status(
                    pmc_id=pmc_id,
                    filename=pdf_filename,
                    status=f"FAILED to fetch file from s3"
                )
                raise RuntimeError(f"Failed to retrieve file from S3: {existing_s3_key}")
            
            logging.info(f"File retrieved from S3 for user upload: {pmc_id}, filetype: {filetype}")
            s3_key = existing_s3_key
        else:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/114.0.0.0 Safari/537.36"
                    )
                )
                page = await context.new_page()

                url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc_id}/pdf/"
                await page.goto(url, timeout=60_000)

                cookie_name = "cloudpmc-viewer-pow"
                for _ in range(60):
                    cookies = await context.cookies()
                    if any(c["name"] == cookie_name for c in cookies):
                        break
                    await asyncio.sleep(1)
                else:
                    await browser.close()
                    raise RuntimeError("PoW validation failed")

                resp = await context.request.get(url)
                content_type = resp.headers.get("content-type", "").lower()

                if not (resp.ok and "application/pdf" in content_type):
                    await browser.close()
                    raise RuntimeError("Downloaded content is not a PDF")

                pdf_bytes = await resp.body()
                await browser.close()

            s3_key = f"{credentials.S3_DATA_STORAGE}/documents/{pmc_id}.pdf"
            await current_s3_client.save_to_s3(
                file_data=pdf_bytes,
                key=s3_key
            )

            logging.info(f"PDF downloaded successfully for {pmc_id}")

        extracted_text, s3_csv_key = await extract_text_from_pdf_data_for_vectorisation(
            pdf_content=pdf_bytes,
            pdf_name=pdf_filename,
            filetype=filetype,
            session_id=session_id,
            pmc_id=pmc_id
        )

        logging.info(f"[DOC-PROCESSING] Extracted text for {pmc_id}: {len(extracted_text) if extracted_text else 0} chars")

        add_document_to_collection_v2(extracted_text, pmc_id)

        update_document_status(
            pmc_id=pmc_id,
            filename=pdf_filename,
            status="SUCCESS",
            s3_key=s3_key,
            s3_csv_key=s3_csv_key
        )

        total_time = time() - start_time
        logging.info(
            f"Document {pmc_id} fully processed in {total_time:.2f} seconds"
        )

        return True

    except Exception as e:
        update_document_status(
            pmc_id=pmc_id,
            filename=pdf_filename,
            status=f"FAILED, ERROR: {e}"
        )
        logging.exception(f"Processing failed for {pmc_id}: {e}")
        raise


def process_document(session_id: str, pmc_id: str, user_upload: bool):
    """
    Process document by running all tasks concurrently.
    Safe to call from ThreadPoolExecutor.
    """
    if is_pmc_already_processed(pmc_id, user_upload):
        msg = f"{pmc_id} already processed successfully. Skipping."
        logging.info(msg)
        return msg

    start_time = time()
    loop = None

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            process_pmc_document(
                session_id=session_id,
                pmc_id=pmc_id,
                user_upload=user_upload
            )
        )
        return f"Document {pmc_id} processed successfully"

    except Exception as e:
        processing_time_taken = time() - start_time
        error_message = (
            f"Document processing failed: {str(e)} | "
            f"Time taken: {processing_time_taken:.2f}s"
        )
        logging.error(error_message)
        return error_message

    finally:
        if loop:
            loop.close()

