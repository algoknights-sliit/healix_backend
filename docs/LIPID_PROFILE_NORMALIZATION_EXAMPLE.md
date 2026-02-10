# Serum Lipid Profile Normalization - Example

## Overview

This document shows the before and after of lipid profile normalization.

## Input: Raw OCR JSON

```json
{
  "raw_text": "ASIRI Laboratories... SERUM LIPID PROFILE...",
  "tables": [
    [
      ["SERUM CHOLESTEROL\n-\nTOTAL", "204.2", "mg/dL", "140.0\n-\n239.0"],
      ["SERUM TRIGLYCERIDES", "219.1", "mg/dL", "H\n10.0\n-\n200.0"],
      [" CHOLESTEROL-H.D.L.", "48.9", "mg/dL", "35.0\n-\n85.0"],
      ["CHOLESTEROL\n-\nNON\n-\nH.D.L", "155.3", "mg/dL", "55.0\n-\n189.0"],
      ["CHOLESTEROL L.D.L", "111.5", "mg/dL", "50.0\n- 159.0"],
      ["CHOLESTEROL\n-\nVLDL", "43.8", "mg/dL", "H\n10.0\n41.0\n-"],
      ["CHOL/HDL", "4.1", "", "2.0\n- 5.0"],
      ["LDL/HDL", "2.28", "", "0.01\n3.30"]
    ]
  ],
  "entities": []
}
```

## Output: Normalized JSON

```json
{
  "patient": {
    "name": "MRS. S N MANEL",
    "age_years": 58,
    "gender": "Female",
    "uhid": "310225949",
    "reference_no": "AHH2006215 / AHH2011800"
  },
  "report": {
    "type": "Serum Lipid Profile",
    "sample_type": "Serum",
    "sample_collected_at": "2025-06-12T06:50:00",
    "reported_at": "2025-06-12T17:04:00"
  },
  "biomarkers": [
    {
      "name": "Total Cholesterol",
      "value": 204.2,
      "unit": "mg/dL",
      "flag": null,
      "ref_range": [140.0, 239.0]
    },
    {
      "name": "Triglycerides",
      "value": 219.1,
      "unit": "mg/dL",
      "flag": "High",
      "ref_range": [10.0, 200.0]
    },
    {
      "name": "HDL Cholesterol",
      "value": 48.9,
      "unit": "mg/dL",
      "flag": null,
      "ref_range": [35.0, 85.0]
    },
    {
      "name": "Non-HDL Cholesterol",
      "value": 155.3,
      "unit": "mg/dL",
      "flag": null,
      "ref_range": [55.0, 189.0]
    },
    {
      "name": "LDL Cholesterol",
      "value": 111.5,
      "unit": "mg/dL",
      "flag": null,
      "ref_range": [50.0, 159.0]
    },
    {
      "name": "VLDL Cholesterol",
      "value": 43.8,
      "unit": "mg/dL",
      "flag": "High",
      "ref_range": [10.0, 41.0]
    },
    {
      "name": "Cholesterol/HDL Ratio",
      "value": 4.1,
      "unit": null,
      "flag": null,
      "ref_range": [2.0, 5.0]
    },
    {
      "name": "LDL/HDL Ratio",
      "value": 2.28,
      "unit": null,
      "flag": null,
      "ref_range": [0.01, 3.3]
    }
  ]
}
```

## Key Normalization Features

### 1. **Patient Information Extraction**
- Name: Extracted "MRS. S N MANEL"
- Age & Gender: Parsed "58 Y/F" → 58 years, Female
- UHID: Extracted from report header
- Reference No: Captured multi-part reference number

### 2. **Report Metadata**
- Auto-detected report type: "Serum Lipid Profile"
- Sample type: Extracted "Serum"
- Dates: Converted to ISO-8601 format

### 3. **Biomarker Name Normalization**
| OCR Text | Normalized Name |
|----------|----------------|
| SERUM CHOLESTEROL - TOTAL | Total Cholesterol |
| CHOLESTEROL-H.D.L. | HDL Cholesterol |
| CHOLESTEROL - NON - H.D.L | Non-HDL Cholesterol |
| CHOLESTEROL L.D.L | LDL Cholesterol |
| CHOLESTEROL - VLDL | VLDL Cholesterol |
| CHOL/HDL | Cholesterol/HDL Ratio |
| LDL/HDL | LDL/HDL Ratio |

### 4. **Flag Detection (H/L → High/Low)**
- Triglycerides: `"H\n10.0\n-\n200.0"` → flag: ` "High"`
- VLDL Cholesterol: `"H\n10.0\n41.0\n-"` → flag: `"High"`
- Other biomarkers: flag: `null`

### 5. **Unit Normalization**
- `"mg/dL"` → `"mg/dL"` (standardized capitalization)
- Ratios: Empty string → `null` (no units for ratios)

### 6. **Reference Range Parsing**
- Handles multi-line ranges: `"140.0\n-\n239.0"` → `[140.0, 239.0]`
- Removes flags from range: `"H\n10.0\n-\n200.0"` → `[10.0, 200.0]`

## Usage

```python
from app.services.normalization_service import normalize_report

# The service auto-detects report type
result = normalize_report(raw_ocr_data)

# Access normalized data
print(result["report"]["type"])  # "Serum Lipid Profile"
print(result["biomarkers"][1]["flag"])  # "High" for Triglycerides
```

## Comparison with FBC Reports

| Feature | FBC Reports | Lipid Profile |
|---------|-------------|---------------|
| Report Type | Full Blood Count | Serum Lipid Profile |
| Patient Fields | name, age, gender, ref_doctor, service_ref_no | name, age, gender, uhid, reference_no |
| Report Fields | type, sample_collected_at, printed_at | type, sample_type, sample_collected_at, reported_at |
| Biomarker Fields | name, value, unit, absolute, ref_range | name, value, unit, flag, ref_range |
| Special Handling | Differential count % inference | H/L flag extraction, ratio detection |

## Multi-Report Support

The system automatically detects report type using keywords:
- **FBC**: "FULL BLOOD COUNT", "FBC", "CBC"
- **Lipid Profile**: "SERUM LIPID PROFILE", "LIPID PROFILE", "LIPID PANEL"

Default: If unclear, defaults to Full Blood Count for backward compatibility.
