import os
import json
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET")
DOC_AI_LOCATION = os.getenv("DOCAI_LOCATION", "us")
DOC_AI_PROCESSOR_ID = os.getenv("DOCAI_PROCESSOR_ID")

# Handle Google Cloud credentials for both local and production environments
credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if credentials_json:
    # Production: Use environment variable (Render deployment)
    # Write credentials to temporary file
    temp_creds_path = "/tmp/google_credentials.json"
    try:
        # Parse to validate JSON
        creds_dict = json.loads(credentials_json)
        with open(temp_creds_path, "w") as f:
            json.dump(creds_dict, f)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_path
        print("✅ Using Google credentials from environment variable")
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")
        raise
else:
    # Local development: Use key.json file
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    key_path = os.path.join(BASE_DIR, "key.json")
    
    if os.path.exists(key_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
        print(f"✅ Using Google credentials from local file: {key_path}")
    else:
        print("⚠️  Warning: No Google credentials found (neither env var nor key.json)")

