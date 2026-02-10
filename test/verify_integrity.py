import requests
import uuid
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
USER_ID = str(uuid.uuid4())

def test_timestamps():
    print("--- Testing Timestamps and Integrity ---")
    
    # 1. Create a metric
    payload = {
        "user_id": USER_ID,
        "metric_name": "Heart Rate",
        "value": 75.0,
        "unit": "bpm"
    }
    
    print(f"[1] Creating metric: {payload['metric_name']} = {payload['value']}")
    response = requests.post(f"{BASE_URL}/health-metrics/", json=payload)
    if response.status_code != 201:
        print(f"FAILED to create metric: {response.text}")
        return
    
    metric = response.json()
    created_at = metric['created_at']
    updated_at = metric['updated_at']
    recorded_at = metric['recorded_at']
    metric_id = metric['id']
    
    print(f"    ID: {metric_id}")
    print(f"    Created At:  {created_at}")
    print(f"    Updated At:  {updated_at}")
    print(f"    Recorded At: {recorded_at}")
    
    # recorded_at should be approximately now (or match created_at if default)
    if not recorded_at:
        print("FAILED: recorded_at is missing")
    
    # 2. Wait a bit and update
    print("\n[2] Waiting 2 seconds before update...")
    time.sleep(2)
    
    update_payload = {
        "value": 85.0
    }
    print(f"    Updating metric {metric_id} value to {update_payload['value']}")
    update_response = requests.put(f"{BASE_URL}/health-metrics/{metric_id}", json=update_payload)
    
    if update_response.status_code != 200:
        print(f"FAILED to update metric: {update_response.text}")
        return
    
    updated_metric = update_response.json()
    new_created_at = updated_metric['created_at']
    new_updated_at = updated_metric['updated_at']
    
    print(f"    New Created At:  {new_created_at}")
    print(f"    New Updated At:  {new_updated_at}")
    
    if new_created_at != created_at:
        print("FAILED: created_at changed after update")
    else:
        print("PASS: created_at remained stable")
        
    if new_updated_at <= updated_at:
        print("FAILED: updated_at did not increase")
    else:
        print("PASS: updated_at increased correctly")

    # 3. Verify manual recorded_at
    past_time = "2020-01-01T12:00:00Z"
    print(f"\n[3] Creating metric with manual recorded_at: {past_time}")
    past_payload = {
        "user_id": USER_ID,
        "metric_name": "Body Temp",
        "value": 36.6,
        "recorded_at": past_time
    }
    past_response = requests.post(f"{BASE_URL}/health-metrics/", json=past_payload)
    if past_response.status_code != 201:
        print(f"FAILED to create past metric: {past_response.text}")
    else:
        past_metric = past_response.json()
        print(f"    Recorded At (Returned): {past_metric['recorded_at']}")
        if "2020-01-01" in past_metric['recorded_at']:
            print("PASS: manual recorded_at preserved integrity")
        else:
            print("FAILED: manual recorded_at was ignored or mangled")

    # 4. Verify NONE integration
    print(f"\n[4] Verifying NONE assessment for Step Count...")
    none_payload = {
        "user_id": USER_ID,
        "metric_name": "Step Count",
        "value": 5000.0
    }
    none_response = requests.post(f"{BASE_URL}/health-metrics/", json=none_payload)
    if none_response.status_code != 201:
        print(f"FAILED to create Step Count: {none_response.text}")
    else:
        none_metric = none_response.json()
        print(f"    Assessment for Step Count: {none_metric['health_assessment']}")
        if none_metric['health_assessment'] == "NONE":
            print("PASS: NONE status correctly applied")
        else:
            print("FAILED: Expected NONE status")

if __name__ == "__main__":
    try:
        test_timestamps()
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Make sure the FastAPI server is running on port 8000.")
