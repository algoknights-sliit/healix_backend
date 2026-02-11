# OCR Pipeline Architecture Documentation

## Overview
This document provides a comprehensive explanation of how the Healix OCR pipeline works, including detailed descriptions of each Python file, their interconnections, and the complete step-by-step data flow.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [File Structure & Responsibilities](#file-structure--responsibilities)
3. [Complete OCR Pipeline Flow](#complete-ocr-pipeline-flow)
4. [Detailed File Descriptions](#detailed-file-descriptions)
5. [Interconnections & Dependencies](#interconnections--dependencies)
6. [Data Flow Diagram](#data-flow-diagram)

---

## Architecture Overview

The Healix OCR pipeline is designed to process medical reports (PDFs) through a multi-stage process:

```
Upload PDF → OCR Processing → Table/Entity Extraction → Normalization → Storage → Retrieval
```

### Key Technologies
- **FastAPI**: REST API framework
- **Google Document AI**: OCR processing
- **Google Cloud Storage**: PDF and JSON storage
- **Background Tasks**: Async processing

### Supported Report Types
1. **Full Blood Count (FBC)** - Default
2. **Serum Lipid Profile** - Auto-detected
3. **Fasting Plasma Glucose (FBS)** - Auto-detected

---

## File Structure & Responsibilities

```
app/
├── main.py                              # FastAPI application entry point
├── api/
│   └── v1/
│       └── reports.py                   # API endpoints for report operations
├── workers/
│   └── ocr_worker.py                    # Background worker orchestrator
├── services/
│   ├── ocr_service.py                   # Google Document AI integration
│   ├── upload_service.py                # Cloud storage operations
│   ├── nlp_service.py                   # Raw JSON builder
│   ├── normalization_service.py         # Main normalization service
│   ├── lipid_normalization.py           # Lipid profile specific logic
│   └── fbs_normalization.py             # FBS specific logic
├── utils/
│   └── text_utils.py                    # OCR data extraction utilities
├── core/
│   ├── config.py                        # Configuration & environment
│   └── cloud.py                         # Cloud client initialization
└── config/
    └── biomarker_config.py              # Biomarker mappings & rules
```

---

## Complete OCR Pipeline Flow

### Step-by-Step Process

#### **Phase 1: Upload & Storage**
1. User uploads PDF via `/api/v1/ocr/upload` endpoint
2. API receives the file and patient NIC
3. File is saved temporarily to disk
4. `upload_service.upload_pdf_to_bucket()` uploads to Google Cloud Storage
5. Returns a unique `file_id` and `gcs_uri`
6. Background task is scheduled for OCR processing
7. Temporary file is deleted

#### **Phase 2: Background OCR Processing**
8. `process_document_worker()` starts in background
9. Calls `ocr_service.process_with_document_ai(gcs_uri)`
10. Google Document AI processes the PDF and returns structured document
11. `text_utils.extract_tables()` extracts table data from OCR result
12. `text_utils.extract_entities()` extracts entities from OCR result
13. `nlp_service.build_report_json()` creates raw JSON structure

#### **Phase 3: Normalization**
14. `normalization_service.normalize_report()` begins normalization
15. Detects report type using `_detect_report_type()`
16. Routes to appropriate normalizer:
    - FBC → `_normalize_fbc_report()`
    - Lipid → `_normalize_lipid_profile()`
    - FBS → `_normalize_fbs_report()`
17. Extracts patient information
18. Extracts report metadata
19. Normalizes biomarkers from tables
20. Returns structured normalized JSON

#### **Phase 4: Storage**
21. Both raw and normalized JSONs are stored to Cloud Storage
22. Raw JSON: `users/{nic}/processed/{file_id}.json`
23. Normalized JSON: `users/{nic}/processed/{file_id}_normalized.json`

#### **Phase 5: Retrieval**
24. Client polls `/api/v1/ocr/report/{nic}/{file_id}/normalized`
25. `upload_service.get_normalized_json()` retrieves from cloud
26. Returns structured medical report data

---

## Detailed File Descriptions

### 1. **app/main.py**
**Purpose**: FastAPI application initialization and configuration

**Key Responsibilities**:
- Creates FastAPI app instance
- Configures CORS middleware for cross-origin requests
- Includes API routers
- Sets up API metadata (title, description, version)

**Code Highlights**:
```python
app = FastAPI(title="Healix Backend API", ...)
app.add_middleware(CORSMiddleware, ...)
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
```

**Connections**:
- Imports and includes `reports.py` router
- Entry point for the entire application

---

### 2. **app/api/v1/reports.py**
**Purpose**: REST API endpoints for medical report operations

**Key Endpoints**:
1. `POST /upload` - Upload medical report PDF
2. `GET /report/{nic}/{file_id}/normalized` - Get normalized report
3. `GET /report/{nic}/{file_id}/raw` - Get raw OCR data
4. `GET /reports/{nic}` - List all reports for a patient

**Key Functions**:
- `upload_report()`: Handles file upload, temporary storage, cloud upload, and background task scheduling
- `get_normalized_report()`: Retrieves normalized JSON from storage
- `get_raw_report()`: Retrieves raw OCR JSON for debugging
- `list_reports()`: Lists all processed reports for a patient

**Dependencies**:
- `upload_service` - For cloud storage operations
- `ocr_worker` - For background processing
- `FastAPI BackgroundTasks` - For async processing

**Data Flow**:
```
Client Request → Endpoint → upload_service → Background Task → Response
```

---

### 3. **app/workers/ocr_worker.py**
**Purpose**: Orchestrates the entire OCR and normalization pipeline

**Key Function**: `process_document_worker(gcs_uri, nic, file_id)`

**Workflow**:
1. Calls Document AI for OCR processing
2. Extracts tables and entities from OCR result
3. Builds raw JSON structure
4. Normalizes the data based on report type
5. Stores both raw and normalized versions

**Dependencies**:
- `ocr_service.process_with_document_ai()` - OCR processing
- `upload_service.store_json()` - Storage
- `nlp_service.build_report_json()` - JSON building
- `normalization_service.normalize_fbc_report()` - Normalization
- `text_utils` - Table/entity extraction

**Critical Note**: This is the **central coordinator** that chains all processing steps together.

---

### 4. **app/services/ocr_service.py**
**Purpose**: Google Document AI integration for OCR processing

**Key Function**: `process_with_document_ai(gcs_uri)`

**What It Does**:
1. Creates a Document AI processor path using project and processor IDs
2. Builds a `ProcessRequest` with GCS document URI
3. Calls Document AI API to process the PDF
4. Returns the processed `document` object containing:
   - Full text extraction
   - Page information
   - Tables
   - Entities
   - Layout information

**Dependencies**:
- `google.cloud.documentai` - Google's Document AI client
- `cloud.py` - Document AI client instance
- `config.py` - Configuration values

**Output Structure**:
```
document (DocumentAI Document object)
├── text: str (full OCR text)
├── pages: [Page objects]
│   └── tables: [Table objects]
│       └── body_rows: [Row objects]
│           └── cells: [Cell objects]
└── entities: [Entity objects]
```

---

### 5. **app/services/upload_service.py**
**Purpose**: All Google Cloud Storage operations

**Key Functions**:

1. **`upload_pdf_to_bucket(local_pdf_path, user_nic)`**:
   - Generates unique file_id using UUID
   - Constructs GCS path: `users/{nic}/reports/{file_id}.pdf`
   - Uploads PDF to cloud storage
   - Returns file_id and gcs_uri

2. **`store_json(user_nic, file_id, data)`**:
   - Stores JSON data to cloud
   - Path: `users/{nic}/processed/{file_id}.json`
   - Pretty-prints JSON with indentation

3. **`get_normalized_json(user_nic, file_id)`**:
   - Retrieves normalized report from cloud
   - Path: `users/{nic}/processed/{file_id}_normalized.json`
   - Raises FileNotFoundError if not exists

4. **`get_raw_json(user_nic, file_id)`**:
   - Retrieves raw OCR JSON for debugging
   - Path: `users/{nic}/processed/{file_id}.json`

5. **`list_user_reports(user_nic)`**:
   - Lists all processed reports for a patient
   - Returns metadata including file_id, type, creation time, size

**Storage Structure**:
```
GCS Bucket
└── users/
    └── {NIC}/
        ├── reports/
        │   └── {file_id}.pdf
        └── processed/
            ├── {file_id}.json (raw)
            └── {file_id}_normalized.json
```

---

### 6. **app/services/nlp_service.py**
**Purpose**: Build raw JSON structure from OCR data

**Key Function**: `build_report_json(document, tables, entities)`

**What It Does**:
- Creates a simple JSON structure containing:
  - `raw_text`: Full OCR text from document
  - `tables`: Extracted table data
  - `entities`: Extracted entities
  - `page_count`: Number of pages in document

**Output Example**:
```json
{
  "raw_text": "PATIENT NAME: John Doe...",
  "tables": [[["Test", "Value", "Unit"], ...]],
  "entities": [{"type": "date", "value": "2025-01-01", ...}],
  "page_count": 2
}
```

This raw JSON is stored for debugging and can be retrieved if needed.

---

### 7. **app/services/normalization_service.py**
**Purpose**: Main normalization service - converts raw OCR to structured medical JSON

**Architecture**: Report type auto-detection with routing to specialized normalizers

**Key Functions**:

1. **`normalize_report(raw_data)`** (Main Entry Point):
   - Auto-detects report type from raw text
   - Routes to appropriate normalizer
   - Returns structured JSON

2. **`_detect_report_type(raw_text)`**:
   - Searches for keywords in text (FBS, Lipid Profile, FBC)
   - Uses `REPORT_TYPE_KEYWORDS` from config
   - Defaults to "Full Blood Count" if unclear

3. **`_normalize_fbc_report(raw_data)`**:
   - Extracts patient info using regex patterns
   - Extracts report metadata (dates)
   - Normalizes FBC biomarkers from tables
   - Returns structured FBC report

4. **`_normalize_lipid_profile(raw_data)`**:
   - Delegates to `lipid_normalization.py`
   - Handles lipid-specific patient info (UHID, reference numbers)
   - Processes lipid biomarkers with flags (H/L)

5. **`_normalize_fbs_report(raw_data)`**:
   - Delegates to `fbs_normalization.py`
   - Handles FBS-specific parsing
   - Calculates flags based on reference ranges

**Helper Functions**:

- **`_extract_patient_info(raw_text)`**: Regex-based extraction of:
  - Patient name
  - Age and gender
  - Referring doctor
  - Service reference number

- **`_extract_report_metadata(raw_text)`**: Extracts:
  - Sample collection date/time
  - Report printed date/time
  - Report type

- **`_normalize_fbc_biomarkers(tables)`**: 
  - Iterates through OCR tables
  - Maps test names to standard biomarker names
  - Cleans numeric values (removes OCR noise)
  - Normalizes units
  - Parses reference ranges
  - Returns array of biomarker objects

- **`_get_standard_biomarker_name(test_name)`**:
  - Maps lab-specific test names to standardized names
  - Uses `BIOMARKER_NAME_MAPPING` from config
  - Handles exact, case-insensitive, and partial matches

- **`_normalize_unit(unit_str)`**:
  - Removes OCR noise
  - Maps to standardized units using `UNIT_MAPPING`
  - Examples: "Per Cumm" → "per cu mm", "g/dl" → "g/dL"

- **`_clean_numeric_value(value_str)`**:
  - Removes OCR noise patterns
  - Strips non-numeric characters
  - Converts to float
  - Returns None if invalid

- **`_parse_reference_range(range_str)`**:
  - Extracts min and max values from ranges
  - Handles formats: "4000 - 11000", "11.0\n16.5"
  - Returns [min, max] array

- **`_parse_datetime(date_str, time_str)`**:
  - Converts DD/MM/YYYY HH:MM AM/PM to ISO-8601
  - Example: "03/06/2025 09:10 AM" → "2025-06-03T09:10:00"

**Output Structure**:
```json
{
  "patient": {
    "name": "John Doe",
    "age_years": 62,
    "gender": "Male",
    "ref_doctor": "Dr. Smith",
    "service_ref_no": "12345"
  },
  "report": {
    "type": "Full Blood Count",
    "sample_collected_at": "2025-06-03T09:10:00",
    "printed_at": "2025-06-03T18:43:00"
  },
  "biomarkers": [
    {
      "name": "WBC",
      "value": 7500,
      "unit": "per cu mm",
      "absolute": null,
      "ref_range": [4000, 11000]
    },
    ...
  ]
}
```

---

### 8. **app/services/lipid_normalization.py**
**Purpose**: Specialized normalization logic for Serum Lipid Profile reports

**Why Separate?**:
- Different patient info fields (UHID, different date formats)
- Different biomarkers (cholesterol, triglycerides, ratios)
- Has flags (High/Low) instead of just reference ranges
- 24-hour time format instead of AM/PM

**Key Functions**:

1. **`extract_lipid_patient_info(raw_text)`**:
   - Similar to FBC but extracts:
     - UHID (hospital ID)
     - Reference numbers (e.g., "AHH2006215 / AHH2011800")

2. **`extract_lipid_report_metadata(raw_text)`**:
   - Extracts sample type (e.g., "SERUM")
   - Parses dates in 24-hour format
   - Returns sample_collected_at and reported_at

3. **`normalize_lipid_biomarkers(tables)`**:
   - Maps lipid test names using `LIPID_PROFILE_BIOMARKER_MAPPING`
   - Extracts H/L flags from reference range column
   - Handles ratios (no units)
   - Returns biomarkers with flag field

4. **`get_standard_lipid_name(test_name)`**:
   - Maps variants like "CHOLESTEROL-H.D.L." → "HDL Cholesterol"

5. **`extract_flag(ref_range_str)`**:
   - Extracts "H" or "L" indicators
   - Maps to "High" or "Low"
   - Returns (flag, cleaned_range)

6. **`parse_datetime_24h(date_str, time_str)`**:
   - Parses 24-hour format: "03/06/2025 14:30"

**Lipid Biomarkers**:
- Total Cholesterol
- Triglycerides
- HDL Cholesterol
- Non-HDL Cholesterol
- LDL Cholesterol
- VLDL Cholesterol
- Cholesterol/HDL Ratio
- LDL/HDL Ratio

---

### 9. **app/services/fbs_normalization.py**
**Purpose**: Specialized normalization for Fasting Plasma Glucose reports

**Challenges**:
- Single biomarker (glucose)
- Complex result cell structure (value, unit, and range in one cell)
- Reference range may be in comments section
- Need to calculate flags based on medical guidelines

**Key Functions**:

1. **`extract_fbs_patient_info(raw_text)`**:
   - Similar to lipid extraction
   - Handles OCR variations in field names

2. **`extract_fbs_report_metadata(raw_text)`**:
   - Reuses lipid date parsing logic
   - Sets report type to "Fasting Plasma Glucose"

3. **`normalize_fbs_biomarkers(tables, raw_text)`**:
   - Extracts FBS value from complex table cells
   - Parses result cell containing value + unit + range
   - Falls back to comment section for reference range
   - Calculates flag based on medical guidelines

4. **`get_standard_fbs_name(test_name)`**:
   - Maps variations: "FASTING\nLASMA GLUCOSE" → "Fasting Plasma Glucose"

5. **`parse_fbs_result_cell(result_cell, raw_text)`**:
   - Parses complex cells like "102.9\nmg/d\n0.\n-\n99."
   - Extracts value (102.9)
   - Extracts unit (mg/dL)
   - Extracts reference range ([70, 99])
   - Falls back to comments if range invalid

6. **`extract_ref_range_from_cell(cell_text)`**:
   - Extracts reference range from table cell
   - Validates range makes sense (min < max, max > 50)

7. **`calculate_fbs_flag(value, ref_range)`**:
   - Applies medical guidelines:
     - < 70 mg/dL → "Low" (Hypoglycemia)
     - 70-99 mg/dL → None (Normal)
     - > 99 mg/dL → "High" (Prediabetes/Diabetes)

---

### 10. **app/utils/text_utils.py**
**Purpose**: Utility functions for extracting data from Document AI objects

**Key Functions**:

1. **`get_text(doc_element, document_text)`**:
   - Extracts text from a document element using text anchors
   - Handles text segmentation
   - Returns clean text string

2. **`extract_tables(document)`**:
   - Iterates through all pages in document
   - Extracts tables from each page
   - Converts table structure to nested arrays:
     - Table → Rows → Cells → Text
   - Returns list of tables

3. **`extract_entities(document)`**:
   - Extracts entities detected by Document AI
   - Returns array of entity objects with:
     - type: Entity type (e.g., "date", "person")
     - value: Entity text
     - confidence: OCR confidence score

**Output Format**:
```python
# Tables
[
  [  # Table 1
    ["Test Name", "Value", "Unit"],  # Row 1
    ["WBC", "7500", "per cu mm"],    # Row 2
    ...
  ],
  ...
]

# Entities
[
  {"type": "date", "value": "03/06/2025", "confidence": 0.98},
  ...
]
```

---

### 11. **app/core/config.py**
**Purpose**: Environment configuration and credentials setup

**Key Elements**:

1. **Environment Variables**:
   - `PROJECT_ID`: Google Cloud project ID
   - `GCS_BUCKET`: Cloud Storage bucket name
   - `DOCAI_LOCATION`: Document AI region (default: "us")
   - `DOCAI_PROCESSOR_ID`: Document AI processor ID

2. **Credentials**:
   - Sets `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Points to `key.json` in project root

**Usage**: Imported by all cloud-related services

---

### 12. **app/core/cloud.py**
**Purpose**: Initialize and provide Google Cloud clients

**Key Elements**:

1. **`storage_client`**: Google Cloud Storage client instance
2. **`docai_client`**: Document AI client with regional endpoint
3. **`get_bucket(bucket_name)`**: Helper to get bucket instance

**Why Separate?**:
- Singleton pattern - clients initialized once
- Shared across all services
- Centralized cloud connectivity

---

### 13. **app/config/biomarker_config.py**
**Purpose**: Centralized configuration for biomarker mappings, units, and OCR cleanup

**Key Configurations**:

1. **FBC_BIOMARKER_MAPPING**:
   - Maps lab test names to standard biomarker names
   - Example: "W.B.C." → "WBC", "NEUTROPHILS" → "Neutrophils"

2. **LIPID_PROFILE_BIOMARKER_MAPPING**:
   - Maps lipid test names
   - Example: "CHOLESTEROL-H.D.L." → "HDL Cholesterol"

3. **FBS_BIOMARKER_MAPPING**:
   - Maps FBS variants
   - Handles OCR noise: "FASTING\nLASMA GLUCOSE" → "Fasting Plasma Glucose"

4. **UNIT_MAPPING**:
   - Standardizes units across reports
   - Examples:
     - "Per Cumm" → "per cu mm"
     - "g/dl" → "g/dL"
     - "mg/dl" → "mg/dL"

5. **FLAG_MAPPING**:
   - Maps flag codes to readable text
   - "H" → "High", "L" → "Low"

6. **REPORT_TYPE_KEYWORDS**:
   - Keywords for auto-detecting report types
   - Order matters: more specific patterns first

7. **OCR_NOISE_PATTERNS**:
   - Common OCR artifacts to remove
   - Examples: Korean characters, "O1O", "olo"

8. **IGNORE_KEYWORDS**:
   - Non-medical content to skip
   - Hospital names, certifications, etc.

**Why Important?**:
- Single source of truth for all mappings
- Easy to extend for new report types
- Maintains consistency across normalizers

---

## Interconnections & Dependencies

### Dependency Graph

```
main.py
  └── reports.py
        ├── upload_service.py
        │     └── cloud.py
        │           └── config.py
        └── ocr_worker.py
              ├── ocr_service.py
              │     ├── cloud.py
              │     └── config.py
              ├── upload_service.py
              ├── nlp_service.py
              ├── text_utils.py
              └── normalization_service.py
                    ├── biomarker_config.py
                    ├── lipid_normalization.py
                    │     └── biomarker_config.py
                    └── fbs_normalization.py
                          ├── biomarker_config.py
                          └── lipid_normalization.py (for datetime parsing)
```

### Component Interactions

#### **Upload Flow**:
```
User → reports.py → upload_service.py → Google Cloud Storage
                 → BackgroundTasks → ocr_worker.py
```

#### **OCR Processing Flow**:
```
ocr_worker.py → ocr_service.py → Google Document AI → Document Object
              → text_utils.py → Tables + Entities
              → nlp_service.py → Raw JSON
```

#### **Normalization Flow**:
```
ocr_worker.py → normalization_service.py → detect_report_type()
                                         ├→ _normalize_fbc_report()
                                         ├→ lipid_normalization.py
                                         └→ fbs_normalization.py
```

#### **Storage Flow**:
```
ocr_worker.py → upload_service.py → Google Cloud Storage
                                   ├ Raw JSON
                                   └ Normalized JSON
```

#### **Retrieval Flow**:
```
User → reports.py → upload_service.py → Google Cloud Storage → JSON Response
```

---

## Data Flow Diagram

### Complete End-to-End Flow

```
┌─────────────┐
│   Client    │
│  (Frontend) │
└──────┬──────┘
       │ POST /upload (PDF + NIC)
       ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI (main.py)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         API Router (reports.py)                      │   │
│  │  - Receives PDF file                                 │   │
│  │  - Saves to temp file                                │   │
│  └───────────────────┬──────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│          Upload Service (upload_service.py)                │
│  - Generates UUID                                          │
│  - Uploads PDF to GCS                                      │
│  - Returns file_id + gcs_uri                               │
└────────────────────┬───────────────────────────────────────┘
                     │
       ┌─────────────┴─────────────┐
       │                           │
       ▼                           ▼
┌──────────────┐         ┌─────────────────────┐
│  Background  │         │    Return Response  │
│    Task      │         │  { file_id, status }│
└──────┬───────┘         └─────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│            OCR Worker (ocr_worker.py)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Step 1: OCR Processing (ocr_service.py)             │  │
│  │   - Calls Google Document AI                         │  │
│  │   - Returns document object                          │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       ▼                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Step 2: Extract Data (text_utils.py)                │  │
│  │   - extract_tables(document)                         │  │
│  │   - extract_entities(document)                       │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       ▼                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Step 3: Build Raw JSON (nlp_service.py)             │  │
│  │   - Creates structure with text, tables, entities    │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       ▼                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Step 4: Normalize (normalization_service.py)        │  │
│  │   ┌───────────────────────────────────────────────┐   │  │
│  │   │ Detect Report Type                            │   │  │
│  │   └──────────┬─────────────────────────────────────┘   │  │
│  │              │                                         │  │
│  │   ┌──────────┴──────────┬──────────────┐              │  │
│  │   ▼                     ▼              ▼              │  │
│  │ ┌─────┐          ┌──────────┐    ┌─────────┐         │  │
│  │ │ FBC │          │  Lipid   │    │   FBS   │         │  │
│  │ └──┬──┘          └────┬─────┘    └────┬────┘         │  │
│  │    └──────────────────┴───────────────┘              │  │
│  │                       │                               │  │
│  │                       ▼                               │  │
│  │   ┌──────────────────────────────────────────────┐    │  │
│  │   │ Normalized JSON                              │    │  │
│  │   │ {patient, report, biomarkers}                │    │  │
│  │   └──────────────────┬───────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                         ▼                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Step 5: Store JSONs (upload_service.py)             │  │
│  │   - Store raw JSON                                   │  │
│  │   - Store normalized JSON                            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Cloud Storage                           │
│  users/{nic}/reports/{file_id}.pdf                          │
│  users/{nic}/processed/{file_id}.json                       │
│  users/{nic}/processed/{file_id}_normalized.json            │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ GET /report/{nic}/{file_id}/normalized
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Client Retrieval                           │
│  reports.py → upload_service.py → GCS → JSON Response       │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Patterns

### 1. **Separation of Concerns**
Each file has a single, well-defined responsibility:
- API layer (reports.py) handles HTTP
- Services handle business logic
- Utils provide reusable functions
- Config centralizes configuration

### 2. **Strategy Pattern**
Normalization service uses strategy pattern:
- Detects report type
- Routes to appropriate normalizer
- Each normalizer implements the same interface

### 3. **Background Processing**
- Upload returns immediately
- Heavy OCR processing happens asynchronously
- Client polls for results

### 4. **Configuration-Driven**
- All biomarker mappings in config
- Easy to extend for new report types
- No hardcoded values in business logic

### 5. **Error Handling**
- FileNotFoundError for missing reports
- Graceful fallbacks (e.g., default report type)
- Try/except in parsing functions

---

## Adding New Report Types

To add a new report type (e.g., "Liver Function Test"):

### Step 1: Update Configuration
**File**: `app/config/biomarker_config.py`

```python
# Add biomarker mapping
LFT_BIOMARKER_MAPPING = {
    "SGOT": "AST",
    "SGPT": "ALT",
    # ...
}

# Add keywords for detection
REPORT_TYPE_KEYWORDS = {
    "Liver Function Test": ["LIVER FUNCTION", "LFT", "HEPATIC PANEL"],
    # ... existing types
}
```

### Step 2: Create Normalizer
**File**: `app/services/lft_normalization.py`

```python
def normalize_lft_biomarkers(tables):
    # Implementation similar to lipid_normalization.py
    pass

def extract_lft_patient_info(raw_text):
    # Implementation
    pass

def extract_lft_report_metadata(raw_text):
    # Implementation
    pass
```

### Step 3: Update Main Normalizer
**File**: `app/services/normalization_service.py`

```python
def normalize_report(raw_data):
    report_type = _detect_report_type(raw_text)
    
    if report_type == "Liver Function Test":
        return _normalize_lft_report(raw_data)
    # ... existing conditions

def _normalize_lft_report(raw_data):
    from app.services.lft_normalization import (
        extract_lft_patient_info,
        extract_lft_report_metadata,
        normalize_lft_biomarkers
    )
    # Implementation
```

### Step 4: Test
Add tests in `tests/test_lft_normalization.py`

---

## Common OCR Challenges & Solutions

### Challenge 1: OCR Noise
**Problem**: OCR generates artifacts like "O1O", Korean characters, etc.

**Solution**:
- Defined in `OCR_NOISE_PATTERNS`
- Removed by all cleaning functions
- Centralized in config for consistency

### Challenge 2: Inconsistent Test Names
**Problem**: Labs use different names for same biomarker

**Solution**:
- Comprehensive mapping dictionaries
- Exact, case-insensitive, and partial matching
- Extensible configuration

### Challenge 3: Complex Table Structures
**Problem**: Merged cells, multi-line text, irregular layouts

**Solution**:
- Document AI extracts structured tables
- Robust parsing with multiple strategies
- Fallback to raw text for reference ranges

### Challenge 4: Date/Time Formats
**Problem**: Multiple formats (AM/PM vs 24-hour)

**Solution**:
- Separate parsing functions for each format
- Regex patterns for flexibility
- ISO-8601 output for consistency

### Challenge 5: Report Type Detection
**Problem**: Needs to determine report type automatically

**Solution**:
- Keyword-based detection
- Priority ordering (specific first)
- Fallback to FBC as default

---

## Performance Considerations

### 1. **Background Processing**
- OCR is slow (5-10 seconds)
- Background tasks prevent blocking API
- Client uses polling for results

### 2. **Cloud Storage**
- PDFs stored in GCS for Document AI
- JSON storage for persistence
- No local file storage (except temp)

### 3. **Caching Opportunities**
- Could cache Document AI responses
- Could cache normalized results
- Trade-off: storage vs processing time

### 4. **Batch Processing**
- Currently processes one document at a time
- Could implement batch upload
- Would require job queue system

---

## Security Considerations

### 1. **Authentication**
- Current implementation has no auth
- Production should add:
  - API key authentication
  - OAuth2/JWT tokens
  - Rate limiting

### 2. **Data Privacy**
- Medical documents contain PHI
- Should implement:
  - Encryption at rest (GCS)
  - Encryption in transit (HTTPS)
  - Access logging
  - Data retention policies

### 3. **Input Validation**
- Validate NIC format
- Check file types (PDF only)
- Limit file sizes
- Sanitize file names

---

## Monitoring & Debugging

### Debug Endpoints

1. **Raw OCR Data**: `/report/{nic}/{file_id}/raw`
   - See what Document AI extracted
   - Check table structure
   - Verify entity extraction

2. **Normalized Data**: `/report/{nic}/{file_id}/normalized`
   - See final output
   - Verify biomarker values
   - Check patient info extraction

### Common Issues

1. **Report not found (404)**
   - Processing may still be running
   - Check background task status
   - Verify file_id is correct

2. **Missing biomarkers**
   - Check raw JSON for table structure
   - Verify test name mapping exists
   - Check table parsing logic

3. **Incorrect values**
   - Check OCR noise patterns
   - Verify numeric cleaning logic
   - Review reference range parsing

4. **Wrong report type detected**
   - Check REPORT_TYPE_KEYWORDS
   - Adjust keyword priority
   - Verify raw text contains expected keywords

---

## Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies (Document AI, GCS)
- Focus on parsing and normalization logic

### Integration Tests
- Test complete pipeline end-to-end
- Use sample PDFs for each report type
- Verify correct JSON output

### Test Files Location
```
tests/
├── test_api.py                    # API endpoint tests
├── test_normalization.py          # FBC normalization tests
├── test_lipid_normalization.py    # Lipid normalization tests
└── test_fbs_normalization.py      # FBS normalization tests
```

---

## Conclusion

The Healix OCR pipeline is a sophisticated multi-stage system that:

1. **Accepts** medical report PDFs via REST API
2. **Processes** them using Google Document AI
3. **Extracts** structured data (tables, entities)
4. **Normalizes** to clean, standardized medical JSON
5. **Stores** both raw and normalized versions
6. **Provides** easy retrieval for applications

The modular architecture allows for:
- Easy extension to new report types
- Clear separation of concerns
- Maintainable and testable code
- Robust error handling
- Scalable cloud-based processing

Understanding this architecture enables developers to:
- Debug issues effectively
- Add new features confidently
- Optimize performance
- Maintain code quality
