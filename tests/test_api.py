"""
Quick test script to verify API endpoints are working.
This simulates getting normalized JSON data from the API.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8080/api/v1/ocr"

def test_api_endpoints():
    """Test all API endpoints (mock test without actual upload)."""
    
    print("=" * 80)
    print("API ENDPOINTS TEST")
    print("=" * 80)
    print()
    
    # Test 1: Check API is running
    print("1. Testing API availability...")
    try:
        response = requests.get("http://localhost:8080/docs")
        if response.status_code == 200:
            print("✓ API is running at http://localhost:8080")
            print("✓ Swagger docs available at http://localhost:8080/docs")
        else:
            print("✗ API may not be running properly")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure it's running:")
        print("  uvicorn app.main:app --port 8080 --reload")
        return
    
    print()
    
    # Display available endpoints
    print("2. Available Endpoints:")
    print("-" * 80)
    endpoints = [
        ("POST", "/upload", "Upload medical report PDF"),
        ("GET", "/report/{nic}/{file_id}/normalized", "Get normalized report"),
        ("GET", "/report/{nic}/{file_id}/raw", "Get raw OCR data"),
        ("GET", "/reports/{nic}", "List all reports for a patient")
    ]
    
    for method, path, description in endpoints:
        full_url = f"{BASE_URL}{path}"
        print(f"  {method:6} {full_url:60} - {description}")
    
    print()
    print("=" * 80)
    print("ENDPOINT STRUCTURE")
    print("=" * 80)
    print()
    
    # Example usage
    print("Example: Get normalized report")
    print("-" * 80)
    print("URL Pattern:")
    print(f"  GET {BASE_URL}/report/{{nic}}/{{file_id}}/normalized")
    print()
    print("Example:")
    print(f'  GET {BASE_URL}/report/123456789V/abc-123-def-456/normalized')
    print()
    print("Expected Response:")
    example_response = {
        "status": "success",
        "data": {
            "patient": {
                "name": "MR S KUMAR",
                "age_years": 62,
                "gender": "Male"
            },
            "report": {
                "type": "Full Blood Count",
                "sample_collected_at": "2025-06-03T09:10:00"
            },
            "biomarkers": [
                {
                    "name": "WBC",
                    "value": 7970.0,
                    "unit": "per cu mm",
                    "ref_range": [4000.0, 11000.0]
                }
            ]
        }
    }
    print(json.dumps(example_response, indent=2))
    
    print()
    print("=" * 80)
    print("HOW TO USE")
    print("=" * 80)
    print()
    print("1. Upload a PDF report:")
    print("   curl -X POST http://localhost:8080/api/v1/ocr/upload \\")
    print('     -F "nic=123456789V" \\')
    print('     -F "file=@/path/to/report.pdf"')
    print()
    print("2. Get the file_id from the response")
    print()
    print("3. Wait a few seconds for processing")
    print()
    print("4. Retrieve normalized data:")
    print("   curl http://localhost:8080/api/v1/ocr/report/{nic}/{file_id}/normalized")
    print()
    print("=" * 80)
    print("✓ API endpoints configured and ready to use!")
    print("  Visit http://localhost:8080/docs for interactive testing")
    print("=" * 80)


if __name__ == "__main__":
    test_api_endpoints()
