# Healix Backend

**AI-Powered Medical Record Digitization System for Sri Lankan Healthcare**

A complete FastAPI-based backend system that processes medical reports through OCR, normalizes biomarker data, and provides secure patient management with authentication.

---

## 🌟 Key Features

### 🔐 Patient Management & Authentication
- **User Registration** with email/password authentication
- **Secure Login** with bcrypt password hashing
- **Patient Profiles** with demographic information
- **NIC-based Identification** for easy access

### 🔍 Medical Report Processing
- **PDF Upload** via FastAPI endpoints
- **Google Document AI** integration for medical document OCR
- **Automatic Table & Entity Extraction**
- **Cloud Storage** with Google Cloud Storage
- **Database Storage** with Supabase for structured queries

### 🧹 Intelligent Document Normalization
- **Smart OCR Noise Removal** - Korean characters, symbols, artifacts
- **Auto-Detection** - Identifies report type automatically
- **Patient Information Extraction** - Name, age, gender parsing
- **Biomarker Standardization** - Maps lab names to medical terminology
- **Unit Normalization** - Standardizes measurement units
- **Reference Range Parsing** - Extracts and validates clinical ranges

### 📊 Supported Report Types
1. **Full Blood Count (FBC)** - WBC, RBC, Hemoglobin, Platelets, etc.
2. **Serum Lipid Profile** - Cholesterol, HDL, LDL, Triglycerides, etc.
3. **Fasting Plasma Glucose (FBS)** - Blood glucose monitoring

### 💾 Dual Storage Architecture
- **Cloud Storage (GCS)** - Organized by NIC for easy browsing
- **Database (Supabase)** - Structured data with foreign key relationships
- **Automatic Sync** - Reports and biomarkers saved to both

---

## 🏗️ Architecture

### Tech Stack
- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database with REST API
- **Google Document AI** - OCR and document understanding
- **Google Cloud Storage** - File storage
- **Bcrypt** - Password hashing
- **Pydantic** - Data validation
- **Python 3.9+** - Core language

### Database Schema

```sql
patients (
  id uuid PRIMARY KEY,
  full_name text NOT NULL,
  email text UNIQUE NOT NULL,
  phone text UNIQUE,
  password_hash text NOT NULL,
  nic text UNIQUE,
  created_at timestamptz
)

reports (
  id uuid PRIMARY KEY,
  patient_id uuid REFERENCES patients(id) ON DELETE CASCADE,
  file_id text NOT NULL,
  report_type text NOT NULL,
  sample_collected_at timestamptz,
  gcs_path text,
  created_at timestamptz
)

biomarkers (
  id uuid PRIMARY KEY,
  report_id uuid REFERENCES reports(id) ON DELETE CASCADE,
  name text NOT NULL,
  value numeric NOT NULL,
  unit text,
  ref_min numeric,
  ref_max numeric,
  flag text
)
```

---

## 📁 Project Structure

```
Healix_Backend/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── patient.py          # Patient auth & CRUD
│   │   └── reports.py          # Report upload & retrieval
│   ├── services/
│   │   ├── patientService.py   # Patient business logic
│   │   ├── reportService.py    # Report & biomarker storage
│   │   ├── ocr_service.py      # Document AI integration
│   │   ├── normalization_service.py    # Main normalizer
│   │   ├── fbs_normalization.py        # FBS-specific
│   │   ├── lipid_normalization.py      # Lipid-specific
│   │   └── upload_service.py   # GCS integration
│   ├── workers/
│   │   └── ocr_worker.py       # Background processing
│   ├── schemas/
│   │   ├── patient.py          # Patient data models
│   │   └── report.py           # Report data models
│   ├── config/
│   │   └── biomarker_config.py # Medical terminology
│   ├── utils/
│   │   └── auth.py             # Password hashing
│   ├── core/
│   │   ├── config.py           # App configuration
│   │   └── cloud.py            # GCS client setup
│   └── db/
│       └── supabase.py         # Database connection
├── docs/                       # Comprehensive documentation
├── requirements.txt
└── .env
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Healix_Backend

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Google Cloud
PROJECT_ID=your_project_id
BUCKET_NAME=your_bucket_name
DOC_AI_LOCATION=us
DOC_AI_PROCESSOR_ID=your_processor_id
GOOGLE_APPLICATION_CREDENTIALS=./key.json
```

Add `key.json` (Google Cloud service account key) to project root.

### 3. Database Setup

Run in Supabase SQL Editor:

```sql
-- Already provided in setup
-- Tables: patients, reports, biomarkers
```

### 4. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

API available at: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

---

## 📚 API Documentation

### Patient Endpoints

#### Register Patient
```http
POST /api/v1/patients/register
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "phone": "+1234567890",
  "nic": "199512345678"
}
```

#### Login
```http
POST /api/v1/patients/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

### Report Endpoints

#### Upload Report
```http
POST /api/v1/reports/upload
Content-Type: multipart/form-data

nic=199512345678
file=@blood_test.pdf
```

#### Get Normalized Report
```http
GET /api/v1/report/{nic}/{file_id}/normalized
```

#### List Patient Reports
```http
GET /api/v1/reports/nic/{nic}?source=database
```

#### Get Report with Biomarkers
```http
GET /api/v1/report/id/{report_id}/complete
```

**Full API Reference**: `docs/API_ENDPOINTS.md`

---

## 🔄 Processing Pipeline

```
1. Patient Registration
   ↓
2. Upload Report (with NIC)
   ↓
3. Look up patient_id from NIC
   ↓
4. Upload PDF to GCS: users/{nic}/reports/{file_id}.pdf
   ↓
5. Background Worker Starts
   ├─ OCR with Document AI
   ├─ Build raw JSON
   ├─ Normalize medical data
   ├─ Save to GCS: users/{nic}/processed/
   └─ Save to Supabase: reports + biomarkers tables
   ↓
6. Retrieve via API
   ├─ From GCS: JSON files
   └─ From Database: Structured queries
```

---

## 💡 Key Design Decisions

### NIC-Based Upload + UUID Database
- **Users provide NIC** (easy to remember)
- **GCS organized by NIC** (`users/199512345678/...`)
- **Database uses patient_id** (UUID foreign keys)
- **Best of both worlds**: User-friendly + Database integrity

### Dual Storage
- **Cloud Storage**: PDF files, OCR artifacts, debugging
- **Database**: Structured queries, relationships, analytics

### Security
- ✅ Bcrypt password hashing
- ✅ Password never in responses
- ✅ Email uniqueness validation
- ✅ Generic login error messages

---

## 📖 Documentation

- **`docs/PATIENT_SCHEMA_UPDATE.md`** - Authentication system
- **`docs/NIC_UPLOAD_SYSTEM.md`** - NIC-based upload flow
- **`docs/REPORT_PROCESSING_GUIDE.md`** - Complete pipeline
- **`docs/BIOMARKER_REF_RANGE_FIX.md`** - Reference range handling
- **`docs/NORMALIZATION.md`** - Normalization details
- **`docs/ADDING_NEW_REPORT_TYPES.md`** - Adding new reports

---

## 🧪 Example Workflow

```bash
# 1. Register patient
curl -X POST http://localhost:8000/api/v1/patients/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","email":"john@example.com","password":"Pass123","nic":"199512345678"}'

# 2. Upload report
curl -X POST http://localhost:8000/api/v1/reports/upload \
  -F "nic=199512345678" \
  -F "file=@blood_test.pdf"

# Returns: {"file_id": "abc-123-..."}

# 3. Wait 10-30 seconds for processing

# 4. Get reports from database
curl http://localhost:8000/api/v1/reports/nic/199512345678?source=database

# 5. Get complete report with biomarkers
curl http://localhost:8000/api/v1/report/id/{report_id}/complete
```

---

## 🎯 Current Features Summary

### ✅ Implemented
- Patient registration & authentication
- Secure password management
- PDF upload with NIC
- OCR processing (Document AI)
- Multi-report type support (FBC, Lipid, FBS)
- Automatic normalization
- Dual storage (GCS + Supabase)
- Reference range extraction
- Biomarker flagging
- RESTful API with FastAPI
- Complete documentation

### 🔄 In Progress
- Frontend integration
- Real-time notifications
- Batch processing

### 📋 Planned
- Additional report types (LFT, RFT, TFT, HbA1c)
- Trend analysis & visualization
- Multi-language support
- Mobile app
- Export features (PDF generation)

---

## 🤝 For Developers

### Adding New Report Types

See `docs/ADDING_NEW_REPORT_TYPES.md` for step-by-step guide.

### Testing

```bash
# Run development server
uvicorn app.main:app --reload --port 8000

# Test in browser
http://localhost:8000/docs
```

### Code Style
- Python 3.9+
- Type hints for all functions
- Docstrings for public APIs
- Pydantic for validation

---

## 📊 Sample Output

### Complete Report Response
```json
{
  "status": "success",
  "data": {
    "report": {
      "id": "550e8400-...",
      "patient_id": "660f9500-...",
      "file_id": "abc-123-...",
      "report_type": "Full Blood Count",
      "sample_collected_at": "2026-02-07T10:30:00Z",
      "gcs_path": "gs://bucket/users/199512345678/reports/abc-123.pdf",
      "created_at": "2026-02-07T14:00:00Z"
    },
    "biomarkers": [
      {
        "id": "bio-uuid-1",
        "name": "Hemoglobin",
        "value": 14.5,
        "unit": "g/dL",
        "ref_min": 12.0,
        "ref_max": 16.0,
        "flag": "NORMAL"
      },
      {
        "id": "bio-uuid-2",
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

---

## 📞 Support

For questions or issues, refer to the comprehensive documentation in `/docs`.

---

## 📜 License

Proprietary - All rights reserved

---

**Healix Backend** - Transforming Sri Lankan healthcare, one report at a time. 🏥
