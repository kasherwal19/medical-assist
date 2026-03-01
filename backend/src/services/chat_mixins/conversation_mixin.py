"""
Conversation management mixin for chat service.
Handles conversation history retrieval, message ID management, and saving conversations.
"""

from typing import List, Dict, Optional
from datetime import datetime
from lib.logger import logging


class ConversationMixin:
    """Mixin class for conversation management methods."""

    async def get_conversation_history(
        self,
        session_id: str,
        upto_message_id: Optional[int]
    ) -> List[Dict]:
        """
        Fetch conversation history by traversing message_ids backwards
        until message_id == 1.
        Returns conversation in chronological order (oldest → newest).
        """
        conversation: List[Dict] = []
        current_message_id = upto_message_id

        try:
            while current_message_id and current_message_id > 0:
                doc = await self.conv_collection.find_one({
                    "session_id": session_id,
                    "message_id": current_message_id
                })

                if not doc:
                    logging.info(
                        f"No conversation found for session={session_id}, "
                        f"message_id={current_message_id}"
                    )
                    break

                if doc.get("chat"):
                    conversation.insert(0, doc["chat"])

                logging.info(
                    f"Fetched message_id {current_message_id}"
                )

                if current_message_id == 1:
                    break

                current_message_id -= 1

            logging.info(f"Retrieved {len(conversation)} messages for session {session_id}")
            return conversation

        except Exception as e:
            logging.error(
                f"Error retrieving conversation history: {e}",
                exc_info=True
            )
            return []

    async def get_next_message_id(self, session_id: str) -> int:
        """
        Get the next message_id number for a session.
        Returns 1 for new sessions, otherwise returns max_message_id + 1.
        """
        try:
            result = await self.conv_collection.find_one(
                {"session_id": session_id},
                sort=[("message_id", -1)]
            )

            if result and "message_id" in result:
                next_message_id = result["message_id"] + 1
                logging.info(f"Next message_id for session {session_id}: {next_message_id}")
                return next_message_id
            else:
                logging.info(f"First message_id for session {session_id}: 1")
                return 1

        except Exception as e:
            logging.error(f"Error getting next message_id: {e}", exc_info=True)
            return 1

    async def save_conversation(
        self,
        session_id: str,
        images: List[str],
        parameters: Dict[str, List],
        message_id: int,
        rag_docs: List[str],
        conversation: Dict[str, str]
    ) -> Optional[str]:
        """
        Save or update conversation in database.
        """
        try:
            schema = {
                "session_id": session_id,
                "message_id": message_id,
                "chat": conversation,
                "parameters": parameters,
                "images": images,
                "rag_docs": rag_docs,
                "timestamp": datetime.utcnow()
            }

            await self.conv_collection.update_one(
                {"session_id": session_id, "message_id": message_id},
                {"$set": schema},
                upsert=True
            )

            logging.info(
                f"Conversation saved: session={session_id}, message_id={message_id}"
            )
            return "saved in db"

        except Exception as e:
            logging.error(f"Failed to save in Database: {str(e)}", exc_info=True)
            return None
