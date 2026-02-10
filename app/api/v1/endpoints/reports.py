from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Path, Query
from app.services.upload_service import upload_pdf_to_bucket, get_normalized_json, get_raw_json, list_user_reports
from app.services.reportService import (
    get_report_by_id,
    get_report_by_file_id,
    list_reports_by_patient,
    get_report_with_biomarkers,
    get_biomarkers_by_report
)

from app.services.patientService import get_patient_by_nic
import os
import tempfile
from app.workers.ocr_worker import process_document_worker

router = APIRouter()

@router.post("/upload")
async def upload_report(
    nic: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload a medical report PDF for OCR processing and normalization.
    Stores in Cloud Storage (organized by NIC) and Supabase database (by patient_id).
    
    Args:
        nic: Patient's National Identity Card number (used for GCS folder structure)
        file: PDF file of medical report
        
    Returns:
        Status and file_id for tracking
    """
    # Look up patient by NIC to get patient_id
    patient_result = get_patient_by_nic(nic)
    if not patient_result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=f"Patient not found with NIC: {nic}. Please register the patient first."
        )
    
    patient_data = patient_result.get("data")
    patient_id = patient_data.get("id")
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        # Upload to GCS using NIC for folder structure
        upload_info = upload_pdf_to_bucket(temp_path, nic)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Background task will process OCR and save to Supabase
    # Pass both NIC (for GCS paths) and patient_id (for database)
    background_tasks.add_task(
        process_document_worker,
        upload_info["gcs_uri"],
        nic,  # For GCS folder organization
        patient_id,  # For database storage
        upload_info["file_id"]
    )

    return {
        "status": "uploaded",
        "message": "Report uploaded and processing started. Data will be saved to database when complete.",
        "file_id": upload_info["file_id"],
        "patient_nic": nic,
        "patient_id": patient_id
    }


@router.get("/report/{nic}/{file_id}/normalized")
async def get_normalized_report(
    nic: str = Path(..., description="Patient's National Identity Card number"),
    file_id: str = Path(..., description="Unique file identifier")
):
    """
    Retrieve the normalized medical report JSON from Cloud Storage.
    
    Args:
        nic: Patient's NIC (used for GCS folder path)
        file_id: File identifier returned from upload
        
    Returns:
        Normalized medical report as JSON
        
    Raises:
        404: If report not found or not yet processed
    """
    try:
        normalized_data = get_normalized_json(nic, file_id)
        return {
            "status": "success",
            "data": normalized_data
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Normalized report not found. It may still be processing. {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report: {str(e)}"
        )


@router.get("/report/{nic}/{file_id}/raw")
async def get_raw_report(
    nic: str = Path(..., description="Patient's National Identity Card number"),
    file_id: str = Path(..., description="Unique file identifier")
):
    """
    Retrieve the raw OCR data from Cloud Storage (for debugging).
    
    Args:
        nic: Patient's NIC (used for GCS folder path)
        file_id: File identifier returned from upload
        
    Returns:
        Raw OCR data as JSON
        
    Raises:
        404: If report not found
    """
    try:
        raw_data = get_raw_json(nic, file_id)
        return {
            "status": "success",
            "data": raw_data
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Report not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report: {str(e)}"
        )


@router.get("/reports/nic/{nic}")
async def list_reports_by_nic(
    nic: str = Path(..., description="Patient's National Identity Card number"),
    source: str = Query("storage", regex="^(database|storage)$")
):
    """
    List all reports for a patient using their NIC.
    
    Args:
        nic: Patient's NIC
        source: 'database' (from Supabase) or 'storage' (from Cloud Storage)
        
    Returns:
        List of reports with metadata
    """
    try:
        if source == "database":
            # Look up patient by NIC first
            patient_result = get_patient_by_nic(nic)
            if not patient_result.get("success"):
                raise HTTPException(status_code=404, detail=f"Patient not found with NIC: {nic}")
            
            patient_id = patient_result.get("data").get("id")
            
            # Get from Supabase database
            result = list_reports_by_patient(patient_id, skip=0, limit=100)
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return {
                "status": "success",
                "source": "database",
                "patient_nic": nic,
                "count": result.get("count"),
                "reports": result.get("data")
            }
        else:
            # Get from Cloud Storage (uses NIC directly)
            reports = list_user_reports(nic)
            return {
                "status": "success",
                "source": "storage",
                "patient_nic": nic,
                "count": len(reports),
                "reports": reports
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing reports: {str(e)}"
        )


@router.get("/reports/{patient_id}")
async def list_reports(
    patient_id: str = Path(..., description="Patient's UUID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source: str = Query("database", regex="^(database|storage)$")
):
    """
    List all reports for a patient by patient_id (database only).
    
    Args:
        patient_id: Patient's UUID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        source: 'database' only (use /reports/nic/{nic} for storage)
        
    Returns:
        List of reports with metadata
    """
    try:
        # Get from Supabase database
        result = list_reports_by_patient(patient_id, skip, limit)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "status": "success",
            "source": "database",
            "count": result.get("count"),
            "reports": result.get("data")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing reports: {str(e)}"
        )


@router.get("/report/id/{report_id}")
async def get_report_by_uuid(
    report_id: str = Path(..., description="Report UUID from database")
):
    """
    Get a report by its database UUID.
    
    Args:
        report_id: Report's UUID in Supabase
        
    Returns:
        Report details
    """
    try:
        result = get_report_by_id(report_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return {
            "status": "success",
            "data": result.get("data")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report: {str(e)}"
        )


@router.get("/report/file/{file_id}")
async def get_report_by_file(
    file_id: str = Path(..., description="File ID from upload")
):
    """
    Get a report by its file_id (from upload).
    
    Args:
        file_id: File identifier from upload response
        
    Returns:
        Report details
    """
    try:
        result = get_report_by_file_id(file_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return {
            "status": "success",
            "data": result.get("data")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report: {str(e)}"
        )


@router.get("/report/id/{report_id}/biomarkers")
async def get_report_biomarkers(
    report_id: str = Path(..., description="Report UUID")
):
    """
    Get all biomarkers for a specific report.
    
    Args:
        report_id: Report's UUID
        
    Returns:
        List of biomarkers
    """
    try:
        result = get_biomarkers_by_report(report_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return {
            "status": "success",
            "count": result.get("count"),
            "biomarkers": result.get("data")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving biomarkers: {str(e)}"
        )


@router.get("/report/id/{report_id}/complete")
async def get_complete_report(
    report_id: str = Path(..., description="Report UUID")
):
    """
    Get a complete report with all biomarkers.
    
    Args:
        report_id: Report's UUID
        
    Returns:
        Complete report with biomarkers
    """
    try:
        result = get_report_with_biomarkers(report_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return {
            "status": "success",
            "data": result.get("data")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving complete report: {str(e)}"
        )

