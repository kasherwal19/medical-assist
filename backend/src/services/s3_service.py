import os
import json
import logging
import pandas as pd
import io
from mimetypes import guess_type
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from lib.logger import logging
from configs.config import credentials


def get_blob_service_client():
    """
    Create Azure Blob Service client using environment variables.
    Never hard-code Azure credentials.
    """
    try:
        if credentials.AZURE_STORAGE_CONNECTION_STRING:
            return BlobServiceClient.from_connection_string(
                credentials.AZURE_STORAGE_CONNECTION_STRING
            )

        account_url = f"https://{credentials.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        return BlobServiceClient(
            account_url=account_url,
            credential=credentials.AZURE_STORAGE_ACCOUNT_KEY
        )
    except Exception as e:
        logging.error(f"Failed to create Azure Blob Service client: {e}")
        raise


def S3PutObject(bucket_name, obj_key, data, type_of_data='other'):
    """
    Upload JSON, text, PDF, DOCX, PPTX, or raw bytes to Azure Blob Storage.

    Note: Function name kept as S3PutObject for backward compatibility,
    but now uses Azure Blob Storage. bucket_name is treated as container_name.
    """
    blob_service_client = get_blob_service_client()

    # MIME types
    content_types = {
        "json": "application/json",
        "text": "text/plain",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "other": "application/octet-stream",
    }

    if type_of_data not in content_types:
        raise ValueError(f"Unsupported type_of_data: {type_of_data}")

    try:
        if type_of_data == 'json':
            body = json.dumps(data).encode("utf-8")
        elif type_of_data == 'text':
            body = data.encode("utf-8")
        else:
            body = data

        # Upload to Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(
            container=bucket_name,
            blob=obj_key
        )

        blob_client.upload_blob(
            body,
            overwrite=True,  # S3 put_object overwrites by default
            content_settings=ContentSettings(content_type=content_types[type_of_data])
        )

        logging.info(f"Uploaded {obj_key} to Azure container {bucket_name}")
        return {
            "status": "success",
            "bucket": bucket_name,  # Keep "bucket" key for compatibility
            "key": obj_key,
            "content_type": content_types[type_of_data]
        }

    except Exception as e:
        logging.error(f"Azure Blob upload failed: {e}")
        raise RuntimeError(f"Azure Blob upload failed: {str(e)}")


def S3GetObject(bucket_name, obj_key, type_of_data='other'):
    """
    Download JSON, text, PDF, DOCX, PPTX, or raw bytes from Azure Blob Storage.

    Note: Function name kept as S3GetObject for backward compatibility,
    but now uses Azure Blob Storage. bucket_name is treated as container_name.

    Returns: data_bytes or parsed data
    """
    blob_service_client = get_blob_service_client()

    supported_types = {"json", "text", "pdf", "docx", "pptx", "other"}
    if type_of_data not in supported_types:
        raise ValueError(f"Unsupported type_of_data: {type_of_data}")

    try:
        blob_client = blob_service_client.get_blob_client(
            container=bucket_name,
            blob=obj_key
        )

        download_stream = blob_client.download_blob()
        body_bytes = download_stream.readall()

        if type_of_data == "json":
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception as e:
                raise RuntimeError(f"Failed to decode JSON: {str(e)}")

        elif type_of_data == "text":
            try:
                data = body_bytes.decode("utf-8")
            except UnicodeDecodeError:
                data = body_bytes.decode("latin-1", errors="ignore")

        else:
            data = body_bytes

        logging.info(f"Downloaded {obj_key} from Azure container {bucket_name}")
        return data

    except ResourceNotFoundError:
        logging.error(f"Blob not found: {obj_key}")
        raise RuntimeError(f"Blob not found: {obj_key}")
    except Exception as e:
        logging.error(f"Azure Blob download failed: {e}")
        raise RuntimeError(f"Azure Blob download failed: {str(e)}")


# Placeholder for DocumentEncoder - will be replaced with actual implementation
DocumentEncoder = ""


class AsyncS3Host:
    """
    Azure Blob Storage async client.

    Note: Class name kept as AsyncS3Host for backward compatibility,
    but now uses Azure Blob Storage instead of AWS S3.
    """

    def __init__(self):
        """Initialize async Azure Blob Storage client."""
        self.account_name = credentials.AZURE_STORAGE_ACCOUNT_NAME or os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = credentials.AZURE_STORAGE_ACCOUNT_KEY or os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        self.connection_string = credentials.AZURE_STORAGE_CONNECTION_STRING or os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        self.bucket_name = credentials.AZURE_CONTAINER_NAME or os.getenv("AZURE_CONTAINER_NAME", "pharma-ai-suite")
        # Note: self.bucket_name kept for compatibility (it's actually container_name in Azure)

    def _get_async_client(self):
        """Get or create async blob service client."""
        if self.connection_string:
            return AsyncBlobServiceClient.from_connection_string(self.connection_string)
        else:
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            return AsyncBlobServiceClient(account_url=account_url, credential=self.account_key)

    async def _upload_to_s3(self, key, data, content_type=None):
        """
        Upload data to Azure Blob Storage.

        Note: Method name kept as _upload_to_s3 for backward compatibility.
        """
        try:
            async with self._get_async_client() as blob_service_client:
                blob_client = blob_service_client.get_blob_client(
                    container=self.bucket_name,
                    blob=key
                )

                content_settings = ContentSettings(content_type=content_type) if content_type else None

                await blob_client.upload_blob(
                    data,
                    overwrite=True,
                    content_settings=content_settings
                )

            logging.info(f"Data uploaded to Azure Blob with name: {key}")
        except Exception as e:
            logging.error(f"Error uploading to Azure Blob: {e}")
            raise e

    async def check_file_exists(self, key: str) -> bool:
        """Check if a blob exists in Azure storage."""
        try:
            async with self._get_async_client() as blob_service_client:
                blob_client = blob_service_client.get_blob_client(
                    container=self.bucket_name,
                    blob=key
                )
                return await blob_client.exists()
        except Exception as e:
            logging.error(f"Error checking blob existence: {e}")
            raise e

    async def get_presigned_upload_url(self, complete_pdf_name: str, userId: str, expire_in_n_seconds: int = 18000):
        """
        Generate SAS URL for uploading a blob.

        Note: Method name kept as get_presigned_upload_url for backward compatibility,
        but returns Azure SAS URL instead of S3 presigned URL.

        Returns: (sas_url, document_id)
        """
        try:
            key = f"DB/USERS/{userId}/docs/{complete_pdf_name}"
            key = await self.get_available_file_key(key)

            final_file_name = key.rsplit("/", 1)[-1]
            document_id = DocumentEncoder.encode_document_id(userId=userId, document_name=final_file_name)

            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.bucket_name,
                blob_name=key,
                account_key=self.account_key,
                permission=BlobSasPermissions(write=True, create=True),  # Upload permissions
                expiry=datetime.utcnow() + timedelta(seconds=expire_in_n_seconds)
            )

            # Construct full URL
            sas_url = f"https://{self.account_name}.blob.core.windows.net/{self.bucket_name}/{key}?{sas_token}"

            return sas_url, document_id

        except Exception as e:
            logging.error(f"Error generating SAS upload URL: {e}")
            raise e

    async def get_presigned_view_url(self, key: str, expire_in_n_seconds: int = 18000):
        """
        Generate SAS URL for viewing/downloading a blob.

        Note: Method name kept as get_presigned_view_url for backward compatibility,
        but returns Azure SAS URL instead of S3 presigned URL.

        Returns: sas_url
        """
        try:
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.bucket_name,
                blob_name=key,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),  # Read-only
                expiry=datetime.utcnow() + timedelta(seconds=expire_in_n_seconds)
            )

            sas_url = f"https://{self.account_name}.blob.core.windows.net/{self.bucket_name}/{key}?{sas_token}"

            logging.info(f"blob_name obtained: {key}")
            return sas_url

        except Exception as e:
            logging.error(f"Error generating SAS view URL: {e}")
            raise e

    async def check_document_exists(self, document_id: str) -> bool:
        """
        Check if a document exists in Azure Blob Storage
        """
        try:
            # Extract complete_pdf_name from document_id (remove userId prefix)
            key = DocumentEncoder.get_original_document_file_key(document_id)
            logging.info(f"Looking for key {key} in the container to process the document with document_id {document_id}")

            try:
                # Check if blob exists
                async with self._get_async_client() as blob_service_client:
                    blob_client = blob_service_client.get_blob_client(
                        container=self.bucket_name,
                        blob=key
                    )
                    return await blob_client.exists()
            except Exception as e:
                logging.error(f"Error checking document existence: {e}")
                return False

        except Exception as e:
            logging.error(f"Error checking document existence: {e}")
            raise e


    async def get_available_file_key(self, key: str) -> str:
        """
        Get an available blob name by appending counter (_1, _2, ...)
        if the original key already exists. Does NOT strip existing suffixes.
        """
        try:
            base_path, file_name = key.rsplit("/", 1)
            name, extension = os.path.splitext(file_name)

            counter = 0
            new_key = key

            async with self._get_async_client() as blob_service_client:
                while True:
                    blob_client = blob_service_client.get_blob_client(
                        container=self.bucket_name,
                        blob=new_key
                    )

                    exists = await blob_client.exists()
                    if not exists:
                        return new_key

                    # Increment and try again
                    counter += 1
                    new_file_name = f"{name}_{counter}{extension}"
                    new_key = f"{base_path}/{new_file_name}"

        except Exception as e:
            logging.error(f"Error getting available file name: {e}")
            raise e

    async def get_from_s3(self, key: str) -> bytes:
        """
        Download blob content as bytes.

        Note: Method name kept as get_from_s3 for backward compatibility.
        """
        try:
            async with self._get_async_client() as blob_service_client:
                blob_client = blob_service_client.get_blob_client(
                    container=self.bucket_name,
                    blob=key
                )

                download_stream = await blob_client.download_blob()
                file_content = await download_stream.readall()

            logging.info(f"Successfully retrieved blob from Azure: {key}")
            return file_content

        except ResourceNotFoundError:
            logging.error(f"Blob not found in Azure: {key}")
            raise RuntimeError(f"Blob not found in Azure: {key}")
        except Exception as e:
            logging.error(f"Unexpected error retrieving blob {key}: {e}")
            raise RuntimeError(f"Failed to retrieve blob from Azure: {e}")


    async def save_to_s3(self, file_data, key):
        """
        Saves a file to Azure Blob Storage.

        Note: Method name kept as save_to_s3 for backward compatibility.

        Args:
            file_data: The data to be uploaded.
            key: The blob name where the file will be stored.

        Returns:
            None
        """
        file_type, _ = guess_type(key)
        await self._upload_to_s3(key, file_data, content_type=file_type)

    async def delete_from_s3(self, key: str):
        """
        Deletes a blob or all blobs within a folder (including subfolders) from Azure Blob Storage.

        Note: Method name kept as delete_from_s3 for backward compatibility.

        Args:
            key (str): The blob name of the file or folder to delete.
        """
        try:
            async with self._get_async_client() as blob_service_client:
                container_client = blob_service_client.get_container_client(self.bucket_name)

                if key.endswith("/"):  # If it's a folder
                    blobs_to_delete = []

                    # List all blobs with prefix
                    async for blob in container_client.list_blobs(name_starts_with=key):
                        blobs_to_delete.append(blob.name)

                    if blobs_to_delete:
                        # Delete each blob individually (Azure SDK doesn't support batch delete)
                        for blob_name in blobs_to_delete:
                            blob_client = container_client.get_blob_client(blob_name)
                            await blob_client.delete_blob()
                        logging.info(f"Deleted {len(blobs_to_delete)} blobs with prefix: {key}")
                    else:
                        logging.info(f"No blobs found with prefix: {key}")

                else:  # If it's a single file
                    blob_client = container_client.get_blob_client(key)
                    await blob_client.delete_blob()
                    logging.info(f"Deleted blob: {key}")

        except Exception as e:
            logging.error(f"Error deleting from Azure Blob: {e}")
            raise e

    async def load_csv_as_dataframe(self, key: str) -> pd.DataFrame:
        """
        Downloads a CSV file from Azure Blob Storage and loads it into a pandas DataFrame.

        Args:
            key (str): The blob name of the CSV file.

        Returns:
            pd.DataFrame: DataFrame loaded from the CSV file.
        """
        try:
            async with self._get_async_client() as blob_service_client:
                blob_client = blob_service_client.get_blob_client(
                    container=self.bucket_name,
                    blob=key
                )

                download_stream = await blob_client.download_blob()
                csv_bytes = await download_stream.readall()
                csv_str = csv_bytes.decode("utf-8")
                df = pd.read_csv(io.StringIO(csv_str))
                return df
        except Exception as e:
            logging.error(f"Error loading CSV from Azure Blob: {e}")
            raise e



# Create an instance of the async client
current_s3_client = AsyncS3Host()
