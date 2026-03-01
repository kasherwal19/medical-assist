from datetime import datetime
from lib.logger import logging
from utils.database import doc_db


async def save_session_images(
    session_id: str,
    document_name: str,
    message_id: int,
    images: list[dict]
):
    """
    Save highlighted image metadata into session_images collection.
    """
    if not images:
        logging.warning("No images to save for session_images")
        return

    payload = {
        "session_id": session_id,
        "document_name": document_name,
        "message_id": message_id,
        "images": images,
        "timestamp": datetime.utcnow()
    }

    await doc_db._db["session_images"].insert_one(payload)
    logging.info(
        f"Saved {len(images)} images for session={session_id}, doc={document_name}"
    )
