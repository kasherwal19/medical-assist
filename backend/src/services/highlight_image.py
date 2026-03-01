import re
from lib.logger import logging
from utils.database import doc_db
from utils.source_highlighter import process_highlights_for_chat_response


def strip_html_tags(text: str) -> str:
    """Remove HTML tags and return plain text content."""
    if not isinstance(text, str):
        return str(text) if text else ""

    try:
        # Remove style and script tags with their content
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<head[^>]*>.*?</head>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove all other HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)

        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")

        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        logging.error(f"[highlight_image] HTML stripping failed: {e}")
        return text


async def process_highlights_for_chat_response_wrapper(
    session_id: str,
    message_id: int
):
    logging.info(
        f"[highlight_image] Triggered | session_id={session_id}, message_id={message_id}"
    )

    convo = await doc_db._db["conversations"].find_one({
        "session_id": session_id,
        "message_id": message_id
    })

    if not convo:
        logging.warning(
            f"[highlight_image] Conversation not found | "
            f"session_id={session_id}, message_id={message_id}"
        )
        return

    # RENAMED for clarity
    rag_docs = convo.get("rag_docs", [])
    assistant_response = convo.get("chat", {}).get("assistant", "")

    # Handle both dict (structured content) and string formats
    if isinstance(assistant_response, dict):
        # Convert structured content to plain text and strip HTML
        text_parts = []
        if "title" in assistant_response:
            text_parts.append(strip_html_tags(assistant_response["title"]))

        for section in assistant_response.get("sections", []):
            if isinstance(section, dict):
                if "heading" in section:
                    text_parts.append(strip_html_tags(section["heading"]))
                if "paragraph" in section:
                    # Paragraphs are the main content - strip HTML from them
                    text_parts.append(strip_html_tags(section["paragraph"]))

        assistant_response = "\n\n".join(text_parts)
        logging.info(
            f"[highlight_image] Converted structured dict to text (HTML stripped) | "
            f"Total length: {len(assistant_response)} chars | "
            f"Preview: {assistant_response[:300]}..."
        )
    elif not isinstance(assistant_response, str):
        assistant_response = str(assistant_response)

    if not rag_docs and not assistant_response:
        logging.warning(
            "[highlight_image] No highlighting inputs found | "
            "rag_docs and assistant_response both empty"
        )
        return

    logging.info(
        f"[highlight_image] Inputs ready | "
        f"rag_docs={len(rag_docs)}, assistant_response_len={len(assistant_response)}"
    )

    await process_highlights_for_chat_response(
        session_id=session_id,
        message_id=message_id,
        rag_docs=rag_docs,
        assistant_response=assistant_response
    )
