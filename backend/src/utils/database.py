from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import List, Optional
from configs.config import mongo_db_settings
from lib.logger import logging

# Singleton pattern for database connections
_async_client: Optional[AsyncIOMotorClient] = None
_sync_client: Optional[MongoClient] = None


def get_database_connection():
    """
    Get synchronous MongoDB database connection.
    Use this for non-async operations.
    """
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(mongo_db_settings.DOCUMENT_DB_CONNECTION_STRING)
    return _sync_client

def get_async_database_connection():
    """
    Get asynchronous MongoDB database connection.
    Use this for async operations (recommended with FastAPI).
    """
    global _async_client
    if _async_client is None:
        _async_client = AsyncIOMotorClient(mongo_db_settings.DOCUMENT_DB_CONNECTION_STRING)
    return _async_client

def get_articles_collection(db_name: str = "epocrates"):
    """
    Get the articles collection from the database.

    Args:
        db_name: Name of the database (default: "epocrates")

    Returns:
        MongoDB collection object for articles
    """
    client = get_database_connection()
    db = client[db_name]
    return db["articles"]

def get_async_articles_collection(db_name: str = "epocrates"):
    """
    Get the articles collection from the database (async version).

    Args:
        db_name: Name of the database (default: "epocrates")

    Returns:
        Async MongoDB collection object for articles
    """
    client = get_async_database_connection()
    db = client[db_name]
    return db["articles"]

def get_selected_articles_collection(db_name: str = "epocrates"):
    """
    Get the selected_articles collection from the database.

    Args:
        db_name: Name of the database (default: "epocrates")

    Returns:
        MongoDB collection object for selected articles
    """
    client = get_database_connection()
    db = client[db_name]
    return db["selected_articles"]

def get_async_selected_articles_collection(db_name: str = "epocrates"):
    """
    Get the selected_articles collection from the database (async version).

    Args:
        db_name: Name of the database (default: "epocrates")

    Returns:
        Async MongoDB collection object for selected articles
    """
    client = get_async_database_connection()
    db = client[db_name]
    return db["selected_articles"]

def close_database_connection():
    """Close database connections."""
    global _sync_client, _async_client
    if _sync_client:
        _sync_client.close()
        _sync_client = None
    if _async_client:
        _async_client.close()
        _async_client = None


from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from configs.config import mongo_db_settings
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from datetime import datetime

ARTICLE_COLLECTION_NAME = "articles"
STATUS_COLLECTION_NAME = "document_status"
SESSION_COLLECTION_NAME = "session_docs"


class AsyncCollection:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def insert_one(self, document: Dict[str, Any]) -> str:
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        result = await self.collection.insert_many(documents)
        return [str(_id) for _id in result.inserted_ids]

    # ---------- READ ----------

    async def find_one(
        self,
        filter: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None,
    ) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one(filter, projection)

    async def find_many(
        self,
        filter: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        cursor = self.collection.find(filter, projection).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.to_list(length=limit)

    async def exists(self, filter: Dict[str, Any]) -> bool:
        doc = await self.collection.find_one(filter, {"_id": 1})
        return doc is not None

    # ---------- UPDATE ----------

    async def update_one(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> int:
        result = await self.collection.update_one(filter, update, upsert=upsert)
        return result.modified_count

    async def update_many(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> int:
        result = await self.collection.update_many(filter, update)
        return result.modified_count

    async def find_one_and_update(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
        return_new: bool = True,
    ) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one_and_update(
            filter,
            update,
            upsert=upsert,
            return_document=ReturnDocument.AFTER if return_new else ReturnDocument.BEFORE,
        )

    # ---------- DELETE ----------

    async def delete_one(self, filter: Dict[str, Any]) -> int:
        result = await self.collection.delete_one(filter)
        return result.deleted_count

    async def delete_many(self, filter: Dict[str, Any]) -> int:
        result = await self.collection.delete_many(filter)
        return result.deleted_count

    # ---------- AGGREGATION ----------

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

class AsyncDBHost:
    _client: Optional[AsyncIOMotorClient] = None

    def __init__(self, db_name: str = "epocrates"):
        self.db_name = db_name
        if AsyncDBHost._client is None:
            AsyncDBHost._client = AsyncIOMotorClient(
                mongo_db_settings.DOCUMENT_DB_CONNECTION_STRING,
                maxPoolSize=20,
                minPoolSize=5,
                retryWrites=False,
            )
        self._db = AsyncDBHost._client[self.db_name]

    def __getitem__(self, collection_name: str) -> "AsyncCollection":
        return AsyncCollection(self._db[collection_name])

    async def close(self):
        if AsyncDBHost._client:
            AsyncDBHost._client.close()
            AsyncDBHost._client = None


doc_db = AsyncDBHost()
article_collection = doc_db[ARTICLE_COLLECTION_NAME]
status_collection = doc_db[STATUS_COLLECTION_NAME]
session_collection = doc_db[SESSION_COLLECTION_NAME]


@staticmethod
def update_document_status(
    pmc_id: str,
    filename: str,
    status: str,
    s3_key: str = None,
    s3_csv_key: str = None,
    
):
    client = get_async_database_connection()
    database = client["epocrates"]
    collection = database["document_status"]

    now = datetime.utcnow()

    collection.update_one(
        {"pmc_id": pmc_id, "filename": filename},
        {
            "$set": {
                "status": status,
                "updatedAt": now,
                "s3_key": s3_key,
                "s3_csv_key": s3_csv_key
            },
            "$setOnInsert": {
                "pmc_id": pmc_id,
                "filename": filename,
                "createdAt": now
            }
        },
        upsert=True
    )

@staticmethod
def upsert_session_documents(
    session_id: str,
    documents: List[str]
):
    client = get_async_database_connection()
    database = client["epocrates"]
    collection = database["session_docs"]

    collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "documents": documents
            },
            "$setOnInsert": {
                "session_id": session_id
            }
        },
        upsert=True
    )

def is_pmc_already_processed(pmc_id: str, user_upload: bool) -> bool:
    """
    Check if a PMC document has been successfully processed AND indexed in Qdrant.
    Returns True only if both MongoDB status is SUCCESS AND document exists in Qdrant.
    """
    from utils.document_handling import DOCUMENT_TEXT_COLLECTION_NAME
    from services.qdrant_host import current_qdrant_client
    from qdrant_client import models
    
    client = get_database_connection()
    collection = client["epocrates"]["document_status"]

    # First check MongoDB status
    doc = collection.find_one(
        {"pmc_id": pmc_id, "status": "SUCCESS"},
        {"_id": 1}
    )
    
    if doc is None:
        logging.debug(f"[PROCESS-CHECK] {pmc_id}: No SUCCESS status in MongoDB")
        return False
    
    # Also verify document is actually indexed in Qdrant
    try:
        result = current_qdrant_client.scroll(
            collection_name=DOCUMENT_TEXT_COLLECTION_NAME,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="pmc_id",
                        match=models.MatchValue(value=pmc_id)
                    )
                ]
            ),
            limit=1
        )
        
        if result[0]:  # If points exist in Qdrant
            logging.debug(f"[PROCESS-CHECK] {pmc_id}: Found in both MongoDB (SUCCESS) and Qdrant")
            return True
        else:
            # Document is marked SUCCESS but NOT in Qdrant - needs reprocessing
            logging.warning(f"[PROCESS-CHECK] {pmc_id}: MongoDB shows SUCCESS but NOT found in Qdrant - will reprocess")
            # Reset the status so it will be reprocessed
            collection.update_one(
                {"pmc_id": pmc_id},
                {"$set": {"status": "NEEDS_REINDEX", "updated_at": datetime.now().isoformat()}}
            )
            return False
    except Exception as e:
        logging.error(f"[PROCESS-CHECK] Error checking Qdrant for {pmc_id}: {e}")
        # If we can't verify Qdrant, assume it needs processing
        return False