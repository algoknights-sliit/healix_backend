import requests
import uuid
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"
UHID = str(uuid.uuid4())

def test_report_crud():
    print("--- Testing Report Extracted Data CRUD ---")
    
    # 1. Create
    payload = {
        "uhid": UHID,
        "report_type": "Blood Test",
        "extracted_json": {
            "glucose": 95,
            "cholesterol": 180,
            "hemoglobin": 14.5
        },
        "raw_text": "Patient blood work shows normal levels..."
    }
    
    print(f"[1] Creating report data for UHID {UHID}...")
    response = requests.post(f"{BASE_URL}/report-extracted-data/", json=payload)
    if response.status_code != 201:
        print(f"FAILED to create report data: {response.text}")
        return
    
    report = response.json()
    report_id = report['id']
    ts_str = report['created_at']
    uhid_returned = report['uhid']
    print(f"    SUCCESS: Created ID {report_id}")
    print(f"    Timestamp: {ts_str}")
    print(f"    UHID: {uhid_returned}")
    
    # Verify the hour matches IST (approximate check)
    from datetime import datetime, timedelta, timezone
    ist_now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    try:
        # FastAPI might return it with or without 'Z' or offset
        ts_obj = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        if ts_obj.hour == ist_now.hour:
            print(f"    PASS: Timestamp hour ({ts_obj.hour}) matches IST hour")
        else:
            print(f"    FAIL: Timestamp hour ({ts_obj.hour}) does not match IST hour ({ist_now.hour})")
    except Exception as e:
        print(f"    ERROR parsing timestamp: {e}")
    
    # 2. Get by ID
    print(f"\n[2] Fetching report {report_id}...")
    response = requests.get(f"{BASE_URL}/report-extracted-data/{report_id}")
    if response.status_code != 200:
        print(f"FAILED to fetch report: {response.text}")
    else:
        print(f"    SUCCESS: Fetched report type: {response.json()['report_type']}")
    
    # 3. Get User Reports
    print(f"\n[3] Fetching all reports for UHID {UHID}...")
    response = requests.get(f"{BASE_URL}/report-extracted-data/", params={"uhid": UHID})
    if response.status_code != 200:
        print(f"FAILED to fetch user reports: {response.text}")
    else:
        count = len(response.json())
        print(f"    SUCCESS: Found {count} report(s)")
    
    # 4. Update
    update_payload = {
        "report_type": "Detailed Blood Analysis",
        "extracted_json": {
            "glucose": 96,
            "cholesterol": 175,
            "hemoglobin": 14.6,
            "notes": "Updated after review"
        }
    }
    print(f"\n[4] Updating report {report_id}...")
    response = requests.put(f"{BASE_URL}/report-extracted-data/{report_id}", json=update_payload)
    if response.status_code != 200:
        print(f"FAILED to update report: {response.text}")
    else:
        updated = response.json()
        print(f"    SUCCESS: New report type: {updated['report_type']}")
        print(f"    SUCCESS: Updated JSON: {json.dumps(updated['extracted_json'], indent=2)}")
    
    # 5. Delete
    print(f"\n[5] Deleting report {report_id}...")
    response = requests.delete(f"{BASE_URL}/report-extracted-data/{report_id}")
    if response.status_code != 204:
        print(f"FAILED to delete report: {response.text}")
    else:
        print("    SUCCESS: Report deleted")
    
    # 6. Verify Deletion
    print(f"\n[6] Verifying deletion of {report_id}...")
    response = requests.get(f"{BASE_URL}/report-extracted-data/{report_id}")
    if response.status_code == 404:
        print("    SUCCESS: Confirmed 404 Not Found")
    else:
        print(f"    FAILED: Report still exists or returned {response.status_code}")

if __name__ == "__main__":
    try:
        test_report_crud()
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Make sure the FastAPI server is running on port 8000.")
