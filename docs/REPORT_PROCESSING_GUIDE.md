# Report Processing & Database Integration Guide

## 🎯 Overview

Complete report processing pipeline that:
1. **Uploads** PDF reports to Google Cloud Storage
2. **Processes** with OCR (Document AI)
3. **Normalizes** medical data to structured JSON
4. **Stores** in both Cloud Storage AND Supabase database
5. **Provides APIs** to access reports and biomarkers

---

## 📊 Database Schema

### `reports` Table
```sql
create table reports (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid references patients(id) on delete cascade,
  file_id text not null,                  -- UUID from cloud storage
  report_type text not null,              -- 'FBC', 'Lipid Profile', etc.
  sample_collected_at timestamptz,        -- When sample was collected
  gcs_path text,                          -- Google Cloud Storage path
  created_at timestamptz default now()
);
```

### `biomarkers` Table
```sql
create table biomarkers (
  id uuid primary key default gen_random_uuid(),
  report_id uuid references reports(id) on delete cascade,
  name text not null,          -- 'Hemoglobin', 'WBC', etc.
  value numeric not null,      -- Measured value
  unit text,                   -- 'g/dL', 'cells/μL', etc.
  ref_min numeric,             -- Reference range minimum
  ref_max numeric,             -- Reference range maximum
  flag text                    -- 'HIGH', 'LOW', 'NORMAL'
);
```

---

## 🔄 Complete Flow

### 1. User Uploads Report
```
POST /api/v1/reports/upload
patient_id=<UUID>&file=report.pdf
```

**What Happens:**
```
1. PDF saved to temp folder
2. Uploaded to GCS: gs://bucket/users/{patient_id}/reports/{file_id}.pdf
3. Background worker started
4. Temp file deleted
5. Returns: file_id for tracking
```

**File Structure in GCS:**
```
users/
  {patient_id}/
    reports/
      {file_id}.pdf                    ← Original PDF
    processed/
      {file_id}.json                   ← Raw OCR data
      {file_id}_normalized.json        ← Normalized medical data
```

### 2. Background Processing (Automatic)
```python
# app/workers/ocr_worker.py
process_document_worker(gcs_uri, patient_id, file_id)
```

**Processing Steps:**
1. **OCR Extraction** - Document AI extracts text, tables, entities
2. **Raw JSON** - Build raw JSON from OCR data
3. **Normalization** - Convert to structured medical format
4. **Cloud Storage** - Save both JSONs to GCS
5. **Database** - Save report + biomarkers to Supabase

**Example Flow:**
```
PDF → Document AI → Raw OCR Data
                      ↓
                  NLP/Extraction
                      ↓
                Normalized JSON
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
  Cloud Storage              Supabase Database
  (both JSONs)            (reports + biomarkers)
```

### 3. Normalized JSON Structure
```json
{
  "report_type": "FBC",
  "sample_collection_date": "2026-02-07T10:30:00Z",
  "biomarkers": [
    {
      "name": "Hemoglobin",
      "value": 14.5,
      "unit": "g/dL",
      "ref_min": 12.0,
      "ref_max": 16.0,
      "flag": "NORMAL"
    },
    {
      "name": "WBC",
      "value": 11.2,
      "unit": "×10³/μL",
      "ref_min": 4.0,
      "ref_max": 11.0,
      "flag": "HIGH"
    }
  ]
}
```

### 4. Database Storage

**Report Entry:**
```json
{
  "id": "a1b2c3...",
  "patient_id": "550e8400...",
  "file_id": "d4e5f6...",
  "report_type": "FBC",
  "sample_collected_at": "2026-02-07T10:30:00Z",
  "gcs_path": "gs://bucket/users/.../reports/d4e5f6.pdf",
  "created_at": "2026-02-07T14:00:00Z"
}
```

**Biomarker Entries:**
```json
[
  {
    "id": "bio1...",
    "report_id": "a1b2c3...",
    "name": "Hemoglobin",
    "value": 14.5,
    "unit": "g/dL",
    "ref_min": 12.0,
    "ref_max": 16.0,
    "flag": "NORMAL"
  },
  {
    "id": "bio2...",
    "report_id": "a1b2c3...",
    "name": "WBC",
    "value": 11.2,
    "unit": "×10³/μL",
    "ref_min": 4.0,
    "ref_max": 11.0,
    "flag": "HIGH"
  }
]
```

---

## 📁 Files & Responsibilities

### Schemas (`app/schemas/report.py`)
- `ReportCreate` - Upload new report
- `ReportOut` - Report response
- `BiomarkerCreate` - Create biomarker
- `BiomarkerOut` - Biomarker response
- `ReportWithBiomarkers` - Complete report

### Services

#### `app/services/reportService.py`
**Report Functions:**
- `create_report(report)` - Insert report into DB
- `get_report_by_id(report_id)` - Fetch by UUID
- `get_report_by_file_id(file_id)` - Fetch by file_id
- `list_reports_by_patient(patient_id)` - All reports for patient
- `update_report(report_id, updates)` - Update metadata
- `delete_report(report_id)` - Delete (cascades to biomarkers)

**Biomarker Functions:**
- `create_biomarker(biomarker)` - Insert single biomarker
- `create_biomarkers_bulk(biomarkers)` - Insert multiple (efficient)
- `get_biomarkers_by_report(report_id)` - All biomarkers for report
- `get_report_with_biomarkers(report_id)` - Complete report

**Special Function:**
- `store_normalized_report_to_db()` - Called by worker to save everything

#### `app/services/upload_service.py`
- `upload_pdf_to_bucket()` - Upload PDF to GCS
- `store_json()` - Save JSON to GCS
- `get_normalized_json()` - Retrieve normalized JSON from GCS
- `get_raw_json()` - Retrieve raw OCR JSON from GCS
- `list_user_reports()` - List from Cloud Storage (legacy)

#### `app/services/ocr_service.py`
- `process_with_document_ai()` - OCR with Google Document AI

#### `app/services/normalization_service.py`
- `normalize_fbc_report()` - Convert raw OCR to structured format

### Worker (`app/workers/ocr_worker.py`)
Background processing pipeline. Now saves to BOTH:
- Cloud Storage (JSON files)
- Supabase (reports + biomarkers tables)

### Endpoints (`app/api/v1/endpoints/reports.py`)

**Upload:**
- `POST /upload` - Upload and process report

**Cloud Storage Access:**
- `GET /report/{patient_id}/{file_id}/normalized` - Get normalized JSON from storage
- `GET /report/{patient_id}/{file_id}/raw` - Get raw OCR JSON from storage

**Database Access:**
- `GET /reports/{patient_id}?source=database` - List reports from DB
- `GET /report/id/{report_id}` - Get report by DB UUID
- `GET /report/file/{file_id}` - Get report by file_id
- `GET /report/id/{report_id}/biomarkers` - Get biomarkers only
- `GET /report/id/{report_id}/complete` - Get report + biomarkers

---

## 🚀 API Examples

### 1. Upload a Report
```bash
curl -X POST "http://localhost:8000/api/v1/reports/upload" \
  -F "patient_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "file=@blood_test.pdf"
```

**Response:**
```json
{
  "status": "uploaded",
  "message": "Report uploaded and processing started. Data will be saved to database when complete.",
  "file_id": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. List Patient Reports (from Database)
```bash
curl "http://localhost:8000/api/v1/reports/{patient_id}?source=database&skip=0&limit=10"
```

**Response:**
```json
{
  "status": "success",
  "source": "database",
  "count": 2,
  "reports": [
    {
      "id": "a1b2c3...",
      "patient_id": "550e8400...",
      "file_id": "d4e5f6...",
      "report_type": "FBC",
      "sample_collected_at": "2026-02-07T10:30:00Z",
      "gcs_path": "gs://...",
      "created_at": "2026-02-07T14:00:00Z"
    }
  ]
}
```

### 3. Get Report with Biomarkers
```bash
curl "http://localhost:8000/api/v1/report/id/{report_id}/complete"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "report": {
      "id": "a1b2c3...",
      "patient_id": "550e8400...",
      "report_type": "FBC",
      ...
    },
    "biomarkers": [
      {
        "id": "bio1...",
        "report_id": "a1b2c3...",
        "name": "Hemoglobin",
        "value": 14.5,
        "unit": "g/dL",
        ...
      }
    ]
  }
}
```

### 4. Get Normalized JSON (Cloud Storage)
```bash
curl "http://localhost:8000/api/v1/report/{patient_id}/{file_id}/normalized"
```

---

## 🔍 Key Changes from Original

### Changed: NIC → patient_id
**Old Way:**
```python
POST /upload?nic=199512345678
GET /reports/{nic}
```

**New Way:**
```python
POST /upload?patient_id=550e8400-e29b-41d4-a716-446655440000
GET /reports/{patient_id}?source=database
```

### Added: Database Storage
- Reports automatically saved to `reports` table
- Biomarkers extracted and saved to `biomarkers` table
- Relationships maintained via foreign keys
- Cascade deletion (delete report → deletes biomarkers)

### Added: New Endpoints
- Get by report UUID
- Get by file_id
- Get biomarkers for a report
- Get complete report (report + biomarkers)
- List from database vs storage

---

## 📊 Data Sources

You now have **TWO** data sources:

### 1. Cloud Storage (Original)
- **Contains:** PDF files, raw JSON, normalized JSON
- **Use for:** File downloads, debugging OCR
- **Access via:** `/report/{patient_id}/{file_id}/normalized`

### 2. Supabase Database (NEW)
- **Contains:** Report metadata, biomarkers
- **Use for:** Querying, filtering, analytics
- **Access via:** `/reports/{patient_id}?source=database`

**Why Both?**
- Cloud Storage: File storage, OCR artifacts
- Database: Structured queries, relationships, fast filtering

---

## ✅ Installation & Setup

### 1. Create Tables in Supabase
```sql
-- Already done! Just verify they exist
SELECT * FROM reports LIMIT 1;
SELECT * FROM biomarkers LIMIT 1;
```

### 2. No New Dependencies
All required packages already installed:
- `supabase-py` (already have)
- `google-cloud-storage` (already have)
- `google-cloud-documentai` (already have)

### 3. Restart Server
Server should auto-reload, but to be safe:
```bash
# Stop and restart
uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Testing the Complete Flow

### Step 1: Upload a Report
```bash
curl -X POST "http://localhost:8000/api/v1/reports/upload" \
  -F "patient_id=YOUR_PATIENT_UUID" \
  -F "file=@test_report.pdf"
```

Save the `file_id` from the response.

### Step 2: Wait for Processing
Processing happens in the background (5-30 seconds depending on report complexity).

### Step 3: Check Database
```bash
# List reports
curl "http://localhost:8000/api/v1/reports/YOUR_PATIENT_UUID?source=database"

# Get specific report
curl "http://localhost:8000/api/v1/report/file/FILE_ID"
```

### Step 4: Get Biomarkers
```bash
# Get report with biomarkers
curl "http://localhost:8000/api/v1/report/id/REPORT_UUID/complete"
```

### Step 5: Verify in Supabase Dashboard
1. Go to Supabase → Table Editor
2. Check `reports` table → Should see your report
3. Check `biomarkers` table → Should see extracted biomarkers

---

## 🎯 Summary

### What You Have Now:

1. ✅ **Upload** → PDF to GCS
2. ✅ **Process** → OCR + Normalization
3. ✅ **Store** → Cloud Storage (JSON) + Supabase (structured data)
4. ✅ **Query** → Rich API endpoints for both sources
5. ✅ **Relationships** → Reports linked to patients, biomarkers linked to reports

### Complete Pipeline:

```
Patient uploads PDF
        ↓
Saved to GCS (/reports/file_id.pdf)
        ↓
Background worker starts
        ↓
Document AI OCR
        ↓
Build raw JSON → Save to GCS (/processed/file_id.json)
        ↓
Normalize medical data → Save to GCS (/processed/file_id_normalized.json)
        ↓
Parse biomarkers from normalized JSON
        ↓
Save to Supabase:
  - reports table (1 row)
  - biomarkers table (N rows)
        ↓
API endpoints provide access to everything!
```

**You're all set!** 🎉
