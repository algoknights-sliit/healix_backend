from google.cloud import storage
from google.cloud import documentai
from app.core.config import PROJECT_ID, DOC_AI_LOCATION

storage_client = storage.Client(project=PROJECT_ID)

docai_client = documentai.DocumentProcessorServiceClient(
    client_options={"api_endpoint": f"{DOC_AI_LOCATION}-documentai.googleapis.com"}
)

def get_bucket(bucket_name: str):
    return storage_client.bucket(bucket_name)
