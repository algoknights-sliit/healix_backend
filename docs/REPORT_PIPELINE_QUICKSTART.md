# Quick Start: Report Processing Pipeline

## 🎯 What It Does

**Uploads PDF → OCR Processing → Saves to Cloud Storage + Supabase**

---

## 📋 Quick Summary

### Tables Created in Supabase ✅
```sql
reports (id, patient_id, file_id, report_type, sample_collected_at, gcs_path, created_at)
biomarkers (id, report_id, name, value, unit, ref_min, ref_max, flag)
```

### Files Created ✅
1. `app/schemas/report.py` - Pydantic models
2. `app/services/reportService.py` - Database operations
3. Updated `app/workers/ocr_worker.py` - Now saves to Supabase
4. Updated `app/api/v1/endpoints/reports.py` - patient_id instead of NIC

---

## 🚀 How to Use

### 1. Upload a Report
```bash
POST /api/v1/reports/upload
  patient_id=<UUID>
  file=<PDF>
```

### 2. Processing Happens Automatically
```
PDF → GCS → OCR → Normalize → Save to:
  - Cloud Storage (JSON files)
  - Supabase (reports + biomarkers tables)
```

### 3. Retrieve Data

**From Database:**
```bash
GET /api/v1/reports/{patient_id}?source=database
GET /api/v1/report/id/{report_id}/complete  # Report + biomarkers
GET /api/v1/report/id/{report_id}/biomarkers  # Just biomarkers
```

**From Cloud Storage:**
```bash
GET /api/v1/report/{patient_id}/{file_id}/normalized  # JSON
GET /api/v1/report/{patient_id}/{file_id}/raw  # Raw OCR
```

---

## 📝 Example Flow

### Upload
```bash
curl -X POST "http://localhost:8000/api/v1/reports/upload" \
  -F "patient_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "file=@blood_test.pdf"
```

**Returns:**
```json
{
  "status": "uploaded",
  "file_id": "abc123...",
  "patient_id": "550e8400..."
}
```

### Check Status (after ~10-30 seconds)
```bash
curl "http://localhost:8000/api/v1/reports/550e8400-e29b-41d4-a716-446655440000?source=database"
```

###  Get Complete Report
```bash
curl "http://localhost:8000/api/v1/report/id/{report_id}/complete"
```

**Returns:**
```json
{
  "status": "success",
  "data": {
    "report": {
      "id": "...",
      "patient_id": "...",
      "report_type": "FBC",
      "sample_collected_at": "2026-02-07T10:30:00Z"
    },
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
}
```

---

## 🔑 Key Changes

### From Old System:
- ❌ Used `nic` (National ID)
- ❌ Only Cloud Storage
- ❌ Manual biomarker parsing

### To New System:
- ✅ Uses `patient_id` (UUID from patients table)
- ✅ Cloud Storage + Supabase Database
- ✅ Automatic biomarker extraction and storage
- ✅ Foreign key relationships (patient → report → biomarkers)
- ✅ Cascade deletion

---

## 📊 Data Flow

```
User                    Backend                  Cloud/DB
│                                                    
├─ Upload PDF ────────► Upload to GCS ────────► gs://bucket/...
│                        │
│                        ├─ Background worker
│                        │   ├─ OCR (Document AI)
│                        │   ├─ Build raw JSON
│                        │   ├─ Normalize
│                        │   │
│                        │   ├─ Save JSONs ──────► Cloud Storage
│                        │   │
│                        │   └─ Save to DB ──────► Supabase
│                        │        ├─ reports table
│                        │        └─ biomarkers table
│                        │
└─ Get report ──────────┤
    ├─ From database ───┤
    │   └─ Biomarkers ──┤
    │                    │
    └─ From storage ────┤
        └─ JSON files ──┘
```

---

## ✅ Next Steps

1. **Test Upload** - Try uploading a sample PDF
2. **Check Supabase** - Go to Table Editor → reports & biomarkers
3. **Use APIs** - Query reports and biomarkers
4. **Integrate Frontend** - Connect to these endpoints

---

## 📖 Full Documentation

See `docs/REPORT_PROCESSING_GUIDE.md` for complete details.

---

**Everything is ready! Just upload a report and watch it all work!** 🎉
