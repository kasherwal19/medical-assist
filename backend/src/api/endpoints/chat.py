from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models.chat_models import ChatRequest, ChatResponse
from lib.logger import logging
from services.chat_service import ConversationRAGPipeline
from services.qdrant_host import current_qdrant_client
from qdrant_client import models

router=APIRouter()

rag_pipeline = ConversationRAGPipeline()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest):
    """
    Endpoint for chat responses based on document context.
    
    Returns a structured JSON response with:
    - session_id: The session identifier
    - selected_template: The template that was used
    - selected_images: List of image URLs
    - user_query: The original user query
    - response: Structured content with title and sections (each section has heading and paragraph)
    
    Args:
        request (ChatRequest): The chat request containing document IDs, prompt, and other parameters
    Returns:
        ChatResponse: Structured JSON response with title, headings, and paragraphs
    """
    try:
        session_id = request.session_id
        query = request.user_query
        template = request.template
        images = request.images
        parameters = request.parameters
        message_id = request.message_id

        # Debug logging for images
        logging.info(f"Chat endpoint received images: {images}")
        if images:
            for idx, img_url in enumerate(images):
                logging.info(f"Image {idx + 1}: {img_url}")
        else:
            logging.warning("No images received in chat request")

        current_qdrant_client.create_payload_index(
            collection_name="epocrates-v2",
            field_name="pmc_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )

        return await rag_pipeline.process_query_v2(session_id=session_id,
                                                   query=query,
                                                   template=template,
                                                   images=images,
                                                   parameters=parameters,
                                                   message_id=message_id)

    except HTTPException as e:
        raise e
    except Exception as e:
        message = f"Error in chat endpoint: {str(e)}"
        logging.error(message)
        raise HTTPException(status_code=500, detail=message)
 