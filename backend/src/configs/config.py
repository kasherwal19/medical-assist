import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend folder
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class AppInfo(BaseSettings):
    PROJECT_NAME: str = "Document Handling API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for vectorisation of given documents and chatting with them"
    API_STR: str = "/api"
    ALLOWED_ORIGINS: List[str] = ["*", "http://localhost:3000"]

class QdrantSettings(BaseSettings):
    QDRANT_HOST_URL:  str = os.getenv("QDRANT_HOST_URL")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME:  str = os.getenv("QDRANT_COLLECTION_NAME")

class OllamaSettings(BaseSettings):
    OLLAMA_ENDPOINT_URL: str = os.getenv("OLLAMA_ENDPOINT_URL")

class DocumentDB(BaseSettings):
    DOCUMENT_DB_CONNECTION_STRING: str = os.getenv("DOCUMENT_DB_CONNECTION_STRING")

class AzureOpenAISettings(BaseSettings):
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

class AzureOpenAIGPTSettings(BaseSettings):
    """Credentials for Azure OpenAI GPT-5.2 Model"""
    AZURE_OPENAI_GPT_ENDPOINT: str = os.getenv("AZURE_OPENAI_GPT_ENDPOINT")
    AZURE_OPENAI_GPT_API_VERSION: str = os.getenv("AZURE_OPENAI_GPT_API_VERSION")
    AZURE_OPENAI_GPT_API_KEY: str = os.getenv("AZURE_OPENAI_GPT_API_KEY")
    AZURE_OPENAI_GPT_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT")

class AzureOpenAIGPT4oSettings(BaseSettings):
    """Credentials for Azure OpenAI GPT-4o Model for highlighting"""
    AZURE_OPENAI_GPT4O_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT")

class AWSCredSettings_OLD(BaseSettings):
    """Old AWS S3 credentials - kept for reference during migration."""
    AWS_ACCESS_KEY_ID: str = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: str = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION: str = os.getenv('AWS_REGION')
    S3_BUCKET_NAME: str = os.getenv('S3_BUCKET_NAME')
    S3_DATA_STORAGE: str = os.getenv('S3_DATA_STORAGE')
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

class AzureCredSettings(BaseSettings):
    """Azure Blob Storage credentials."""
    AZURE_STORAGE_ACCOUNT_NAME: str = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
    AZURE_STORAGE_ACCOUNT_KEY: str = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
    AZURE_CONTAINER_NAME: str = os.getenv('AZURE_CONTAINER_NAME')
    AZURE_DATA_STORAGE: str = os.getenv('AZURE_DATA_STORAGE', 'Epocrates')

    # Backward compatibility alias for existing code
    S3_DATA_STORAGE: str = os.getenv('AZURE_DATA_STORAGE', 'Epocrates')

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

class NewsConfigSettings(BaseSettings):
    """
    Configuration for NewsData.io integration.
    """
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")
    NEWS_BASE_URL: str = "https://newsdata.io/api/1/latest"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

mongo_db_settings = DocumentDB()

credentials = AzureCredSettings()

azure_openai_settings = AzureOpenAISettings()

azure_gpt_settings = AzureOpenAIGPTSettings()

azure_gpt4o_settings = AzureOpenAIGPT4oSettings()

qdrant_creds = QdrantSettings()

news_config = NewsConfigSettings()