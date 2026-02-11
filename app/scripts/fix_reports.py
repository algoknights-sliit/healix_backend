
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Ensure we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.supabase import supabase
from app.services.upload_service import get_normalized_json

def fix_reports():
    print("Fetching reports with 'Unknown' type...")
    
    # Get all reports
    # We filter in python to be safe, or we could filter in query
    response = supabase.table("reports").select("*").execute()
    
    if not response.data:
        print("No reports found.")
        return

    count = 0
    updated = 0
    
    for report in response.data:
        count += 1
        
        # Only process if type is Unknown or missing
        if report.get("report_type") not in ["Unknown", None, ""]:
            continue
            
        print(f"Processing Report {report['id']} (Current Type: {report.get('report_type')})")
        
        try:
            # Extract NIC from GCS path
            # Format: gs://bucket/users/{nic}/reports/{file_id}.pdf
            gcs_path = report.get("gcs_path", "")
            if not gcs_path:
                print("  Skipping: No GCS path")
                continue
                
            parts = gcs_path.split("/")
            if "users" not in parts:
                print(f"  Skipping: Invalid GCS path format ({gcs_path})")
                continue
                
            # Find 'users' index and get next part
            users_idx = parts.index("users")
            if len(parts) <= users_idx + 1:
                print("  Skipping: Cannot parse NIC from path")
                continue
                
            nic = parts[users_idx + 1]
            file_id = report.get("file_id")
            
            print(f"  Fetching JSON for NIC: {nic}, File: {file_id}")
            
            # Fetch normalized JSON
            try:
                data = get_normalized_json(nic, file_id)
            except Exception as e:
                print(f"  Error fetching JSON: {e}")
                continue
            
            # Extract correct type and date
            # Try nested first (correct) then root (legacy)
            report_data = data.get("report", {})
            
            new_type = report_data.get("type") or data.get("report_type") or "Medical Report"
            new_date = report_data.get("sample_collected_at") or data.get("sample_collection_date")
            
            # Update Supabase
            updates = {
                "report_type": new_type
            }
            if new_date:
                try:
                    # Parse to ensure valid format
                    dt = datetime.fromisoformat(new_date)
                    updates["sample_collected_at"] = dt.isoformat()
                except:
                    pass

            print(f"  Updating to Type: {new_type}")
            
            supabase.table("reports").update(updates).eq("id", report['id']).execute()
            updated += 1
            
        except Exception as e:
            print(f"  Error processing report: {e}")

    print(f"Done. Processed {count} reports. Updated {updated} reports.")

if __name__ == "__main__":
    fix_reports()
