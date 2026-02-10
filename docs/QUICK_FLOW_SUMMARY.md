# Quick Summary - How Database Updates Work

## 🎯 Simple Answer

When you POST to `/api/v1/patients/`, here's what happens:

**7 Files Work Together:**

1. **`.env`** → Stores Supabase credentials
2. **`app/main.py`** → Entry point, routes requests
3. **`app/api/v1/endpoints/patient.py`** → Handles the HTTP POST request
4. **`app/schemas/patient.py`** → Validates the data (nic, name, age, gender)
5. **`app/services/patientService.py`** → Calls Supabase to insert data
6. **`app/db/supabase.py`** → Connects to Supabase database
7. **Supabase Database** → Stores the patient record

## 📝 Example Request & Response

### Request:
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

### What Each File Does:

```python
# 1. app/main.py (Line 23)
app.include_router(patient.router, prefix="/api/v1")
# → Routes /api/v1/patients/ to patient endpoints

# 2. app/api/v1/endpoints/patient.py (Line 17-23)
@router.post("/", status_code=201)
def create_patient_endpoint(patient: PatientCreate):
    result = create_patient(patient)  # Calls service
    return result
# → Receives request, calls service, returns response

# 3. app/schemas/patient.py (Line 7-11)
class PatientCreate(BaseModel):
    nic: str
    name: str
    age_years: int  # Must be 0-150
    gender: str
# → Validates data is correct format

# 4. app/services/patientService.py (Line 8-20)
def create_patient(patient: PatientCreate) -> dict:
    response = supabase.table("patients").insert({
        "nic": patient.nic,
        "name": patient.name,
        "age_years": patient.age_years,
        "gender": patient.gender
    }).execute()
    return {"success": True, "data": response.data[0]}
# → Inserts into Supabase database

# 5. app/db/supabase.py (Line 1-11)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
# → Connects to Supabase using credentials from .env

# 6. Supabase Database
# → Executes: INSERT INTO patients (...) VALUES (...)
# → Auto-generates: id (UUID) and created_at (timestamp)
# → Returns the complete patient record
```

### Response (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",  ← Auto-generated
    "nic": "199512345678",
    "name": "John Doe",
    "age_years": 29,
    "gender": "Male",
    "created_at": "2026-02-07T12:29:30.123Z"  ← Auto-generated
  }
}
```

## 🔄 The Complete Flow

```
POST Request
    ↓
main.py (routes to patient endpoint)
    ↓
patient.py (receives request)
    ↓
schemas/patient.py (validates data: nic, name, age, gender)
    ↓
patientService.py (calls supabase.table("patients").insert(...))
    ↓
supabase.py (connects using credentials)
    ↓
Supabase Database (inserts row, generates id & created_at)
    ↓
Response flows back through all layers
    ↓
Client receives: {success: true, data: {...}}
```

## ✨ Key Points

1. **You only send 4 fields**: nic, name, age_years, gender
2. **Supabase auto-generates 2 fields**: id (UUID) and created_at (timestamp)
3. **Service layer** does all the database work
4. **Schemas** ensure data is valid before it reaches the database
5. **Same pattern for all CRUD operations** (GET, PATCH, DELETE)

---

## 📖 Full Documentation

- **Detailed flow**: `DATABASE_UPDATE_FLOW.md`
- **Visual diagram**: Run `python view_flow_diagram.py`

## 🧪 Test It

```bash
# Create a patient
curl -X POST http://localhost:8000/api/v1/patients/ \
  -H "Content-Type: application/json" \
  -d '{"nic":"123456789","name":"Test","age_years":25,"gender":"Male"}'

# Or use PowerShell
$body = @{nic='123456789'; name='Test'; age_years=25; gender='Male'} | ConvertTo-Json
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/patients/' -Method Post -Body $body -ContentType 'application/json'
```

That's it! All 7 files work together to store your data in Supabase! 🎉
