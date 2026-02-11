import uuid
import json
from app.core.cloud import get_bucket
from app.core.config import BUCKET_NAME


def upload_pdf_to_bucket(local_pdf_path: str, user_nic: str):
    if not BUCKET_NAME:
        raise ValueError("GCS_BUCKET environment variable is not set")

    try:
        bucket = get_bucket(BUCKET_NAME)

        file_id = str(uuid.uuid4())
        gcs_path = f"users/{user_nic}/reports/{file_id}.pdf"

        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(
            local_pdf_path,
            content_type="application/pdf"
        )

        return {
            "file_id": file_id,
            "gcs_uri": f"gs://{BUCKET_NAME}/{gcs_path}"
        }
    except Exception as e:
        raise RuntimeError(f"GCS Upload Failed: {str(e)}")


def store_json(user_nic: str, file_id: str, data: dict):
    bucket = get_bucket(BUCKET_NAME)
    path = f"users/{user_nic}/processed/{file_id}.json"

    blob = bucket.blob(path)
    blob.upload_from_string(
        json.dumps(data, indent=2),
        content_type="application/json"
    )

    return f"gs://{BUCKET_NAME}/{path}"


def get_normalized_json(user_nic: str, file_id: str) -> dict:
    """
    Retrieve normalized JSON report from cloud storage.
    
    Args:
        user_nic: Patient's National Identity Card number
        file_id: Unique file identifier
        
    Returns:
        Dictionary containing normalized medical report data
        
    Raises:
        FileNotFoundError: If the normalized JSON doesn't exist
    """
    bucket = get_bucket(BUCKET_NAME)
    path = f"users/{user_nic}/processed/{file_id}_normalized.json"
    
    blob = bucket.blob(path)
    
    if not blob.exists():
        raise FileNotFoundError(f"Normalized report not found: {file_id}")
    
    # Download and parse JSON
    json_string = blob.download_as_string()
    return json.loads(json_string)


def get_raw_json(user_nic: str, file_id: str) -> dict:
    """
    Retrieve raw OCR JSON from cloud storage.
    
    Args:
        user_nic: Patient's National Identity Card number
        file_id: Unique file identifier
        
    Returns:
        Dictionary containing raw OCR data
        
    Raises:
        FileNotFoundError: If the JSON doesn't exist
    """
    bucket = get_bucket(BUCKET_NAME)
    path = f"users/{user_nic}/processed/{file_id}.json"
    
    blob = bucket.blob(path)
    
    if not blob.exists():
        raise FileNotFoundError(f"Report not found: {file_id}")
    
    json_string = blob.download_as_string()
    return json.loads(json_string)


def list_user_reports(user_nic: str) -> list:
    """
    List all reports for a given user.
    
    Args:
        user_nic: Patient's National Identity Card number
        
    Returns:
        List of dictionaries containing file_id and report type info
    """
    bucket = get_bucket(BUCKET_NAME)
    prefix = f"users/{user_nic}/processed/"
    
    blobs = bucket.list_blobs(prefix=prefix)
    
    reports = []
    seen_file_ids = set()
    
    for blob in blobs:
        # Extract file_id from path
        filename = blob.name.split("/")[-1]
        
        if filename.endswith("_normalized.json"):
            file_id = filename.replace("_normalized.json", "")
            if file_id not in seen_file_ids:
                reports.append({
                    "file_id": file_id,
                    "type": "normalized",
                    "created": blob.time_created.isoformat() if blob.time_created else None,
                    "size_bytes": blob.size
                })
                seen_file_ids.add(file_id)
    
    return reports
