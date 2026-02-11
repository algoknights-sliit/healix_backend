# Patient CRUD Flow - How Database Updates Work

## 📋 Overview

When you make a POST request to create a patient, here's the complete journey through your backend:

```
Client Request
    ↓
FastAPI Main App (app/main.py)
    ↓
Router/Endpoint (app/api/v1/endpoints/patient.py)
    ↓
Pydantic Validation (app/schemas/patient.py)
    ↓
Service Layer (app/services/patientService.py)
    ↓
Supabase Client (app/db/supabase.py)
    ↓
Supabase Database (Cloud)
```

---

## 🔄 Detailed Flow for POST Request (Create Patient)

### Step 1: Client Sends Request
```http
POST http://localhost:8000/api/v1/patients/
Content-Type: application/json

{
  "nic": "199512345678",
  "name": "John Doe",
  "age_years": 29,
  "gender": "Male"
}
```

---

### Step 2: FastAPI Main App Receives Request
**File:** `app/main.py`

```python
# Line 7-11: FastAPI app is created
app = FastAPI(
    title="Healix Backend API",
    description="AI-powered medical record system",
    version="1.0.0"
)

# Line 23: Patient router is registered
app.include_router(patient.router, prefix="/api/v1", tags=["Patients"])
```

**What happens:**
- FastAPI receives the request
- Looks for a route matching `/api/v1/patients/`
- Forwards to the `patient.router`

---

### Step 3: Router/Endpoint Handles Request
**File:** `app/api/v1/endpoints/patient.py`

```python
# Line 14: Router is defined with prefix
router = APIRouter(prefix="/patients", tags=["Patients"])

# Line 17-23: POST endpoint for creating patient
@router.post("/", status_code=201)
def create_patient_endpoint(patient: PatientCreate):
    """Create a new patient"""
    result = create_patient(patient)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create patient"))
    return result
```

**What happens:**
1. Route matches: `POST /patients/` (combined with prefix = `/api/v1/patients/`)
2. FastAPI automatically validates request body against `PatientCreate` schema
3. If validation passes, calls `create_patient()` from service layer
4. Returns result or raises HTTP exception if failed

---

### Step 4: Pydantic Validates Data
**File:** `app/schemas/patient.py`

```python
# Line 7-11: PatientCreate schema defines expected fields
class PatientCreate(BaseModel):
    nic: str = Field(..., description="National Identity Card number, must be unique")
    name: str = Field(..., description="Patient's full name")
    age_years: int = Field(..., ge=0, le=150, description="Patient's age in years")
    gender: str = Field(..., description="Patient's gender")
```

**What happens:**
- Validates all required fields are present
- Checks data types (str, int)
- Validates age is between 0-150
- If validation fails, returns 422 error automatically
- If passes, creates a `PatientCreate` object

---

### Step 5: Service Layer Processes Request
**File:** `app/services/patientService.py`

```python
# Line 8-20: create_patient function
def create_patient(patient: PatientCreate) -> dict:
    """Create a new patient in Supabase"""
    try:
        response = supabase.table("patients").insert({
            "nic": patient.nic,
            "name": patient.name,
            "age_years": patient.age_years,
            "gender": patient.gender
        }).execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Failed to create patient"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**What happens:**
1. Converts `PatientCreate` object to dictionary
2. Calls Supabase client to insert data
3. Supabase generates UUID and timestamp automatically
4. Returns success/failure response

---

### Step 6: Supabase Client Connects to Database
**File:** `app/db/supabase.py`

```python
# Line 1-11: Supabase client initialization
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
```

**What happens:**
1. Reads credentials from `.env` file
2. Creates authenticated Supabase client
3. This client is imported by service layer
4. Sends HTTP request to Supabase API

---

### Step 7: Supabase Database Executes
**Location:** Supabase Cloud (https://hbrqbkgaznqcnkkrxiqd.supabase.co)

**SQL Executed:**
```sql
INSERT INTO patients (nic, name, age_years, gender)
VALUES ('199512345678', 'John Doe', 29, 'Male')
RETURNING *;
```

**What happens:**
1. PostgreSQL generates UUID for `id` field
2. Sets `created_at` to current timestamp
3. Checks `nic` uniqueness constraint
4. Inserts row into `patients` table
5. Returns the complete row with all fields

---

### Step 8: Response Flows Back to Client

**Path:**
```
Supabase DB → Supabase Client → Service Layer → Endpoint → FastAPI → Client
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nic": "199512345678",
    "name": "John Doe",
    "age_years": 29,
    "gender": "Male",
    "created_at": "2026-02-07T06:59:01.123456+00:00"
  }
}
```

---

## 📁 All Files Involved (in order)

### 1. Configuration Files
- **`.env`** - Stores Supabase credentials
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`

### 2. Core Application Files
- **`app/main.py`**
  - Entry point
  - Registers routers
  - Lines involved: 1-27

### 3. Database Connection
- **`app/db/supabase.py`**
  - Creates Supabase client
  - Loads environment variables
  - Lines involved: 1-11

### 4. API Layer
- **`app/api/v1/endpoints/patient.py`**
  - Defines API endpoints
  - Handles HTTP requests/responses
  - Lines for POST: 17-23

### 5. Data Validation Layer
- **`app/schemas/patient.py`**
  - Defines data models
  - Validates input/output
  - PatientCreate: Lines 7-11
  - PatientOut: Lines 19-27

### 6. Business Logic Layer
- **`app/services/patientService.py`**
  - Contains CRUD logic
  - Interacts with Supabase
  - create_patient: Lines 8-20

### 7. External Service
- **Supabase Database** (Cloud)
  - PostgreSQL database
  - Table: `patients`

---

## 🔍 Other CRUD Operations

### GET Request Flow (Read Patient)
```
Client → main.py → patient.py (endpoint) → patientService.py → supabase.py → Supabase DB
```

**Service function:**
```python
# app/services/patientService.py - Line 22-30
def get_patient_by_id(patient_id: str) -> Optional[dict]:
    response = supabase.table("patients").select("*").eq("id", patient_id).execute()
```

### PATCH Request Flow (Update Patient)
```
Client → Validation (PatientUpdate) → Service → Supabase → DB
```

**Service function:**
```python
# app/services/patientService.py - Line 52-66
def update_patient(patient_id: str, updates: PatientUpdate) -> dict:
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    response = supabase.table("patients").update(update_data).eq("id", patient_id).execute()
```

### DELETE Request Flow
```
Client → Endpoint → Service → Supabase → DB
```

**Service function:**
```python
# app/services/patientService.py - Line 68-75
def delete_patient(patient_id: str) -> dict:
    response = supabase.table("patients").delete().eq("id", patient_id).execute()
```

---

## 🎯 Key Concepts

### 1. **Layered Architecture**
- **API Layer** (`endpoints/`) - HTTP interface
- **Service Layer** (`services/`) - Business logic
- **Data Layer** (`db/`) - Database connection
- **Schema Layer** (`schemas/`) - Data validation

### 2. **Separation of Concerns**
- Each file has a specific responsibility
- Easy to test and maintain
- Changes in one layer don't affect others

### 3. **Data Flow**
- **Inbound:** Request → Validation → Processing → Storage
- **Outbound:** Storage → Processing → Serialization → Response

### 4. **Error Handling**
- Pydantic handles validation errors (422)
- Service layer catches database errors
- Endpoint layer converts to HTTP errors (400, 404, 500)

---

## 🛠️ How to Extend

### Add a New Field
1. Update Supabase schema (add column)
2. Update `PatientCreate` in `schemas/patient.py`
3. Update `PatientOut` in `schemas/patient.py`
4. Service layer automatically handles it

### Add a New Endpoint
1. Add function in `services/patientService.py`
2. Add route in `endpoints/patient.py`
3. That's it! FastAPI handles the rest

### Add Validation
1. Update schema in `schemas/patient.py`
2. Use Pydantic Field validators
3. Automatic validation on all requests

---

## 📊 Database Auto-Generated Fields

These fields are automatically created by Supabase:

```sql
id uuid primary key default gen_random_uuid()     -- Generated by Supabase
created_at timestamptz default now()              -- Generated by Supabase
```

You don't need to send these in the request - Supabase handles them automatically!

---

## ✅ Summary

**For a POST request creating a patient:**

1. **Request arrives** at FastAPI (`main.py`)
2. **Router matches** `/api/v1/patients/` (`patient.py` endpoint)
3. **Pydantic validates** data (`schemas/patient.py`)
4. **Service processes** request (`patientService.py`)
5. **Supabase client** sends to database (`supabase.py`)
6. **Database inserts** row and generates UUID/timestamp
7. **Response flows back** through all layers to client

**Files involved (in order):**
1. `.env` (config)
2. `app/main.py` (routing)
3. `app/api/v1/endpoints/patient.py` (endpoint)
4. `app/schemas/patient.py` (validation)
5. `app/services/patientService.py` (business logic)
6. `app/db/supabase.py` (database connection)
7. Supabase Database (storage)

That's the complete flow! 🎉
