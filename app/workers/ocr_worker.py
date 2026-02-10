from app.services.ocr_service import process_with_document_ai
from app.services.upload_service import store_json
from app.services.nlp_service import build_report_json
from app.services.normalization_service import normalize_fbc_report
from app.services.reportService import store_normalized_report_to_db
from app.utils.text_utils import extract_tables, extract_entities
from uuid import UUID

def process_document_worker(gcs_uri: str, nic: str, patient_id: str, file_id: str):
    """
    Process medical document: extract OCR data, normalize to structured JSON,
    and save to both cloud storage (organized by NIC) and Supabase database (by patient_id).
    
    Args:
        gcs_uri: Google Cloud Storage URI of the document
        nic: Patient's NIC (for organizing GCS folders)
        patient_id: Patient's UUID (for database foreign key)
        file_id: Unique file identifier
    """
    try:
        # Extract raw OCR data using Document AI
        document = process_with_document_ai(gcs_uri)

        # Extract tables and entities from OCR
        tables = extract_tables(document)
        entities = extract_entities(document)

        # Build raw JSON (for debugging/archival)
        raw_json = build_report_json(document, tables, entities)
        
        # Normalize to clean, structured medical JSON
        normalized_json = normalize_fbc_report(raw_json)

        # Store both raw and normalized versions in Cloud Storage (organized by NIC)
        store_json(nic, file_id, raw_json)  # users/{nic}/processed/{file_id}.json
        store_json(nic, f"{file_id}_normalized", normalized_json)  # users/{nic}/processed/{file_id}_normalized.json
        
        # Store report and biomarkers in Supabase database (using patient_id)
        db_result = store_normalized_report_to_db(
            patient_id=UUID(patient_id),
            file_id=file_id,
            gcs_path=gcs_uri,
            normalized_json=normalized_json
        )
        
        if not db_result.get("success"):
            print(f"Warning: Failed to store to Supabase: {db_result.get('error')}")
            # Continue anyway - data is still in cloud storage
        else:
            print(f"Successfully stored report {file_id} to Supabase for patient {patient_id}")
            print(f"GCS folder: users/{nic}/")
            if db_result.get("warning"):
                print(f"Warning: {db_result.get('warning')}")
        
    except Exception as e:
        print(f"Error processing document {file_id}: {str(e)}")
        raise  # Re-raise so the error is logged properly
    
