"""
Test Biomarker Storage - Debug Reference Ranges
This script helps diagnose issues with biomarker storage
"""

from app.services.reportService import store_normalized_report_to_db
from uuid import UUID
import json

# Example normalized JSON with different ref_min/ref_max formats
test_cases = [
    {
        "name": "Valid Numbers",
        "data": {
            "report_type": "FBC",
            "sample_collection_date": "2026-02-07T10:30:00",
            "biomarkers": [
                {
                    "name": "Hemoglobin",
                    "value": 14.5,
                    "unit": "g/dL",
                    "ref_min": 12.0,
                    "ref_max": 16.0,
                    "flag": "NORMAL"
                }
            ]
        }
    },
    {
        "name": "String Numbers",
        "data": {
            "report_type": "FBC",
            "biomarkers": [
                {
                    "name": "WBC",
                    "value": "11.2",
                    "unit": "×10³/μL",
                    "ref_min": "4.0",
                    "ref_max": "11.0",
                    "flag": "HIGH"
                }
            ]
        }
    },
    {
        "name": "Missing ref_max",
        "data": {
            "report_type": "FBC",
            "biomarkers": [
                {
                    "name": "Platelets",
                    "value": 250,
                    "unit": "×10³/μL",
                    "ref_min": 150,
                    "ref_max": None,
                    "flag": "NORMAL"
                }
            ]
        }
    },
    {
        "name": "Empty String refs",
        "data": {
            "report_type": "FBC",
            "biomarkers": [
                {
                    "name": "Test",
                    "value": 100,
                    "unit": "mg/dL",
                    "ref_min": "",
                    "ref_max": "",
                    "flag": None
                }
            ]
        }
    },
    {
        "name": "No refs provided",
        "data": {
            "report_type": "FBC",
            "biomarkers": [
                {
                    "name": "CustomTest",
                    "value": 50,
                    "unit": "U/L"
                }
            ]
        }
    }
]

print("="*70)
print("BIOMARKER STORAGE TEST")
print("="*70)

# You need to provide a valid patient_id for testing
print("\nNOTE: Replace this with a real patient_id from your database")
TEST_PATIENT_ID = "550e8400-e29b-41d4-a716-446655440000"  # Replace with actual UUID
TEST_FILE_ID = "test-biomarker-debug"
TEST_GCS_PATH = "gs://test/path.pdf"

print(f"\nTest Patient ID: {TEST_PATIENT_ID}")
print(f"Test File ID: {TEST_FILE_ID}\n")

for test_case in test_cases:
    print(f"\n{'─'*70}")
    print(f"Test Case: {test_case['name']}")
    print(f"{'─'*70}")
    
    # Show the input data
    print("\nInput Biomarkers:")
    for bm in test_case['data'].get('biomarkers', []):
        print(f"  - {bm.get('name')}")
        print(f"    value: {bm.get('value')} (type: {type(bm.get('value')).__name__})")
        print(f"    ref_min: {bm.get('ref_min')} (type: {type(bm.get('ref_min', None)).__name__})")
        print(f"    ref_max: {bm.get('ref_max')} (type: {type(bm.get('ref_max', None)).__name__})")
    
    # Try to store
    try:
        result = store_normalized_report_to_db(
            patient_id=UUID(TEST_PATIENT_ID),
            file_id=f"{TEST_FILE_ID}-{test_case['name'].replace(' ', '-').lower()}",
            gcs_path=TEST_GCS_PATH,
            normalized_json=test_case['data']
        )
        
        if result.get("success"):
            print(f"\n✅ SUCCESS")
            if result.get("warning"):
                print(f"⚠️  Warning: {result.get('warning')}")
            
            # Show stored biomarkers
            biomarkers = result.get("data", {}).get("biomarkers", [])
            if biomarkers:
                print(f"\nStored {len(biomarkers)} biomarker(s):")
                for bm in biomarkers:
                    print(f"  - {bm.get('name')}")
                    print(f"    value: {bm.get('value')}")
                    print(f"    ref_min: {bm.get('ref_min')}")
                    print(f"    ref_max: {bm.get('ref_max')}")
                    print(f"    flag: {bm.get('flag')}")
        else:
            print(f"\n❌ FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")

print(f"\n{'='*70}")
print("TEST COMPLETE")
print(f"{'='*70}")
print("\nCheck your Supabase database:")
print("1. Go to Supabase → Table Editor")
print("2. Select 'biomarkers' table")
print("3. Look for test entries with file_id starting with 'test-biomarker-debug'")
print("4. Verify ref_min and ref_max are stored correctly")
print("\nTo clean up test data:")
print("DELETE FROM reports WHERE file_id LIKE 'test-biomarker-debug%';")
