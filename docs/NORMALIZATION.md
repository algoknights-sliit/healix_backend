# Medical Document Normalization Engine

## Overview

This module provides a comprehensive medical document normalization engine that converts noisy OCR output from Google Document AI into clean, structured, clinically meaningful JSON for Full Blood Count (FBC) reports.

## Architecture

### Components

1. **`app/config/biomarker_config.py`** - Configuration file containing:
   - Biomarker name mappings (lab terms → standardized names)
   - Unit normalization rules
   - OCR noise patterns
   
2. **`app/services/normalization_service.py`** - Core normalization service with functions to:
   - Extract patient demographics
   - Parse dates/times to ISO-8601 format
   - Normalize biomarker names and values
   - Clean OCR noise
   - Parse reference ranges

3. **`app/workers/ocr_worker.py`** - Updated to integrate normalization into the OCR pipeline

## How It Works

### Pipeline Flow

```
PDF Upload → Document AI OCR → Raw JSON → Normalization → Clean JSON
```

1. **OCR Extraction**: Google Document AI extracts raw text, tables, and entities
2. **Raw JSON**: Data is assembled into a raw JSON structure
3. **Normalization**: The normalization service processes the raw JSON:
   - Extracts patient information from unstructured text
   - Parses dates and converts to ISO-8601
   - Maps lab test names to standard biomarker names
   - Cleans OCR noise (Korean characters, symbols, merged values)
   - Normalizes units (e.g., "Per Cumm" → "per cu mm")
   - Separates percentage values from absolute counts
   - Parses reference ranges into numeric arrays
4. **Storage**: Both raw and normalized JSON are stored to Cloud Storage

### Input Format

```json
{
  "raw_text": "Full unstructured OCR text...",
  "tables": [
    [
      ["TEST NAME", "VALUE", "UNIT", "ABS COUNT", "REF RANGE"],
      ["W.B.C.", "7970", "Per Cumm", "", "4000\n-\n11000"]
    ]
  ],
  "entities": [...],
  "page_count": 1
}
```

### Output Format

```json
{
  "patient": {
    "name": "MR S KUMAR",
    "age_years": 62,
    "gender": "Male",
    "ref_doctor": "OPD",
    "service_ref_no": "CHL000735039"
  },
  "report": {
    "type": "Full Blood Count",
    "sample_collected_at": "2025-06-03T09:10:00",
    "printed_at": "2025-06-03T18:43:00"
  },
  "biomarkers": [
    {
      "name": "WBC",
      "value": 7970.0,
      "unit": "per cu mm",
      "absolute": null,
      "ref_range": [4000.0, 11000.0]
    },
    {
      "name": "Neutrophils",
      "value": 79.0,
      "unit": "%",
      "absolute": 6296.3,
      "ref_range": null
    }
    // ... more biomarkers
  ]
}
```

## Normalization Rules

### Patient Information Extraction

- **Name**: Extracted from "PATIENT NAME:" field
- **Age**: Extracted from pattern "AGE NN Y/O"
- **Gender**: Extracted from M/F indicator after age
- **Ref Doctor**: Extracted from "REF.DOCTOR:" field
- **Service Ref**: Extracted from "SERVICE REF.NO:" field

### Date/Time Parsing

- Input format: `DD/MM/YYYY HH:MM AM/PM`
- Output format: ISO-8601 `YYYY-MM-DDTHH:MM:SS`
- Sample collected and printed dates are both extracted

### Biomarker Name Mapping

Standard names used:
- **WBC**: White Blood Cells
- **Neutrophils, Lymphocytes, Eosinophils, Monocytes, Basophils**: Differential count
- **Hemoglobin**: Hemoglobin concentration
- **RBC**: Red Blood Cells
- **MCV, MCH, MCHC**: Red cell indices
- **PCV**: Packed Cell Volume (Hematocrit)
- **Platelets**: Platelet count

### Unit Normalization

| OCR Input | Normalized Output |
|-----------|-------------------|
| Per Cumm, Per Cu mm | per cu mm |
| g/dl, gm/dl | g/dL |
| Pg, PG | pg |
| fL, fl | fL |
| 10^6 /UL | 10^6/uL |

Differential counts automatically get "%" unit when missing.

### OCR Noise Removal

Common noise patterns removed:
- `응` (Korean character)
- `olo` (OCR artifact)
- Leading zeros (e.g., "02" → 2.0)
- Strange symbols and merged text

### Reference Range Parsing

- Extracts two numbers from reference range field
- Handles formats: "min - max", "min\nmax"
- Returns as `[min, max]` array
- Returns `null` if not parseable

## Usage

### In Your API

The normalization is automatically integrated into the OCR worker:

```python
# When a PDF is uploaded
process_document_worker(gcs_uri, nic, file_id)

# This will:
# 1. Extract OCR data
# 2. Build raw JSON
# 3. Normalize to clean JSON
# 4. Store both versions:
#    - {file_id}.json (raw)
#    - {file_id}_normalized.json (clean)
```

### Direct Usage

```python
from app.services.normalization_service import normalize_fbc_report

raw_data = {
    "raw_text": "...",
    "tables": [...],
    "entities": [...],
    "page_count": 1
}

clean_data = normalize_fbc_report(raw_data)
```

### Testing

Run the test script to verify normalization:

```bash
python tests/simple_test.py
```

Output will be saved to `tests/normalized_output.json`.

## Adding New Report Types

Currently, only FBC reports are supported. To add support for other report types (e.g., Lipid Panel, Liver Function Tests):

1. **Create new mapping in `biomarker_config.py`**:
   ```python
   LIPID_PANEL_MAPPING = {
       "TOTAL CHOLESTEROL": "Total Cholesterol",
       "LDL": "LDL Cholesterol",
       # ...
   }
   ```

2. **Add report type detection in `normalization_service.py`**:
   ```python
   def _detect_report_type(raw_text: str) -> str:
       if "FULL BLOOD COUNT" in raw_text.upper():
           return "Full Blood Count"
       elif "LIPID PROFILE" in raw_text.upper():
           return "Lipid Panel"
       # ...
   ```

3. **Create type-specific normalization function**:
   ```python
   def normalize_lipid_panel(raw_data: dict) -> dict:
       # Similar to normalize_fbc_report but with lipid-specific logic
   ```

## Files Modified/Created

### New Files
- ✅ `app/config/__init__.py`
- ✅ `app/config/biomarker_config.py`
- ✅ `app/services/normalization_service.py`
- ✅ `tests/test_normalization.py`
- ✅ `tests/simple_test.py`

### Modified Files
- ✅ `app/workers/ocr_worker.py` - Added normalization step

## Benefits

1. **Clean Data**: Removes OCR noise and standardizes terminology
2. **Long-term Storage**: ISO dates and numeric values enable trend analysis
3. **Interoperability**: Standard biomarker names work across different labs
4. **Extensibility**: Easy to add new report types
5. **Debugging**: Both raw and normalized data are stored
6. **Clinical Validity**: No hallucinated values, only what exists in the input

## Support

For questions or to add support for additional report types, please contact the development team.
