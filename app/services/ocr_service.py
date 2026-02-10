from google.cloud import documentai
from app.core.cloud import docai_client
from app.core.config import PROJECT_ID, DOC_AI_LOCATION, DOC_AI_PROCESSOR_ID

def process_with_document_ai(gcs_uri: str):
    name = docai_client.processor_path(
        PROJECT_ID, DOC_AI_LOCATION, DOC_AI_PROCESSOR_ID
    )

    request = documentai.ProcessRequest(
        name=name,
        gcs_document=documentai.GcsDocument(
            gcs_uri=gcs_uri,
            mime_type="application/pdf"
        )
    )

    result = docai_client.process_document(request=request)
    return result.document
