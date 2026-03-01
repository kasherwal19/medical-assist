from lib.logger import logging
from utils.database import doc_db
from services.highlight_image import process_highlights_for_chat_response_wrapper


class SourceService:
    """
    Service responsible for:
    - Triggering highlight pipeline 
    - Returning source image metadata
    """

    async def process_source_request(self, request):
        session_id = request.session_id
        message_id = request.message_id

        logging.info(
            f"[source_service] Processing request | "
            f"session_id={session_id}, message_id={message_id}"
        )

        # 1. Validate conversation exists (fetch parameters with rag_docs + response_text)
        conversation = await doc_db._db["conversations"].find_one({
            "session_id": session_id,
            "message_id": message_id
        })

        if not conversation:
            logging.warning(
                f"[source_service] Conversation not found | "
                f"session_id={session_id}, message_id={message_id}"
            )
            return {
                "session_id": session_id,
                "message_id": message_id,
                "count": 0,
                "source_url": []
            }

        # No cache - trigger fresh highlight generation
        logging.info(
            f"[source_service] No cached highlights found, triggering generation for "
            f"session {session_id}, message_id {message_id}"
        )

        # 2. Trigger highlight pipeline (rag_docs + response_text now in DB)

        try:
            await process_highlights_for_chat_response_wrapper(
                session_id=session_id,
                message_id=message_id
            )
        except Exception as e:
            logging.error(
                f"[source_service] Highlight pipeline failed | session_id={session_id}",
                exc_info=True
            )

        # 3. Fetch results after highlighting
        cursor = doc_db._db["session_images"].find({
            "session_id": session_id,
            "message_id": message_id
        })

        images = []
        async for doc in cursor:
            doc_name = doc.get("document_name")  
            for img in doc.get("images", []):
                images.append({
                    "url": img.get("url"),
                    "page_no": img.get("page_no"),
                    "document_name": doc_name  
                })

        if not images:
            logging.warning(
                f"[source_service] No images generated | "
                f"session_id={session_id}, message_id={message_id}"
            )

        return {
            "session_id": session_id,
            "message_id": message_id,
            "count": len(images),
            "source_url": images
        }


# Singleton instance
source_service = SourceService()
