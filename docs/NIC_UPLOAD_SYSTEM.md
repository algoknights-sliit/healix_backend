# Report Upload System - NIC + Database Integration

## 🎯 System Design

### Best of Both Worlds:
- **Upload with NIC** → User-friendly, easy to remember
- **GCS organized by NIC** → `users/{nic}/reports/...` (human-readable folders)
- **Database uses patient_id** → Proper foreign key relationships

---

## 🔄 Complete Flow

### 1. User Uploads Report
```bash
POST /api/v1/reports/upload
  nic=199512345678
  file=blood_test.pdf
```

### 2. Backend Processing
```
1. Receive NIC from user
   ↓
2. Look up patient by NIC in database
   ↓
3. Get patient_id (UUID)
   ↓
4. Upload PDF to GCS: users/{nic}/reports/{file_id}.pdf
   ↓
5. Start background worker with BOTH nic and patient_id
   ↓
6. Return file_id to user
```

### 3. Background Worker
```
1. OCR with Document AI
   ↓
2. Build raw JSON
   ↓
3. Normalize medical data
   ↓
4. Save to GCS (organized by NIC):
   - users/{nic}/processed/{file_id}.json
   - users/{nic}/processed/{file_id}_normalized.json
   ↓
5. Save to Database (linked by patient_id):
   - reports table (with patient_id foreign key)
   - biomarkers table (with report_id foreign key)
```

---

## 📁 GCS Folder Structure

```
users/
  199512345678/          ← NIC (human-readable!)
    reports/
      abc-123.pdf
      def-456.pdf
    processed/
      abc-123.json                    ← Raw OCR
      abc-123_normalized.json         ← Normalized
      def-456.json
      def-456_normalized.json
  
  987654321012/          ← Another patient's NIC
    reports/
      ...
```

**Benefits:**
- Easy to browse in GCS console
- Can quickly find patient's data
- Folder name is memorable (NIC vs UUID)

---

## 💾 Database Structure

```sql
patients
  ├─ id (UUID)
  ├─ nic (text, unique)
  ├─ full_name
  └─ ...
      ↓ (patient_id FK)
reports
  ├─ id (UUID)
  ├─ patient_id → patients.id
  ├─ file_id (text)
  ├─ report_type
  ├─ gcs_path
  └─ ...
      ↓ (report_id FK)
biomarkers
  ├─ id (UUID)
  ├─ report_id → reports.id
  ├─ name
  ├─ value
  └─ ...
```

**Benefits:**
- Proper relational integrity
- Cascade deletes work correctly
- Can join tables efficiently

---

## 🚀 API Endpoints

### Upload (uses NIC)
```bash
POST /api/v1/reports/upload
  nic=199512345678
  file=@report.pdf
```

**Response:**
```json
{
  "status": "uploaded",
  "file_id": "abc-123-def-456",
  "patient_nic": "199512345678",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Cloud Storage Access (uses NIC)
```bash
# Get normalized JSON
GET /api/v1/report/{nic}/{file_id}/normalized

# Get raw OCR JSON
GET /api/v1/report/{nic}/{file_id}/raw

# List reports from storage
GET /api/v1/reports/nic/{nic}?source=storage
```

### Database Access (uses patient_id OR NIC)

**By NIC (looks up patient_id automatically):**
```bash
GET /api/v1/reports/nic/{nic}?source=database
```

**By patient_id (direct database query):**
```bash
GET /api/v1/reports/{patient_id}?source=database
```

**By report UUID:**
```bash
GET /api/v1/report/id/{report_id}/complete
GET /api/v1/report/id/{report_id}/biomarkers
```

**By file_id:**
```bash
GET /api/v1/report/file/{file_id}
```

---

## 📝 Complete Example

### Step 1: Register Patient
```bash
curl -X POST "http://localhost:8000/api/v1/patients/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "nic": "199512345678"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nic": "199512345678",
    ...
  }
}
```

### Step 2: Upload Report (using NIC)
```bash
curl -X POST "http://localhost:8000/api/v1/reports/upload" \
  -F "nic=199512345678" \
  -F "file=@blood_test.pdf"
```

**Response:**
```json
{
  "status": "uploaded",
  "message": "Report uploaded and processing started...",
  "file_id": "abc-123-def-456",
  "patient_nic": "199512345678",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**What happens:**
- PDF → `users/199512345678/reports/abc-123-def-456.pdf`
- Background worker starts
- After ~10-30 seconds, processing completes

### Step 3: List Reports (using NIC)
```bash
curl "http://localhost:8000/api/v1/reports/nic/199512345678?source=database"
```

**Response:**
```json
{
  "status": "success",
  "source": "database",
  "patient_nic": "199512345678",
  "count": 1,
  "reports": [
    {
      "id": "report-uuid-here",
      "patient_id": "550e8400...",
      "file_id": "abc-123-def-456",
      "report_type": "FBC",
      "sample_collected_at": "2026-02-07T10:30:00Z",
      "gcs_path": "gs://bucket/users/199512345678/reports/abc-123-def-456.pdf",
      "created_at": "2026-02-07T14:00:00Z"
    }
  ]
}
```

### Step 4: Get Complete Report
```bash
curl "http://localhost:8000/api/v1/report/id/{report_id}/complete"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "report": {
      "id": "report-uuid",
      "patient_id": "550e8400...",
      "report_type": "FBC",
      ...
    },
    "biomarkers": [
      {
        "id": "bio-uuid-1",
        "report_id": "report-uuid",
        "name": "Hemoglobin",
        "value": 14.5,
        "unit": "g/dL",
        "ref_min": 12.0,
        "ref_max": 16.0,
        "flag": "NORMAL"
      },
      {
        "id": "bio-uuid-2",
        "report_id": "report-uuid",
        "name": "WBC",
        "value": 11.2,
        "unit": "×10³/μL",
        "ref_min": 4.0,
        "ref_max": 11.0,
        "flag": "HIGH"
      }
    ]
  }
}
```

### Step 5: Get JSON Files (using NIC)
```bash
# Get normalized medical data
curl "http://localhost:8000/api/v1/report/199512345678/abc-123-def-456/normalized"

# Get raw OCR data (debugging)
curl "http://localhost:8000/api/v1/report/199512345678/abc-123-def-456/raw"
```

---

## 🔑 Why This Design?

### User Experience
- ✅ **Upload with NIC** - Easy to remember and type
- ✅ **Browse GCS with NIC** - Human-readable folder names
- ✅ **No need to remember UUIDs** - Use NIC for everything user-facing

### Database Integrity
- ✅ **Foreign keys with UUIDs** - Proper relational design
- ✅ **Cascade deletes** - Delete patient → deletes reports → deletes biomarkers
- ✅ **Efficient queries** - UUID indexed for fast lookups

### Flexibility
- ✅ **Access by NIC** - User-friendly routes
- ✅ **Access by patient_id** - Direct database queries
- ✅ **Access by file_id** - Track specific uploads
- ✅ **Access by report_id** - Database record queries

---

## 🎯 Summary

### Upload Flow:
```
User provides NIC
  ↓
Backend looks up patient_id from NIC
  ↓
Upload to GCS: users/{nic}/reports/...
  ↓
Background worker saves to:
  - GCS (organized by NIC)
  - Database (linked by patient_id)
```

### Access Patterns:
```
users/{nic}/...              ← GCS paths use NIC
reports.patient_id           ← Database FK uses UUID
API accepts both NIC & UUID  ← Flexible access
```

**Perfect balance: User-friendly + Database-correct** 🎉
