import json
import mimetypes
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from utils.database import get_database_connection
from configs.config import credentials
from azure.storage.blob import generate_blob_sas, BlobSasPermissions


class ImageService:

    def __init__(self, base_url: str = "http://localhost:8000", db_name: str = "epocrates", collection_name: str = "images"):
        self.images: List[dict] = []
        self.base_url = base_url.rstrip("/")
        client = get_database_connection()
        self.collection = client[db_name][collection_name]
        self._ensure_seed_data()
        self._load_images()

    def _ensure_seed_data(self):
        """Check if images are seeded, if not seed from upload results"""
        if self.collection.count_documents({}) > 0:
            return
        self._seed_from_upload_results()

    def _seed_from_upload_results(self):
        """Seed database from image_upload_results.json after Azure upload"""
        results_path = Path(__file__).parent.parent.parent / "image_upload_results.json"

        if not results_path.exists():
            # Fallback to local seeding with Azure upload
            self._seed_from_local_with_azure()
            return

        with open(results_path, "r", encoding="utf-8") as f:
            upload_results = json.load(f)

        uploaded_images = upload_results.get("uploaded", [])

        for img in uploaded_images:
            content_type = mimetypes.guess_type(img["filename"])[0] or "application/octet-stream"

            doc = {
                "id": img.get("id"),
                "filename": img.get("filename"),
                "speciality": img.get("speciality"),
                "disease_area": img.get("disease_area", []),
                "azure_url": img.get("azure_url"),
                "blob_key": img.get("blob_key"),
                "content_type": content_type,
                "created_at": datetime.utcnow(),
            }

            self.collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)

    def _seed_from_local_with_azure(self):
        """Fallback: seed from local files and generate Azure URLs"""
        json_path = Path(__file__).parent.parent.parent / "imglibrary.json"

        if not json_path.exists():
            return

        with open(json_path, "r", encoding="utf-8") as f:
            raw_images = json.load(f)

        for img in raw_images:
            filename = img["filename"]
            blob_key = f"Epocrates/images/{filename}"
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

            # Generate long-lived SAS URL (10 years)
            try:
                sas_token = generate_blob_sas(
                    account_name=credentials.AZURE_STORAGE_ACCOUNT_NAME,
                    container_name=credentials.AZURE_CONTAINER_NAME,
                    blob_name=blob_key,
                    account_key=credentials.AZURE_STORAGE_ACCOUNT_KEY,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(days=3650)
                )

                azure_url = f"https://{credentials.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{credentials.AZURE_CONTAINER_NAME}/{blob_key}?{sas_token}"
            except:
                azure_url = None

            doc = {
                "id": img.get("id"),
                "filename": img.get("filename"),
                "speciality": img.get("speciality"),
                "disease_area": img.get("disease_area", []),
                "azure_url": azure_url,
                "blob_key": blob_key,
                "content_type": content_type,
                "created_at": datetime.utcnow(),
            }

            self.collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)

    def _load_images(self):
        docs = list(self.collection.find({}))
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        self.images = docs
    
    def search_images(self, speciality: Optional[str] = "all", disease_area: Optional[str] = "all") -> dict:
        spec = (speciality or "all").strip().lower()
        disease = (disease_area or "all").strip().lower()

        self._load_images()

        def matches(image: dict) -> bool:
            spec_ok = spec == "all" or image.get("speciality", "").lower() == spec
            if not spec_ok:
                return False

            if disease == "all":
                return True

            diseases = [d.lower() for d in image.get("disease_area", [])]
            return disease in diseases

        filtered = [img for img in self.images if matches(img)]

        return {
            "total": len(filtered),
            "results": filtered
        }


image_service = ImageService()

