
from io import StringIO
import uuid
import fitz
from time import time
import pandas as pd
from lib.logger import logging
from services.s3_service import current_s3_client
from utils.chunker import create_optimized_marked_chunks
from services.qdrant_host import current_qdrant_client
from qdrant_client.http.models import PointStruct, Distance, VectorParams
from configs.config import azure_openai_settings
from services.llm_service import azure_embedding_client

DOCUMENT_TEXT_COLLECTION_NAME = "epocrates-v2"

def initialize_collection_v2(collection_name: str) -> bool:
    """
    Initialize a collection if it doesn't exist.
    Returns True if collection was created, False if it already existed."""

    # Validate input
    if not collection_name or not isinstance(collection_name, str):
        raise ValueError("collection_name must be a non-empty string")
    
    if not collection_name.strip():
        raise ValueError("collection_name cannot be whitespace only")
    
    collection_name = collection_name.strip()
    
    try:
        if current_qdrant_client.collection_exists(collection_name):
            return False

        # Azure OpenAI text-embedding-3-large uses 3072 dimensions
        current_qdrant_client.create_collection(
            collection_name=collection_name,
            shard_number=5,
            vectors_config=VectorParams(
                size=3072,  # text-embedding-3-large dimension
                distance=Distance.COSINE
            )
        )
        logging.info(f"Created collection '{collection_name}' with Azure OpenAI embeddings (3072 dimensions)")
        return True

    except Exception as e:
        logging.error(f"Failed to initialize collection '{collection_name}': {e}")
        raise

def add_document_to_collection_v2(document_extracted_text: str, pmc_id: str) -> str:
    """
    Add a document to an existing collection with chunking and Azure OpenAI embeddings.
    """
    # Input validation
    if not document_extracted_text or not isinstance(document_extracted_text, str):
        logging.error(f"[ADD-DOC] Invalid document_extracted_text for {pmc_id}: type={type(document_extracted_text)}, empty={not document_extracted_text}")
        raise ValueError("document_extracted_text must be a non-empty string")

    if not pmc_id or not isinstance(pmc_id, str):
        raise ValueError("pmc_id must be a non-empty string")

    pmc_id = pmc_id.strip()
    logging.info(f"[ADD-DOC] Processing document {pmc_id}, text length: {len(document_extracted_text)} chars")
    # azure_client = None

    try:
        start_time = time()
        chunks = create_optimized_marked_chunks(document_extracted_text)

        if not chunks:
            logging.error(f"[ADD-DOC] No chunks created for document {pmc_id} - text extraction may have failed")
            raise ValueError(f"No chunks created for document {pmc_id}. Text extraction may have failed or document is empty.")

        logging.info(f"Created {len(chunks)} chunks for document {pmc_id}")
        embed_start = time()

        # Generate embeddings using Azure OpenAI
        response = azure_embedding_client.embeddings.create(
            input=chunks,
            model=azure_openai_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        )

        embeddings = [item.embedding for item in response.data]

        embed_time = time() - embed_start
        logging.info(f"Azure OpenAI embedding took {embed_time:.2f} seconds for {len(chunks)} chunks")
 
        points = []
        max_id = (1 << 63)-1

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            if embedding is None or not isinstance(embedding, list):
                logging.warning(f"Invalid embedding for chunk {i} in document {pmc_id}, skipping")
                continue

            if len(embedding) != 3072:
                logging.warning(f"Wrong embedding dimension {len(embedding)} for chunk {i}, expected 3072")
                continue

            points.append(
                PointStruct(
                    id=uuid.uuid4().int & max_id,
                    payload={
                        "text": chunk,
                        "pmc_id": pmc_id,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "timestamp": start_time
                    },
                    vector=embedding  # Dense vector from Azure OpenAI
                )
            )
        
        if not points:
            raise ValueError(f"No valid points created for document {pmc_id}")
        
        logging.info(f"Uploading {len(points)} points to collection for document {pmc_id}")
        
        batch_size = 100
        total_batches = (len(points) - 1) // batch_size + 1
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            batch_num = i // batch_size + 1
            try:
                logging.info(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} points) for {pmc_id}")
                # Use explicit operation with timeout
                operation_result = current_qdrant_client.upsert(
                    collection_name=DOCUMENT_TEXT_COLLECTION_NAME,
                    points=batch,
                    wait=True
                )
                logging.info(f"✓ Batch {batch_num}/{total_batches} uploaded for {pmc_id}. Result: {operation_result}")
            except Exception as batch_error:
                logging.error(f"✗ Failed to upload batch {batch_num}/{total_batches} for {pmc_id}: {type(batch_error).__name__}: {batch_error}")
                raise
        
        end_time = time()
        total_time = end_time - start_time
        
        logging.info(
            f"✓ Successfully added document {pmc_id} to collection. "
            f"Total time: {total_time:.2f}s, Chunks: {len(points)}, "
            f"Embedding: {embed_time:.2f}s, Upload: {(total_time - embed_time):.2f}s"
        )
        
        return pmc_id
        
    except ValueError as e:
        logging.error(f"Validation error for document {pmc_id}: {e}")
        raise
    
    except Exception as e:
        logging.error(
            f"Failed to add document {pmc_id} to collection: {type(e).__name__}: {e}",
            exc_info=True)
        raise


async def extract_text_from_pdf_data_for_vectorisation(pdf_content: bytes, pdf_name: str,filetype: str, session_id:str, pmc_id: str) -> str:
    """
    Asynchronously extract text from PDF content.
    """
    pdf_document = None
    try:
        # TEXT EXTRACTION INTO DATAFRAME FOR HIGHLIGHTS
        highlights_helper_table = []
        pdf_document = fitz.open(stream=pdf_content, filetype= filetype)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            lines = page.get_text("dict")["blocks"]
 
            line_counter = 1
            for block in lines:
                for line in block.get("lines", []):
                    line_text = " ".join([span["text"] for span in line["spans"]]).strip()
                    if line_text:
                        #get bounding box from the line itself
                        x0 = min([span["bbox"][0] for span in line["spans"]])
                        y0 = min([span["bbox"][1] for span in line["spans"]])
                        x1 = max([span["bbox"][2] for span in line["spans"]])
                        y1 = max([span["bbox"][3] for span in line["spans"]])
 
                        highlights_helper_table.append({
                            "Page Number": page_num + 1,
                            "Line Number": line_counter,
                            "Content": line_text,
                            "Coordinates": (x0, y0, x1, y1)
                        })
                        line_counter += 1

        df = pd.DataFrame(highlights_helper_table)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, escapechar='\\', doublequote=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")  # Convert to bytes

        # Define the key
        key = f'Epocrates/highlight_helper_tables/{pmc_id}.csv'

        # Upload using AsyncS3Host
        await current_s3_client.save_to_s3(csv_bytes, key)

        # TEXT EXTRACTION FOR VECTORISATION
        extracted_text = []
        extracted_text.append(f'DOCUMENT <{pdf_name}> CONTENTS STARTS HERE')
        
        logging.info(f"[TEXT-EXTRACTION] Starting text extraction for {pmc_id}, PDF has {len(pdf_document)} pages")
        
        total_text_content = 0  # Track actual text content extracted
       
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text("text") or ""
            page_text = page_text.replace("©", "").replace("�", "")
            page_text_stripped = page_text.strip()
            total_text_content += len(page_text_stripped)
           
            extracted_text.append(f'PAGE NUMBER {page_num + 1} STARTS HERE')
            extracted_text.append(page_text_stripped)
            extracted_text.append(f'PAGE NUMBER {page_num + 1} ENDS HERE')
            
            if page_num == 0:
                logging.info(f"[TEXT-EXTRACTION] Page 1 text length: {len(page_text_stripped)} chars")
       
        extracted_text.append(f'DOCUMENT <{pdf_name}> CONTENTS ENDS HERE')
        
        output = "\n".join(extracted_text)
        logging.info(f"[TEXT-EXTRACTION] Total extracted text length for {pmc_id}: {len(output)} chars (actual content: {total_text_content} chars)")
        
        # Check if PDF is likely image-based (no extractable text)
        if total_text_content < 50:
            logging.warning(f"[TEXT-EXTRACTION] PDF {pdf_name} appears to be image-based or has minimal text ({total_text_content} chars). OCR may be required.")
            raise ValueError(f"PDF '{pdf_name}' appears to be a scanned/image-based document with no extractable text. Please upload a text-based PDF or use OCR to convert the document first.")
        
        return output, key

    except Exception as e:
        logging.exception(f"[TEXT-EXTRACTION] Error extracting text from PDF {pdf_name}")
        raise Exception(f"Error extracting text from PDF {pdf_name}: {str(e)}")
    
    finally:
        if pdf_document:
            pdf_document.close()

 
