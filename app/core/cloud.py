from google.cloud import storage, documentai
from app.core.config import PROJECT_ID, DOC_AI_LOCATION
import os

_storage_client = None
_docai_client = None


def get_storage_client():
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


def get_docai_client():
    global _docai_client
    if _docai_client is None:
        _docai_client = documentai.DocumentProcessorServiceClient(
            client_options={
                "api_endpoint": f"{DOC_AI_LOCATION}-documentai.googleapis.com"
            }
        )
    return _docai_client


def get_bucket(bucket_name: str):
    return get_storage_client().bucket(bucket_name)
