# app/services/reportService.py
from app.db.supabase import supabase
from app.schemas.report import ReportCreate, ReportUpdate, BiomarkerCreate
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime

def create_report(report: ReportCreate) -> dict:
    """Create a new report record in Supabase"""
    try:
        # Prepare report data
        report_data = {
            "patient_id": str(report.patient_id),
            "file_id": report.file_id,
            "report_type": report.report_type,
            "gcs_path": report.gcs_path,
        }
        
        # Add sample_collected_at if provided
        if report.sample_collected_at:
            report_data["sample_collected_at"] = report.sample_collected_at.isoformat()
        
        # Insert into Supabase
        response = supabase.table("reports").insert(report_data).execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Failed to create report"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_report_by_id(report_id: str) -> dict:
    """Get a report by UUID"""
    try:
        response = supabase.table("reports").select("*").eq("id", report_id).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Report not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_report_by_file_id(file_id: str) -> dict:
    """Get a report by file_id"""
    try:
        response = supabase.table("reports").select("*").eq("file_id", file_id).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Report not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_reports_by_patient(patient_id: str, skip: int = 0, limit: int = 100) -> dict:
    """List all reports for a patient"""
    try:
        response = supabase.table("reports")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .order("created_at", desc=True)\
            .range(skip, skip + limit - 1)\
            .execute()
        
        return {"success": True, "data": response.data, "count": len(response.data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_report(report_id: str, updates: ReportUpdate) -> dict:
    """Update a report"""
    try:
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            return {"success": False, "error": "No fields to update"}
        
        # Convert datetime to ISO format if present
        if 'sample_collected_at' in update_data:
            update_data['sample_collected_at'] = update_data['sample_collected_at'].isoformat()
        
        response = supabase.table("reports").update(update_data).eq("id", report_id).execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Report not found or update failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_report(report_id: str) -> dict:
    """Delete a report (cascade deletes biomarkers)"""
    try:
        response = supabase.table("reports").delete().eq("id", report_id).execute()
        return {"success": True, "message": "Report deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Biomarker functions
def create_biomarker(biomarker: BiomarkerCreate) -> dict:
    """Create a biomarker record"""
    try:
        biomarker_data = {
            "report_id": str(biomarker.report_id),
            "name": biomarker.name,
            "value": float(biomarker.value),
            "unit": biomarker.unit,
            "ref_min": float(biomarker.ref_min) if biomarker.ref_min is not None else None,
            "ref_max": float(biomarker.ref_max) if biomarker.ref_max is not None else None,
            "flag": biomarker.flag
        }
        
        response = supabase.table("biomarkers").insert(biomarker_data).execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Failed to create biomarker"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_biomarkers_bulk(biomarkers: List[BiomarkerCreate]) -> dict:
    """Create multiple biomarkers at once (more efficient)"""
    try:
        biomarker_data = []
        for biomarker in biomarkers:
            biomarker_data.append({
                "report_id": str(biomarker.report_id),
                "name": biomarker.name,
                "value": float(biomarker.value),
                "unit": biomarker.unit,
                "ref_min": float(biomarker.ref_min) if biomarker.ref_min is not None else None,
                "ref_max": float(biomarker.ref_max) if biomarker.ref_max is not None else None,
                "flag": biomarker.flag
            })
        
        response = supabase.table("biomarkers").insert(biomarker_data).execute()
        
        if response.data:
            return {"success": True, "data": response.data, "count": len(response.data)}
        return {"success": False, "error": "Failed to create biomarkers"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_biomarkers_by_report(report_id: str) -> dict:
    """Get all biomarkers for a specific report"""
    try:
        response = supabase.table("biomarkers")\
            .select("*")\
            .eq("report_id", report_id)\
            .order("name")\
            .execute()
        
        return {"success": True, "data": response.data, "count": len(response.data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_report_with_biomarkers(report_id: str) -> dict:
    """Get a complete report with all its biomarkers"""
    try:
        # Get report
        report_result = get_report_by_id(report_id)
        if not report_result.get("success"):
            return report_result
        
        # Get biomarkers
        biomarkers_result = get_biomarkers_by_report(report_id)
        if not biomarkers_result.get("success"):
            return biomarkers_result
        
        return {
            "success": True,
            "data": {
                "report": report_result["data"],
                "biomarkers": biomarkers_result["data"]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def store_normalized_report_to_db(
    patient_id: UUID,
    file_id: str,
    gcs_path: str,
    normalized_json: dict
) -> dict:
    """
    Store normalized report and biomarkers to Supabase.
    This is called after OCR processing is complete.
    
    Args:
        patient_id: Patient's UUID
        file_id: Unique file identifier
        gcs_path: Path to PDF in GCS
        normalized_json: Normalized medical report JSON
        
    Returns:
        Dictionary with success status and created report/biomarkers
    """
    try:
        # Extract metadata from normalized JSON
        # Structure is { "patient":{...}, "report": { "type": "...", ... }, "biomarkers": [...] }
        report_data = normalized_json.get("report", {})
        report_type = report_data.get("type", "Unknown")
        sample_date_str = report_data.get("sample_collected_at")
        
        # Parse sample collection date if provided
        sample_date = None
        if sample_date_str:
            try:
                sample_date = datetime.fromisoformat(sample_date_str)
            except:
                pass  # If parsing fails, keep as None
        
        # Create report record
        report_data = ReportCreate(
            patient_id=patient_id,
            file_id=file_id,
            report_type=report_type,
            sample_collected_at=sample_date,
            gcs_path=gcs_path
        )
        
        report_result = create_report(report_data)
        if not report_result.get("success"):
            return {"success": False, "error": f"Failed to create report: {report_result.get('error')}"}
        
        report_id = report_result["data"]["id"]
        
        # Extract and create biomarkers
        biomarkers_data = normalized_json.get("biomarkers", [])
        if biomarkers_data:
            biomarkers = []
            for bm in biomarkers_data:
                # Safely parse ref_min and ref_max
                def safe_float(value):
                    """Safely convert value to float, return None if invalid"""
                    if value is None or value == "":
                        return None
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return None
                
                # Handle ref_range array format from normalization service
                # ref_range can be: [min, max] or separate ref_min/ref_max fields
                ref_min = None
                ref_max = None
                
                if "ref_range" in bm and bm["ref_range"] is not None:
                    # Normalization service returns [min, max]
                    ref_range = bm["ref_range"]
                    if isinstance(ref_range, list) and len(ref_range) >= 2:
                        ref_min = safe_float(ref_range[0])
                        ref_max = safe_float(ref_range[1])
                else:
                    # Handle separate ref_min/ref_max fields
                    ref_min = safe_float(bm.get("ref_min"))
                    ref_max = safe_float(bm.get("ref_max"))
                
                biomarker = BiomarkerCreate(
                    report_id=UUID(report_id),
                    name=bm.get("name", ""),
                    value=float(bm.get("value", 0)),
                    unit=bm.get("unit"),
                    ref_min=ref_min,
                    ref_max=ref_max,
                    flag=bm.get("flag")
                )
                biomarkers.append(biomarker)
            
            biomarkers_result = create_biomarkers_bulk(biomarkers)
            if not biomarkers_result.get("success"):
                # Report created but biomarkers failed - still return success with warning
                return {
                    "success": True,
                    "warning": f"Report created but biomarkers failed: {biomarkers_result.get('error')}",
                    "data": {
                        "report": report_result["data"],
                        "biomarkers": []
                    }
                }
            
            return {
                "success": True,
                "data": {
                    "report": report_result["data"],
                    "biomarkers": biomarkers_result["data"]
                }
            }
        
        # No biomarkers in normalized JSON
        return {
            "success": True,
            "data": {
                "report": report_result["data"],
                "biomarkers": []
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
